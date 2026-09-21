# NETTA LEE LOG

Newest entries first. Technical changes and measured experiments live here; README describes the current organism.

## 2026-09-21 — Game consequences, temporal perception and shared routing

Added independently selectable `quality` and `trace` learning mechanisms to the
standalone organisms. The quality head has 545 parameters and learns continuous
reward from completed, actually observed game episodes. Executed-line credit
selects generated choices overlapping lines encountered in actual play; probe
validation supplies no episode trace, and repeated loop execution cannot multiply
credit. Runtime/syntax learning stays separate. An initial development variant
also omitted penalties for unplayed corpus replays; the corrected gate preserves
those penalties and was measured separately. Both mechanisms remain off in the
published states and are available through the bridges' `--control-learning`
option. Settings, learned parameters and counts survive save/resume.

2048 used two replicas per arm, with 128 training and 64 fresh evaluation attempts
each. Completed score per raw attempt was 557.90625 for existing learning,
541.8125 for quality, 557.90625 for corrected trace and 541.8125 for both. No arm
met the advancement rule. Corrected trace and baseline produced identical
held-out programs and games; 302 of 325 completed corrective-training programs
executed every statement line. Mean statement coverage was 99.36%. The existing
`states/2048.json` is retained. Independent transition accounting covers the
original and corrective runs; compact summaries include the random and fixed
greedy controls.

Doom Generic now records capped actual monster health removed by direct player
attacks, player-attributed kills and actual damage received after armor. Native
Doom killcount remains separate. Infighting, non-monster targets and barrel
inflictors are excluded from direct-player credit. Counter instrumentation
preserved a historical 512-decision trajectory and combat-image hash. Optional
`--reward-mode attributed` uses player damage, received damage and ammunition;
the reward contract is bound to a separate state.

After 128 additional training attempts, 64 shared held-out Doom starts gave
39/64 played attempts before training and 38/64 afterward. Actual player damage
rose 3,118 to 3,562; direct kills 92 to 97; received damage fell 3,003 to 2,356.
Reward per raw attempt was 0.290485 versus 0.306757. Paired difference +0.016272,
bootstrap 95% interval [-0.055207, 0.084070]. A forward-only control accumulated
39 native kills with zero player damage; turning-only control retained neutral
reward 0.5. The published Doom state is retained.

Optional `--sensor temporal` adds previous action, movement, received damage and
coarse target distance. Its separate code-only `corpora/doom_temporal.txt` island
has 64 programs in four families, passing 168 fixed probes with 52 distinct probe
behaviors. Unseen actual observations execute the unchanged source on demand;
live policy failure ends the episode with zero policy reward. Development played
13/32 training and 4/16 held-out attempts. The selected gallery policy used the
new inputs and caused 120 direct damage and four kills over 128 decisions.

Either model's `ask` now dispatches cross-species routes to the matching sibling
body, which validates its own snapshot. All six routes passed a real execution
check: 48/48 generated sources reproduced exactly and every saved state remained
unchanged. The final suite passes 212 tests. README and gallery describe the
current mechanisms; [the fourth-pass report](reports/iteration4/REPORT.md) keeps
compact comparisons, protocols and audits. Raw rows, recovered tails, checkpoints
and full trajectories remain in the separate compressed experiment archive.

## 2026-09-21 — Game adapters renamed; reports published

The game adapters are now `doomer.py`, `doom.py` (its short entry point), and
`2048.py`. Both standalone models dispatch game routes to the new paths.
The rename passed the 166-test suite and actual JSON-routed game execution:
2048 completed its generated-policy episode; three of four Doom attempts
reached the game. Saved state bytes were unchanged. The verification receipt
is in `reports/verification/bridge-rename.json`.

`reports/INDEX.md` links nine unique historical reports and the retained
protocols, measured summaries, independent audits and recovery receipts.
The duplicate audit is represented once; superseded development READMEs and
full raw experiment ZIP payloads remain in the separate archives. Their
inventory is recorded under reports. New reports belong in this directory.
The README uses current adapter names and commands; gallery links the reports.

