#!/usr/bin/env python3
"""Doomer: Netta Lee writes policies for Doom Generic or optional ViZDoom.

The Generic backend uses the vendored C engine and an external IWAD. The exact source is executed on every
possible legacy compact observation before play. The optional temporal sensor
executes previously unseen inputs on demand in the same bounded Python judge.
"""
import argparse
from collections import Counter
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import re
import signal
import struct
import subprocess
import sys
import zlib

from nettalee import Organism, judge_batch, program_key, read_island

ROOT = Path(__file__).resolve().parent
ACTION_NAMES = ("turn_left", "turn_right", "move_forward", "strafe_left", "strafe_right", "shoot")
BUTTON_NAMES = ("TURN_LEFT", "TURN_RIGHT", "MOVE_FORWARD", "MOVE_LEFT", "MOVE_RIGHT", "ATTACK")
VARIABLE_NAMES = {"health": "HEALTH", "ammo": "SELECTED_WEAPON_AMMO", "x": "POSITION_X",
                  "y": "POSITION_Y", "angle": "ANGLE", "kills": "KILLCOUNT"}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def fingerprint(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_text(path, text):
    path = Path(path)
    temporary = path.with_name(path.name + ".pending-" + str(os.getpid()))
    with temporary.open("w", encoding="utf-8") as stream:
        stream.write(text)
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def write_json(path, value):
    atomic_text(path, json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def write_trajectory(output, lines):
    """Publish a completed immutable record before its compatibility pathname."""
    content = "".join(lines)
    digest = hashlib.sha256(content.encode()).hexdigest()
    filename = "trajectory-" + digest + ".jsonl"
    immutable = Path(output) / filename
    if immutable.exists():
        if file_hash(immutable) != digest:
            raise RuntimeError("existing immutable trajectory does not match its content hash")
    else:
        atomic_text(immutable, content)
    if file_hash(immutable) != digest:
        raise RuntimeError("completed trajectory failed readback")
    atomic_text(Path(output) / "trajectory.jsonl", content)
    return {"file": filename, "sha256": digest, "rows": len(lines)}


def load_config(path):
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    if config.get("format") != 1 or not re.fullmatch(r"[a-zA-Z0-9_]+", config.get("scenario", "")):
        raise ValueError("unsupported Doom configuration")
    if config.get("actions") != dict(zip(ACTION_NAMES, BUTTON_NAMES)):
        raise ValueError("six literal action/button mappings required")
    obs = config["observation"]
    if obs.get("health_thresholds") != [25, 75] or obs.get("health_values") != [25, 60, 100]:
        raise ValueError("health schema must match the code island")
    if obs.get("ammo_values") != [0, 10] or obs.get("scene_values") != ["empty", "left", "center", "right"]:
        raise ValueError("ammo/scene schema must match the code island")
    if obs.get("excluded_labels") != ["DoomPlayer", "Blood", "BulletPuff"]:
        raise ValueError("perception excludes player and two transient effects")
    for key, limit in (("decision_quantum", 16), ("max_decisions", 10000)):
        if type(config[key]) is not int or not 1 <= config[key] <= limit:
            raise ValueError("invalid " + key)
    reward = config["reward"]
    for key in ("kill_weight", "damage_weight", "ammo_weight", "scale"):
        if type(reward[key]) not in (int, float) or not math.isfinite(reward[key]) or reward[key] <= 0:
            raise ValueError("reward coefficients must be positive finite numbers")
    if config.get("sensor", "legacy") not in {"legacy", "temporal"}:
        raise ValueError("Doom sensor must be legacy or temporal")
    if config.get("reward_mode", "legacy") not in {"legacy", "attributed", "combat"}:
        raise ValueError("Doom reward mode must be legacy, attributed, or combat")
    return config


def observations(config):
    schema = config["observation"]
    base = [{"health": health, "ammo": ammo, "scene": scene}
            for health, ammo, scene in itertools.product(schema["health_values"], schema["ammo_values"], schema["scene_values"])]
    if config.get("sensor", "legacy") == "legacy":
        return base
    # Public novelty/validity probes, not an exhaustive temporal truth table.
    # Live inputs outside this set are executed on demand, never approximated.
    return [dict(obs, previous_action=action, moved=bool(index & 1),
                 took_damage=bool(index & 2),
                 distance="none" if obs["scene"] == "empty" else ("near" if index & 1 else "far"))
            for obs in base for index, action in enumerate(("none",) + ACTION_NAMES)]


def temporal_observation(raw, previous, action):
    variables = raw["variables"]
    old = previous["variables"] if previous else variables
    focus = raw.get("focus")
    return dict(raw["observation"], previous_action=action or "none",
                moved=math.hypot(variables["x"] - old["x"], variables["y"] - old["y"]) >= 1.0,
                took_damage=variables["player_damage_received"] > old["player_damage_received"],
                distance="none" if not focus else "near" if focus["distance"] <= 256 else "far")


def observation_key(obs):
    return canonical(obs)


def perceive(raw, width, config):
    if not isinstance(width, (int, float)) or not math.isfinite(width) or width <= 0:
        raise ValueError("positive screen width required")
    values = raw["variables"]
    if any(not math.isfinite(values[name]) for name in ("health", "ammo")):
        raise ValueError("finite health and ammunition observations required")
    health = 25 if values["health"] <= 25 else 60 if values["health"] <= 75 else 100
    labels = [item for item in raw["labels"] if item["name"] not in config["observation"]["excluded_labels"]]
    focus = max(labels, key=lambda item: (item["width"] * item["height"], -item["id"]), default=None)
    scene = "empty"
    if focus is not None:
        x = focus["x"] + focus["width"] / 2
        scene = "left" if x < width / 3 else "right" if x > 2 * width / 3 else "center"
    return {"health": health, "ammo": 10 if values["ammo"] > 0 else 0, "scene": scene}


def validate_policy(source, config):
    """Return only actions actually produced by the unchanged source."""
    rows = []
    inputs = observations(config)
    results = []
    for offset in range(0, len(inputs), 48):
        results.extend(judge_batch(source, observations=[{"obs": obs} for obs in inputs[offset:offset+48]],
                                   actions=list(ACTION_NAMES)))
    if len(results) != len(inputs):
        raise RuntimeError("incomplete execution evidence")
    for obs, result in zip(inputs, results):
        if not result.get("accepted") or result.get("action") not in ACTION_NAMES:
            return {"accepted": False, "status": result.get("status", "invalid_action"),
                    "error_line": result.get("error_line"), "reason": result.get("reason", "invalid action"),
                    "failed_observation": obs, "judge": result, "rows": rows}
        rows.append({"observation": obs, "action": result["action"],
                     "executed_lines": result.get("metrics", {}).get("executed_lines", [])})
    table = {observation_key(row["observation"]): row["action"] for row in rows}
    reactive = len(set(table.values())) >= 2
    policy = {"accepted": reactive, "status": "ready" if reactive else "unreactive",
            "reason": "" if reactive else "the same action for every observation",
            "rows": rows, "table": table, "behavior_hash": fingerprint(table),
            "source_hash": hashlib.sha256(source.encode()).hexdigest()}
    if config.get("sensor", "legacy") == "temporal":
        policy.update(source=source, sensor="temporal", novelty_scope="168 fixed probes; live inputs executed on demand")
    return policy


def check_table(policy, config):
    expected = {observation_key(obs) for obs in observations(config)}
    table = policy.get("table", {})
    if set(table) != expected or any(value not in ACTION_NAMES for value in table.values()):
        raise ValueError("policy must map every compact observation to one literal action")
    if policy.get("behavior_hash") != fingerprint(table):
        raise ValueError("policy action table changed after source execution")
    if config.get("sensor", "legacy") == "temporal":
        if policy.get("sensor") != "temporal" or not isinstance(policy.get("source"), str):
            raise ValueError("temporal policy requires unchanged source")
        if hashlib.sha256(policy["source"].encode()).hexdigest() != policy.get("source_hash"):
            raise ValueError("temporal policy source changed after validation")


def prepare_reference(organism, config):
    """Recompute only if the corpus, perception, or execution judge changed."""
    provenance = fingerprint({"programs": organism.programs, "observation": config["observation"],
                              "actions": config["actions"], "judge": file_hash(ROOT / "nettalee.py")})
    cached = organism.reference.get("control")
    if cached and cached.get("provenance") == provenance:
        return cached
    records = []
    for index, source in enumerate(organism.programs):
        policy = validate_policy(source, config)
        if not policy["accepted"]:
            raise ValueError("island policy %d failed: %s" % (index, policy["status"]))
        records.append({"index": index, "source_hash": hashlib.sha256(source.encode()).hexdigest(),
                        "behavior_hash": policy["behavior_hash"], "rows": policy["rows"]})
    return {"provenance": provenance, "records": records,
            "behavior_hashes": sorted({r["behavior_hash"] for r in records})}


def snapshot(game, variables):
    state = game.get_state()
    return {"tic": int(game.get_episode_time()), "terminal": bool(game.is_episode_finished()),
            "dead": bool(game.is_player_dead()),
            "variables": {key: float(game.get_game_variable(value)) for key, value in variables.items()},
            "labels": [] if state is None else [
                {"id": int(label.object_id), "name": label.object_name, "x": int(label.x), "y": int(label.y),
                 "width": int(label.width), "height": int(label.height)} for label in state.labels]}


def save_frame(game, path):
    state = game.get_state()
    if state is None:
        return False
    rgb = state.screen_buffer
    height, width, channels = rgb.shape
    if channels != 3:
        raise ValueError("RGB24 framebuffer required")
    def chunk(kind, payload):
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xffffffff)
    rows = b"".join(b"\0" + rgb[row].tobytes() for row in range(height))
    content = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    Path(path).write_bytes(content + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b""))
    return True


