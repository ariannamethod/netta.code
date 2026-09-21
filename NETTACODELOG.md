# NETTA CODE LOG

Newest entries first. Technical changes and measured experiments live here; README describes the current organism.

## 2026-09-21 — Learned units compose an ordered recurrent state

Added optional `sequence_memory` to the standalone body: eight hidden channels,
two 8×32 input projections, learned write/proposal biases and an outcome readout,
537 parameters in total. `--sequence-memory` / `--no-sequence-memory` work on
init/play and task-learning ask with save; omission preserves the selected life.
The hidden state resets per generated program, while acquired parameters and
update count survive save/resume. OFF retains weights and stops their use and
acquisition. Existing saved lives remain off.

The bounded input-gated cell follows §3.1.1 of the minGRU paper. Every actual
learned byte unit, BOS and actual EOS enter the recurrence, including deterministic
continuations. Candidate states are hypothetical until a unit is selected. An
independent RNG and zero initial readout preserve birth sampling. Actual ordinary
execution/novelty reward trains up to twelve equally spaced eligible choice
positions using averaged BCE, one full BPTT pass and one globally clipped SGD
update per program. No source or indentation repair is performed.

The actually.life review contributed the sequence principle: composed units
change the state from which the next unit is chosen. Netta retains its own
byte-pair alphabet. Learned weights belong to Code's mixed life; Lee keeps
separate acquired parameters for each specialist life. Source/token/history/EOS
alignment is checked before enabled external observation mutates state.

The fixed Code comparison used 4,096 attempts, two replicas for each of table
and sorted-number tasks, 128 training attempts per arm, then 128 task and 128
separate no-task evaluations per arm. The existing first-unit anchor stays on;
eight-unit context memory stays off. Table productive executions changed
93→95/256 (+1 in each replica), complete table passes remained zero, numeric
passes changed 171→172/256 and numeric corpus source replay 6→8. No-task productive
execution changed 192→191/512. The gate failed three conditions; confirmation
and public-state promotion were not performed.

Same-trained-checkpoint OFF produced 94 table productive executions and 172
numeric passes. Removing the readout changes four of 512 task-conditioned
sources and one of 512 free-play sources. Independent reconstruction reproduces
all 1,024 training generations/choices and whole final states, including 512
recurrent updates at 3,378 independently bound loss positions.

The five-way frozen assay covers 2,560 generations over 512 fixed seeds.
OFF changes 4 sources; restoring initial transitions, zeroing the current
hidden prefix and permuting protected early history each change zero sources.
The order intervention still changes actual candidate probabilities, with
maximum total variation 2.7586e−6. Every head makes 128 updates and all 537
parameters change. The useful next target is candidate-specific access to the
remembered prefix: the current common linear history term cancels between
choices, leaving small gate differences to carry most contextual contrast.
No additional quality sweep followed these measurements.

The shared release passes 363 tests. All 537 derivatives agree with independent
finite differences (maximum absolute error 1.763744713972025e−10). Compatibility
reproduces 252 generation records, 20 learning attempts and all six caller routes.
The gallery preserves the prospectively selected seed 222000039, its exact
computed values and its `experience_replay`/failed-task status. The
[ninth-pass report](reports/iteration9/REPORT.md) records the research, protocols,
independent checks and compact results; raw evidence remains separately archived.

## 2026-09-21 — Acquired outcomes retain eight units of history

Added optional general-Code `context_credit` and the saved `context_memory`
setting. `--context-memory` activates a sparse acquired outcome association
over the preceding eight units and next sampled unit; `--no-context-memory`
stops its readout and acquisition while retaining counts. The options work on
init/play and task-learning ask with a separate save path. Old lives remain off;
omitted options retain the saved configuration.

