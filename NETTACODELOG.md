# NETTA CODE LOG

Newest entries first. Technical changes and measured experiments live here; README describes the current organism.

## 2026-09-21 — A mixed island for executable combinations

Published `nettacode.py` as an independent standard-library Python file with its mixed code-only TXT island and saved experience. The complete execution judge and JSON caller are included in the file. No import from Netta Lee is required.

Code uses a shorter default continuation context than Lee and more frequent corridor escape. It generates its own whitespace and receives exact CPython execution feedback. Exploration, practice, acquired local continuations, and two learned heads are present in both organisms.

The published mixed memory completed 2,000 games. In 600 fresh frozen attempts it produced 205 productive executions versus 19 after erasing learned experience; distinct behaviors were 62/19 and behaviors new beyond final memory were 26/12. Independent CPython re-execution agreed with counted productive outputs. The shared release suite passed 123 tests.

Initial implementation commit: `832383ba73341cc0869459e7993c63fb44763b7b`.