def reward_from_totals(totals, config):
    weights = config["reward"]
    if config.get("reward_mode", "legacy") == "combat":
        score = (totals["player_damage_dealt"] / 100.0 - weights["damage_weight"] * totals["player_damage_received"]
                 - weights["ammo_weight"] * totals["ammo_spent"])
        return {"score": score,
                "normalized": (0.0 if totals["player_damage_dealt"] <= 0 else
                               0.5 + 0.5 * math.tanh(score / weights["scale"])),
                "formula": "0 if player_damage_dealt<=0 else 0.5+0.5*tanh((player_damage_dealt/100 - damage_weight*player_damage_received - ammo_weight*ammo_spent)/scale)"}
    if config.get("reward_mode", "legacy") == "attributed":
        score = (totals["player_damage_dealt"] / 100.0 - weights["damage_weight"] * totals["player_damage_received"]
                 - weights["ammo_weight"] * totals["ammo_spent"])
        return {"score": score, "normalized": 0.5 + 0.5 * math.tanh(score / weights["scale"]),
                "formula": "0.5 + 0.5*tanh((player_damage_dealt/100 - damage_weight*player_damage_received - ammo_weight*ammo_spent)/scale)"}
    score = (weights["kill_weight"] * totals["kills"] - weights["damage_weight"] * totals["damage"]
             - weights["ammo_weight"] * totals["ammo_spent"])
    return {"score": score, "normalized": 0.5 + 0.5 * math.tanh(score / weights["scale"]),
            "formula": "0.5 + 0.5*tanh((kill_weight*kills - damage_weight*damage - ammo_weight*ammo_spent)/scale)"}


