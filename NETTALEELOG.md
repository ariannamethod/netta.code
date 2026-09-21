# NETTA LEE LOG

Newest entries first. Technical changes and measured experiments live here; README describes the current organism.

## 2026-09-21 — The final action acquires exact source eligibility

Added `2048.py play --decision-credit provenance` and the saved contract
`2048-action-provenance-v1`. It retains the eight-move temporal target and
changes its eligibility: the CPython observer follows the final stored action
through actual value assignments, guarding predicates and loop occurrences.
Exact UTF-8 spans connect this derivation to recorded stochastic source choices.
The core validates source, token/key alignment and nested trace containment
before mutation; repeated associations still receive one mean trial per episode.

The source is executed unchanged. Unsupported provenance keeps real gameplay
and ordinary episode learning, with no invented local-credit fallback. The
explicit scope is last stored action, aggregate container origins and later
negative guards excluded. CPython 3.12 is the supported observation runtime;
ordinary behavior remains the default.

Actual iterator exhaustion exposed a missing comprehension dependency in the
first implementation. The observer now resolves the branch from the next
observed opcode, retaining the populated list's real body values. Semantic atom
projection also handles broad synthetic dictionary-key positions, skipped
alternatives, Unicode boundaries and folded comments. Static projection is
cached by instruction offset. Full detailed receipts match in 128/128 cached
versus uncached checks; CPU falls from 12.049 to 7.227 seconds on that fixed set.
A real 128-move policy now completes under the unchanged ten-second worker cap.

The fixed comparison uses three arms and two replicas, each with 128 learning
and 64 fresh evaluation attempts. Completed score per raw attempt is 658.75
for temporal line credit, 644.21875 for matched span coverage and 639.3125 for
action provenance. Provenance plays and completes 80/128 evaluations; matched
coverage completes 81/128. Replica gains against coverage are −9.8125 and 0,
so the registered advancement gate fails. The public states and defaults remain.
All 1,152 generated attempts and 256 distinct control episodes are retained.

The final CLI continuation check exposed an incomplete streamed journal despite
four completed attempts and a four-step advanced snapshot. The underlying loss
cause is unproven. CLI archives now retain each attempt separately, atomically
close the aggregate journal and verify its count and hashes before final state
and summary publication. Ten focused bridge tests pass, including three new
persistence regressions. The measured comparison retains its original frozen
bridge; this subsequent change only affects CLI evidence persistence.

Two interrupted instrument-validation runs retain 67 and 817 complete receipts
outside the corrected comparison. Their defects, exact hashes and restart
rules are recorded in the [seventh-pass report](reports/iteration7/REPORT.md).
The gallery adds a fixed-rule measured example with selectable execution,
action-dependency and sampled-choice highlighting. The full suite passes 315
tests; compatibility covers 532 exact generation records, 25 actual learning
steps and all six real caller routes.

## 2026-09-21 — Temporal consequences and visible Doom play

Added the explicit `2048-temporal-return-v1` decision contract through
`2048.py play --decision-credit temporal`. Each target uses the discounted mean
of the current move's gain and up to seven subsequent actual gains (discount
0.9), centered around the existing episode reward and bounded to [0,1]. Common
source choices retain the episode mean, while conditional choices can receive
distinct credit. Constant-gain and endpoint-rounding cases have focused tests.
Generation, exact indentation, game actions and the shared core are unchanged.

Two replicas per arm used 128 learning and 64 fresh evaluation attempts.
Existing learning played 76/128 attempts and scored 568.15625 per raw attempt;
uniform and temporal credit both played 80/128 and scored 606.6875. All 128
generated sources and play outcomes matched between uniform and temporal
(80 played episodes per arm). Training
had one differing source in an unplayed rejection and identical actual episodes.
The temporal table nevertheless received distinct key-level feedback in 21 of
153 credited episodes, affecting 22/1047 episode-key pairs, with maximum
deviation 0.0229352. It failed the declared requirement to beat uniform, so the
published state/defaults remain unchanged and no confirmation sweep followed.

The source-level diagnosis traces the narrow signal to sampling choices:
conditional runtime lines often contain only deterministic continuations.
An exact replay of the preceding 768 training attempts found changed temporal
credit in 44/3519 episode-key pairs. In one concrete policy the sampled choice
was a merge-score multiplier; final action assignment itself was deterministic.
The current line union also includes computations for discarded directions.

README now includes exact generated Code, 2048 and Doom policies and three
original Doom Generic PNGs: a shot, incoming projectile and ammunition pickup.
The files live in `doom/assets/` with source/episode/frame provenance.
`requirements.txt` remains package-free; `requirements-doom.txt` retains its
ViZDoom pin only for the optional backend. Generic uses make, a C compiler and
an external IWAD.

