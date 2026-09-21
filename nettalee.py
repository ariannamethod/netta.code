#!/usr/bin/env python3
"""Netta Lee: learned byte units, lived continuations, execution feedback.

One-file, standard-library Python organism. The complete release also contains
its process judge and its small JSON caller below. GPL-3.0-or-later.
"""
import argparse
import ast
from collections import Counter, defaultdict
import hashlib
import json
import math
import os
from pathlib import Path
import random
import re
import sys
import tempfile

SPECIES = "nettalee"
DEFAULT_ORDER = 6
FORMAT = 3
BOUNDARY = "# === PROGRAM ==="
BOS, EOS = -1, -2


def digest(value):
    if isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def read_island(path):
    """Framing is removed; every byte inside each program is retained."""
    text = Path(path).read_bytes().decode("utf-8")
    programs, lines = [], []
    for line in text.splitlines(keepends=True):
        if line.rstrip("\r\n") == BOUNDARY:
            if lines:
                program = "".join(lines)
                if program.strip():
                    programs.append(program)
                lines = []
        else:
            lines.append(line)
    if lines and "".join(lines).strip():
        programs.append("".join(lines))
    if len(programs) < 2:
        raise ValueError("an island needs at least two framed programs")
    if sum(len(p.encode()) for p in programs) > 2_000_000:
        raise ValueError("island exceeds 2 MB")
    return programs


class Units:
    """Netta's deterministic byte-pair growth, separately within each script."""
    def __init__(self, programs=None, merges=256, pairs=None):
        self.pairs = [] if pairs is None else [tuple(p) for p in pairs]
        self.expansions = [bytes([i]) for i in range(256)]
        for a, b in self.pairs:
            if not (0 <= a < len(self.expansions) and 0 <= b < len(self.expansions)):
                raise ValueError("invalid unit ancestry")
            self.expansions.append(self.expansions[a] + self.expansions[b])
        if programs is not None:
            streams = [list(p.encode("utf-8")) for p in programs]
            for _ in range(merges):
                counts = Counter()
                for stream in streams:
                    counts.update(zip(stream, stream[1:]))
                viable = [(n, pair) for pair, n in counts.items()
                          if n >= 3 and len(self.expansions[pair[0]]) +
                          len(self.expansions[pair[1]]) <= 24]
                if not viable:
                    break
                _, pair = min(viable, key=lambda x: (-x[0], x[1]))
                token = len(self.expansions)
                self.expansions.append(self.expansions[pair[0]] + self.expansions[pair[1]])
                self.pairs.append(pair)
                streams = [self.merge(s, pair, token) for s in streams]

    @staticmethod
    def merge(stream, pair, token):
        out, i = [], 0
        while i < len(stream):
            if i + 1 < len(stream) and (stream[i], stream[i + 1]) == pair:
                out.append(token)
                i += 2
            else:
                out.append(stream[i])
                i += 1
        return out

    def encode(self, source):
        stream = list(source.encode("utf-8"))
        for i, pair in enumerate(self.pairs, 256):
            stream = self.merge(stream, pair, i)
        return stream

    def decode(self, tokens):
        return b"".join(self.expansions[t] for t in tokens if t >= 0)


class OutcomeHead:
    """Small learned tanh network scoring continuation outcomes, from birth.

    Inputs describe unit identity/context/counts, without Python syntax facts.
    Online binary outcome updates reach all layers; no pretrained parameters.
    """
    DIM, HIDDEN = 32, 16

    def __init__(self, seed=0, state=None):
        if state is not None:
            self.w, self.b, self.v, self.bias, self.steps = (
                state[k] for k in ("w", "b", "v", "bias", "steps"))
        else:
            rng = random.Random(seed ^ 0x4E45545441)
            self.w = [[rng.gauss(0, .16) for _ in range(self.DIM)]
                      for _ in range(self.HIDDEN)]
            self.b = [0.0] * self.HIDDEN
            self.v = [0.0] * self.HIDDEN
            self.bias = 0.0
            self.steps = 0

    def state(self):
        return {k: getattr(self, k) for k in ("w", "b", "v", "bias", "steps")}

    @staticmethod
    def features(history, token, depth, frequency, total, position):
        x = [0.0] * 32
        pairs = [(token, 1)]
        for i, previous in enumerate(reversed(history[-4:]), 2):
            pairs.append(((previous + 3) * 65537 + token + 3, i))
        for value, salt in pairs:
            h = ((value + 7) * 0x9E3779B1 ^ salt * 0x85EBCA77) & 0xffffffff
            x[h % 27] += .5 if h & 0x80000000 else -.5
        x[27] = depth / 8
        x[28] = frequency / total
        x[29] = min(1.0, position / 256)
        x[30] = 1.0 if token == EOS else 0.0
        x[31] = 1.0
        return x

    def forward(self, x):
        h = [math.tanh(sum(a * b for a, b in zip(row, x)) + bias)
             for row, bias in zip(self.w, self.b)]
        logit = self.bias + sum(a * b for a, b in zip(self.v, h))
        return logit, h

    def update(self, x, target):
        logit, h = self.forward(x)
        p = 1 / (1 + math.exp(-max(-20, min(20, logit))))
        # Balanced per-program sampling bounds long-program credit.
        rate = .025 / math.sqrt(1 + self.steps / 4000)
        error = target - p
        old = self.v[:]
        for j in range(self.HIDDEN):
            delta = error * old[j] * (1 - h[j] * h[j])
            self.v[j] += rate * (error * h[j] - .001 * self.v[j])
            self.b[j] += rate * delta
            for i, value in enumerate(x):
                if value:
                    self.w[j][i] += rate * delta * value
        self.bias += rate * error
        self.steps += 1


