#!/usr/bin/env python3
"""Optional real ViZDoom bridge: Netta Lee writes the policy it lives through.

Only this module needs ViZDoom. The exact generated source is executed on every
possible compact observation before play. Its resulting table is a complete,
finite memoization of that program; no handwritten policy chooses actions.
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


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


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
    return config


def observations(config):
    schema = config["observation"]
    return [{"health": health, "ammo": ammo, "scene": scene}
            for health, ammo, scene in itertools.product(schema["health_values"], schema["ammo_values"], schema["scene_values"])]


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
    results = judge_batch(source, observations=[{"obs": obs} for obs in inputs], actions=list(ACTION_NAMES))
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
    return {"accepted": reactive, "status": "ready" if reactive else "unreactive",
            "reason": "" if reactive else "the same action for every observation",
            "rows": rows, "table": table, "behavior_hash": fingerprint(table),
            "source_hash": hashlib.sha256(source.encode()).hexdigest()}


def check_table(policy, config):
    expected = {observation_key(obs) for obs in observations(config)}
    table = policy.get("table", {})
    if set(table) != expected or any(value not in ACTION_NAMES for value in table.values()):
        raise ValueError("policy must map every compact observation to one literal action")
    if policy.get("behavior_hash") != fingerprint(table):
        raise ValueError("policy action table changed after source execution")


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
    score = (weights["kill_weight"] * totals["kills"] - weights["damage_weight"] * totals["damage"]
             - weights["ammo_weight"] * totals["ammo_spent"])
    return {"score": score, "normalized": 0.5 + 0.5 * math.tanh(score / weights["scale"]),
            "formula": "0.5 + 0.5*tanh((kill_weight*kills - damage_weight*damage - ammo_weight*ammo_spent)/scale)"}


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
    try:
        game.init()
        save_frame(game, output / "frame_000.png")
        initial = snapshot(game, variables)
        with (output / "trajectory.jsonl").open("w", encoding="utf-8") as journal:
            while not game.is_episode_finished() and steps < config["max_decisions"]:
                before = snapshot(game, variables)
                obs = perceive(before, game.get_screen_width(), config)
                action = policy["table"][observation_key(obs)]
                vector = [name == action for name in ACTION_NAMES]
                raw_reward = float(game.make_action(vector, config["decision_quantum"]))
                after = snapshot(game, variables)
                changes = {"kills": max(0.0, after["variables"]["kills"] - before["variables"]["kills"]),
                           "damage": max(0.0, before["variables"]["health"] - after["variables"]["health"]),
                           "ammo_spent": max(0.0, before["variables"]["ammo"] - after["variables"]["ammo"]),
                           "engine_reward": raw_reward}
                for name, value in changes.items():
                    totals[name] += value
                journal.write(canonical({"step": steps, "before": before, "observation": obs, "action": action,
                                         "buttons": vector, "after": after, "consequences": changes}) + "\n")
                counts[action] += 1
                steps += 1
                if steps in {1, 16, 64, config["max_decisions"]}:
                    save_frame(game, output / ("frame_%03d.png" % steps))
        result = {"seed": seed, "decisions": steps, "actions": dict(counts), "initial": initial,
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
            "totals": {key: sum(item["totals"][key] for item in episodes) for key in episodes[0]["totals"]},
            "reward": {"normalized": sum(item["reward"]["normalized"] for item in episodes) / len(episodes),
                       "aggregation": "arithmetic mean over every specified game seed"}}


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
    if not play:
        receipt["reward"] = None
    receipt["training_applied"] = bool(learn and receipt["reward"] is not None)
    if receipt["training_applied"]:
        diagnostic = None if policy["accepted"] else policy.get("judge", {
            "status": policy["status"], "reason": policy.get("reason", ""), "error_line": policy.get("error_line")})
        organism.observe(generated, receipt["reward"], receipt["runtime_ok"], policy.get("error_line"),
                         behavior=policy.get("behavior_hash"), diagnostic=diagnostic)
    receipt["state_after"] = fingerprint(organism.state_dict())
    if not learn and receipt["state_after"] != before:
        raise RuntimeError("frozen Doom evaluation changed the organism")
    write_json(output / "receipt.json", receipt)
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["train", "evaluate", "check", "doctor"],
                        help="check executes generated code on all observations without the game engine")
    parser.add_argument("--state", type=Path)
    parser.add_argument("--island", type=Path, help="Birth island for a new training state")
    parser.add_argument("--config", type=Path, default=ROOT / "doom.json")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--episodes", "--attempts", type=int, default=16, help="Generated policy attempts; invalid attempts also count")
    parser.add_argument("--seed", type=int, default=701)
    parser.add_argument("--game-seed", type=int, help="Independent first engine seed; defaults to seed + 100000")
    parser.add_argument("--episode-repeats", type=int, default=1,
                        help="Play each unchanged policy on this many consecutive engine seeds, then learn once")
    parser.add_argument("--decisions", type=int, help="Override the configuration's episode decision budget")
    parser.add_argument("--visible", action="store_true")
    args = parser.parse_args(argv)
    if args.command != "doctor" and args.state is None:
        parser.error("--state is required for check, train, and evaluate")
    if not 1 <= args.episodes <= 10000 or not 0 <= args.seed <= 2**30:
        parser.error("episodes must be 1..10000 and seed 0..2**30")
    game_seed = args.seed + 100000 if args.game_seed is None else args.game_seed
    if not 0 <= game_seed <= 2**30 or not 1 <= args.episode_repeats <= 16:
        parser.error("game seed must be 0..2**30 and episode repeats 1..16")
    config = load_config(args.config)
    if args.decisions is not None:
        if not 1 <= args.decisions <= 10000:
            parser.error("decisions must be 1..10000")
        config["max_decisions"] = args.decisions
    # Dependency failure is reported before generating or updating a life.
    engine_version = None
    if args.command != "check":
        try:
            import vizdoom as vzd
            engine_version = vzd.__version__
        except ImportError:
            parser.error("install the optional bridge: python -m pip install -r requirements-doom.txt")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    if args.command != "check":
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
        reference = {"full": [program_key(p) for p in programs], "active": [], "shapes": [],
                     "chunks": {}, "outcomes": [], "behaviors": []}
        organism = Organism(programs, seed=args.seed, mode="control", _reference=reference)
    else:
        parser.error("supply an existing state, or --island when training a new one")
    reference = prepare_reference(organism, config)
    if args.command == "train" or new_state:
        organism.reference["control"] = reference
    if new_state:
        organism.save(args.state)
    offset = organism.stats["games"] if args.command == "train" else 0
    organism.save(output / "initial-state.json")
    write_json(output / "corpus-policies.json", reference)
    write_json(output / "manifest.json", {"config": config, "config_file_sha256": file_hash(args.config),
               "seed": args.seed, "attempt_offset": offset, "attempts": args.episodes, "learning": args.command == "train",
               "game_seed": game_seed, "episode_repeats": args.episode_repeats,
               "vizdoom": engine_version, "bridge_sha256": file_hash(__file__),
               "engine_execution": args.command != "check",
               "organism_sha256": file_hash(ROOT / "nettalee.py"), "initial_state": fingerprint(organism.state_dict()),
               "policy_scope": "one unchanged generated program per episode; all 24 inputs exhaustively memoized"})
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
               "mean_reward_per_attempt": (sum(record["reward"] for record in records) / len(records)
                                            if all(record["reward"] is not None for record in records) else None),
               "state_after": fingerprint(organism.state_dict()), "learning": args.command == "train"})
    return 2 if any(record["status"] == "engine_unavailable" for record in records) else 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--episode-worker"]:
        request = json.load(sys.stdin)
        if request["operation"] == "probe":
            probe_engine(request["config"], request["seed"], Path(request["output"]), request["visible"])
        elif request["operation"] == "episode":
            run_episode(request["policy"], request["config"], request["seed"], Path(request["output"]), request["visible"])
        else:
            raise ValueError("unknown engine worker operation")
    else:
        raise SystemExit(main())
