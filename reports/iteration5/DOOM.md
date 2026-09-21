# Doom: zero passive combat credit

The optional `--reward-mode combat` uses a new explicit saved-state contract, `player-combat-engagement-v1`:

`reward = 0 if player_damage_dealt <= 0 else 0.5 + 0.5*tanh((player_damage_dealt/100 - .01*player_damage_received - .005*ammo_spent)/3)`

The new mode removes positive reward from episodes with no direct player damage. Every active-combat reward remains exactly equal to attributed-v1. This preserves the model's existing reward-above-0.5 threshold for acquiring successful continuations. Legacy and attributed modes retain their formulas and state contracts. Native Doom physics and telemetry are unchanged.

A preliminary rescaled-reward protocol was interrupted after 37 completed attributed-arm training attempts, before evaluation, when its changed acquisition threshold was identified. Its source, protocol, checkpoint, and receipts remain separate. The final engagement-gate protocol was registered with new generation seeds before the primary experiment.

## Fixed comparison

Both arms copy the same published Doom state from commit `ea8e1519`, then train for 128 attempts each. They share generation seeds, training phases 0–127, and 64 fresh evaluation phases 128–191. MAP02, skill 3, and the 512-decision budget are fixed. The model, bridge, and native engine are frozen. Only the reward differs; quality-head and trace options remain disabled. The final checkpoint is designated before evaluation, with no checkpoint search.

Both arms are assessed using the SAME combat-engagement reward, with rejected attempts counted as zero:

| Measurement / raw attempt | Attributed-v1 training | Combat-engagement training |
|---|---:|---:|
| Played attempts | 33 / 64 | 38 / 64 |
| Shared combat reward | 0.258924 | 0.282559 |
| Direct player damage | 48.812500 | 53.687500 |
| Direct player kills | 1.390625 | 1.531250 |
| Received damage | 31.765625 | 36.984375 |

Paired common-reward difference: **+0.023635**, fixed-seed bootstrap 95% interval **[−0.013769, +0.063611]**. Total direct damage is 3,124 versus 3,436; direct kills are 89 versus 98. Both experimental checkpoints remain private; the published Doom state is preserved.

## Actual-game controls

Each control plays 16 fixed starts. Both reward formulas are computed from the same recorded episode consequences.

| Policy | Direct damage | Direct kills | Native Doom kills | Attributed reward | Combat reward |
|---|---:|---:|---:|---:|---:|
| Turn left continuously | 0 | 0 | 0 | 0.500000 | 0.000000 |
| Move forward continuously | 0 | 0 | 39 | 0.339244 | 0.000000 |
| Aim and fire | 1,687 | 52 | 61 | 0.506722 | 0.506722 |

The gate removes the passive reward while preserving the active control's exact reward. These are comparison policies; generated model policies remain unchanged.

## Temporal development

A separate comparison starts both organisms from birth, with 64 training and 32 evaluation attempts per arm, the same combat reward, matching game starts, and 512 decisions. It changes the sensor together with its matching 64-program corpus: legacy uses the original corpus; temporal uses the corpus containing previous action, movement, received-damage, and coarse-distance conditions.

| Frozen evaluation | Legacy sensor/corpus | Temporal sensor/corpus |
|---|---:|---:|
| Played / raw | 17 / 32 | 14 / 32 |
| Combat reward / raw | 0.261235 | 0.219324 |
| Direct damage / raw | 48.875000 | 41.093750 |
| Direct kills / raw | 1.312500 | 1.468750 |
| Received damage / raw | 39.937500 | 33.625000 |

Paired reward difference: −0.041911; bootstrap 95% interval [−0.148878, +0.065973]. These development states remain private.

## Verification and example

42 Doom tests pass. New tests establish zero reward without player damage, exact preservation of every tested active attributed reward and acquisition decision, bounded reward, configuration acceptance, and rejection of silently resuming an attributed state under the combat contract. Every completed primary episode was reread immediately: all **109,266 transitions** matched step counts, final states, and summed counter deltas. Persisted-file inspection found 28 truncated trajectory tails across the primary/control and temporal runs. Separate deterministic replays restored 3,269 rows; every retained prefix matches byte for byte, and all final states, counters, source hashes, and engine hashes match. Originals remain untouched. All 28 recovered files passed hash and row-count verification after the worker closed.

The bridge now first writes a complete immutable `trajectory-<sha256>.jsonl` artifact and binds its filename, hash, and row count in the episode receipt. The compatibility `trajectory.jsonl` path is written only after completion; no partial canonical trajectory is streamed. Two new tests verify immutable-file independence from the compatibility path and the absence of canonical streaming during native execution.

The first played held-out combat attempt (`combat/evaluate/0000`, generation seed 28,000,000, engine seed 128) writes a reactive aiming/shooting program. In its 512-decision episode it deals 77 damage, makes two direct kills, records three native Doom kills, and receives 57 damage. `candidate.py`, `episode.json`, `trajectory.jsonl`, and `frame_064.png` preserve the exact example. Source SHA256: `d86c38dddf4b81c4a68eef805517027c220857fae2257ba9888efbf92c053683`.

Use `--reward-mode combat` explicitly when creating or resuming a separate combat state. Existing default commands keep their established reward behavior.