The two model files retain the same learned-memory implementation. Current
intentional differences are the module description, `SPECIES`, and
`DEFAULT_ORDER` (Lee 6, Code 4). Shared implementation changes are assembled
into both standalone files. Further mechanism differences will be recorded
with their experiments. This change preserves learning behavior and states.

## 2026-09-21 — Commands acquire memory; two games become executable islands

Both standalone organisms now learn a declared output contract through `ask --learn-task --save SNAPSHOT`. A contract indexes its own 545-parameter outcome head and continuation credit. Actual execution supplies the feedback; the TXT islands remain code only. Ordinary `ask` keeps memory frozen. Removing only task memory provides a paired control. Capacity errors are checked before state mutation.

Three independent runs per command used 512 training attempts and 256 fresh evaluation attempts each. Art completed 427/768 declared tasks versus 308 after task-memory erasure and 343 after ordinary training. Records completed 250/768 versus 80 and 65. Exported art and records states are replica 00, selected before the measurements. Free play matched the previous implementation byte-for-byte over 160 learning games across four islands.

Added `netta2048.py`, a standard-library game host, and `corpora/2048.txt`: 64 Python policies in eight families. The organism receives sixteen cells and four legal-action flags; the generated program chooses its action. Board transitions, spawning, score and reward belong to the host. Corpus validation executed all 64 programs on 24 observations (1,536 executions).

After 800 raw training attempts, the final state played 156/256 fresh evaluation attempts, versus 13 without learned experience. Scores per raw attempt: 589.59375 learned, 41.171875 erased, 949.421875 random legal actions. A selected evaluation episode and its full move sequence appear in `gallery.html`. Independent accounting checked every one of 96,029 training/evaluation transitions.

The Doom bot is now `nettadoomer.py`; `nettadoom.py` preserves the previous entry point. `doom/` contains the pinned Doom Generic engine sources, host adapter, build recipe and upstream license. The game uses an external IWAD, supplied with `--iwad` or `NETTA_DOOM_IWAD`. Real engine startup and combat work here through the generic backend.

On Freedoom 2 MAP02, 24 generation attempts yielded 12 played attempts with 11 distinct generated programs and 24 actual episodes. Doom killcount total: 88 (the standard single-player counter includes monster infighting). Eight attempts repeated corpus behavior; four had syntax errors. Health loss and ammunition expenditure enter the actual episode reward. A generated-policy combat frame and its exact Python source are in `gallery.html`.

A further frozen paired Doom check used 16 shared generation/game seeds: 11 played attempts with learned experience versus 9 in the initial state. Mean reward difference per attempt was +0.0921; its bootstrap 95% interval was [-0.1267, 0.3128]. Replaying one archived policy with the same engine seed reproduced the trajectory and PNG hashes exactly. The saved environment binds backend, IWAD hash, map and difficulty.

Technical measurements remain in private experiment artifacts. Four task comparisons account for 12,288 training rows and 12,288 evaluation rows. Original incomplete logs were retained: 39 evaluation rows and one training row were recovered by deterministic replay; the training recovery matched its surviving prefix and final checkpoint exactly. Future measurement writers flush and fsync their output.

## 2026-09-21 — The islands acquire a public home

Published the standalone Python organism, JSON caller, art / strings / records / Doom code islands, held-out programs, and saved island memories. The corpus separator is `# === PROGRAM ===`; generated source and indentation reach CPython unchanged.

The organism combines learned byte units, local continuations, acquired continuation memory, execution and syntax heads, and separate exploration/practice search. The JSON caller selects saved experience and checks declared output contracts. At this point the contract filters execution results; it does not yet condition learning.

The published art, strings and records memories each completed 2,000 games. In 600 fresh frozen attempts per island, productive executions with learned experience versus its removal were 271/46, 180/45 and 136/24. New behaviors beyond final memory were 52/32, 39/40 and 13/13. The release test suite passed 123 tests. Full experiment receipts remain with the research artifacts.

The Doom bridge supports real episodes and repeated game starts. Engine startup in this environment returned socket EPERM and SIGSEGV; no real Doom episode completed here.

Initial implementation commit: `832383ba73341cc0869459e7993c63fb44763b7b`.
