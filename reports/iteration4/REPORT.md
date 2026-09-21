# Fourth engineering pass — measured changes

Baseline: `6b12cc0c9e4a8465b858038e230b6f2c3ec2e9a2`. Corpus programs, output contracts and generation budgets were fixed before each comparison. All original attempts remain in the denominator.

## Code: optional distant continuation memory

`nettacode.py --anchor-memory` explicitly enables a sparse association between the first ordinary learned unit, the current 0–2-unit suffix and its continuation. It weights existing candidates softly. Acquired programs update the associations; snapshots retain them. Lee keeps its existing local memory. Old Code snapshots retain exactly their previous generation and save format until activation.

Three replicas × 256 fresh evaluation attempts per task:

| Task | Baseline | Anchor | Same trained state, anchor disabled |
|---|---:|---:|---:|
| Sorted numeric output | 377/768 | **422/768** | 393/768 |
| Table output | 0/768 | 1/768 | 0/768 |

Numeric improvement: +5.86 percentage points, paired bootstrap 95% interval +3.26 to +8.59. Summed within-replica distinct successful numeric programs: 17 → 28. Table execution improved, but successful table output remains rare. The same mixed corpus contains 52 numeric-task examples and only eight table-task examples. No corpus or contract was changed.

The feature ships as an opt-in. `states/code.json` remains unchanged; no export replica was designated prospectively. [Mechanism and complete compact results](CODE.md).

## 2048: separate return prediction and executed-line credit

Both bodies now support an optional 545-parameter environment-return head and optional executed-line eligibility. The game hosts supply traces from actual decisions; validation probes do not supply episode credit. Rejected corpus replays retain their existing negative credit. The settings are saved with experience, and remain off in the published snapshots.

Two replicas, 128 training and 64 fresh evaluation attempts per arm:

| Arm | Played / raw attempts | Completed score / raw attempt |
|---|---:|---:|
| Existing learning | 72/128 | 557.91 |
| Quality head | 71/128 | 541.81 |
| Executed-line credit | 72/128 | 557.91 |
| Both | 71/128 | 541.81 |

Corrected trace and baseline produced identical held-out programs and episodes. In the corrective training runs, 302 of 325 completed programs executed every statement line; average coverage was 99.36%. Episode-wide line eligibility therefore supplies little discrimination for these short policies.

On the 72 seeds actually played by baseline/trace, mean score was 991.83, versus random legal actions 983.33 and fixed greedy play 1288.06. No arm met the predeclared advancement rule; there was no confirmation sweep and `states/2048.json` remains unchanged. [Decision, budgets and controls](2048-decision.json).

## Doom: attribution and temporal observations

Native engine instrumentation records actual player damage, direct kills and damage received after the engine's armor/invulnerability handling. Overkill is capped by remaining monster health. Infighting and barrel explosions do not earn direct-player credit. A 512-decision legacy replay retained exact trajectory and PNG parity.

Optional `--reward-mode attributed` uses these counters. Optional `--sensor temporal` adds previous action, movement, damage receipt and coarse target distance. Its separate code-only island contains 64 programs with 52 distinct behaviors across 168 probes. Unprobed actual observations execute the exact generated source on demand.

After 128 training attempts, paired evaluation on 64 new starts gave:

| Outcome | Initial | Trained |
|---|---:|---:|
| Played attempts | 39/64 | 38/64 |
| Reward / raw attempt | .290485 | .306757 |
| Actual player damage | 3118 | 3562 |
| Direct player kills | 92 | 97 |
| Damage received | 3003 | 2356 |

Paired reward difference +.016272; bootstrap 95% interval −.055207 to +.084070. The published Doom snapshot and legacy reward remain unchanged.

A movement-only control accumulated 39 standard Doom kills with zero player damage; attributed credit excludes those kills. Safe turning retains neutral reward .5, identifying the next reward-design question. Temporal development played 13/32 training attempts and 4/16 evaluation attempts. The selected gallery episode caused 120 player damage, four direct kills and 12 damage received in 128 decisions. [Doom protocol, controls and measurements](DOOM.md).

## Caller, verification and evidence

Either standalone body can now dispatch an ordinary request to the sibling body that owns the selected snapshot. Every selected body validates and loads its own state. The caller retains human-editable JSON routing and does not merge island experience.

Independent accounting checked 8,960 Code attempts, 155,175 generated-policy 2048 transitions, and 78,747 Doom decisions including controls and temporal development. Separate CPython executions checked source outputs/actions/traces. Some completed-run journal tails were absent: 22 Code rows, 319 2048 rows, and 3,205 decisions across 27 Doom trajectories were recovered into separate files by frozen deterministic replay. Surviving prefixes and final checkpoints/counters matched; originals were retained. New completed-phase writers use atomic replacement.

**212 tests pass** in the final suite ([output](tests.log)). All six routes ran through `nettalee.py`, including sibling Code dispatch and actual games: 48/48 generated sources reproduced exactly and all six snapshots remained unchanged ([route receipt](routes.json), [independent audit](audit-summary.json)). Only compact reports, protocols and audit receipts are published here; raw attempts, checkpoints and complete trajectories remain in a separate compressed research archive.

Protocols: [Code confirmation](protocol-code.json), [2048 original](protocol-2048-original.json), [2048 correction](protocol-2048-corrected.json), [Doom](protocol-doom.json).

## Next hypotheses

- Code: remember a later learned context to distinguish record families whose beginnings coincide.
- 2048: condition credit on board/action decisions; nearly every line receives the same end-of-episode return today.
- Doom: test a combat objective that gives no positive reinforcement for zero damage dealt, then compare temporal and legacy sensing on matched starts.

These are subsequent experiments, not changes silently applied to the measured runs. Relevant primary research and our concrete design choices are recorded in [research.json](research.json): [CodeRL](https://arxiv.org/abs/2207.01780), [RUDDER](https://arxiv.org/abs/1806.07857), and [memory-based control](https://arxiv.org/abs/1512.04455).
