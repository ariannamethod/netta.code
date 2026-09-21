#!/usr/bin/env python3
"""Real, seeded 2048 for Netta Lee's generated Python policies (stdlib only).

Policies receive the actual board and legal-move flags as
scalar observations. The bridge never substitutes a move: invalid output ends
that policy's episode. Every episode uses a bounded isolated CPython worker.
"""
import argparse
from collections import Counter
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import random
import selectors
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nettalee as core

ROOT = Path(__file__).resolve().parent
ACTIONS = ('left', 'right', 'up', 'down')
DECISION_CONTRACTS = {'uniform': '2048-uniform-v1', 'advantage': '2048-action-advantage-v1',
                      'temporal': '2048-temporal-return-v1',
                      'provenance': '2048-action-provenance-v1'}
PROVENANCE_COVERAGE_CONTRACT = '2048-provenance-coverage-v1'
PROVENANCE_CONTRACTS = {DECISION_CONTRACTS['provenance'], PROVENANCE_COVERAGE_CONTRACT}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def fingerprint(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def archive_record(out, arm, index, record):
    """Preserve each completed attempt independently; never overwrite a receipt."""
    path = Path(out) / 'records' / arm / ('%05d.json' % index)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + '\n')
        stream.flush()
        os.fsync(stream.fileno())


def _archive_text_atomic(path, text):
    path = Path(path)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + '.', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def finalize_archive(out, arm, records):
    """Verify receipts, atomically close the journal, and publish its hash manifest."""
    out = Path(out)
    folder = out / 'records' / arm
    expected = ['%05d.json' % index for index in range(len(records))]
    if sorted(path.name for path in folder.glob('*.json')) != expected:
        raise RuntimeError('archive receipt inventory differs from completed attempts: ' + arm)
    hashes = {}
    for name, record in zip(expected, records):
        path = folder / name
        data = path.read_bytes()
        try:
            retained = json.loads(data)
        except (ValueError, UnicodeError) as error:
            raise RuntimeError('invalid archive receipt: ' + str(path)) from error
        if retained != record:
            raise RuntimeError('archive receipt differs from completed attempt: ' + str(path))
        hashes[str(path.relative_to(out))] = hashlib.sha256(data).hexdigest()
    journal = out / (arm + '.jsonl')
    _archive_text_atomic(journal, ''.join(json.dumps(record, ensure_ascii=False, allow_nan=False) + '\n'
                                         for record in records))
    data = journal.read_bytes()
    if [json.loads(line) for line in data.splitlines()] != records:
        raise RuntimeError('completed archive journal failed readback: ' + arm)
    manifest = {'count': len(records), 'jsonl_sha256': hashlib.sha256(data).hexdigest(),
                'receipts': hashes}
    path = out / (arm + '-receipts.json')
    _archive_text_atomic(path, json.dumps(manifest, indent=2, allow_nan=False) + '\n')
    if json.loads(path.read_bytes()) != manifest:
        raise RuntimeError('archive receipt manifest failed readback: ' + arm)
    return manifest


def validate_board(board):
    if type(board) not in (list, tuple) or len(board) != 16:
        raise ValueError('board requires sixteen cells')
    if any(type(value) is not int or value < 0 or value > 2 ** 29 or
           value and (value < 2 or value & (value - 1)) for value in board):
        raise ValueError('cells must be zero or bounded powers of two')
    return list(board)


def merge_line(line):
    values = [value for value in line if value]
    merged, score, index = [], 0, 0
    while index < len(values):
        if index + 1 < len(values) and values[index] == values[index + 1]:
            value = 2 * values[index]
            merged.append(value)
            score += value
            index += 2
        else:
            merged.append(values[index])
            index += 1
    return merged + [0] * (4 - len(merged)), score


