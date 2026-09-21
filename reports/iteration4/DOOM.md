# Doom: attributed consequences and temporal observation

The bridge now records actual monster health removed by player attacks, capped at the target's remaining health, and player-attributed direct kills. Doom's native killcount remains a separate counter. Damage to non-monsters, monster infighting, and barrel explosion inflictors are excluded from direct attack credit. Received damage is recorded after immunity and armor, so health pickups cannot hide it.

`--reward-mode attributed` selects the explicit formula
`0.5 + 0.5*tanh((player_damage_dealt/100 - .01*player_damage_received - .005*ammo_spent)/3)`.
The existing state and default legacy reward are unchanged. A different reward or sensor requires a separately bound state.

## Fixed paired comparison

The protocol was written before execution. Both arms start from the published Doom experience; one receives 128 additional training attempts with attributed reward. Evaluation uses the same 64 generation seeds and 64 distinct held-out Doom RNG phases, MAP02, skill 3, 512 decisions. Training uses phases 0–127, evaluation 128–191. Frozen source and engine hashes are in the private manifest. This run uses the existing learning mechanism, with the new quality/trace options off.

| Measurement | Baseline | After 128 training attempts |
|---|---:|---:|
| Played / raw attempts | 39 / 64 | 38 / 64 |
| Reward per raw attempt | 0.290485 | 0.306757 |
| Actual player damage | 3,118 | 3,562 |
| Direct player kills | 92 | 97 |
| Received damage | 3,003 | 2,356 |
| Native Doom killcount | 131 | 119 |

Paired reward difference: +0.016272; fixed-seed bootstrap 95% interval: −0.055207 to +0.084070. `states/doom.json` is preserved; the trained comparison state stays with the experiment.

Three handwritten controls each played the first 16 held-out starts. They are comparison policies and never replace generated code:

| Control | Actual player damage | Direct kills | Native killcount | Mean attributed reward |
|---|---:|---:|---:|---:|
| Turn left continuously | 0 | 0 | 0 | 0.500000 |
| Move forward continuously | 0 | 0 | 39 | 0.339244 |
| Aim and fire | 1,687 | 52 | 61 | 0.506722 |

The forward control makes the native killcount distinction concrete. Safe turning still receives the formula's neutral 0.5; the next reward experiment should address reinforcement without combat contribution.

## Temporal sensor

`--sensor temporal` adds `previous_action`, `moved`, `took_damage`, and coarse `distance` to the original health/ammo/scene inputs. These are host observations; Lee writes the decisions. Each unseen observation executes the unchanged program in the bounded Python judge, then caches its exact result. A live execution failure ends the episode with zero policy reward. No action fallback or indentation repair is used.

The separate `corpora/doom_temporal.txt` contains 64 scripts in four structural families. All 64 pass 168 fixed public probe inputs; 52 distinct probe behaviors occur. Novelty is measured on those probes, not by asserting exhaustive temporal equivalence. The separate development run played 13 of 32 training attempts and 4 of 16 frozen evaluation attempts. Its first played held-out policy uses damage and previous-action/movement inputs, performs 128 decisions, and earns four direct kills / 120 actual damage. This developmental state does not replace the published Doom state.

Both games expose the same opt-in `--control-learning legacy|quality|trace|both` interface. Doom supplies only lines executed on observations actually encountered in an episode. An eight-attempt native smoke run with `both` played three episodes and recorded exactly three quality observations.

## Verification and trace completeness

33 Doom tests pass, including compilation of the actual C accounting function against fixtures for overkill, monster damage, environment damage, non-monsters, and stale player attribution on barrel inflictors. MAP02's 196-object THINGS lump contains zero barrels. Adding counters preserved all 512 historical trajectory rows' existing fields and the combat-frame image hash. The final barrel-excluding engine preserved all 512 instrumented rows as well.

Independent inspection found 27 complete episodes with truncated raw trajectory tails. The original files were retained. Separate deterministic replays restored 3,205 rows, matching every retained prefix byte for byte and all final counters, states, source hashes, and frozen-engine hashes. The bridge now writes completed trajectories by atomic replacement of the complete bounded in-memory record; JSON receipts are flushed, synced, and atomically replaced. Two recovered files also required a second replay; those second replays matched the complete hashes from the first replay. All original and intermediate files remain preserved. Recovery mappings remain with the private raw experiment.