def configure_backend(config, backend=None, iwad=None, engine=None, episode=None, level=None, skill=None):
    config = dict(config)
    config["backend"] = backend or config.get("backend", "generic")
    if config["backend"] not in {"generic", "vizdoom"}:
        raise ValueError("unknown Doom backend")
    if config["backend"] == "vizdoom":
        return config
    generic = dict(config.get("generic", {}))
    wad = iwad or os.environ.get("NETTA_DOOM_IWAD") or generic.get("iwad") or ROOT / "doom" / "freedoom1.wad"
    wad = Path(wad).expanduser().resolve()
    if not wad.is_file():
        raise ValueError("Doom Generic needs a game IWAD: pass --iwad PATH or set NETTA_DOOM_IWAD")
    with wad.open("rb") as stream:
        header = stream.read(12)
        if len(header) != 12:
            raise ValueError("truncated IWAD")
        magic, count, offset = struct.unpack("<4sII", header)
        if magic != b"IWAD" or not 1 <= count <= 100000 or offset + count * 16 > wad.stat().st_size:
            raise ValueError("a complete IWAD file is required")
        stream.seek(offset)
        lumps = {stream.read(16)[8:].rstrip(b"\0") for _ in range(count)}
    if b"MAP01" not in lumps and b"E1M1" not in lumps:
        raise ValueError("IWAD has neither a Doom 1 nor a Doom 2 starting map")
    generic.update(iwad=str(wad), iwad_sha256=file_hash(wad), commercial=b"MAP01" in lumps,
                   episode=episode if episode is not None else generic.get("episode", 1),
                   map=level if level is not None else generic.get("map", 1),
                   skill=skill if skill is not None else generic.get("skill", 3))
    if any(type(generic[key]) is not int for key in ("episode", "map", "skill")) or not (
            1 <= generic["episode"] <= 4 and 1 <= generic["map"] <= 32 and 1 <= generic["skill"] <= 5):
        raise ValueError("episode 1..4, map 1..32, and skill 1..5 required")
    map_name = ("MAP%02d" % generic["map"] if generic["commercial"] else
                "E%dM%d" % (generic["episode"], generic["map"]))
    if map_name.encode("ascii") not in lumps:
        raise ValueError("IWAD does not contain " + map_name)
    binary = Path(engine or generic.get("engine") or ROOT / "doom" / "bin" / "doomgeneric").expanduser().resolve()
    generic["engine"] = str(binary)
    generic["custom_engine"] = bool(engine or generic.get("custom_engine", False))
    config["generic"] = generic
    return config


def environment_contract(config):
    contract = {"backend": config["backend"], "decision_quantum": config["decision_quantum"],
                "reward": config["reward"]}
    if config["backend"] == "generic":
        contract.update({key: config["generic"][key] for key in
                         ("iwad_sha256", "commercial", "episode", "map", "skill")})
        contract["perception"] = "generic-los-angular-v1"
    else:
        contract.update(scenario=config["scenario"], perception="vizdoom-label-thirds-v1")
    if config.get("sensor", "legacy") == "temporal":
        contract["perception"] = "generic-los-temporal-v2"
        contract["sensor"] = "temporal"
    if config.get("reward_mode", "legacy") == "attributed":
        contract["reward_mode"] = "player-attributed-v1"
    if config.get("reward_mode", "legacy") == "combat":
        contract["reward_mode"] = "player-combat-engagement-v1"
    return contract