The additional logit is
`2.5*n8/(n8+4)*((w8+1)/(n8+2)-(w3+1)/(n3+2))`.
It begins empty and uses actual general runtime/novelty outcomes, with the same
eligible error/success choices and decay convention as ordinary credit. Each
long association is updated once per program; different long histories sharing
one local key stay distinct. Choice histories are source-validated before any
mutation. First-unit anchor memory, ordinary three-unit credit, candidate
support and exact-source execution retain their roles.

The mechanism followed a 512-source historical diagnosis: nine local
associations were shared by NameError failures and successful programs, all
inside the same first-unit anchor. Eight-unit context separated two conflicts,
including the dominant loop-variable confusion whose useful unit was seven
positions back. No context-length sweep followed this choice.

The fixed comparison contains 4,096 attempts across 32 closed streams. With
two replicas of 128 training and 128 task-evaluation attempts, table-conditioned
corpus-novel execution increased 83→97/256, gains +8 and +6; distinct productive
behaviors increased 67→84. Actual table-contract passes remained zero. Numeric
task completions changed 146→142/256 and source replay 10→18. Separate no-task
evaluation of the same checkpoints changed 200→181/512 productive executions,
with distinct productive behaviors 124→99. Three advancement conditions failed;
confirmation and public-state promotion were not performed.

Independent reconstruction reaches all eight trained final snapshots exactly
after 1,024 updates. It reconciles 4,077 long-context updates and 960 stored
entries across the four candidate lives. Frozen generation isolates readout:
turning it off changes 134/512 original task-conditioned sources; permuting
count pairs changes 152/512. All genuine sources match recorded evaluation and
intervention states remain unchanged. Same-state readout-off restores 197/512
no-task productive executions, identifying selective retrieval as a concrete
next hypothesis.

The gallery keeps the prospectively chosen seed 152000001: an accepted generated
drawing beside the baseline's SyntaxError, explicitly recording that the table
request failed. The final shared suite passes 345 tests, including exact
save/resume and source-validation checks. The [eighth-pass report](reports/iteration8/REPORT.md)
holds compact evidence; complete sources, receipts and checkpoints remain in
the separate archive. Public states, corpora and caller contracts keep their bytes.

## 2026-09-21 — Execution provenance reaches the shared byte-credit interface

The standalone Code body now includes the optional CPython 3.12 action
observer and the shared `source_spans` decision-attribution interface. Hosts
can bind credit to exact UTF-8 intervals in a generated source, with receipt
containment and token/choice alignment checked before learning. A choice
qualifies by direct overlap; deterministic gaps receive no invented parent.

Code's first-unit distant memory and task learner keep their current behavior.
The new action contract is integrated with the 2048 Lee life. A future Code
output contract can use this interface for actual printed or retained values,
after measuring support for those programs; it is not silently enabled here.

Across both bodies, independent comparison covers 532 exact generation
records, 25 actual CPython learning steps and all six real caller routes.
The final suite passes 315 tests. Public states and corpora retain their bytes.
The [seventh-pass report](reports/iteration7/REPORT.md) documents the exact
observer scope, runtime cost, fixed comparison and separate full archive.

## 2026-09-21 — Branching distant context and exact execution examples

Tested a single private extension of first-anchor memory. Later context could
modify the first-anchor continuation prior only when it supported at least two
available successors. Its arithmetic-mixture weight was the bounded ratio of
later-context to first-context Gini impurity; unary later support fell back
exactly to the first-anchor law. The model kept the same candidates, smoothing,
strength, corpus and execution judge. No syntax or indentation was rewritten.

The fixed comparison used two replicas per task, each with 128 training and
128 fresh evaluation attempts. Table productive execution changed 82→68 out of
256 and source replays increased 39→58. Complete table tasks changed 0→1.
Numeric task completions changed 141→143 out of 256, with source replays 10→12.
Restoring first-only generation on the candidate-trained checkpoints produced
73 table productive executions and 145 numeric task completions. The candidate
failed the declared advancement gate; no confirmation or public model/state
replacement followed. All 2,560 measured attempts remain in immutable receipts.