def slide(board, action):
    """Pure 2048 transition before spawning; each tile merges at most once."""
    board = validate_board(board)
    if action not in ACTIONS:
        raise ValueError('unknown action')
    result, score = list(board), 0
    for line in range(4):
        cells = ([line * 4 + column for column in range(4)] if action in ('left', 'right')
                 else [row * 4 + line for row in range(4)])
        if action in ('right', 'down'):
            cells.reverse()
        merged, gained = merge_line([board[index] for index in cells])
        for index, value in zip(cells, merged):
            result[index] = value
        score += gained
    return result, score, result != board


def action_credit(board, action):
    """Host-only immediate merge comparison; no tile spawn or RNG access.

    Legal actions with identical merge gains receive neutral .5. Otherwise the
    actual selected gain is scaled between the minimum and maximum legal gain.
    This measures one-move merge quality, not a prediction of future tiles.
    """
    gains = {}
    for alternative in ACTIONS:
        _, gain, changed = slide(board, alternative)
        if changed:
            gains[alternative] = gain
    legal = action in gains
    low, high = min(gains.values(), default=0), max(gains.values(), default=0)
    chosen = gains.get(action)
    target = (0.5 if high == low else (chosen - low) / (high - low)) if legal else 0.0
    return {'legal_gains': gains, 'chosen_action': action, 'chosen_gain': chosen,
            'minimum_gain': low, 'maximum_gain': high, 'action_legal': legal,
            'informative': legal and high != low, 'target': target}


def temporal_targets(trajectory, reward):
    """Allocate unchanged episode reward by short realized merge returns.

    Each window includes the current move and at most seven actual later moves,
    with discount .9. Truncated windows use their available discount mass. The
    centered, bounded targets preserve the episode mean, so a source choice
    executed at every decision receives exactly the uniform episode target.
    """
    if not trajectory:
        raise ValueError('temporal targets require actual decisions')
    if type(reward) not in (int, float) or not math.isfinite(reward) or not 0 <= reward <= 1:
        raise ValueError('temporal reward must be finite and bounded')
    gains = [transition['gain'] for transition in trajectory]
    if any(type(gain) is not int or gain < 0 for gain in gains):
        raise ValueError('temporal targets require nonnegative host merge gains')
    # Constant gains can produce ulp-sized differences between weighted means
    # of different window lengths. They carry no temporal preference.
    if len(set(gains)) == 1:
        return [float(reward)] * len(gains)
    returns = []
    for index in range(len(gains)):
        weights = [.9 ** offset for offset in range(min(8, len(gains) - index))]
        returns.append(math.fsum(weight * gains[index + offset]
                                 for offset, weight in enumerate(weights)) / math.fsum(weights))
    mean = math.fsum(returns) / len(returns)
    radius = max(abs(value - mean) for value in returns)
    if radius == 0:
        return [float(reward)] * len(gains)
    amplitude = min(reward, 1 - reward)
    # Normalize before scaling and bound final rounding at zero/one; a negative
    # ulp at an endpoint must not turn a genuine episode into invalid feedback.
    return [max(0.0, min(1.0, reward + amplitude * ((value - mean) / radius)))
            for value in returns]


