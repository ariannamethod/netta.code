# NETTA LEE LOG

Newest entries first. Technical changes and measured experiments live here; README describes the current organism.

## 2026-09-21 — The islands acquire a public home

Published the standalone Python organism, JSON caller, art / strings / records / Doom code islands, held-out programs, and saved island memories. The corpus separator is `# === PROGRAM ===`; generated source and indentation reach CPython unchanged.

The organism combines learned byte units, local continuations, acquired continuation memory, execution and syntax heads, and separate exploration/practice search. The JSON caller selects saved experience and checks declared output contracts. At this point the contract filters execution results; it does not yet condition learning.

The published art, strings and records memories each completed 2,000 games. In 600 fresh frozen attempts per island, productive executions with learned experience versus its removal were 271/46, 180/45 and 136/24. New behaviors beyond final memory were 52/32, 39/40 and 13/13. The release test suite passed 123 tests. Full experiment receipts remain with the research artifacts.

The Doom bridge supports real episodes and repeated game starts. Engine startup in this environment returned socket EPERM and SIGSEGV; no real Doom episode completed here.

Initial implementation commit: `832383ba73341cc0869459e7993c63fb44763b7b`.