The full suite passes 274 tests. Independent accounting verifies all 3968
fixed-experiment attempts without recovery, 106504 board transitions, six
real routes and exact temporal save/resume. All six public states remain
unchanged. The [sixth-pass report](reports/iteration6/REPORT.md) and gallery
record the comparisons; the full archive stays separate from public reports.

## 2026-09-21 — Decision-specific credit and combat engagement

Added a separate optional per-decision credit table to both standalone bodies.
The host binds its receipt to the exact generated source and named target
contract. Each actually encountered decision carries executed lines and a
bounded target. Each continuation association receives the mean target over
decisions in which it participated, followed by one trial per episode. Repeated
loop events and longer episodes cannot multiply credit. The existing episode
credit, runtime/syntax heads, search and acquisition are preserved. Empty new
memory has zero influence on generation and RNG use.

`2048.py play --decision-credit advantage` computes a target from the selected
move's immediate merge gain relative to the minimum and maximum among that
board's legal moves; ties receive 0.5. The generated code still chooses every
action. `uniform` supplies the same kind of actual trace with terminal reward
assigned to each decision; `off` disables the extra influence while retaining
acquired associations. Omitted flags preserve saved settings. Different learned
contracts have separate states. Complete receipt validation precedes state
mutation, and failed partial episodes retain ordinary failure learning without
a decision-credit update. Thirteen focused core contracts pass on both bodies.

The fixed 2048 development comparison used two replicas, each with 128 training
and 64 fresh evaluation attempts per arm. Legacy, uniform and advantage each
played 84/128 evaluated attempts. Completed score per raw attempt was 659.78125,
687.6875 and 683.875 respectively; mean played score was 1005.38095, 1047.90476
and 1042.09524. Advantage improved by 17.375 and 30.8125 per raw attempt in the
two replicas, for a pooled gain of 24.09375 over legacy, with paired bootstrap
95% interval [-22.25, 72.71875]. It scored 3.8125 below the uniform control.
The predefined gate required at least 25 pooled points of gain and a result
above uniform; it was not met. No confirmation sweep or state promotion followed.
The published state and defaults remain unchanged. Random legal and fixed greedy
controls scored 987.125 and 1277.875 per raw attempt across all 128 starts.

Doom's explicit `--reward-mode combat` returns zero when the player deals no
direct monster damage. With positive direct damage, it returns exactly the
existing attributed formula, including the same damage and ammunition terms.
A preliminary reward-rescaling run stopped after 37 training attempts and before
evaluation when its changed acquisition threshold was identified; its evidence
is retained separately. The final engagement gate preserves active-combat reward
and the existing reward-above-0.5 acquisition rule.
Both contracts trained from the same saved experience for 128 attempts, followed
by 64 fresh shared engine starts evaluated with one common combat metric.
Attributed versus combat-trained states played 33/64 versus 38/64 attempts,
caused 3,124 versus 3,436 direct damage and 89 versus 98 direct kills. Received
damage was 2,033 versus 2,367. Shared combat reward per raw attempt was 0.258924
versus 0.282559; paired difference +0.023635, bootstrap 95% interval
[-0.013769, 0.063611]. Published states and default reward contracts are retained.

Controls each played 16 fixed starts. Turning-only and forward-only policies
received zero combat reward; forward-only play still accumulated 39 native
Doom kills with zero direct player damage. The aiming/shooting control dealt
1,687 direct damage, made 52 direct kills and received mean reward 0.506722,
identical under the two formulas on those same episodes.

A separate temporal comparison changed the sensor and its code island together,
using 64 training attempts and 32 fresh evaluation attempts per arm. Temporal
played 14/32 attempts with reward/raw 0.219324; the legacy sensor/island played
17/32 with 0.261235. Direct kills were 47 versus 42, direct damage 1,315 versus
1,564. Temporal perception remains an explicit capability; these experimental
states remain separate from the published life.

Doom now publishes each completed trajectory under a content-hash filename,
then binds its name, SHA256 and row count in the episode receipt. The canonical
trajectory is written only after completion. Independent accounting recovered
28 earlier truncated journals (3,269 missing rows) into separately identified
immutable files, verifying every retained prefix and final native counter; all
originals remain preserved. The final writer also passed a real native
split-versus-uninterrupted save/resume comparison.

The final shared suite passes 253 tests. README and gallery retain
the current anatomy and measured examples. The compact
[fifth-pass report](reports/iteration5/REPORT.md) links protocols, comparisons
and audits; full raw attempts, checkpoints and trajectories stay in the separate
compressed experiment archive.

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