def decision_feedback(source, episode, contract):
    """Bind host decision targets to the exact executed source and real steps."""
    if contract not in set(DECISION_CONTRACTS.values()) | {PROVENANCE_COVERAGE_CONTRACT}:
        raise ValueError('unsupported 2048 decision-credit contract')
    if not episode['completed']:
        raise ValueError('incomplete episodes do not provide positive decision credit')
    source_hash = hashlib.sha256(source.encode()).hexdigest()
    decisions = []
    for transition in episode['trajectory']:
        executed = transition['decision']
        if (not transition['valid'] or executed['source_hash'] != source_hash or
                executed['action'] != transition['action'] or not executed['accepted']):
            raise ValueError('decision receipt does not match executed source/action')
        comparison = action_credit(transition['before'], transition['action'])
        if (comparison != transition['action_credit'] or not comparison['action_legal'] or
                comparison['chosen_gain'] != transition['gain']):
            raise ValueError('decision gain does not match host transition')
        target = episode['reward'] if contract == DECISION_CONTRACTS['uniform'] else comparison['target']
        if contract in PROVENANCE_CONTRACTS:
            provenance = executed.get('action_provenance')
            if (not isinstance(provenance, dict) or
                    provenance.get('contract') != 'cpython-action-slice-v1' or
                    provenance.get('source_hash') != source_hash or
                    provenance.get('input_hash') != fingerprint({'obs': transition['observation']}) or
                    provenance.get('action') != transition['action']):
                raise ValueError('action provenance does not match actual source, input and action')
            status = provenance.get('status')
            spans, selected = provenance.get('executed_spans'), provenance.get('credit_spans')
            if status not in ('ok', 'unsupported', 'incomplete') or not isinstance(spans, list) or not isinstance(selected, list):
                raise ValueError('invalid action provenance receipt')
            if status != 'ok' and selected:
                raise ValueError('unsupported provenance cannot provide selected credit')
            credit = spans if contract == PROVENANCE_COVERAGE_CONTRACT and status == 'ok' else selected
            decisions.append({'executed_spans': spans, 'credit_spans': credit,
                              'provenance_status': status, 'target': target})
        else:
            decisions.append({'executed_lines': executed['executed_lines'], 'target': target})
    if contract == DECISION_CONTRACTS['temporal'] or contract in PROVENANCE_CONTRACTS:
        for decision, target in zip(decisions, temporal_targets(episode['trajectory'], episode['reward'])):
            decision['target'] = target
    return {'source_hash': source_hash, 'contract': contract, 'decisions': decisions}


class Game2048:
    def __init__(self, seed=1, board=None):
        self.rng = random.Random(seed)
        self.seed = seed
        self.board = [0] * 16 if board is None else validate_board(board)
        self.score = 0
        self.moves = 0
        if board is None:
            self.spawn()
            self.spawn()

    def spawn(self):
        empty = [index for index, value in enumerate(self.board) if value == 0]
        if not empty:
            return None
        index = self.rng.choice(empty)
        value = 2 if self.rng.random() < .9 else 4
        self.board[index] = value
        return {'cell': index, 'value': value}

    def legal_actions(self):
        return [action for action in ACTIONS if slide(self.board, action)[2]]

    def observation(self):
        obs = {'c' + str(index): value for index, value in enumerate(self.board)}
        for action in ACTIONS:
            _, _, changed = slide(self.board, action)
            obs['valid_' + action] = changed
        return obs

    def step(self, action):
        before = list(self.board)
        moved, gained, changed = slide(before, action)
        if not changed:
            return {'action': action, 'before': before, 'after': before,
                    'valid': False, 'gain': 0, 'spawn': None, 'score': self.score}
        self.board = moved
        self.score += gained
        self.moves += 1
        spawned = self.spawn()
        return {'action': action, 'before': before, 'after': list(self.board),
                'valid': True, 'gain': gained, 'spawn': spawned, 'score': self.score}


def probe_observations():
    """Fixed non-rewarded legal positions; an anti-copy screen, not a full state space."""
    boards = []
    for index in (0, 3, 12, 15):
        board = [0] * 16
        board[index] = 2
        boards.append(board)
    for seed in range(5):
        game = Game2048(17000 + seed)
        chooser = random.Random(29000 + seed)
        for move in range(16):
            legal = game.legal_actions()
            if not legal:
                break
            game.step(chooser.choice(legal))
            if move in (3, 7, 11, 15):
                boards.append(list(game.board))
    return [Game2048(board=board).observation() for board in boards]


