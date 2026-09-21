# NETTA CODE LOG

Newest entries first. Technical changes and measured experiments live here; README describes the current organism.

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