def saved_environment(path):
    """Read checked metadata without constructing or changing the organism."""
    if path is None or not Path(path).exists():
        return None
    try:
        wrapped = json.loads(Path(path).read_text(encoding="utf-8"))
        payload = json.dumps(wrapped["body"], ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        if hashlib.sha256(payload.encode()).hexdigest() != wrapped["sha256"]:
            return None  # The complete organism loader will reject this snapshot.
        return wrapped["body"]["reference"].get("environment")
    except (KeyError, TypeError, ValueError):
        return None


def bind_environment(config, environment=None, backend=None, iwad=None, engine=None, episode=None, level=None, skill=None):
    environment = environment or {}
    config = configure_backend(config, backend or environment.get("backend"), iwad, engine,
                               episode if episode is not None else environment.get("episode"),
                               level if level is not None else environment.get("map"),
                               skill if skill is not None else environment.get("skill"))
    if config["backend"] != "generic" and (config.get("sensor", "legacy") != "legacy" or
                                             config.get("reward_mode", "legacy") != "legacy"):
        raise ValueError("temporal observations and attributed reward require the Generic backend")
    if environment and environment != environment_contract(config):
        raise ValueError("saved Doom environment differs; use a new state for another backend, IWAD, map, or control setup")
    return config


def ensure_generic_engine(config, output):
    settings = config["generic"]
    binary = Path(settings["engine"])
    sources = [ROOT / "doom" / "headless.c", ROOT / "doom" / "Makefile", *ROOT.joinpath("doom", "src").glob("*.[ch]")]
    if not settings["custom_engine"] and (not binary.exists() or any(p.stat().st_mtime > binary.stat().st_mtime for p in sources)):
        result = subprocess.run(["make", "-C", str(ROOT / "doom"), "-j2"], capture_output=True, text=True, timeout=60)
        (output / "build.stdout.txt").write_text(result.stdout, encoding="utf-8")
        (output / "build.stderr.txt").write_text(result.stderr, encoding="utf-8")
        if result.returncode:
            raise RuntimeError("Doom Generic compilation failed; see build.stderr.txt")
    if not binary.is_file():
        raise ValueError("Doom Generic executable is missing: " + str(binary))


class GenericSession:
    def __init__(self, config, seed, output):
        settings = config["generic"]
        warp = [str(settings["map"])] if settings["commercial"] else [str(settings["episode"]), str(settings["map"])]
        self.output = Path(output)
        self.command = [settings["engine"], "-iwad", settings["iwad"], "-warp", *warp, "-skill", str(settings["skill"]),
                        "-config", str(self.output / "game.cfg"), "-netta-seed", str(seed)]
        self.process = subprocess.Popen(self.command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=sys.stderr, text=True, cwd=self.output, bufsize=1)

    def receive(self):
        while True:
            line = self.process.stdout.readline()
            if not line:
                raise RuntimeError("Doom Generic protocol ended, return code " + str(self.process.poll()))
            if line.startswith("NETTA "):
                return json.loads(line[6:])
            print(line, end="", flush=True)

    def send(self, command):
        self.process.stdin.write(command + "\n")
        self.process.stdin.flush()
        return self.receive()

    def frame(self, filename):
        ppm = self.output / Path(filename).with_suffix(".ppm").name
        self.send("frame " + ppm.name)
        header, dimensions, maximum, pixels = ppm.read_bytes().split(b"\n", 3)
        width, height = map(int, dimensions.split())
        if header != b"P6" or maximum != b"255" or len(pixels) != width * height * 3:
            raise ValueError("invalid engine framebuffer")
        def chunk(tag, data):
            return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)
        rows = b"".join(b"\0" + pixels[y * width * 3:(y + 1) * width * 3] for y in range(height))
        png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        (self.output / filename).write_bytes(png + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b""))
        ppm.unlink()

    def close(self):
        if self.process.poll() is None:
            try:
                self.process.stdin.write("quit\n")
                self.process.stdin.flush()
                self.process.wait(timeout=3)
            except (BrokenPipeError, subprocess.TimeoutExpired):
                self.process.kill()
                self.process.wait()
        self.process.stdin.close()
        self.process.stdout.close()


def run_generic(config, seed, output, policy=None):
    if policy is not None:
        check_table(policy, config)
    session = GenericSession(config, seed, output)
    try:
        initial = before = session.receive()
        session.frame("frame_000.png")
        settings = config["generic"]
        meta = {"backend": "generic", "engine": "doomgeneric", "seed": seed,
                "rng_phase_offset": seed % 256, "command": session.command,
                "engine_sha256": file_hash(settings["engine"]), "iwad_sha256": settings["iwad_sha256"],
                "perception": "largest angular live monster in 90-degree FOV with P_CheckSight; thirds at +/-15 degrees",
                "kills_metric": "Doom killcount (includes monster infighting)",
                "initial": initial}
        if policy is None:
            meta.update(status="ready", executed_actions=0, gameplay=False)
            write_json(output / "engine-check.json", meta)
            return meta
        totals = {"kills": 0.0, "damage": 0.0, "ammo_spent": 0.0, "engine_reward": None,
                  "player_damage_dealt": 0, "player_direct_kills": 0, "player_damage_received": 0}
        counts, steps = Counter(), 0
        cache = {observation_key(row["observation"]): (row["action"], row.get("executed_lines", []))
                 for row in policy.get("rows", [])}
        temporal = config.get("sensor", "legacy") == "temporal"
        previous, previous_action, executed_lines, policy_failure = None, None, set(), None
        trajectory = []
        while not before["terminal"] and steps < config["max_decisions"]:
            obs = temporal_observation(before, previous, previous_action) if temporal else before["observation"]
            key = observation_key(obs)
            if temporal and key not in cache:
                result = judge_batch(policy["source"], [{"obs": obs}], list(ACTION_NAMES))[0]
                if not result.get("accepted") or result.get("action") not in ACTION_NAMES:
                    policy_failure = dict(result, failed_observation=obs)
                    break
                cache[key] = result["action"], result.get("metrics", {}).get("executed_lines", [])
            action = cache[key][0] if temporal else policy["table"][key]
            used_lines = cache.get(key, (None, []))[1]
            executed_lines.update(used_lines)
            after = session.send("step %s %d" % (action, config["decision_quantum"]))
            changes = {"kills": max(0, after["variables"]["kills"] - before["variables"]["kills"]),
                       "damage": max(0, before["variables"]["health"] - after["variables"]["health"]),
                       "ammo_spent": sum(max(0, a - b) for a, b in zip(before["variables"]["ammo_inventory"],
                                                                      after["variables"]["ammo_inventory"])),
                       "engine_reward": None}
            for name in ("player_damage_dealt", "player_direct_kills", "player_damage_received"):
                changes[name] = after["variables"][name] - before["variables"][name]
            for name in ("kills", "damage", "ammo_spent", "player_damage_dealt", "player_direct_kills", "player_damage_received"):
                totals[name] += changes[name]
            line = canonical({"step": steps, "before": before, "observation": obs, "action": action,
                              "executed_lines": used_lines, "after": after, "consequences": changes}) + "\n"
            trajectory.append(line)
            previous, previous_action = before, action
            before = after
            counts[action] += 1
            steps += 1
            if steps in {1, 16, 64, config["max_decisions"]}:
                session.frame("frame_%03d.png" % steps)
        trajectory_record = write_trajectory(output, trajectory)
        session.frame("frame_final.png")
        meta.update(decisions=steps, actions=dict(counts), final=before, totals=totals,
                    reward=reward_from_totals(totals, config), engine_total_reward=None,
                    executed_lines=sorted(executed_lines), policy_failure=policy_failure, trajectory=trajectory_record,
                    sensor=config.get("sensor", "legacy"),
                    attribution="capped actual monster health lost directly to console player; infighting and barrel inflictors excluded",
                    policy_source_sha256=policy.get("source_hash"), policy_behavior_sha256=policy["behavior_hash"])
        if policy_failure is not None:
            meta["reward"] = {"normalized": 0.0, "score": None, "formula": "failed live policy"}
        write_json(output / "episode.json", meta)
        return meta
    finally:
        session.close()