def policy_worker():
    """Fresh process per policy; bounded CPython runtime reset on every observation."""
    import resource
    resource.setrlimit(resource.RLIMIT_AS, (256 << 20, 256 << 20))
    resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
    resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))
    resource.setrlimit(resource.RLIMIT_NOFILE, (16, 16))
    request = json.loads(sys.stdin.readline(core.RUNTIME_SOURCE_LIMIT * 8))
    source = request['source']
    provenance = request.get('provenance', False)
    if type(provenance) is not bool:
        raise ValueError('provenance flag requires a boolean')
    if type(source) is not str or len(source.encode()) > core.RUNTIME_SOURCE_LIMIT:
        raise ValueError('source limit')
    for line in sys.stdin:
        try:
            obs = json.loads(line)
            options = {'provenance': True} if provenance else {}
            result = core._runtime_execute(source, 'control', {'obs': obs}, list(ACTIONS), **options)
            # Compact receipts avoid pipe backpressure while retaining the actual
            # action, diagnostics and exact source identity for every decision.
            receipt = {key: result.get(key) for key in ('status', 'accepted', 'action', 'reason',
                       'source_hash', 'error_line', 'error_column', 'exception_type')}
            receipt['executed_lines'] = result.get('metrics', {}).get('executed_lines', [])
            if provenance:
                observed = result.get('metrics', {}).get('action_provenance')
                receipt['action_provenance'] = ({key: observed.get(key) for key in (
                    'contract', 'status', 'reason', 'source_hash', 'input_hash', 'action',
                    'writer', 'credit_spans', 'executed_spans', 'event_count',
                    'slice_event_count', 'trace_hash')} if isinstance(observed, dict) else None)
        except Exception as error:
            receipt = {'status': 'worker_error', 'accepted': False,
                       'reason': type(error).__name__ + ': ' + str(error)[:200]}
        print(json.dumps(receipt, allow_nan=False), flush=True)


class PolicyProcess:
    def __init__(self, source, timeout=1.5, provenance=False):
        self.timeout = timeout
        self.process = subprocess.Popen([sys.executable, '-P', '-s', str(Path(__file__).resolve()), '--policy-worker'],
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.DEVNULL, text=True, bufsize=1,
                                        cwd='/tmp', env={'PATH': os.defpath, 'PYTHONHASHSEED': '0'})
        self.process.stdin.write(canonical({'source': source, 'provenance': provenance}) + '\n')
        self.process.stdin.flush()
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.process.stdout, selectors.EVENT_READ)

    def decide(self, obs):
        try:
            self.process.stdin.write(canonical(obs) + '\n')
            self.process.stdin.flush()
            if not self.selector.select(self.timeout):
                self.close()
                return {'accepted': False, 'status': 'timeout', 'reason': 'policy response timeout'}
            line = self.process.stdout.readline()
            if not line:
                return {'accepted': False, 'status': 'worker_error', 'reason': 'policy process exited'}
            return json.loads(line)
        except (BrokenPipeError, OSError, ValueError) as error:
            return {'accepted': False, 'status': 'worker_error', 'reason': str(error)[:200]}

    def close(self):
        if getattr(self, 'selector', None):
            self.selector.close()
            self.selector = None
        if self.process.poll() is None:
            self.process.kill()
        self.process.wait(timeout=2)
        for pipe in (self.process.stdin, self.process.stdout):
            if pipe:
                pipe.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def validate_policy(source, probes=None, provenance=False):
    if not isinstance(source, str) or len(source.encode()) > core.RUNTIME_SOURCE_LIMIT:
        return {'accepted': False, 'status': 'encoding', 'reason': 'missing or oversized source'}
    probes = probe_observations() if probes is None else probes
    actions = []
    with PolicyProcess(source, provenance=provenance) as worker:
        for obs in probes:
            result = worker.decide(obs)
            if not result.get('accepted'):
                return dict(result, accepted=False)
            action = result.get('action')
            if action not in ACTIONS or not obs['valid_' + action]:
                return {'accepted': False, 'status': 'invalid_move', 'reason': 'policy chose an immobile direction'}
            actions.append(action)
    if len(set(actions)) < 2:
        return {'accepted': False, 'status': 'unreactive', 'reason': 'constant action on fixed probes'}
    return {'accepted': True, 'status': 'ready', 'actions': actions,
            'behavior_hash': fingerprint(actions), 'source_hash': hashlib.sha256(source.encode()).hexdigest()}