README now includes an exact accepted numeric program from the prior frozen
evaluation, its `[12, 15]` output and an independent CPython replay. The shared
gallery and [compact report](reports/iteration6/REPORT.md) record the new memory
comparison; the complete candidate and experiments are kept separately. The
shared regression suite passes 274 tests; independent replay verifies every
measured source and all 1024 Code training updates.

## 2026-09-21 — Recent-context experiment retains the first-unit memory

Tested one fixed alternative to the published first-unit anchor. The candidate
uses the most recently introduced ordinary unit preceding the local context,
with suffix depths 2/1/0, strength 1 and smoothing 2. The existing first-unit
memory supplies a fallback at each suffix depth. Both candidates use the same
corpus, units, execution court and declared output contracts.

Two replicas per task used 128 training and 128 fresh evaluation attempts per
arm. The third evaluation restored first-anchor mode on the same recent-trained
checkpoint. Table task completions remained 0/256 in both learning arms. Table
runtime successes rose 148 to 159 and NameError fell 18 to 11, while source replay
rose 56 to 100 and productive execution fell 91 to 57. Numeric task completions
fell 140 to 129/256; productive execution fell 151 to 139 and source replay doubled
14 to 28. Numeric NameError fell 7 to 3.

The advancement rule required two additional table completions, no numeric-task
loss and no productive-execution loss on either task. It was not met, so the
conditional confirmation and production integration were not run. The public
first-unit memory, its CLI and `states/code.json` remain unchanged. Increased
rejected source replay is the measured reason for retaining the existing rule.

All 2,560 measured attempts reside in 20 complete atomic JSONL streams, checked
by row count and file hash; per-attempt shards preserve the exact measured rows.
No regeneration was needed. Nine isolated candidate tests passed. A retained
source-replay example is generated seed 2,200,000,003: it
exactly reproduces corpus program 149, executes successfully and is rejected by
the unchanged whole-source replay check.

Both standalone bodies also acquire the optional generic per-decision credit
API used by the 2048 bridge. Source-bound host receipts assign targets to actual
executed choices; each association receives one mean update per episode.
Ordinary Code learning and old snapshots retain their previous behavior when
the option is disabled. The final shared suite passes 253 tests.
The [fifth-pass report](reports/iteration5/REPORT.md) links compact comparisons,
protocols and audits. Full raw attempts, candidate sources and checkpoints stay
in the separate compressed archive.

## 2026-09-21 — Code acquires an optional distant continuation memory

Code/general now has an explicitly enabled memory mechanism distinct from Lee's
local island memory. It associates the first ordinary learned unit of a program
with the latest zero to two units and the next continuation. Corpus associations
are derived lazily from the same island; successful generated programs add
acquired counts. A finite likelihood ratio weights existing candidates. Source
units, indentation, candidates, execution rules and command contracts are
unchanged. The mixed island supplies 2,381 sparse anchor contexts.

`--anchor-memory` enables the mechanism on `init`, `play`, or
`ask --learn-task --save SNAPSHOT`. Strength and acquired counts persist in the
saved state. API `configure_anchor_memory(strength=0)` disables its influence
while retaining acquired associations for reactivation. Old snapshots without
anchor fields keep strength zero and exact generation/save behavior. Erasing
experience preserves the active mechanism's setting and clears acquired counts.
`nettacode.py` remains standalone; Lee does not receive the Code-specific memory.

The frozen comparison used three replicas, each with 256 training and 256 fresh
evaluation attempts per task and arm. Sorted-number task completions were
377/768 for existing memory, 422/768 with the anchor, and 393/768 after disabling
only the anchor on the same candidate-trained checkpoints. Each replica improved:
141 to 147, 114 to 120, and 122 to 155. The paired gain was 5.86 percentage points,
bootstrap 95% interval 3.26 to 8.59. Summed within-replica distinct successful
numeric programs increased from 17 to 28.

