# Fifth pass: later Code context

**Decision: retain the released first-unit memory.** The single fixed later-context candidate failed its prospective development gate, so confirmation and production integration were not run. The published Code helper and input snapshot remain unchanged.

The candidate keeps the most recently introduced ordinary unit preceding the local order window as its distant anchor. Sparse continuation counts are learned from the same source corpus and acquired programs, using suffix depths 2/1/0, strength 1 and smoothing 2. At each suffix depth the existing first-unit memory supplies the fallback. It uses no AST information, identifier rules, source repair, token masks, templates or additional programs. Its corpus has 4,720 recent contexts; the released first-anchor memory has 2,381.

## Prospective protocol

Two development replicas per task received 128 training attempts per arm and 128 fresh evaluation attempts per arm. Arms: released first-anchor law, recent-anchor law, and the same recent-trained checkpoint with only its mode switched back to first. All begin with the same published state, contracts, corpus and units. Training seeds begin at 2,100,000,000; evaluation seeds at 2,200,000,000; task stride 100,000 and replica stride 1,000,000. Export replica 0 was designated for each task before measurement.

The gate required at least two additional table passes, no numeric-pass loss, and no productive-execution loss on either task. A three-replica confirmation with 256 training/evaluation attempts was declared in advance and remained conditional on this gate. No sweep or replacement candidate followed the failed gate.

## Measured development result

All 256 evaluation attempts per task remain in each denominator.

| Outcome | First | Recent | Recent-trained, first mode restored |
|---|---:|---:|---:|
| Table task passes | 0 | 0 | 0 |
| Table productive executions | 91 | 57 | 89 |
| Table runtime successes | 148 | 159 | 146 |
| Numeric task passes | 140 | 129 | 126 |
| Numeric productive executions | 151 | 139 | 147 |
| Numeric runtime successes | 167 | 169 | 166 |

The detailed result explains the rejection. Table syntax failures fell 89 → 81 and `NameError` fell 18 → 11, while `source_replay` rose 56 → 100. Numeric `NameError` fell 7 → 3, while `source_replay` doubled 14 → 28. Numeric syntax failures changed 76 → 80; truncations changed 2 → 0. More executions completed, but more were copies rejected by the unchanged novelty judge. Productive generation declined on both tasks.

A source-only diagnostic counted a median 31 recent-anchor changes per corpus program, 30 in generated table attempts, and 20 in generated numeric attempts; the first anchor never changes. These counts cover every position where an anchor could be consulted, including deterministic continuations. In generated table attempts, 5,235 of 13,166 such positions selected punctuation/whitespace-only bytes, and 2,812 selected identifier-shaped bytes. Common selected units included `-`, `+`, `2`, `for ` and ` * `. Identifier-shaped byte units can also occur in string literals; the implementation assigns no semantic categories to them.

My interpretation is that this rule strengthens particular familiar continuations more readily than useful recombinations. The observed increase in rejected source replay is the concrete reason to retain the first-anchor law. A later memory design needs a criterion for keeping a relevant earlier context beyond simple introduction order.

## Evidence and preservation

All 2,560 measured attempts are stored in 20 completed atomic JSONL streams. Each stream was fsynced, renamed, reread and checked against its row count/hash; all streams passed a further check after the stage completed. Exact measured rows also have immutable per-attempt JSON shards and manifests. No rows required regeneration or recovery.

Nine isolated candidate tests passed, including 64-seed first-mode generation parity, byte-identical old active-snapshot roundtrip, save/resume learning, disabled parity, mode-only erasure, ordinary-unit acquisition and frozen CLI handling. Production still exposes the existing first-anchor interface; the candidate mode remains private.

An illustrative rejected generation is preserved in `gallery_replay_example.json`: seed 2,200,000,003 exactly reproduces corpus program 149, a 17-row ASCII pattern. It executes successfully and is rejected as `source_replay/whole_source`. Its source SHA-256 is `4d52b4d137c68605816f31998eef36b7cf03831332d6d6918743341fec0910eb`.

Hashes:

- Candidate standalone: `9257027d59fd51c251f90ad5f4f9c3145cbb58427b36469b5b054e40b83a138f`.
- Runner: `4de25748e5f23d5cb30a33faa0e5ae61552c1a06764ae0322b8bd09864b711a8`.
- Unchanged production helper: `00c308905f88706684f6204d9295d197f16bff3e2e2489b97a7bcd39b0f4d799`.
- Unchanged input snapshot: `8a3d638578f1e0748c6311a29c685990ae77dbf8327ceda09f167187462ffed6`.

Compact evidence: `development/protocol.json`, `development/summary.json`, `diagnosis.json`, `tests.log`. Complete raw attempts, states, candidate sources and measured shards stay in the private experiment archive.