def make_reference(programs):
    probes = probe_observations()
    records = []
    for index, source in enumerate(programs):
        result = validate_policy(source, probes)
        if not result['accepted']:
            raise ValueError('corpus policy %d failed: %s' % (index + 1, result))
        records.append({'index': index, 'source_key': core.program_key(source),
                        'behavior_hash': result['behavior_hash']})
    return {'kind': '2048', 'format': 1, 'probes': probes, 'records': records,
            'programs_hash': fingerprint(programs),
            'behavior_hashes': sorted({record['behavior_hash'] for record in records}),
            'source_keys': sorted({record['source_key'] for record in records})}


def run_episode(source, seed, max_moves=128, provenance=False):
    if type(max_moves) is not int or not 1 <= max_moves <= 2048:
        raise ValueError('max_moves must be 1..2048')
    game = Game2048(seed)
    initial = list(game.board)
    trajectory, status, diagnostic = [], 'move_limit', None
    executed_lines = set()
    executed_spans = set()
    started = time.monotonic()
    with PolicyProcess(source, provenance=provenance) as worker:
        for index in range(max_moves):
            if not game.legal_actions():
                status = 'terminal'
                break
            if time.monotonic() - started > 30:
                status = 'timeout'
                break
            obs = game.observation()
            decision = worker.decide(obs)
            executed_lines.update(decision.get('executed_lines', []))
            if provenance:
                observed = decision.get('action_provenance') or {}
                executed_spans.update(tuple(span) for span in observed.get('executed_spans', []))
            if not decision.get('accepted'):
                status, diagnostic = decision.get('status', 'worker_error'), decision
                break
            action = decision.get('action')
            if action not in ACTIONS:
                status = 'invalid_action'
                break
            transition = game.step(action)
            transition.update(observation=obs, decision=decision)
            transition['action_credit'] = action_credit(transition['before'], action)
            trajectory.append(transition)
            if not transition['valid']:
                status = 'invalid_move'
                break
    if status == 'move_limit' and not game.legal_actions():
        status = 'terminal'
    completed = status in ('terminal', 'move_limit')
    # Real merge score only. An invalid/failed policy receives no learning reward.
    reward = game.score / (game.score + 512.0) if completed else 0.0
    episode = {'seed': seed, 'status': status, 'completed': completed, 'score': game.score,
            'max_tile': max(game.board), 'moves': game.moves, 'reward': reward,
            'initial_board': initial, 'final_board': game.board, 'trajectory': trajectory,
            'diagnostic': diagnostic, 'max_moves': max_moves,
            'executed_lines': sorted(executed_lines)}
    if provenance:
        episode['executed_spans'] = [list(span) for span in sorted(executed_spans)]
        receipts = [(transition['decision'].get('action_provenance') or {}) for transition in trajectory]
        episode['provenance_coverage'] = {
            'decisions': len(receipts),
            'statuses': dict(Counter(receipt.get('status', 'missing') for receipt in receipts)),
            'unsupported_reasons': dict(Counter(receipt.get('reason') or 'unspecified'
                                               for receipt in receipts if receipt.get('status') != 'ok')),
            'empty_selected_slices': sum(not receipt.get('credit_spans') for receipt in receipts),
            'selected_span_occurrences': sum(len(receipt.get('credit_spans') or []) for receipt in receipts),
            'executed_span_occurrences': sum(len(receipt.get('executed_spans') or []) for receipt in receipts),
        }
    return episode


