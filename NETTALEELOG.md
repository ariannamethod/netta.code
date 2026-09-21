# NETTA LEE LOG

Newest entries first. Technical changes and measured experiments live here; README describes the current organism.

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
