# Fifth engineering pass — decisions become learning signals

Baseline: `ea8e1519db2453375373ec3283a9988288b2b026`. The two standalone bodies retain standard-library execution and exact generated source. Published island states remain unchanged. The new game learning/reward modes are explicit choices.

## 2048: credit for actual decisions

The host compares the selected move's immediate merge gain with all legal moves on the actual pre-spawn board. Minimum and maximum gains define a target in [0,1]; ties receive .5. The code still selects every action. After the episode, each generated continuation association receives the mean target from decisions whose execution included it, and one credit update. Repeated loop traces and longer episodes do not multiply the trial count.

The separate saved decision-credit table softly weights future generated programs. Existing episode credit, runtime/syntax learning and continuation acquisition keep their original rules. The explicit `uniform` control uses the same trace and credit-update rules, applied to each arm's actual decisions, with terminal episode reward at every decision. This separates the new feedback information from adding another credit table.

Two replicas, 128 training and 64 fresh evaluation attempts per arm:

| Learning | Played / raw | Completed score / raw | Mean score when played |
|---|---:|---:|---:|
| Existing | 84/128 | 659.78 | 1005.38 |
| Uniform decision targets | 84/128 | 687.69 | 1047.90 |
| Board-relative targets | 84/128 | 683.88 | 1042.10 |

Board-relative targets improved score/raw by +17.375 and +30.8125 in the two replicas. The pooled gain was +24.09375, with paired bootstrap 95% interval [−22.25,72.72]. Uniform targets were ahead by 3.8125 points/raw. The predeclared advancement rule required at least +25 points/raw and an advantage over the uniform control, so no confirmation sweep or snapshot replacement followed.

The implementation is available through `2048.py play --decision-credit advantage`, with `uniform` and `off` for controls. Omission retains the saved setting. The host receives board information during play; the program generator receives its learned state. [Mechanism and API](LEARNING.md), [fixed protocol](protocol-2048.json), [complete compact decision](2048-decision.json).

## Doom: reward belongs to combat

`doomer.py --reward-mode combat` assigns zero reward when the player dealt no damage. Once the player has dealt damage, the attributed-v1 formula remains exactly unchanged. This preserves the established acquisition threshold for active combat.

The initial rescaling proposal would also have shifted the core's reward>.5 continuation-acquisition threshold. Its development run was stopped after 37 training attempts and retained separately. The gated comparison started with a fresh protocol and disjoint generation seeds.

Each arm trained for 128 attempts, then faced the same 64 fresh generation/game starts. Both are evaluated below using the same combat reward:

| Outcome | Attributed training | Combat-gated training |
|---|---:|---:|
| Played attempts | 33/64 | 38/64 |
| Common reward / raw attempt | .258924 | .282559 |
| Actual player damage | 3124 | 3436 |
| Direct player kills | 89 | 98 |
| Damage received | 2033 | 2367 |

Paired common-reward difference +.023635; bootstrap 95% interval [−.013769,.063611]. The current release state and default reward are preserved; the new reward is an explicit environment contract.

Controls establish the rule directly. Turning without combat changes from .5 to zero; forward movement with 39 native infighting kills and no player damage changes from .339244 to zero. The aim-and-shoot control remains .506722 on the same episodes.

A separate development comparison trained fresh legacy and temporal islands for 64 attempts each and evaluated 32 attempts each under the combat reward. Legacy played 17/32 with reward/raw .261235; temporal played 14/32 with .219324. Corpus and observation contract changed together. Both experimental states remain separate. [Doom report](DOOM.md), [primary protocol](protocol-doom.json), [temporal protocol](protocol-doom-temporal.json), [compact outcomes](doom-comparison.json).

## Code: preserve coherence without copying the whole island

The fixed candidate used the most recently introduced ordinary learned unit outside the local context window, with the existing first-unit memory as fallback. It was evaluated in two replicas, each with 128 training and 128 fresh evaluation attempts per task. The corpus, judge, output contracts and candidate probabilities stayed explicit and unchanged except for this memory rule.

| Outcome, 256 attempts per task | Existing first anchor | Recent anchor |
|---|---:|---:|
| Table productive executions | 91 | 57 |
| Table task completions | 0 | 0 |
| Numeric task completions | 140 | 129 |
| Table source replays | 56 | 100 |
| Numeric source replays | 14 | 28 |

Table runtime successes increased 148→159 and NameError decreased 18→11. Numeric NameError decreased 7→3. The concrete loss was the increased frequency of corpus copies rejected by the existing novelty court. The candidate failed its prospective gate and remains in the research archive. The published first-anchor mechanism is unchanged. [Code report](CODE.md), [protocol](protocol-code.json), [outcomes](code-comparison.json).

## Verification and evidence

The completed full suite passes [253 tests](tests.json), with [full test output](tests.log). The independent audit reconciles [4,592 completed experiment attempts](audit-summary.json). All [six real routes](routes.json) reproduced exact generated source and preserved their published states. Opted-in [split-versus-uninterrupted resume checks](resume.json) produced byte-identical final states for both 2048 modes and native Doom combat. Code preserved all 2,560 measured attempts. The 2048 experiment preserved 1,152 generated attempts and 256 control episodes using immutable per-attempt receipts and hash manifests.

Doom accounting verifies 141,401 native transitions. Twenty-eight original journals had truncated tails: deterministic recovery restored 3,269 rows into separate immutable files, with byte-identical retained prefixes and matching final counters. Original partial journals remain in the archive. The final bridge publishes complete trajectories under content-hash filenames and binds each name, SHA256 and row count in the episode receipt; [independent validation](archive-validation.json) exercised this writer in real native play. One 2048 resume smoke journal retained seven of eight rows; the complete measured split journals and byte-identical final states are preserved, with the partial journal identified explicitly in the audit.

The gallery preserves exact generated code, a real 2048 decision with its board/action targets, a native Doom frame and an executed corpus replay rejected by the court. Public reports contain compact summaries, protocols and verification receipts; full attempts, checkpoints and trajectories are stored in a [separate compressed archive](private-archive-inventory.json).

## Next questions grounded in this pass

Code needs a memory-selection rule that keeps useful variable relationships while retaining new combinations. The recent-anchor experiment separates improved execution from increased source copying. In 2048, uniformly reinforcing recent successful experience is the stronger current comparator; a more informative action objective must exceed it. Doom can now learn under a reward contract where passive survival receives no combat credit.

Related primary research: [COMA](https://arxiv.org/abs/1705.08926) studies counterfactual action baselines for credit assignment; [RUDDER](https://arxiv.org/abs/1806.07857) studies redistribution of delayed return. Our specific host targets and comparisons are described in [research.json](research.json) and the fixed protocols above.