def attempt(model, sample_seed, episode_seed, learn=True, max_moves=128, provenance=None):
    before = fingerprint(model.state_dict())
    generated = model.generate(seed=sample_seed)
    config = getattr(model, 'decision_credit_config', {'enabled': False})
    needs_provenance = config.get('enabled') and config.get('contract') in PROVENANCE_CONTRACTS
    if provenance is None:
        provenance = bool(needs_provenance)
    elif type(provenance) is not bool or needs_provenance and not provenance:
        raise ValueError('active provenance credit requires runtime observation')
    source = generated.get('source')
    reference = model.reference
    if reference.get('kind') != '2048' or reference.get('programs_hash') != fingerprint(model.programs):
        raise ValueError('state is not a matching 2048 island')
    record = {'sample_seed': sample_seed, 'episode_seed': episode_seed, 'source': source,
              'source_hash': hashlib.sha256(source.encode()).hexdigest() if isinstance(source, str) else None,
              'reward': 0.0, 'played': False, 'training_applied': False}
    policy, runtime_ok, diagnostic = None, False, None
    if source is None:
        record['status'] = 'encoding'
    elif generated.get('truncated'):
        record['status'] = 'truncated'
    elif core.program_key(source) in reference['source_keys']:
        record['status'] = 'corpus_source_replay'
        runtime_ok = True
    else:
        policy = validate_policy(source, reference['probes'], provenance=provenance)
        runtime_ok = policy['accepted']
        diagnostic = policy
        record['policy'] = policy
        if not runtime_ok:
            record['status'] = policy['status']
        elif policy['behavior_hash'] in reference['behavior_hashes']:
            record['status'] = 'corpus_probe_behavior_replay'
        else:
            episode = run_episode(source, episode_seed, max_moves, provenance=provenance)
            record.update(played=True, episode=episode, status=episode['status'], reward=episode['reward'])
            diagnostic = episode.get('diagnostic') or {'status': 'ok' if episode['completed'] else episode['status']}
            runtime_ok = episode['completed']
    record['runtime_ok'] = runtime_ok
    record['executed_lines'] = record.get('episode', {}).get('executed_lines', [])
    if learn:
        feedback = None
        if config['enabled'] and record['played'] and runtime_ok:
            feedback = decision_feedback(source, record['episode'], config['contract'])
        options = {'executed_spans': record.get('episode', {}).get('executed_spans', [])} if needs_provenance else {}
        model.observe(generated, record['reward'], runtime_ok,
                      error_line=(diagnostic or {}).get('error_line'),
                      behavior=policy.get('behavior_hash') if policy and policy['accepted'] else None,
                      diagnostic=diagnostic or {'status': record['status']},
                      executed_lines=record['executed_lines'],
                      environment_observed=record['played'],
                      decision_feedback=feedback, **options)
        record['training_applied'] = True
    elif fingerprint(model.state_dict()) != before:
        raise AssertionError('frozen episode changed organism')
    record['state_before'] = before
    record['state_after'] = fingerprint(model.state_dict())
    return record


def random_legal_episode(seed, max_moves=128):
    """Explicit nonlearned baseline, using its own seeded action RNG."""
    game = Game2048(seed)
    chooser = random.Random(seed ^ 0x2048)
    initial, trajectory = list(game.board), []
    for index in range(max_moves):
        actions = game.legal_actions()
        if not actions:
            break
        transition = game.step(chooser.choice(actions))
        trajectory.append(transition)
    terminal = not game.legal_actions()
    return {'seed': seed, 'status': 'terminal' if terminal else 'move_limit',
            'completed': True, 'score': game.score, 'max_tile': max(game.board),
            'moves': game.moves, 'reward': game.score / (game.score + 512.0),
            'initial_board': initial, 'final_board': game.board, 'trajectory': trajectory,
            'max_moves': max_moves, 'baseline': 'uniform_random_legal'}


def fixed_greedy_episode(seed, max_moves=128):
    """Explicit baseline: immediate merge score, then empty cells, then L/D/R/U.

    This policy is evaluated independently; generated programs never call it.
    It sees the same board and performs no random-spawn lookahead.
    """
    game = Game2048(seed)
    initial, trajectory = list(game.board), []
    tie_order = ('left', 'down', 'right', 'up')
    for _ in range(max_moves):
        choices = []
        for rank, action in enumerate(tie_order):
            after, gained, changed = slide(game.board, action)
            if changed:
                choices.append(((gained, after.count(0), -rank), action))
        if not choices:
            break
        trajectory.append(game.step(max(choices)[1]))
    terminal = not game.legal_actions()
    return {'seed': seed, 'status': 'terminal' if terminal else 'move_limit',
            'completed': True, 'score': game.score, 'max_tile': max(game.board),
            'moves': game.moves, 'reward': game.score / (game.score + 512.0),
            'initial_board': initial, 'final_board': game.board, 'trajectory': trajectory,
            'max_moves': max_moves, 'baseline': 'greedy_merge_then_empty_LDRU'}