def setup_game(config, seed, visible=False):
    import vizdoom as vzd
    game = vzd.DoomGame()
    buttons = [getattr(vzd.Button, config["actions"][name]) for name in ACTION_NAMES]
    variables = {name: getattr(vzd.GameVariable, value) for name, value in VARIABLE_NAMES.items()}
    scenario = Path(vzd.scenarios_path) / (config["scenario"] + ".cfg")
    game.load_config(str(scenario))
    game.set_mode(vzd.Mode.PLAYER)
    game.set_seed(seed)
    game.set_window_visible(visible)
    game.set_sound_enabled(False)
    game.set_screen_format(vzd.ScreenFormat.RGB24)
    game.set_labels_buffer_enabled(True)
    game.set_objects_info_enabled(False)
    game.set_sectors_info_enabled(False)
    game.set_available_buttons(buttons)
    game.set_available_game_variables(list(variables.values()))
    game.set_episode_timeout(config["decision_quantum"] * config["max_decisions"] + 10)
    return game, variables, scenario, vzd.__version__


def probe_engine(config, seed, output, visible=False):
    """Initialize and read a real framebuffer without applying any policy."""
    game, variables, scenario, version = setup_game(config, seed, visible)
    try:
        game.init()
        state = game.get_state()
        if state is None:
            raise RuntimeError("engine did not expose an initial game state")
        result = {"status": "ready", "seed": seed, "vizdoom": version,
                  "executed_actions": 0, "gameplay": False,
                  "screen_shape": list(state.screen_buffer.shape),
                  "initial": snapshot(game, variables),
                  "scenario_config_sha256": file_hash(scenario),
                  "scenario_wad_sha256": file_hash(scenario.with_suffix(".wad"))}
        save_frame(game, output / "engine-initial.png")
        write_json(output / "engine-check.json", result)
        return result
    finally:
        game.close()


def run_episode(policy, config, seed, output, visible=False):
    check_table(policy, config)
    game, variables, scenario, version = setup_game(config, seed, visible)
    totals = {"kills": 0.0, "damage": 0.0, "ammo_spent": 0.0, "engine_reward": 0.0}
    counts = Counter()
    steps = 0
    lines_by_input = {observation_key(row["observation"]): row.get("executed_lines", [])
                      for row in policy.get("rows", [])}
    executed_lines, trajectory = set(), []
    try:
        game.init()
        save_frame(game, output / "frame_000.png")
        initial = snapshot(game, variables)
        while not game.is_episode_finished() and steps < config["max_decisions"]:
            before = snapshot(game, variables)
            obs = perceive(before, game.get_screen_width(), config)
            action = policy["table"][observation_key(obs)]
            used_lines = lines_by_input.get(observation_key(obs), [])
            executed_lines.update(used_lines)
            vector = [name == action for name in ACTION_NAMES]
            raw_reward = float(game.make_action(vector, config["decision_quantum"]))
            after = snapshot(game, variables)
            changes = {"kills": max(0.0, after["variables"]["kills"] - before["variables"]["kills"]),
                       "damage": max(0.0, before["variables"]["health"] - after["variables"]["health"]),
                       "ammo_spent": max(0.0, before["variables"]["ammo"] - after["variables"]["ammo"]),
                       "engine_reward": raw_reward}
            for name, value in changes.items():
                totals[name] += value
            line = canonical({"step": steps, "before": before, "observation": obs, "action": action,
                              "executed_lines": used_lines, "buttons": vector, "after": after,
                              "consequences": changes}) + "\n"
            trajectory.append(line)
            counts[action] += 1
            steps += 1
            if steps in {1, 16, 64, config["max_decisions"]}:
                save_frame(game, output / ("frame_%03d.png" % steps))
        trajectory_record = write_trajectory(output, trajectory)
        result = {"seed": seed, "decisions": steps, "actions": dict(counts), "initial": initial,
                  "executed_lines": sorted(executed_lines), "trajectory": trajectory_record,
                  "final": snapshot(game, variables), "totals": totals, "reward": reward_from_totals(totals, config),
                  "engine_total_reward": float(game.get_total_reward()), "vizdoom": version,
                  "policy_source_sha256": policy.get("source_hash"),
                  "policy_behavior_sha256": policy["behavior_hash"],
                  "scenario_config_sha256": file_hash(scenario), "scenario_wad_sha256": file_hash(scenario.with_suffix(".wad"))}
        write_json(output / "episode.json", result)
        return result
    finally:
        game.close()