Table productive executions rose 233 to 271; complete table-task outputs were
0/768 versus 1/768. Executing all 272 corpus programs found eight table examples
from one percentage-record family and 52 sorted-number examples. Table syntax
failures fell 366 to 322, while NameError rose 40 to 48; numeric NameError fell
35 to 15. The first-unit anchor helps broad continuation coherence. Remembering
a later learned context is the next hypothesis for record programs sharing the
same beginning but using different variable families.

The mechanism is available as an opt-in. `states/code.json` stays unchanged; no
export replica was prospectively designated. An independent checker reconciled
8,960 training/evaluation attempts and 97 direct CPython source executions.
Twenty-two absent raw-log tail rows were recovered separately by complete frozen
replays matching all 362 surviving rows and both original summaries. Original
logs remain unchanged in the private experiment archive.

Shared changes add optional game-quality and executed-line learning, exact
cross-species caller dispatch and save/resume checks. They preserve ordinary
generation when disabled. The final suite passes 212 tests; six actual caller
routes reproduced 48/48 sources and left all states unchanged. See the compact
[fourth-pass report](reports/iteration4/REPORT.md), its Code comparison and
independent audit; README and gallery keep the current public anatomy and
selected results. Full raw experiments remain outside the repository.

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

## 2026-09-21 — A declared task guides a mixed island

Added independent task heads and continuation credit to Code, using the same execution-based contract mechanism as Lee. `ask --learn-task --save SNAPSHOT` acquires this experience; `ask` uses it without changing the state. The editable JSON now includes a `code` route to the mixed island, alongside the Lee specializations and game routes.

For `code:sorted_values`, three independent runs each used 512 training attempts and 256 fresh evaluation attempts. The task-trained organism completed 407/768 numeric-list tasks. Erasing only task memory from those exact checkpoints gave 8/768; ordinary training gave 5/768; the initial state gave 4/768. Replica 00 was designated for export before measurements and is published as `states/code.json`.

The separate `code:table` experiment remains recorded: 3/768 task completions versus 0 after task-memory erasure, with 312 versus 401 meaningful executions. Its checkpoint was not promoted. Output contracts and evaluation budgets were preserved throughout both experiments.

Two changes to generic exploration/memory were tested without changing the shipped defaults. Removing shorter acquired contexts reduced productive generation. A stagnation-triggered exploration schedule produced 117 productive executions against 119 for the existing schedule across 384 evaluation attempts; summed distinct behaviors were 50/56 and behaviors new beyond final memory 17/23. The existing schedule stays in place.

Both organisms preserve ordinary no-task trajectories and snapshots; the independent reader checked 160 learning games across art, strings, records and Code. Task memories also pass save/resume, interleaving, frozen evaluation and atomic-capacity tests.

Four task comparisons were independently reconciled, including explicit recovery of 39 missing evaluation rows and one training row while preserving every original log. Forty-eight frozen checkpoints and 225 deterministic replay checks agreed. `gallery.html` keeps the result table and visible outputs separately from this technical log.

## 2026-09-21 — A mixed island for executable combinations

Published `nettacode.py` as an independent standard-library Python file with its mixed code-only TXT island and saved experience. The complete execution judge and JSON caller are included in the file. No import from Netta Lee is required.

Code uses a shorter default continuation context than Lee and more frequent corridor escape. It generates its own whitespace and receives exact CPython execution feedback. Exploration, practice, acquired local continuations, and two learned heads are present in both organisms.

The published mixed memory completed 2,000 games. In 600 fresh frozen attempts it produced 205 productive executions versus 19 after erasing learned experience; distinct behaviors were 62/19 and behaviors new beyond final memory were 26/12. Independent CPython re-execution agreed with counted productive outputs. The shared release suite passed 123 tests.

Initial implementation commit: `832383ba73341cc0869459e7993c63fb44763b7b`.