def summarize(records):
    episodes = [record['episode'] for record in records if record['played']]
    return {'raw_attempts': len(records), 'played': len(episodes),
            'runtime_ok': sum(record.get('runtime_ok', record['played']) for record in records),
            'syntax_error': sum(record['status'] == 'syntax_error' for record in records),
            'corpus_replay': sum(record['status'] in ('corpus_source_replay', 'corpus_probe_behavior_replay') for record in records),
            'distinct_played_sources': len({record['source_hash'] for record in records if record['played'] and record.get('source_hash')}),
            'completed': sum(episode['completed'] for episode in episodes),
            'completed_score_per_raw_attempt': sum(episode['score'] for episode in episodes if episode['completed']) / max(1, len(records)),
            'reward_per_raw_attempt': sum(record.get('reward', record.get('episode', {}).get('reward', 0.0)) for record in records) / max(1, len(records)),
            'score_per_raw_attempt': sum(episode['score'] for episode in episodes) / max(1, len(records)),
            'mean_played_score': sum(episode['score'] for episode in episodes) / max(1, len(episodes)),
            'best_score': max((episode['score'] for episode in episodes), default=0),
            'max_tile': max((episode['max_tile'] for episode in episodes), default=0),
            'statuses': dict(Counter(record['status'] for record in records))}