def execute_worker(request, output, filename, timeout=180):
    """Keep native engine failures outside the organism's learning process."""
    output = Path(output).resolve()
    request = dict(request, output=str(output))
    command = [sys.executable, str(Path(__file__).resolve()), "--episode-worker"]
    write_json(output / "engine-request.json", request)
    with subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, cwd=output, start_new_session=os.name == "posix") as process:
        try:
            stdout, stderr = process.communicate(canonical(request), timeout=timeout)
            returncode = process.returncode
        except subprocess.TimeoutExpired:
            if os.name == "posix":
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            else:
                process.kill()
            stdout, stderr = process.communicate()
            returncode = "timeout"
    (output / "engine.stdout.txt").write_text(stdout, encoding="utf-8")
    (output / "engine.stderr.txt").write_text(stderr, encoding="utf-8")
    write_json(output / "engine-process.json", {"command": command, "returncode": returncode,
               "bridge_sha256": file_hash(__file__), "expected_result": filename, "timeout_seconds": timeout})
    if returncode != 0 or not (output / filename).exists():
        return {"error": "engine failed before completing " + request["operation"], "returncode": returncode}
    return json.loads((output / filename).read_text(encoding="utf-8"))


def execute_episode(policy, config, seed, output, visible=False):
    check_table(policy, config)
    request = {"operation": "episode", "policy": policy, "config": config, "seed": seed, "visible": visible}
    return execute_worker(request, output, "episode.json")


def preflight(config, seed, output, visible=False):
    """Native availability is tested before any learning or state writes."""
    Path(output).mkdir()
    result = execute_worker({"operation": "probe", "config": config, "seed": seed, "visible": visible},
                            output, "engine-check.json", timeout=30)
    write_json(Path(output) / "receipt.json", result)
    return result


def evaluate_policy(policy, config, seeds, output, visible=False):
    episodes = []
    for index, seed in enumerate(seeds):
        directory = output if len(seeds) == 1 else output / ("episode_%03d" % index)
        if directory != output:
            directory.mkdir()
        episode = execute_episode(policy, config, seed, directory, visible)
        if "error" in episode:
            return dict(episode, failed_seed=seed, completed_episodes=episodes)
        episodes.append(episode)
    if len(episodes) == 1:
        return episodes[0]
    return {"episodes": episodes, "episode_seeds": seeds,
            "executed_lines": sorted({line for episode in episodes for line in episode.get("executed_lines", [])}),
            "policy_failure": next((episode.get("policy_failure") for episode in episodes if episode.get("policy_failure")), None),
            "totals": {key: (sum(item["totals"][key] for item in episodes)
                             if all(item["totals"][key] is not None for item in episodes) else None)
                       for key in episodes[0]["totals"]},
            "reward": {"normalized": (0.0 if any(item.get("policy_failure") for item in episodes) else
                                       sum(item["reward"]["normalized"] for item in episodes) / len(episodes)),
                       "aggregation": "zero on any live policy failure; otherwise arithmetic mean over every specified game seed"}}


def attempt(organism, config, reference, generation_seed, episode_seed, output, learn, visible=False, play=True,
            episode_repeats=1):
    if type(episode_repeats) is not int or not 1 <= episode_repeats <= 16:
        raise ValueError("episode_repeats must be 1..16")
    output.mkdir()
    before = fingerprint(organism.state_dict())
    generated = organism.generate(seed=generation_seed)
    source = generated["source"]
    receipt = {"generation_seed": generation_seed, "episode_seed": episode_seed,
               "episode_seeds": list(range(episode_seed, episode_seed + episode_repeats)),
               "state_before": before, "strategy": generated["strategy"], "tokens": generated["tokens"],
               "source_hash": hashlib.sha256(source.encode()).hexdigest() if source is not None else None,
               "learn": learn, "reward": 0.0, "runtime_ok": False}
    if source is not None:
        (output / "candidate.py").write_bytes(source.encode())
    if source is None or generated["truncated"]:
        policy = {"accepted": False, "status": "encoding" if source is None else "truncated"}
    else:
        policy = validate_policy(source, config)
    receipt["validation"] = policy
    receipt["status"] = policy["status"]
    receipt["runtime_ok"] = bool(policy["accepted"])
    if policy["accepted"]:
        if policy["behavior_hash"] in reference["behavior_hashes"]:
            receipt["status"] = "corpus_behavior_replay"
        elif play:
            episode = evaluate_policy(policy, config, receipt["episode_seeds"], output, visible)
            receipt["episode"] = episode
            receipt["status"] = "engine_unavailable" if "error" in episode else "played"
            receipt["reward"] = None if "error" in episode else episode["reward"]["normalized"]
            if episode.get("policy_failure"):
                receipt["status"], receipt["runtime_ok"] = "live_policy_failure", False
    if not play:
        receipt["reward"] = None
    receipt["training_applied"] = bool(learn and receipt["reward"] is not None)
    if receipt["training_applied"]:
        diagnostic = None if policy["accepted"] else policy.get("judge", {
            "status": policy["status"], "reason": policy.get("reason", ""), "error_line": policy.get("error_line")})
        if receipt.get("episode", {}).get("policy_failure"):
            diagnostic = receipt["episode"]["policy_failure"]
        feedback = {}
        if callable(getattr(organism, "configure_control_learning", None)):
            episode = receipt.get("episode", {})
            feedback = {"executed_lines": episode.get("executed_lines", []),
                        "environment_observed": receipt["status"] in {"played", "live_policy_failure"}}
        organism.observe(generated, receipt["reward"], receipt["runtime_ok"],
                         diagnostic.get("error_line") if diagnostic else policy.get("error_line"),
                         behavior=policy.get("behavior_hash"), diagnostic=diagnostic, **feedback)
    receipt["state_after"] = fingerprint(organism.state_dict())
    if not learn and receipt["state_after"] != before:
        raise RuntimeError("frozen Doom evaluation changed the organism")
    write_json(output / "receipt.json", receipt)
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Game data is external: use your Doom IWAD or the freely distributable
Freedoom IWAD from https://freedoom.github.io/download.html. No WAD is bundled.
The Generic engine builds locally from doom/; it needs make and a C compiler.