class Organism:
    def __init__(self, programs, seed=1, order=DEFAULT_ORDER, merges=256,
                 mode="general", _pairs=None, _reference=None):
        if not 1 <= order <= 8 or not 0 <= merges <= 1024:
            raise ValueError("order must be 1..8; merges must be 0..1024")
        if mode not in ("general", "art", "control") or len(programs) < 2:
            raise ValueError("invalid mode or fewer than two programs")
        if mode == "control" and _reference is None:
            raise ValueError("a control island needs the environment's explicit reference")
        if any(not isinstance(p, str) or len(p.encode()) > 8192 for p in programs):
            raise ValueError("programs must be strings of at most 8192 bytes")
        self.programs = programs[:]
        self.seed, self.order, self.mode = seed, order, mode
        self.units = Units(programs if _pairs is None else None, merges, _pairs)
        self.rng = random.Random(seed)
        self.tables = defaultdict(Counter)
        for program in programs:
            history = [BOS]
            for token in self.units.encode(program) + [EOS]:
                for depth in range(min(order, len(history)) + 1):
                    context = tuple(history[-depth:]) if depth else ()
                    self.tables[context][token] += 1
                history.append(token)
        self.reference = (build_reference(programs, judge, mode)
                          if _reference is None else _reference)
        self.credit = {}
        self.head = OutcomeHead(seed)
        self.syntax_head = OutcomeHead(seed ^ 0x53594E)
        # Acquired local transitions, not an archive of executable programs.
        self.lived = defaultdict(Counter)
        self.visits = {}
        self.exploration = .5
        self.memory_strength = 1.5
        # Locality is a learned choice too. These are sampling settings over
        # the same lived continuations; none contains Python grammar or code.
        self.search = [[0.0, 0.0] for _ in range(5)]
        self.explore_search = [[0.0, 0.0] for _ in range(5)]
        self.seen = set()
        self.behaviors = set()
        self.stats = {"games": 0, "accepted": 0, "runtime_ok": 0,
                      "source_replay": 0, "experience_replay": 0, "behavior_replay": 0}

    def _distribution(self, history, rng, streak, strategy, exploring=False):
        locality = [(self.order, 0.0, 64), (self.order, .02, 24),
                    (self.order, .04, 12), (max(1, self.order - 2), .02, 24),
                    (max(1, self.order - 2), .08, 8)]
        maximum, exploration, corridor = locality[strategy]
        available = []
        for depth in range(min(maximum, len(history)), -1, -1):
            context = tuple(history[-depth:]) if depth else ()
            base = self.tables.get(context)
            lived = None if exploring else self.lived.get(context)
            if base or lived:
                counts = Counter(base or {})
                if lived:
                    scale = self.memory_strength * max(1, sum(counts.values())) / sum(lived.values())
                    for token, count in lived.items():
                        counts[token] += scale * count
                available.append((context, counts))
        context, counts = available[0]
        veto = None
        # Real Netta-style escape: a corridor exit must choose another token.
        if len(counts) == 1 and streak >= corridor:
            singleton = next(iter(counts))
            for shorter, alternatives in available[1:]:
                if any(t != singleton for t in alternatives):
                    context, counts, veto = shorter, alternatives, singleton
                    break
        elif len(available) > 1 and rng.random() < exploration:
            options = [entry for entry in available[1:] if len(entry[1]) > 1]
            if options:
                context, counts = options[0]
        candidates = [(t, n) for t, n in counts.items() if t != veto]
        candidates.sort(key=lambda item: (-item[1], item[0]))
        candidates = candidates[:24]
        if len(candidates) == 1:
            return candidates[0][0], 1, None
        total = sum(n for _, n in candidates)
        entries = []
        for token, count in candidates:
            x = OutcomeHead.features(history, token, len(context), count, total, len(history))
            logit, _ = self.head.forward(x)
            key = tuple(history[-3:]) + (token,)
            wins, trials = self.credit.get(key, (0.0, 0.0))
            association = (wins + 1) / (trials + 2)
            evidence = trials / (trials + 4)
            value = math.log(count) / .9 + 2.5 * evidence * (association - .5)
            # The neural common bias cancels in the normalized distribution.
            value += .8 * max(-4, min(4, logit - self.head.bias))
            syntax_logit, _ = self.syntax_head.forward(x)
            value += .8 * max(-4, min(4, syntax_logit - self.syntax_head.bias))
            entries.append((token, value, x, key))
        peak = max(e[1] for e in entries)
        weights = [math.exp(e[1] - peak) for e in entries]
        target = rng.random() * sum(weights)
        chosen = len(entries) - 1
        for i, weight in enumerate(weights):
            target -= weight
            if target < 0:
                chosen = i
                break
        token, _, x, key = entries[chosen]
        return token, len(entries), {"key": key, "x": x,
                                   "context": context, "token": token}

    def generate(self, seed=None):
        rng = self.rng if seed is None else random.Random(seed)
        exploring = rng.random() < self.exploration
        search = self.explore_search if exploring else self.search
        merit = [((wins + .5) / (trials + 10)) ** 2 for wins, trials in search]
        probabilities = [.10 / len(merit) + .90 * value / sum(merit) for value in merit]
        pick, strategy = rng.random(), len(merit) - 1
        for i, probability in enumerate(probabilities):
            pick -= probability
            if pick < 0:
                strategy = i
                break
        history, tokens, choices, streak, size = [BOS], [], [], 0, 0
        line = 1
        terminated = False
        for _ in range(1024):
            token, alternatives, choice = self._distribution(history, rng, streak, strategy, exploring)
            if alternatives > 1:
                choice["line"] = line
                choice["end_line"] = line + (self.units.expansions[token].count(b"\n") if token >= 0 else 0)
                choice["byte_start"] = size
                choice["byte_end"] = size + (len(self.units.expansions[token]) if token >= 0 else 0)
                choices.append(choice)
                streak = 0
            else:
                streak += 1
            if token == EOS:
                terminated = True
                break
            tokens.append(token)
            history.append(token)
            size += len(self.units.expansions[token])
            line += self.units.expansions[token].count(b"\n")
            if size > 4096:
                break
        raw = self.units.decode(tokens)
        try:
            source = raw.decode("utf-8")
        except UnicodeDecodeError:
            # Never silently replace malformed generated bytes.
            return {"source": None, "raw_hex": raw.hex(), "tokens": tokens,
                    "choices": choices, "truncated": not terminated, "strategy": strategy,
                    "exploring": exploring}
        return {"source": source, "tokens": tokens, "choices": choices,
                "truncated": not terminated, "strategy": strategy, "exploring": exploring}

    def game(self, seed=None, learn=True):
        if self.mode == "control":
            raise ValueError("control islands play through their environment bridge")
        rng_state = self.rng.getstate() if not learn and seed is None else None
        try:
            generated = self.generate(seed)
        finally:
            if rng_state is not None:
                self.rng.setstate(rng_state)
        source = generated["source"]
        if source is None:
            result = {"status": "encoding", "accepted": False, "output": "",
                      "metrics": {}, "reason": "generated bytes are not UTF-8"}
        elif generated["truncated"]:
            result = {"status": "truncated", "accepted": False, "output": "",
                      "metrics": {}, "reason": "program did not emit its end unit"}
        else:
            result = judge(source, mode=self.mode)
        runtime_ok = bool(result["accepted"])
        status = result["status"]
        key, shape = None, None
        novelty = None
        if runtime_ok:
            novelty = classify_source(source, result.get("metrics", {}), self.reference)
            key, shape = novelty["key"], novelty["shape"]
            if novelty["status"] == "source_replay":
                status = "source_replay"
            elif novelty["status"] == "behavior_replay":
                status = "behavior_replay"
            elif key in self.seen:
                status = "experience_replay"
            elif result.get("metrics", {}).get("behavior_hash") in self.behaviors:
                status = "behavior_replay"
            else:
                status = "accepted"
        accepted = status == "accepted"
        reward = 1.0 if accepted else 0.0
        behavior = result.get("metrics", {}).get("behavior_hash")
        productive = bool(runtime_ok and novelty and novelty["status"] == "novel")
        visits = self.visits.get(behavior, 0) if productive else 0
        learning_reward = (1.0 if accepted else .25 / math.sqrt(1 + visits)) if productive else 0.0
        record = {"source": source, "source_hash": digest(source) if source is not None else None,
                  "status": status, "accepted": accepted, "reward": reward,
                  "productive": productive, "learning_reward": learning_reward,
                  "runtime_ok": runtime_ok, "program_key": key,
                  "new_shape": bool(novelty and novelty["new_shape"]),
                  "novelty": novelty,
                  "new_behavior": bool(behavior and behavior not in self.behaviors),
                  "tokens": generated["tokens"], "decisions": len(generated["choices"]),
                  "strategy": generated["strategy"],
                  "exploring": generated["exploring"],
                  "judge": result}
        if learn:
            self.stats["games"] += 1
            self.stats["runtime_ok"] += int(runtime_ok)
            if status in self.stats:
                self.stats[status] += 1
            error_line = result.get("error_line")
            self._learn(generated, learning_reward, runtime_ok, error_line, result)
            if productive and behavior:
                self.visits[behavior] = visits + 1
            if accepted:
                self._acquire(generated["tokens"])
                self.seen.add(key)
                if behavior:
                    self.behaviors.add(behavior)
        return record

    def _acquire(self, tokens):
        history, counted = [BOS], set()
        for token in tokens + [EOS]:
            for depth in range(1, min(self.order, len(history)) + 1):
                context = tuple(history[-depth:])
                key = context + (token,)
                if key not in counted:
                    self.lived[context][token] += 1
                    counted.add(key)
            history.append(token)

    def _learn(self, generated, reward, runtime_ok, error_line=None, result=None):
        exploring = generated.get("exploring", False)
        search = (self.explore_search if exploring else self.search)[generated["strategy"]]
        if search[1] >= 128:
            search[0] *= .99
            search[1] *= .99
        search[0] += float(reward >= 1.0) if exploring and self.mode != "control" else reward
        search[1] += 1
        # Localize failed decisions using CPython's actual error position.
        chosen = generated["choices"]
        if not runtime_ok:
            exact = []
            if result and error_line and result.get("error_column") is not None and generated["source"]:
                lines = generated["source"].encode().splitlines(keepends=True)
                if 1 <= error_line <= len(lines):
                    start = sum(map(len, lines[:error_line - 1])) + result["error_column"]
                    end_line = result.get("error_end_line") or error_line
                    end_column = result.get("error_end_column")
                    end = (sum(map(len, lines[:end_line - 1])) + end_column
                           if end_column is not None and 1 <= end_line <= len(lines) else start + 1)
                    end = max(start + 1, end)
                    exact = [c for c in chosen if c.get("byte_start", -1) < end
                             and c.get("byte_end", -1) > start]
                    # A parser often points immediately after a missing unit.
                    if result.get("status") == "syntax_error":
                        prior = [c for c in chosen if c.get("byte_end", -1) <= start]
                        exact = prior[-1:] + exact
            if exact:
                chosen = exact[-4:]
            elif error_line:
                preceding = [c for c in chosen if c["line"] <= error_line]
                chosen = preceding[-4:] if preceding else chosen[:1]
            else:
                chosen = chosen[-4:]
        unique = {choice["key"]: choice["x"] for choice in chosen}
        for association, x in unique.items():
            wins, trials = self.credit.get(association, (0.0, 0.0))
            if trials >= 64:
                wins *= .95
                trials *= .95
            self.credit[association] = [wins + reward, trials + 1]
        # Each decision is counted once; loops cannot multiply reward.
        values = list(unique.values())
        for i in range(min(12, len(values))):
            self.head.update(values[i * len(values) // min(12, len(values))], float(runtime_ok))
        if result and result.get("status") not in ("encoding", "truncated", "timeout", "worker_error"):
            syntax_ok = result.get("exception_type") not in ("SyntaxError", "IndentationError", "TabError")
            syntax_ok = syntax_ok and result.get("status") not in ("syntax", "syntax_error")
            grammar_choices = generated["choices"] if syntax_ok else chosen
            grammar_values = list({tuple(c["key"]): c["x"] for c in grammar_choices}.values())
            for i in range(min(12, len(grammar_values))):
                self.syntax_head.update(grammar_values[i * len(grammar_values) // min(12, len(grammar_values))], float(syntax_ok))

    def observe(self, generated, reward, runtime_ok, error_line=None, behavior=None, diagnostic=None):
        """Acquire a bounded outcome supplied by an external environment.

        Used by the Doom bridge after real actions and consequences. A raw
        generated attempt is charged once, including attempts that fail to run.
        """
        if self.mode != "control":
            raise ValueError("external outcomes require a control island")
        if not isinstance(reward, (int, float)) or not math.isfinite(reward) or not 0 <= reward <= 1:
            raise ValueError("environment reward must be finite and in [0, 1]")
        if behavior is not None and (not isinstance(behavior, str) or not re.fullmatch(r"[0-9a-f]{64}", behavior)):
            raise ValueError("environment behavior must be a SHA-256 action-table hash")
        self.stats["games"] += 1
        self.stats["runtime_ok"] += int(bool(runtime_ok))
        self.stats["accepted"] += int(reward > 0)
        self.stats["environment_reward"] = self.stats.get("environment_reward", 0.0) + reward
        self._learn(generated, reward, bool(runtime_ok), error_line, diagnostic)
        if runtime_ok and behavior:
            self.visits[behavior] = self.visits.get(behavior, 0) + 1
            if reward > .5 and behavior not in self.behaviors:
                self._acquire(generated["tokens"])
                self.behaviors.add(behavior)

    def state_dict(self):
        return {"format": FORMAT, "species": SPECIES,
                "python_random_version": 3, "programs": self.programs,
                "seed": self.seed, "order": self.order, "mode": self.mode,
                "pairs": self.units.pairs, "rng": self.rng.getstate(),
                "head": self.head.state(), "stats": self.stats,
                "syntax_head": self.syntax_head.state(), "exploration": self.exploration,
                "memory_strength": self.memory_strength,
                "lived": [[list(k), sorted(v.items())] for k, v in sorted(self.lived.items())],
                "visits": self.visits,
                "search": self.search,
                "explore_search": self.explore_search,
                "reference": self.reference,
                "credit": [[list(k), v] for k, v in sorted(self.credit.items())],
                "seen": sorted(self.seen), "behaviors": sorted(self.behaviors)}

    def save(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        body = self.state_dict()
        payload = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        wrapped = json.dumps({"sha256": digest(payload), "body": body}, ensure_ascii=False,
                             sort_keys=True, separators=(",", ":"))
        fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
                stream.write(wrapped + "\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    @classmethod
    def load(cls, path):
        path = Path(path)
        if path.stat().st_size > 64_000_000:
            raise ValueError("snapshot exceeds 64 MB")
        wrapped = json.loads(path.read_text(encoding="utf-8"))
        body = wrapped["body"]
        payload = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        if wrapped["sha256"] != digest(payload):
            raise ValueError("snapshot checksum mismatch")
        if body["format"] not in (2, FORMAT) or body["species"] != SPECIES:
            raise ValueError("incompatible snapshot")
        organism = cls(body["programs"], body["seed"], body["order"],
                       mode=body["mode"], _pairs=body["pairs"], _reference=body["reference"])
        organism.rng.setstate((body["rng"][0], tuple(body["rng"][1]), body["rng"][2]))
        organism.head = OutcomeHead(state=body["head"])
        if "syntax_head" in body:
            organism.syntax_head = OutcomeHead(state=body["syntax_head"])
        organism.exploration = body.get("exploration", .5)
        organism.memory_strength = body.get("memory_strength", 1.5)
        organism.lived = defaultdict(Counter, {tuple(k): Counter(dict(v)) for k, v in body.get("lived", [])})
        organism.visits = body.get("visits", {})
        organism.search = body["search"]
        organism.explore_search = body.get("explore_search", [[0.0, 0.0] for _ in range(5)])
        organism.credit = {tuple(k): v for k, v in body["credit"]}
        organism.seen = set(body["seen"])
        organism.behaviors = set(body["behaviors"])
        organism.stats = body["stats"]
        return organism

    def without_experience(self):
        return Organism(self.programs, self.seed, self.order, mode=self.mode,
                        _pairs=self.units.pairs, _reference=self.reference)


def summarize(records):
    counts = Counter(r["status"] for r in records)
    accepted = [r for r in records if r["accepted"]]
    return {"attempts": len(records), "accepted": len(accepted),
            "productive": sum(r.get("productive", False) for r in records),
            "unique_accepted": len({r["program_key"] for r in accepted}),
            "new_shapes": sum(r["new_shape"] for r in accepted),
            "statuses": dict(sorted(counts.items()))}


def run_cli():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="grow units and continuations from a TXT island")
    init.add_argument("--island", required=True)
    init.add_argument("--state", required=True)
    init.add_argument("--seed", type=int, default=1)
    init.add_argument("--order", type=int, default=DEFAULT_ORDER)
    init.add_argument("--merges", type=int, default=256)
    init.add_argument("--judge", choices=("general", "art"), default="general")
    play = sub.add_parser("play", help="generate, execute, acquire experience, save")
    play.add_argument("--state", required=True)
    play.add_argument("--games", type=int, default=100)
    play.add_argument("--log")
    play.add_argument("--explore", type=float, help="fraction of games devoted to searching the island (0..1)")
    sample = sub.add_parser("sample", help="sample with a fixed raw-attempt budget")
    sample.add_argument("--state", required=True)
    sample.add_argument("--attempts", type=int, default=32)
    sample.add_argument("--seed", type=int, default=10001)
    sample.add_argument("--out")
    sample.add_argument("--log")
    inspect = sub.add_parser("inspect")
    inspect.add_argument("--state", required=True)
    ask = sub.add_parser("ask", help="choose a specialization from editable JSON")
    ask.add_argument("request")
    ask.add_argument("--tools", required=True)
    ask.add_argument("--attempts", type=int, default=32)
    ask.add_argument("--seed", type=int, default=10001)
    ask.add_argument("--out")
    ask.add_argument("--log")
    args = parser.parse_args()
    if args.command == "init":
        if Path(args.state).exists():
            parser.error("state exists; choose a new path to preserve its experience")
        model = Organism(read_island(args.island), args.seed, args.order, args.merges, args.judge)
        model.save(args.state)
        print(json.dumps({"state": args.state, "programs": len(model.programs),
                          "units": len(model.units.expansions), "species": SPECIES}))
        return 0
    if args.command == "ask":
        config_path = Path(args.tools).resolve()
        call = select_state(args.request, json.loads(config_path.read_text(encoding="utf-8")))
        print(json.dumps(call, ensure_ascii=False), file=sys.stderr)
        if call["status"] != "selected":
            return 2
        args.state = str(config_path.parent / call["selection"]["state"])
    model = Organism.load(args.state)
    if args.command == "ask" and model.mode != call["selection"]["mode"]:
        parser.error("caller judge does not match selected snapshot")
    if args.command == "ask" and model.mode == "control":
        if not args.out:
            parser.error("Doom calls require --out DIRECTORY for episode records")
        bridge = Path(__file__).resolve().with_name("nettadoom.py")
        if not bridge.is_file():
            parser.error("install the optional nettadoom.py bridge beside this file")
        return subprocess.call([sys.executable, str(bridge), "evaluate", "--state", args.state,
                                "--episodes", str(args.attempts), "--seed", str(args.seed),
                                "--output", args.out])
    if args.command == "inspect":
        print(json.dumps({"species": SPECIES, "stats": model.stats, "mode": model.mode,
                          "programs": len(model.programs), "units": len(model.units.expansions),
                          "associations": len(model.credit), "neural_updates": model.head.steps,
                          "syntax_updates": model.syntax_head.steps, "exploration": model.exploration,
                          "lived_contexts": len(model.lived), "visited_behaviors": len(model.visits)}, indent=2))
        return 0
    learning = args.command == "play"
    if learning and args.explore is not None:
        if not 0 <= args.explore <= 1:
            parser.error("--explore must be between 0 and 1")
        model.exploration = args.explore
    attempts = args.games if learning else args.attempts
    if not 1 <= attempts <= 1_000_000:
        parser.error("attempt budget must be 1..1000000")
    statuses, unique = Counter(), set()
    completed = accepted_count = productive_count = shapes = 0
    task_statuses = Counter()
    def progress():
        result = {"attempts": completed, "accepted": accepted_count, "productive": productive_count,
                  "unique_accepted": len(unique), "new_shapes": shapes, "statuses": dict(sorted(statuses.items()))}
        if args.command == "ask":
            result.update(task_passed=task_statuses["passed"], task_statuses=dict(task_statuses))
        return result
    destination = None
    if not learning and args.out:
        destination = Path(args.out)
        destination.mkdir(parents=True, exist_ok=True)
    log = None
    if args.log:
        Path(args.log).parent.mkdir(parents=True, exist_ok=True)
        log = open(args.log, "a" if learning else "w", encoding="utf-8")
    try:
        for i in range(attempts):
            record = model.game(None if learning else args.seed + i, learn=learning)
            exportable = record["productive"]
            if args.command == "ask":
                record["task_check"] = check_task_output(call, record)
                task_statuses[record["task_check"]["status"]] += 1
                if call["task"]["status"] == "matched":
                    exportable = exportable and record["task_check"]["passed"]
            completed += 1
            statuses[record["status"]] += 1
            accepted_count += int(record["accepted"])
            productive_count += int(record["productive"])
            if record["accepted"]:
                unique.add(record["program_key"])
                shapes += int(record["new_shape"])
            if destination is not None and exportable:
                (destination / ("game_%06d.py" % (args.seed + i))).write_bytes(record["source"].encode())
            if log:
                log.write(json.dumps(record, ensure_ascii=False) + "\n")
                log.flush()
            if learning and (i + 1) % 50 == 0:
                model.save(args.state)
                print(json.dumps({"completed": i + 1, **progress()}), file=sys.stderr)
        if learning:
            model.save(args.state)
        print(json.dumps(progress(), ensure_ascii=False, indent=2))
        if args.command == "ask" and call["task"]["status"] == "matched" and not task_statuses["passed"]:
            return 3
        return 0
    except KeyboardInterrupt:
        if learning:
            model.save(args.state)
        print(json.dumps(progress(), ensure_ascii=False), file=sys.stderr)
        return 130
    finally:
        if log:
            log.close()


# Process judge and JSON caller are included below in each complete source.


"""Bounded CPython execution judge. Safe subset, not an OS security boundary."""
import ast
import builtins
import collections
import dis
import hashlib
import io
import json
import keyword
import math
import os
import subprocess
import sys
import tempfile
import warnings

RUNTIME_SOURCE_LIMIT = 32768
RUNTIME_STEP_LIMIT = 50000
RUNTIME_OUTPUT_LIMIT = 8192
RUNTIME_FILENAME = '<netta-island>'
_SAFE_FUNCTIONS = ('abs all any bool chr dict divmod enumerate float int len list max min '
                   'ord pow range reversed round set sorted str sum tuple zip').split()
_SAFE_METHODS = set(('append extend insert pop remove reverse sort copy count index clear '
                     'get keys values items setdefault update add discard union intersection difference '
                     'lower upper strip lstrip rstrip split join replace startswith endswith '
                     'capitalize title swapcase center ljust rjust isalpha isdigit isalnum isspace '
                     'partition rpartition splitlines zfill').split())
_ALLOWED_AST = {getattr(ast, name) for name in (
    'Module Expr Constant Name Load Store List Tuple Set Dict Assign AnnAssign AugAssign '
    'BinOp UnaryOp BoolOp Compare If IfExp For Break Continue Pass FunctionDef arguments arg '
    'Return Call keyword Attribute Subscript Slice ListComp SetComp DictComp GeneratorExp comprehension While Starred '
    'JoinedStr FormattedValue Add Sub Mult Div FloorDiv Mod Pow UAdd USub Not And Or Eq NotEq '
    'Lt LtE Gt GtE In NotIn Is IsNot BitAnd BitOr BitXor LShift RShift Invert'
).split()}
_COMPUTE_FUNCTIONS = set(_SAFE_FUNCTIONS) - {'range', 'enumerate', 'zip', 'reversed', 'list', 'tuple', 'dict', 'set', 'bool', 'str', 'int', 'float'}
_COMPUTE_OPS = {'BINARY_OP', 'BINARY_SUBSCR', 'COMPARE_OP', 'CONTAINS_OP', 'IS_OP',
                'UNARY_NEGATIVE', 'UNARY_INVERT', 'UNARY_NOT', 'LIST_APPEND', 'SET_ADD', 'MAP_ADD'}


class RuntimePolicyError(ValueError):
    pass


def _runtime_tree(source):
    if not isinstance(source, str) or len(source.encode('utf-8')) > RUNTIME_SOURCE_LIMIT:
        raise RuntimePolicyError('source size limit')
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', SyntaxWarning)
        tree = ast.parse(source, filename=RUNTIME_FILENAME, mode='exec')
    nodes = list(ast.walk(tree))
    if len(nodes) > 4000:
        raise RuntimePolicyError('AST size limit')
    functions = {n.name for n in nodes if isinstance(n, ast.FunctionDef)}
    called_names = {id(n.func) for n in nodes if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    for node in nodes:
        if type(node) not in _ALLOWED_AST:
            raise RuntimePolicyError('unsupported syntax: ' + type(node).__name__)
        if isinstance(node, (ast.Name, ast.arg)):
            name = node.id if isinstance(node, ast.Name) else node.arg
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and name in functions and id(node) not in called_names:
                raise RuntimePolicyError('functions are called directly, not used as data')
            if name.startswith('_'):
                raise RuntimePolicyError('private names unavailable')
        if isinstance(node, ast.FunctionDef):
            if node.name.startswith('_') or node.decorator_list:
                raise RuntimePolicyError('private functions/decorators unavailable')
        if isinstance(node, ast.Attribute):
            if not isinstance(node.ctx, ast.Load) or node.attr not in _SAFE_METHODS:
                raise RuntimePolicyError('attribute unavailable: ' + node.attr)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (str, bytes)) and len(node.value) > 8192:
                raise RuntimePolicyError('literal size limit')
            if isinstance(node.value, int) and node.value.bit_length() > 4096:
                raise RuntimePolicyError('integer literal size limit')
        if isinstance(node, ast.Call):
            if not isinstance(node.func, (ast.Name, ast.Attribute)):
                raise RuntimePolicyError('indirect callable unavailable')
            if isinstance(node.func, ast.Name):
                functions = {n.name for n in nodes if isinstance(n, ast.FunctionDef)}
                if node.func.id not in set(_SAFE_FUNCTIONS) | {'print'} | functions:
                    raise RuntimePolicyError('call unavailable: ' + node.func.id)
        if isinstance(node, ast.FormattedValue):
            if node.conversion not in (-1, 115, 114, 97):
                raise RuntimePolicyError('format conversion unavailable')
            if any(isinstance(part, (ast.Call, ast.GeneratorExp)) for part in ast.walk(node.value)):
                raise RuntimePolicyError('compute format expressions before formatting')
    return tree


def _runtime_plain(value, depth=0):
    """Bounded data view: never invokes repr on user-defined objects."""
    if depth > 5:
        return {'truncated': 'depth'}
    if value is None or type(value) in (bool, int, float, str):
        if type(value) is int and value.bit_length() > 4096:
            return {'integer_bits': value.bit_length()}
        if type(value) is float and not math.isfinite(value):
            return {'float': str(value)}
        if type(value) is str and len(value) > 1024:
            return {'string_prefix': value[:1024], 'length': len(value)}
        return value
    if type(value) in (list, tuple, set, frozenset):
        items = list(value)
        if type(value) in (set, frozenset):
            items.sort(key=lambda v: (type(v).__name__, str(v)[:256]))
        result = [_runtime_plain(v, depth + 1) for v in items[:64]]
        if len(items) > 64:
            result.append({'remaining': len(items) - 64})
        return result
    if type(value) is dict:
        return [[_runtime_plain(k, depth + 1), _runtime_plain(v, depth + 1)]
                for k, v in list(value.items())[:64]]
    return {'type': type(value).__name__}


def _runtime_result(status, source, reason='', output='', metrics=None, accepted=False):
    return {'status': status, 'accepted': accepted, 'reason': reason, 'output': output,
            'source_hash': hashlib.sha256(source.encode('utf-8')).hexdigest(),
            'metrics': metrics or {}}


def _runtime_diagnostic(exc, source):
    """Native exception identity and exact generated-source range.

    Lines are one-based; columns are zero-based UTF-8 byte offsets with an
    exclusive end, matching CPython instruction and AST positions.
    """
    diagnostic = {'exception_type': type(exc).__name__, 'error_line': None,
                  'error_column': None, 'error_end_line': None, 'error_end_column': None}
    if isinstance(exc, SyntaxError):
        lines = source.splitlines(keepends=True)
        def byte_column(line, offset):
            if line is None or offset is None or offset <= 0 or not 1 <= line <= len(lines):
                return None
            return len(lines[line - 1][:offset - 1].encode('utf-8'))
        diagnostic.update(error_line=exc.lineno, error_end_line=exc.end_lineno,
                          error_column=byte_column(exc.lineno, exc.offset),
                          error_end_column=byte_column(exc.end_lineno, exc.end_offset),
                          syntax_offset=exc.offset, syntax_end_offset=exc.end_offset)
        return diagnostic
    generated = None
    cursor = exc.__traceback__
    while cursor is not None:
        if cursor.tb_frame.f_code.co_filename == RUNTIME_FILENAME:
            generated = cursor
        cursor = cursor.tb_next
    if generated is not None:
        diagnostic['error_line'] = generated.tb_lineno
        instruction = next((item for item in dis.get_instructions(generated.tb_frame.f_code, show_caches=True)
                            if item.offset == generated.tb_lasti), None)
        if instruction is not None:
            pos = instruction.positions
            diagnostic.update(error_line=pos.lineno if pos.lineno is not None else generated.tb_lineno,
                              error_column=pos.col_offset, error_end_line=pos.end_lineno,
                              error_end_column=pos.end_col_offset)
    return diagnostic


def _runtime_control_request(mode, inputs, actions):
    if mode != 'control':
        if inputs is not None or actions is not None:
            raise ValueError('inputs and actions require control mode')
        return {}, []
    if type(inputs) is not dict or set(inputs) != {'obs'} or type(inputs['obs']) is not dict:
        raise ValueError("control requires explicit inputs={'obs': {...}}")
    obs = inputs['obs']
    if not {'health', 'ammo', 'scene'} <= set(obs) or not 3 <= len(obs) <= 16:
        raise ValueError('obs requires health, ammo, scene and at most 16 fields')
    for name, value in obs.items():
        if type(name) is not str or len(name) > 48 or not name.isidentifier() or name.startswith('_') or keyword.iskeyword(name):
            raise ValueError('observation field names must be public identifiers')
        if type(value) not in (str, int, float, bool, type(None)):
            raise ValueError('observation values must be JSON scalars')
        if type(value) is str and len(value) > 256:
            raise ValueError('observation string limit')
        if type(value) in (int, float) and (abs(value) > 1000000000 or not math.isfinite(value)):
            raise ValueError('observation numeric limit')
    if type(actions) not in (list, tuple) or not 1 <= len(actions) <= 16:
        raise ValueError('control requires 1..16 explicit actions')
    for action in actions:
        if type(action) is not str or len(action) > 48 or not action.isidentifier() or action.startswith('_') or keyword.iskeyword(action):
            raise ValueError('actions must be public identifiers up to 48 characters')
    if len(set(actions)) != len(actions):
        raise ValueError('actions must be unique')
    # Copy even in direct internal execution; candidates never receive parent objects.
    return json.loads(json.dumps(inputs, allow_nan=False)), list(actions)


def _runtime_execute(source, mode, inputs=None, actions=None):
    input_values, allowed_actions = _runtime_control_request(mode, inputs, actions)
    try:
        tree = _runtime_tree(source)
        if any(isinstance(node, ast.FunctionDef) and node.name in input_values for node in ast.walk(tree)):
            raise RuntimePolicyError('function name collides with runtime input')
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', SyntaxWarning)
            code = compile(source, RUNTIME_FILENAME, 'exec')
    except SyntaxError as exc:
        result = _runtime_result('syntax_error', source, '%s at line %s' % (exc.msg, exc.lineno))
        result.update(_runtime_diagnostic(exc, source))
        return result
    except (RuntimePolicyError, ValueError, RecursionError) as exc:
        result = _runtime_result('policy_rejected', source, str(exc))
        result.update(_runtime_diagnostic(exc, source))
        return result
    output = io.StringIO()
    output_count = 0
    def data_text(value):
        pending, seen = [value], set()
        while pending:
            item = pending.pop()
            if type(item) in (str, int, float, bool, type(None), range):
                continue
            if type(item) not in (list, tuple, set, frozenset, dict):
                raise RuntimePolicyError('text conversion requires ordinary data')
            if id(item) in seen:
                continue
            seen.add(id(item))
            pending.extend(item)
            if type(item) is dict:
                pending.extend(item.values())
            if len(seen) + len(pending) > 10000:
                raise RuntimePolicyError('text conversion size limit')
        return str(value)
    def bounded_print(*args, sep=' ', end='\n', **kwargs):
        nonlocal output_count
        if kwargs or not isinstance(sep, str) or not isinstance(end, str):
            raise RuntimePolicyError('print supports text output only')
        message = sep.join(data_text(item) for item in args) + end
        output_count += len(message.encode('utf-8'))
        if output_count > RUNTIME_OUTPUT_LIMIT:
            raise RuntimePolicyError('output limit')
        output.write(message)
    safe = {name: getattr(builtins, name) for name in _SAFE_FUNCTIONS}
    safe['print'] = bounded_print
    safe['str'] = lambda value='': data_text(value)
    namespace = {'__builtins__': safe}
    namespace.update(input_values)
    executed = set()
    computational = set()
    counts = collections.Counter()
    instructions = {}
    def span(node):
        return (node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
    def contains(outer, inner):
        return (outer[0], outer[1]) <= (inner[0], inner[1]) and (inner[2], inner[3]) <= (outer[2], outer[3])
    stores = {}
    subscript_stores = {}
    conditional_stores = {}
    parents = {id(child): node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
    calls = []
    returns = {}
    formatted = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            controls = []
            ancestor = parents.get(id(node))
            while ancestor is not None:
                if isinstance(ancestor, (ast.If, ast.While)):
                    controls.append(ancestor.test)
                ancestor = parents.get(id(ancestor))
            for target in targets:
                for leaf in ast.walk(target):
                    if isinstance(leaf, ast.Subscript) and isinstance(leaf.ctx, ast.Store):
                        root = leaf.value
                        while isinstance(root, ast.Subscript):
                            root = root.value
                        if isinstance(root, ast.Name):
                            subscript_stores[span(leaf)] = (root.id, node.value, controls)
                    if isinstance(leaf, ast.Name) and isinstance(leaf.ctx, ast.Store):
                        key = (leaf.lineno, leaf.col_offset, leaf.id)
                        stores[key] = node if isinstance(node, ast.AugAssign) else node.value
                        conditional_stores[key] = controls
        elif isinstance(node, ast.Call):
            calls.append(node)
        elif isinstance(node, ast.FormattedValue):
            formatted.append(node.value)
        elif isinstance(node, ast.Return) and node.value is not None:
            returns[node.lineno] = node.value
    taints = {}
    function_results = {}
    compute_spans = {}
    sink_steps = {}
    output_computed = False
    pending_mutations = {}
    noop_mutations = set()
    changed_mutations = set()
    called_firstlines = set()
    executed_spans = set()
    steps = 0
    def expression_computed(node, frame, after=0):
        if node is None:
            return False
        region = span(node)
        if any(when > after and contains(region, location) for location, when in compute_spans.items()):
            return True
        local = taints.get(id(frame), {})
        global_taints = taints.get('globals', {})
        for part in ast.walk(node):
            if isinstance(part, ast.Name) and isinstance(part.ctx, ast.Load):
                if local.get(part.id, global_taints.get(part.id, False)):
                    return True
            if isinstance(part, ast.Call) and isinstance(part.func, ast.Name):
                if function_results.get(part.func.id, False):
                    return True
        return False
    def trace(frame, event, arg):
        nonlocal steps, output_computed
        if frame.f_code.co_filename != RUNTIME_FILENAME:
            return None
        frame.f_trace_opcodes = True
        pending = pending_mutations.pop(id(frame), None)
        if pending is not None:
            name, value, before, position = pending
            after = repr(value)
            if before != after:
                taints[id(frame)][name] = True
                changed_mutations.add(position)
            else:
                noop_mutations.add(position)
                compute_spans.pop(position, None)
        if event == 'call':
            taints[id(frame)] = {} if frame.f_code.co_name != '<module>' else taints.setdefault('globals', {})
            if frame.f_code.co_name != '<module>':
                called_firstlines.add(frame.f_code.co_firstlineno)
                function_results[frame.f_code.co_name] = False
        if event == 'line':
            executed.add(frame.f_lineno)
        elif event == 'opcode':
            steps += 1
            if steps > RUNTIME_STEP_LIMIT:
                raise RuntimePolicyError('instruction limit')
            mapping = instructions.get(frame.f_code)
            if mapping is None:
                mapping = {item.offset: item for item in dis.get_instructions(frame.f_code)}
                instructions[frame.f_code] = mapping
            instruction = mapping.get(frame.f_lasti)
            if instruction is None or not instruction.positions.lineno:
                return trace
            op = instruction.opname
            pos = instruction.positions
            executed_spans.add((pos.lineno, pos.end_lineno, pos.col_offset, pos.end_col_offset))
            location = (pos.lineno, pos.col_offset, pos.end_lineno, pos.end_col_offset)
            call = next((n for n in calls if span(n) == location), None) if op.startswith('CALL') else None
            computational_call = call is not None and (isinstance(call.func, ast.Attribute) or
                isinstance(call.func, ast.Name) and call.func.id in _COMPUTE_FUNCTIONS)
            if op in _COMPUTE_OPS or computational_call:
                computational.add(frame.f_lineno)
                counts[op] += 1
                compute_spans[location] = steps
            if op in ('STORE_NAME', 'STORE_FAST'):
                key = (pos.lineno, pos.col_offset, instruction.argval)
                rhs = stores.get(key)
                sink = (id(frame), 'store', instruction.argval, location)
                taints[id(frame)][instruction.argval] = expression_computed(rhs, frame, sink_steps.get(sink, 0)) or any(expression_computed(test, frame) for test in conditional_stores.get(key, []))
                sink_steps[sink] = steps
            if op == 'STORE_SUBSCR' and location in subscript_stores:
                name, rhs, controls = subscript_stores[location]
                if expression_computed(rhs, frame) or any(expression_computed(test, frame) for test in controls):
                    value = frame.f_locals.get(name, namespace.get(name))
                    before = repr(value)
                    if len(before) > 131072:
                        raise RuntimePolicyError('mutation observation size limit')
                    pending_mutations[id(frame)] = (name, value, before, location)
            if call is not None:
                if isinstance(call.func, ast.Name) and call.func.id == 'print':
                    sink = (id(frame), 'print', location)
                    output_computed |= any(expression_computed(value, frame, sink_steps.get(sink, 0)) for value in call.args)
                    sink_steps[sink] = steps
                elif isinstance(call.func, ast.Attribute) and call.func.attr in {
                    'append', 'extend', 'insert', 'pop', 'remove', 'reverse', 'sort', 'clear',
                    'setdefault', 'update', 'add', 'discard'}:
                    root = call.func.value
                    if isinstance(root, ast.Name):
                        value = frame.f_locals.get(root.id, namespace.get(root.id))
                        before = repr(value)
                        if len(before) > 131072:
                            raise RuntimePolicyError('mutation observation size limit')
                        pending_mutations[id(frame)] = (root.id, value, before, location)
            if op == 'FORMAT_VALUE':
                for value in formatted:
                    if contains(location, span(value)):
                        for part in ast.walk(value):
                            if isinstance(part, ast.Name) and isinstance(part.ctx, ast.Load):
                                data_text(frame.f_locals.get(part.id, namespace.get(part.id)))
            if op == 'RETURN_VALUE':
                function_results[frame.f_code.co_name] = expression_computed(returns.get(frame.f_lineno), frame)
        return trace
    status, reason = 'ok', ''
    error_diagnostic = {}
    try:
        # Python 3.12 enables opcode monitoring only if a current frame opts in.
        sys._getframe().f_trace_opcodes = True
        sys.settrace(trace)
        exec(code, namespace, namespace)
    except BaseException as exc:
        status = 'limit' if isinstance(exc, (RuntimePolicyError, MemoryError, RecursionError)) else 'runtime_error'
        reason = type(exc).__name__ + ': ' + str(exc)[:200]
        error_diagnostic = _runtime_diagnostic(exc, source)
    finally:
        sys.settrace(None)
    final = {name: _runtime_plain(value) for name, value in sorted(namespace.items())
             if not name.startswith('_') and not callable(value)}
    final_json = json.dumps(final, sort_keys=True, ensure_ascii=True, separators=(',', ':'))
    metrics = {'executed_lines': sorted(executed), 'computational_lines': sorted(computational),
               'computational_ops': dict(counts), 'instructions': steps, 'final_values': final,
               'executed_code_firstlines': sorted(called_firstlines),
               'executed_spans': sorted(executed_spans),
               'final_state_hash': hashlib.sha256(final_json.encode()).hexdigest(),
               'output_bytes': output_count,
               'computed_final_names': sorted(name for name in final if taints.get('globals', {}).get(name)),
               'computed_output': output_computed,
               'noop_mutation_spans': sorted((a,c,b,d) for a,b,c,d in noop_mutations - changed_mutations)}
    values = [final[name] for name in metrics['computed_final_names']]
    selected_action = namespace.get('action')
    observed = (selected_action if type(selected_action) is str else None) if mode == 'control' else (output.getvalue() if mode == 'art' else [output.getvalue(), sorted(values, key=lambda x: json.dumps(x, sort_keys=True))])
    behavior = json.dumps(observed, sort_keys=True, ensure_ascii=True)
    metrics['behavior_hash'] = hashlib.sha256(behavior.encode()).hexdigest()
    emitted = output.getvalue()
    nonspace = sum(not c.isspace() for c in emitted)
    visible_lines = [line for line in emitted.splitlines() if line.strip()]
    meaningful = bool(metrics['computed_final_names']) or (output_computed and bool(emitted.strip()))
    if mode == 'art':
        geometry = len(set(visible_lines)) >= 2
        meaningful = len(visible_lines) >= 2 and nonspace >= 6 and (geometry or len(set(emitted) - set(' \r\n\t')) >= 2)
    if mode == 'control':
        meaningful = type(selected_action) is str and selected_action in allowed_actions
        if status == 'ok' and not meaningful:
            status, reason = 'invalid_action', 'action must be a string in the supplied action list'
    accepted = status == 'ok' and meaningful
    if status == 'ok' and not accepted:
        status, reason = 'trivial', 'no observed computation with a result' if mode == 'general' else 'insufficient visible drawing'
    result = _runtime_result(status, source, reason, emitted, metrics, accepted)
    if mode == 'control':
        result['action'] = selected_action if type(selected_action) is str else None
    result.update(error_diagnostic)
    return result


def worker_entry():
    """Private subprocess protocol; call only for --judge-worker."""
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))
        resource.setrlimit(resource.RLIMIT_CPU, (2, 2))
        resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))
        resource.setrlimit(resource.RLIMIT_NOFILE, (16, 16))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        request = json.loads(sys.stdin.read(RUNTIME_SOURCE_LIMIT * 64))
        if 'observations' in request:
            observations = request['observations']
            if type(observations) is not list or not 1 <= len(observations) <= 48:
                raise ValueError('batch requires 1..48 observations')
            result = [_runtime_execute(request['source'], 'control', item, request['actions']) for item in observations]
        else:
            result = _runtime_execute(request['source'], request['mode'], request.get('inputs'), request.get('actions'))
    except BaseException as exc:
        result = {'status': 'worker_error', 'accepted': False, 'output': '',
                  'metrics': {}, 'reason': type(exc).__name__ + ': ' + str(exc)[:200]}
    sys.stdout.write(json.dumps(result, ensure_ascii=True, allow_nan=False))


def judge(source, timeout=1.5, mode='general', inputs=None, actions=None):
    """Execute exact source in a restricted, bounded CPython subprocess.

    Reports executed computational operations connected to retained values or output.
    The allowlist supports an introductory subset of Python.
    """
    if not isinstance(source, str):
        raise TypeError('source must be str')
    if mode not in ('general', 'art', 'control'):
        raise ValueError('unknown judge mode')
    _runtime_control_request(mode, inputs, actions)
    if not 0 < timeout <= 30:
        raise ValueError('timeout must be in (0, 30]')
    try:
        _runtime_tree(source)
    except SyntaxError as exc:
        result = _runtime_result('syntax_error', source, '%s at line %s' % (exc.msg, exc.lineno))
        result.update(_runtime_diagnostic(exc, source))
        return result
    except (RuntimePolicyError, ValueError, RecursionError) as exc:
        result = _runtime_result('policy_rejected', source, str(exc))
        result.update(_runtime_diagnostic(exc, source))
        return result
    with tempfile.TemporaryDirectory(prefix='netta-run-') as workdir:
        try:
            proc = subprocess.run([sys.executable, '-P', '-s', os.path.abspath(__file__), '--judge-worker'],
                                  input=json.dumps({'source': source, 'mode': mode, 'inputs': inputs, 'actions': actions}), text=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=workdir,
                                  env={'PATH': os.defpath, 'PYTHONHASHSEED': '0'}, timeout=timeout)
        except subprocess.TimeoutExpired:
            return _runtime_result('timeout', source, 'wall-clock limit')
    if proc.returncode:
        return _runtime_result('limit', source, 'worker exit %s' % proc.returncode)
    try:
        result = json.loads(proc.stdout)
        if not isinstance(result, dict) or not isinstance(result.get('accepted'), bool):
            raise ValueError('bad worker response')
        return result
    except (ValueError, TypeError):
        return _runtime_result('worker_error', source, 'invalid worker response')


def judge_batch(source, observations, actions, timeout=3):
    """Evaluate one unchanged controller over explicit inputs in a private child.

    Each observation has a fresh candidate namespace and instruction budget.
    The batch shares the child's overall CPU, memory, and wall-clock limits.
    """
    if not isinstance(source, str):
        raise TypeError('source must be str')
    if type(observations) is not list or not 1 <= len(observations) <= 48:
        raise ValueError('batch requires 1..48 observation input mappings')
    for inputs in observations:
        _runtime_control_request('control', inputs, actions)
    if not 0 < timeout <= 30:
        raise ValueError('timeout must be in (0, 30]')
    def failures(status, reason, exception=None):
        results = [_runtime_result(status, source, reason) for _ in observations]
        if exception is not None:
            for result in results:
                result.update(_runtime_diagnostic(exception, source))
        return results
    try:
        _runtime_tree(source)
    except SyntaxError as exc:
        return failures('syntax_error', '%s at line %s' % (exc.msg, exc.lineno), exc)
    except (RuntimePolicyError, ValueError, RecursionError) as exc:
        return failures('policy_rejected', str(exc), exc)
    with tempfile.TemporaryDirectory(prefix='netta-control-') as workdir:
        try:
            proc = subprocess.run([sys.executable, '-P', '-s', os.path.abspath(__file__), '--judge-worker'],
                                  input=json.dumps({'source': source, 'observations': observations, 'actions': actions}),
                                  text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=workdir,
                                  env={'PATH': os.defpath, 'PYTHONHASHSEED': '0'}, timeout=timeout)
        except subprocess.TimeoutExpired:
            return failures('timeout', 'batch wall-clock limit')
    if proc.returncode:
        return failures('limit', 'batch worker exit %s' % proc.returncode)
    try:
        results = json.loads(proc.stdout)
        if type(results) is not list or len(results) != len(observations) or any(
                type(item) is not dict or type(item.get('accepted')) is not bool for item in results):
            raise ValueError('invalid batch result')
        return results
    except (ValueError, TypeError):
        return failures('worker_error', 'invalid batch worker response')



"""Execution-aware novelty against the island, independently of generation.

Included in each standalone organism.  These functions inspect generated code;
they never change the code submitted to CPython.
"""


_NOVELTY_BUILTINS = set("print range len str int float bool list tuple dict set sorted reversed enumerate zip sum min max abs round any all chr ord True False None".split())


def _canonical_tree(tree, shape=False):
    # AST parsing gives a fresh tree for each caller; deepcopy also makes
    # repeated segmentation independent of earlier alpha renaming.
    import copy
    tree = copy.deepcopy(tree)
    names = {}

    def rename(name):
        if name in _NOVELTY_BUILTINS:
            return name
        return names.setdefault(name, "v" + str(len(names)))

    class Canonical(ast.NodeTransformer):
        def visit_Name(self, node):
            node.id = rename(node.id)
            return node

        def visit_arg(self, node):
            node.arg = rename(node.arg)
            return self.generic_visit(node)

        def visit_FunctionDef(self, node):
            node.name = rename(node.name)
            return self.generic_visit(node)

        def visit_Constant(self, node):
            if shape:
                node.value = "<" + type(node.value).__name__ + ">"
            return node

    return ast.dump(Canonical().visit(tree), include_attributes=False)


def _project_tree(source, evidence=None):
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError, TypeError, RecursionError):
        return None
    if evidence is not None and not isinstance(evidence, dict):
        evidence = {"executed_lines": evidence}
    lines = None if evidence is None else set(evidence.get("executed_lines", ()))
    spans = None if evidence is None else evidence.get("executed_spans")
    called = None if evidence is None else evidence.get("executed_code_firstlines")
    noop_mutations = set() if evidence is None else {
        tuple(item) for item in evidence.get("noop_mutation_spans", ())
    }

    def literal_value(node):
        try:
            ast.literal_eval(node)
            return True
        except (ValueError, TypeError, SyntaxError, RecursionError):
            pass
        # CPython folds expressions such as 0 + 0 into a literal before
        # execution.  Examine that compilation without evaluating the code.
        import dis
        try:
            expression = compile(ast.Expression(body=node), "<novelty>", "eval")
            return all(instruction.opname in {
                "RESUME", "LOAD_CONST", "RETURN_VALUE", "RETURN_CONST", "NOP", "CACHE"
            } for instruction in dis.get_instructions(expression))
        except (ValueError, TypeError, SyntaxError, RecursionError):
            return False

    def was_executed(node):
        if evidence is None:
            return True
        if spans is not None:
            begin = (node.lineno, node.col_offset)
            end = (node.end_lineno, node.end_col_offset)
            # Runtime spans are [line, end_line, col, end_col].  Requiring
            # containment avoids charging a one-line dead body for its header.
            return any(line is not None and end_line is not None and
                       col is not None and end_col is not None and
                       begin <= (line, col) < end and
                       (line, col) <= (end_line, end_col) <= end
                       for line, end_line, col, end_col in spans)
        return any(getattr(n, "lineno", -1) in lines for n in ast.walk(node))

    class Active(ast.NodeTransformer):
        def visit(self, node):
            if isinstance(node, ast.Pass):
                return None
            if isinstance(node, ast.Expr) and isinstance(node.value, (ast.Constant, ast.Name)):
                return None
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                call = node.value
                location = (call.lineno, call.end_lineno, call.col_offset, call.end_col_offset)
                if location in noop_mutations:
                    return None
            if isinstance(node, ast.stmt) and not was_executed(node):
                return None
            if isinstance(node, ast.FunctionDef) and called is not None:
                if node.lineno not in called:
                    return None
            return super().visit(node)

        def visit_If(self, node):
            # Constant condition wrappers are padding.  A failed generated
            # indent remains failed: this is a signature only, never repair.
            if isinstance(node.test, ast.Constant):
                chosen = node.body if bool(node.test.value) else node.orelse
                result = []
                for item in chosen:
                    item = self.visit(item)
                    if isinstance(item, list):
                        result.extend(item)
                    elif item is not None:
                        result.append(item)
                return result
            node = self.generic_visit(node)
            if not node.body and not node.orelse:
                return None
            return node

        def visit_For(self, node):
            node = self.generic_visit(node)
            return node if node.body or node.orelse else None

        def visit_While(self, node):
            if isinstance(node.test, ast.Constant) and not bool(node.test.value):
                result = []
                for item in node.orelse:
                    item = self.visit(item)
                    if isinstance(item, list):
                        result.extend(item)
                    elif item is not None:
                        result.append(item)
                return result
            node = self.generic_visit(node)
            return node if node.body or node.orelse else None

    tree = Active().visit(tree)
    # Remove dead definitions and unused literal stores to a fixed point;
    # names mentioned only in removed branches cannot keep padding alive.
    for _ in range(8):
        before = ast.dump(tree, include_attributes=False)
        reads = {n.id for n in ast.walk(tree)
                 if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
        functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        unused_functions = set()
        if evidence is None:
            for fn in functions:
                outside = []
                class Outside(ast.NodeVisitor):
                    def visit_FunctionDef(self, node):
                        if node is not fn:
                            self.generic_visit(node)
                    def visit_Name(self, node):
                        if isinstance(node.ctx, ast.Load):
                            outside.append(node.id)
                Outside().visit(tree)
                if fn.name not in outside:
                    unused_functions.add(id(fn))

        class DeadStores(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                if id(node) in unused_functions:
                    return None
                return self.generic_visit(node)

            def visit_Assign(self, node):
                names = [n.id for target in node.targets for n in ast.walk(target)
                         if isinstance(n, ast.Name)]
                if literal_value(node.value) and names and not any(n in reads for n in names):
                    return None
                return self.generic_visit(node)

            def visit_AnnAssign(self, node):
                # Only a plain type-name annotation is inert here.  An
                # annotation that executes an expression is retained.
                if isinstance(node.target, ast.Name) and node.target.id not in reads:
                    if literal_value(node.value) and isinstance(node.annotation, ast.Name) and node.annotation.id in _NOVELTY_BUILTINS:
                        return None
                return self.generic_visit(node)

        tree = DeadStores().visit(tree)
        if ast.dump(tree, include_attributes=False) == before:
            break
    return tree


def program_key(source, executed=None, shape=False):
    tree = _project_tree(source, executed)
    return None if tree is None else digest(_canonical_tree(tree, shape))


def build_reference(programs, judge, mode="general"):
    full, active, shapes, behaviors = set(), set(), set(), set()
    chunks, outcomes = {}, []
    for source in programs:
        full_tree = _project_tree(source)
        if full_tree is None:
            raise ValueError("island contains an unparseable program")
        full.add(digest(_canonical_tree(full_tree)))
        result = judge(source, mode=mode)
        outcomes.append({"source_hash": digest(source), "status": result["status"],
                         "accepted": bool(result["accepted"])})
        # A failed source still has a full-source replay signature; its
        # execution cannot supply a reference for productive behavior.
        if not result["accepted"]:
            continue
        behavior = result.get("metrics", {}).get("behavior_hash")
        if behavior:
            behaviors.add(behavior)
        tree = _project_tree(source, result.get("metrics", {}))
        key = digest(_canonical_tree(tree))
        active.add(key)
        shapes.add(digest(_canonical_tree(tree, shape=True)))
        if tree.body:
            chunks.setdefault(str(len(tree.body)), set()).add(key)
    return {"full": sorted(full), "active": sorted(active), "shapes": sorted(shapes),
            "behaviors": sorted(behaviors),
            "chunks": {n: sorted(keys) for n, keys in chunks.items()},
            "outcomes": outcomes}


def classify_source(source, metrics, references):
    tree = _project_tree(source, metrics)
    if tree is None:
        return {"status": "invalid", "key": None, "shape": None, "new_shape": False}
    key = digest(_canonical_tree(tree))
    shape = digest(_canonical_tree(tree, shape=True))
    full_key = program_key(source)
    reason = None
    if full_key in references["full"]:
        reason = "whole_source"
    elif key in references["active"] or key in references["full"]:
        reason = "active_source"
    else:
        # A concatenation of whole known programs is still replay.  Rebase
        # alpha names separately in each segment so renaming cannot evade it.
        lengths = sorted(int(n) for n in references["chunks"])
        reachable = {0}
        for start in range(len(tree.body)):
            if start not in reachable:
                continue
            for length in lengths:
                end = start + length
                if end > len(tree.body):
                    break
                segment = ast.Module(body=tree.body[start:end], type_ignores=[])
                fingerprint = digest(_canonical_tree(segment))
                if fingerprint in references["chunks"][str(length)]:
                    reachable.add(end)
        if tree.body and len(tree.body) in reachable:
            reason = "whole_program_concatenation"
    status = "source_replay" if reason else "novel"
    behavior = metrics.get("behavior_hash")
    if reason is None and behavior and behavior in references.get("behaviors", ()):
        status, reason = "behavior_replay", "equivalent_source_behavior"
    return {"status": status, "key": key,
            "shape": shape, "new_shape": shape not in references["shapes"],
            "reason": reason}


"""Small Wolfe-inspired caller: declared lexical evidence chooses one saved island.

The caller never emits code or executes commands. The organism loaded from the
selected snapshot generates code. Scores are evidence strengths, not probabilities.
"""
import ast
import hashlib
import math
import re
import unicodedata
from pathlib import PurePosixPath


def _caller_tokens(text):
    text = unicodedata.normalize("NFKC", text).casefold().replace("ё", "е")
    return tuple(re.findall(r"[^\W_]+(?:['’][^\W_]+)*", text))


def _caller_command_text(text):
    # Command profiles use whole phrases. Punctuation and signs remain significant.
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def _caller_output_schema(output):
    bounds = {"min_lines": 1024, "max_lines": 1024, "min_width": 4096,
              "max_width": 4096, "min_items": 1024, "max_items": 1024}
    allowed = set(bounds) | {"equals", "contains", "literal_type", "item_type", "unique", "sorted"}
    if not isinstance(output, dict) or not output or set(output) - allowed:
        raise ValueError("output requires nonempty supported constraints")
    for key, limit in bounds.items():
        if key in output and (type(output[key]) is not int or not 1 <= output[key] <= limit):
            raise ValueError("invalid output bound " + key)
    for dimension in ("lines", "width", "items"):
        if output.get("min_" + dimension, 0) > output.get("max_" + dimension, 65536):
            raise ValueError("contradictory output bounds")
    if "equals" in output and (not isinstance(output["equals"], str) or not 1 <= len(output["equals"]) <= 4096):
        raise ValueError("equals must be nonempty text of at most 4096 characters")
    if "contains" in output:
        values = output["contains"]
        if not isinstance(values, list) or not 1 <= len(values) <= 16 or any(
                not isinstance(s, str) or not 1 <= len(s) <= 128 for s in values):
            raise ValueError("contains requires 1..16 nonempty strings")
    if "literal_type" in output and output["literal_type"] != "list":
        raise ValueError("literal_type supports list")
    list_fields = {"min_items", "max_items", "item_type", "unique", "sorted"}
    if list_fields.intersection(output) and output.get("literal_type") != "list":
        raise ValueError("list constraints require literal_type list")
    if "item_type" in output and output["item_type"] not in ("string", "number", "record"):
        raise ValueError("item_type must be string, number, or record")
    if "unique" in output and output["unique"] is not True:
        raise ValueError("unique must be true")
    if "sorted" in output and output["sorted"] not in ("ascending", "descending"):
        raise ValueError("sorted must be ascending or descending")
    if {"unique", "sorted"}.intersection(output) and output.get("item_type") not in ("string", "number"):
        raise ValueError("unique/sorted requires a scalar item_type")
    if not {"equals", "contains", "min_lines", "min_width", "literal_type"}.intersection(output):
        raise ValueError("output needs a positive requirement")
    return {key: list(value) if isinstance(value, list) else value for key, value in output.items()}


def _caller_config(config):
    if not isinstance(config, dict) or set(config) != {"version", "states"}:
        raise ValueError("caller config requires exactly version and states")
    if type(config["version"]) is not int or config["version"] != 1:
        raise ValueError("unsupported caller config version")
    entries = config["states"]
    if not isinstance(entries, list) or not 1 <= len(entries) <= 64:
        raise ValueError("states must contain 1..64 entries")
    names, prepared, command_requests = set(), [], set()
    for entry in entries:
        allowed = {"name", "state", "judge", "keywords", "phrases", "examples", "commands"}
        if not isinstance(entry, dict) or set(entry) - allowed:
            raise ValueError("unexpected state entry fields")
        name, path = entry.get("name"), entry.get("state")
        if not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9_-]{0,47}", name):
            raise ValueError("state name must be a short lowercase identifier")
        if name in names:
            raise ValueError("duplicate state name")
        names.add(name)
        if not isinstance(path, str) or not path or len(path) > 512:
            raise ValueError("state must name a relative .json snapshot")
        p = PurePosixPath(path)
        if p.is_absolute() or ".." in p.parts or p.suffix != ".json":
            raise ValueError("state must name a relative .json snapshot")
        if "\\" in path or ":" in path or any(ord(c) < 32 for c in path):
            raise ValueError("invalid snapshot path")
        mode = entry.get("judge", "general")
        if mode not in ("art", "general", "control"):
            raise ValueError("judge must be art, general, or control")
        prepared_entry = {"name": name, "state": path, "mode": mode}
        for kind in ("keywords", "phrases", "examples"):
            values = entry.get(kind, [])
            if not isinstance(values, list) or len(values) > 128:
                raise ValueError(kind + " must be a list of at most 128 strings")
            items = []
            for value in values:
                if not isinstance(value, str) or not 1 <= len(value) <= 512:
                    raise ValueError("invalid " + kind + " text")
                tokens = _caller_tokens(value)
                if not tokens or (kind == "keywords" and len(tokens) != 1):
                    raise ValueError("keywords are single words; phrases/examples contain words")
                items.append((value, tokens))
            prepared_entry[kind] = items
        commands = entry.get("commands", [])
        if not isinstance(commands, list) or len(commands) > 32:
            raise ValueError("commands must be a list of at most 32 profiles")
        if mode == "control" and commands:
            raise ValueError("control outcomes are verified by the game bridge")
        prepared_entry["commands"] = []
        profile_names = set()
        for command in commands:
            if not isinstance(command, dict) or set(command) != {"name", "requests", "output"}:
                raise ValueError("command requires exactly name, requests, and output")
            profile = command["name"]
            if not isinstance(profile, str) or not re.fullmatch(r"[a-z][a-z0-9_-]{0,47}", profile):
                raise ValueError("invalid command name")
            if profile in profile_names:
                raise ValueError("duplicate command name")
            profile_names.add(profile)
            requests = command["requests"]
            if not isinstance(requests, list) or not 1 <= len(requests) <= 32 or any(
                    not isinstance(s, str) or not s.strip() or len(s) > 512 for s in requests):
                raise ValueError("command requests must be 1..32 nonempty phrases")
            normalized = {_caller_command_text(s) for s in requests + [name + ":" + profile]}
            if normalized & command_requests:
                raise ValueError("command requests must be unambiguous")
            command_requests.update(normalized)
            prepared_entry["commands"].append({"name": profile, "requests": normalized,
                                                "output": _caller_output_schema(command["output"])})
        prepared.append(prepared_entry)
    return prepared


def select_state(request, config):
    """Return status, optional selection {name, state, mode}, and ranked evidence.

    Paths are relative to the caller JSON file. The caller does not open them.
    Unknown language, negated commands, and close competing evidence abstain;
    direct CLI state selection remains available for those requests.
    """
    entries = _caller_config(config)
    if not isinstance(request, str) or len(request) > 8192:
        raise ValueError("request must be text of at most 8192 characters")
    no_match = {"status": "no_match", "profile": None,
                "reason": "no declared command matched the complete request"}
    phrase = _caller_command_text(request)
    for entry in entries:
        for command in entry["commands"]:
            if phrase in command["requests"]:
                return {"status": "selected",
                        "selection": {key: entry[key] for key in ("name", "state", "mode")},
                        "evidence": [{"name": entry["name"], "score": 1.25,
                                      "hits": [{"kind": "command", "text": request, "score": 1.25}]}],
                        "reason": "declared command profile",
                        "task": {"status": "matched", "profile": entry["name"] + ":" + command["name"],
                                 "output": command["output"]}}
    query = _caller_tokens(request)
    negative = {"не", "нет", "без", "not", "no", "never", "don't", "don’t", "dont", "without"}
    if not query or negative.intersection(query):
        return {"status": "unknown", "selection": None, "evidence": [], "task": no_match,
                "reason": "empty request" if not query else "negated request; select a state explicitly"}
    documents = {}
    for entry in entries:
        words = set()
        for kind in ("keywords", "phrases", "examples"):
            for _, tokens in entry[kind]:
                words.update(tokens)
        for word in words:
            documents.setdefault(word, set()).add(entry["name"])
    evidence, qset = [], set(query)
    for entry in entries:
        hits = []
        if query == _caller_tokens(entry["name"]):
            hits.append({"kind": "name", "text": entry["name"], "score": 1.1})
        for kind in ("keywords", "phrases", "examples"):
            for text, tokens in entry[kind]:
                exact = any(query[i:i + len(tokens)] == tokens
                            for i in range(len(query) - len(tokens) + 1))
                score = 0.0
                if kind != "examples" and exact:
                    score = 1.0 if kind == "keywords" else 1.1
                elif kind == "examples":
                    words = set(tokens)
                    matched = words & qset
                    if any(len(documents[w]) == 1 for w in matched):
                        total = sum(1 / len(documents[w]) for w in words)
                        score = .95 * sum(1 / len(documents[w]) for w in matched) / total
                if score > 0:
                    hits.append({"kind": kind, "text": text, "score": round(score, 6)})
        score = max((hit["score"] for hit in hits), default=0.0)
        evidence.append({"name": entry["name"], "score": score, "hits": hits})
    evidence.sort(key=lambda item: (-item["score"], item["name"]))
    best = evidence[0]
    runner = evidence[1]["score"] if len(evidence) > 1 else 0.0
    if best["score"] < .72:
        status, reason = "unknown", "insufficient declared evidence"
    elif runner >= .72 and best["score"] - runner < .15:
        status, reason = "ambiguous", "competing specializations"
    else:
        status, reason = "selected", "declared evidence"
    chosen = next(entry for entry in entries if entry["name"] == best["name"])
    selection = ({key: chosen[key] for key in ("name", "state", "mode")}
                 if status == "selected" else None)
    return {"status": status, "selection": selection, "evidence": evidence, "reason": reason,
            "task": no_match}


def check_task_output(call, record):
    """Check a declared profile against the host's exact-source execution receipt.

    Does not execute, rewrite, repair, or feed requirements into generated source.
    Corpus/productivity admission remains a prerequisite for task success.
    """
    task = call.get("task", {})
    receipt = {"status": "no_match", "passed": False, "profile": task.get("profile"), "checks": []}
    if call.get("status") != "selected" or task.get("status") != "matched":
        return receipt
    constraints = _caller_output_schema(task["output"])
    execution = record.get("judge", {})
    if record.get("runtime_ok") is not True or execution.get("accepted") is not True or execution.get("status") != "ok":
        receipt["status"] = "runtime_failed"
        return receipt
    source, output = record.get("source"), execution.get("output")
    if not isinstance(source, str) or not isinstance(output, str) or len(output.encode("utf-8")) > 65536:
        receipt["status"] = "invalid_receipt"
        return receipt
    source_hash = hashlib.sha256(source.encode("utf-8")).hexdigest()
    if record.get("source_hash") != source_hash or execution.get("source_hash") != source_hash:
        receipt["status"] = "invalid_receipt"
        return receipt
    receipt["source_hash"] = source_hash
    receipt["output_sha256"] = hashlib.sha256(output.encode("utf-8")).hexdigest()
    if record.get("productive") is not True:
        receipt["status"] = "ineligible"
        return receipt
    lines = output.splitlines()
    dimensions = {"lines": len(lines), "width": max(map(len, lines), default=0)}
    value, parse_error = None, None
    if "literal_type" in constraints:
        try:
            value = ast.literal_eval(output)
        except (ValueError, SyntaxError, TypeError, MemoryError, RecursionError) as exc:
            parse_error = type(exc).__name__
    is_list = type(value) is list
    items = value if is_list else []
    item_kind = constraints.get("item_type")
    def finite_number(item):
        return type(item) is int or type(item) is float and math.isfinite(item)
    scalar_items = is_list and all(type(item) is str if item_kind == "string" else
                                  finite_number(item) for item in items)
    valid_items = (is_list and all(type(item) is list and len(item) == 2 and
                                  type(item[0]) is str and finite_number(item[1]) for item in items)
                   if item_kind == "record" else scalar_items)
    for key, expected in constraints.items():
        if key == "equals":
            actual, passed = output, output == expected
        elif key == "contains":
            actual = [text for text in expected if text in output]
            passed = len(actual) == len(expected)
        elif key in ("min_lines", "max_lines", "min_width", "max_width"):
            actual = dimensions[key[4:]]
            passed = actual >= expected if key.startswith("min_") else actual <= expected
        elif key == "literal_type":
            actual, passed = parse_error or type(value).__name__, is_list
        elif key in ("min_items", "max_items"):
            actual = len(items) if is_list else None
            passed = is_list and (len(items) >= expected if key == "min_items" else len(items) <= expected)
        elif key == "item_type":
            actual, passed = sorted({type(item).__name__ for item in items}), valid_items
        elif key == "unique":
            actual = scalar_items and len(set(items)) == len(items)
            passed = actual
        else:  # sorted: schema validation exhausts the supported keys.
            actual = scalar_items and items == sorted(items, reverse=expected == "descending")
            passed = actual
        receipt["checks"].append({"constraint": key, "expected": expected, "actual": actual, "passed": bool(passed)})
    receipt["passed"] = bool(receipt["checks"]) and all(check["passed"] for check in receipt["checks"])
    receipt["status"] = "passed" if receipt["passed"] else "failed"
    return receipt


if __name__ == "__main__":
    if sys.argv[1:] == ["--judge-worker"]:
        worker_entry()
    else:
        try:
            raise SystemExit(run_cli())
        except (ValueError, OSError, KeyError, TypeError) as error:
            print(SPECIES + ": " + str(error), file=sys.stderr)
            raise SystemExit(2)
