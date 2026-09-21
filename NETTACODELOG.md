# NETTA CODE LOG

Newest entries first. Technical changes and measured experiments live here; README describes the current organism.

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