Examples (from the project directory):
  python doomer.py doctor --iwad /path/to/freedoom2.wad --map 2 --output runs/doctor
  python doomer.py train --island corpora/doom.txt --state states/my-doom.json \\
    --iwad /path/to/freedoom2.wad --map 2 --attempts 24 --decisions 512 --output runs/train
  python doomer.py evaluate --state states/my-doom.json \\
    --iwad /path/to/freedoom2.wad --map 2 --seed 90001 --output runs/evaluate
NETTA_DOOM_IWAD may supply the IWAD path in place of --iwad.
Vanilla Doom has 256 RNG phases; seeds separated by 256 select the same phase.
""")
    parser.add_argument("command", choices=["train", "evaluate", "check", "doctor"],
                        help="check executes generated code on all observations without the game engine")
    parser.add_argument("--state", type=Path)
    parser.add_argument("--island", type=Path, help="Birth island for a new training state")
    parser.add_argument("--config", type=Path, default=ROOT / "doom.json")
    parser.add_argument("--backend", choices=["generic", "vizdoom"], help="Default from doom.json; no automatic backend fallback")
    parser.add_argument("--iwad", type=Path, help="External Doom/Freedoom IWAD; also NETTA_DOOM_IWAD or doom/freedoom1.wad")
    parser.add_argument("--engine", type=Path, help="Doom Generic executable; default builds vendored doom/ with make and cc")
    parser.add_argument("--episode", type=int, help="Doom 1 episode, 1..4")
    parser.add_argument("--map", type=int, dest="level", help="Map number")
    parser.add_argument("--skill", type=int, help="Engine difficulty, 1..5")
    parser.add_argument("--sensor", choices=["legacy", "temporal"], help="Explicit sensor contract; temporal requires a separate state")
    parser.add_argument("--reward-mode", choices=["legacy", "attributed", "combat"], help="Explicit reward contract; a changed contract requires a separate state")
    parser.add_argument("--control-learning", choices=["legacy", "quality", "trace", "both"],
                        help="Training only: opt in to a learned outcome head, executed-branch credit, or both")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--episodes", "--attempts", type=int, default=16, help="Generated policy attempts; invalid attempts also count")
    parser.add_argument("--seed", type=int, default=701)
    parser.add_argument("--game-seed", type=int, help="Independent first engine seed; defaults to seed + 100000")
    parser.add_argument("--episode-repeats", type=int, default=1,
                        help="Play each unchanged policy on this many consecutive engine seeds, then learn once")
    parser.add_argument("--decisions", type=int, help="Override the configuration's episode decision budget")
    parser.add_argument("--visible", action="store_true")
    parser.add_argument("--sequence-memory", action=argparse.BooleanOptionalAction,
                        default=None, help="Training only: acquired recurrent memory of ordered code units")
    args = parser.parse_args(argv)
    if args.sequence_memory is not None and args.command != "train":
        parser.error("--sequence-memory is a training option; evaluation preserves the saved settings")
    if args.command != "doctor" and args.state is None:
        parser.error("--state is required for check, train, and evaluate")
    if args.control_learning is not None and args.command != "train":
        parser.error("--control-learning is a training option; evaluation preserves the saved settings")
    if not 1 <= args.episodes <= 10000 or not 0 <= args.seed <= 2**30:
        parser.error("episodes must be 1..10000 and seed 0..2**30")
    game_seed = args.seed + 100000 if args.game_seed is None else args.game_seed
    if not 0 <= game_seed <= 2**30 or not 1 <= args.episode_repeats <= 16:
        parser.error("game seed must be 0..2**30 and episode repeats 1..16")
    config = load_config(args.config)
    if args.sensor is not None:
        config["sensor"] = args.sensor
    if args.reward_mode is not None:
        config["reward_mode"] = args.reward_mode
    if args.command != "check":
        try:
            config = bind_environment(config, saved_environment(args.state), args.backend, args.iwad, args.engine,
                                      args.episode, args.level, args.skill)
        except ValueError as exc:
            parser.error(str(exc))
    if args.decisions is not None:
        if not 1 <= args.decisions <= 10000:
            parser.error("decisions must be 1..10000")
        config["max_decisions"] = args.decisions
    # Dependency failure is reported before generating or updating a life.
    engine_version = None
    if args.command != "check" and config["backend"] == "vizdoom":
        try:
            import vizdoom as vzd
            engine_version = vzd.__version__
        except ImportError:
            parser.error("install the optional bridge: python -m pip install -r requirements-doom.txt")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    if args.command != "check":
        if config["backend"] == "generic":
            ensure_generic_engine(config, output)
        engine = preflight(config, game_seed, output / "engine-check", args.visible)
        if "error" in engine or args.command == "doctor":
            write_json(output / "summary.json", {"status": "engine_unavailable" if "error" in engine else "engine_ready",
                       "engine": engine, "learning": False, "played": 0, "state_written": False})
            print(canonical({"status": "engine_unavailable" if "error" in engine else "engine_ready"}), flush=True)
            return 2 if "error" in engine else 0
    new_state = not args.state.exists()
    if args.state.exists():
        organism = Organism.load(args.state)
        if organism.mode != "control":
            parser.error("Doom needs a separate control-island state")
        if args.island and read_island(args.island) != organism.programs:
            parser.error("island differs from the saved specialization")
    elif args.command in {"train", "check"} and args.island:
        programs = read_island(args.island)
        reference = {"kind": "doom", "full": [program_key(p) for p in programs], "active": [], "shapes": [],
                     "chunks": {}, "outcomes": [], "behaviors": []}
        organism = Organism(programs, seed=args.seed, mode="control", _reference=reference)
    else:
        parser.error("supply an existing state, or --island when training a new one")
    if args.sequence_memory is not None:
        organism.configure_sequence_memory(args.sequence_memory)
    if args.control_learning is not None:
        organism.configure_control_learning(quality=args.control_learning in {"quality", "both"},
                                             executed_credit=args.control_learning in {"trace", "both"})
    reference = prepare_reference(organism, config)
    if args.command == "train" or new_state:
        organism.reference["control"] = reference
        organism.reference["kind"] = "doom"
        if args.command == "train":
            organism.reference["environment"] = environment_contract(config)
    if new_state:
        organism.save(args.state)
    offset = organism.stats["games"] if args.command == "train" else 0
    organism.save(output / "initial-state.json")
    write_json(output / "corpus-policies.json", reference)
    write_json(output / "manifest.json", {"config": config, "config_file_sha256": file_hash(args.config),
               "seed": args.seed, "attempt_offset": offset, "attempts": args.episodes, "learning": args.command == "train",
               "game_seed": game_seed, "episode_repeats": args.episode_repeats,
               **({"sequence_memory_override": args.sequence_memory} if args.sequence_memory is not None else {}),
               "vizdoom": engine_version, "bridge_sha256": file_hash(__file__),
               "engine_execution": args.command != "check",
               "organism_sha256": file_hash(ROOT / "nettalee.py"), "initial_state": fingerprint(organism.state_dict()),
               "policy_scope": ("one unchanged generated program per episode; 168 public novelty probes and exact on-demand live execution"
                                if config.get("sensor", "legacy") == "temporal" else
                                "one unchanged generated program per episode; all 24 inputs exhaustively memoized")})
    records = []
    for index in range(args.episodes):
        item = attempt(organism, config, reference, args.seed + offset + index,
                       game_seed + (offset + index) * args.episode_repeats,
                       output / ("attempt_%05d" % index), args.command == "train", args.visible,
                       args.command != "check", args.episode_repeats)
        records.append(item)
        if args.command == "train":
            organism.save(args.state)
        print(canonical({"attempt": index, "status": item["status"], "reward": item["reward"],
                         "kills": item.get("episode", {}).get("totals", {}).get("kills", 0)}), flush=True)
        if item["status"] == "engine_unavailable":
            break
    organism.save(output / "final-state.json")
    played = [record for record in records if record["status"] == "played"]
    write_json(output / "summary.json", {"attempts": len(records), "played": len(played),
               "statuses": dict(Counter(record["status"] for record in records)),
               "kills": sum(record["episode"]["totals"]["kills"] for record in played),
               "kills_metric": "Doom killcount (includes monster infighting)" if config.get("backend") == "generic" else "ViZDoom KILLCOUNT",
               "mean_reward_per_attempt": (sum(record["reward"] for record in records) / len(records)
                                            if all(record["reward"] is not None for record in records) else None),
               "state_after": fingerprint(organism.state_dict()), "learning": args.command == "train"})
    return 2 if any(record["status"] == "engine_unavailable" for record in records) else 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--episode-worker"]:
        request = json.load(sys.stdin)
        if request["config"].get("backend") == "generic":
            run_generic(request["config"], request["seed"], Path(request["output"]), request.get("policy"))
        elif request["operation"] == "probe":
            probe_engine(request["config"], request["seed"], Path(request["output"]), request["visible"])
        elif request["operation"] == "episode":
            run_episode(request["policy"], request["config"], request["seed"], Path(request["output"]), request["visible"])
        else:
            raise ValueError("unknown engine worker operation")
    else:
        raise SystemExit(main())