def run_cli():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    init = sub.add_parser('init')
    init.add_argument('--island', type=Path, default=ROOT / 'corpora' / '2048.txt')
    init.add_argument('--state', type=Path, required=True)
    init.add_argument('--seed', type=int, default=71)
    for command in ('play', 'evaluate'):
        item = sub.add_parser(command)
        item.add_argument('--state', type=Path, required=True)
        item.add_argument('--out', type=Path, required=True)
        item.add_argument('--attempts', type=int, default=100)
        item.add_argument('--seed', type=int, default=3100000 if command == 'play' else 3500000)
        item.add_argument('--episode-seed', type=int, default=3200000 if command == 'play' else 3600000)
        item.add_argument('--max-moves', type=int, default=128)
        if command == 'play':
            item.add_argument('--sequence-memory', action=argparse.BooleanOptionalAction,
                              default=None, help='ordered-unit recurrent memory; omitted preserves saved choice')
            item.add_argument('--experience-support', type=float,
                              help='Lee experienced-suffix count mass (0..0.25); omitted preserves saved choice')
            item.add_argument('--control-learning', choices=('legacy', 'quality', 'trace', 'both'),
                              help='optional learning experiment, stored in the saved state; omitted preserves its current choice')
            item.add_argument('--decision-credit', choices=('off', 'uniform', 'advantage', 'temporal', 'provenance'),
                              help='optional decision-local credit; omitted preserves the saved choice')
    args = parser.parse_args()
    if args.command == 'init':
        programs = core.read_island(args.island)
        reference = make_reference(programs)
        model = core.Organism(programs, seed=args.seed, mode='control', _reference=reference)
        model.save(args.state)
        print(canonical({'state': str(args.state), 'programs': len(programs),
                         'probe_behavior_count': len(reference['behavior_hashes'])}))
        return
    if not 1 <= args.attempts <= 100000:
        parser.error('attempts must be 1..100000')
    model = core.Organism.load(args.state)
    if args.command == 'play' and args.sequence_memory is not None:
        model.configure_sequence_memory(args.sequence_memory)
    if args.command == 'play' and args.experience_support is not None:
        model.configure_experience_support(args.experience_support)
    if args.command == 'play' and args.control_learning is not None:
        model.configure_control_learning(quality=args.control_learning in ('quality', 'both'),
                                         executed_credit=args.control_learning in ('trace', 'both'))
    if args.command == 'play' and args.decision_credit is not None:
        model.configure_decision_credit(enabled=args.decision_credit != 'off',
                                        contract=DECISION_CONTRACTS.get(args.decision_credit),
                                        attribution=(None if args.decision_credit == 'off' else
                                                     'source_spans' if args.decision_credit == 'provenance' else 'executed_lines'))
    args.out.mkdir(parents=True, exist_ok=False)
    protocol = {'command': args.command, 'attempts': args.attempts, 'sample_seed': args.seed,
                'episode_seed': args.episode_seed, 'max_moves': args.max_moves,
                'state_sha256': hashlib.sha256(args.state.read_bytes()).hexdigest(),
                'bridge_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'core_sha256': hashlib.sha256(Path(core.__file__).read_bytes()).hexdigest()}
    if args.command == 'play':
        if args.sequence_memory is not None:
            protocol['sequence_memory_override'] = args.sequence_memory
        protocol['control_learning_override'] = args.control_learning
        protocol['decision_credit_override'] = args.decision_credit
        if args.experience_support is not None:
            protocol['experience_support_override'] = args.experience_support
    save_json(args.out / 'protocol.json', protocol)
    reports = {}
    controls = [('trained', model)]
    if args.command == 'evaluate':
        control = model.without_experience()
        control.seen, control.behaviors = set(model.seen), set(model.behaviors)
        control.visits, control.stats = dict(model.visits), dict(model.stats)
        control.exploration, control.memory_strength = model.exploration, model.memory_strength
        control.rng.setstate(model.rng.getstate())
        controls.append(('without_experience', control))
    for arm, organism in controls:
        records = []
        with (args.out / (arm + '.jsonl')).open('w', encoding='utf-8') as stream:
            for index in range(args.attempts):
                record = attempt(organism, args.seed + index, args.episode_seed + index,
                                 args.command == 'play', args.max_moves)
                records.append(record)
                archive_record(args.out, arm, index, record)
                stream.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + '\n')
                stream.flush()
                if args.command == 'play' and (index + 1) % 25 == 0:
                    organism.save(args.state)
        finalize_archive(args.out, arm, records)
        if args.command == 'play':
            organism.save(args.state)
        reports[arm] = summarize(records)
    if args.command == 'evaluate':
        for name, baseline in (('random_legal', random_legal_episode), ('fixed_greedy', fixed_greedy_episode)):
            records = []
            with (args.out / (name + '.jsonl')).open('w', encoding='utf-8') as stream:
                for index in range(args.attempts):
                    episode = baseline(args.episode_seed + index, args.max_moves)
                    record = {'played': True, 'episode': episode, 'status': episode['status']}
                    records.append(record)
                    archive_record(args.out, name, index, record)
                    stream.write(json.dumps(record, allow_nan=False) + '\n')
            finalize_archive(args.out, name, records)
            reports[name] = summarize(records)
        if hashlib.sha256(args.state.read_bytes()).hexdigest() != protocol['state_sha256']:
            raise AssertionError('evaluation mutated saved state')
    protocol['bridge_sha256_after'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    protocol['core_sha256_after'] = hashlib.sha256(Path(core.__file__).read_bytes()).hexdigest()
    protocol['frozen_sources'] = all(protocol[key] == protocol[key + '_after'] for key in ('bridge_sha256', 'core_sha256'))
    save_json(args.out / 'protocol.json', protocol)
    if not protocol['frozen_sources']:
        raise RuntimeError('bridge/core changed during this run; raw evidence retained, rerun frozen sources')
    save_json(args.out / 'summary.json', reports)
    print(json.dumps(reports, indent=2))


if __name__ == '__main__':
    if sys.argv[1:] == ['--policy-worker']:
        policy_worker()
    else:
        run_cli()
