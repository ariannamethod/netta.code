# Fourth pass: Code continuation memory

The frozen mixed island has 272 programs. Executing every source and checking the unchanged output contracts found 8 table examples, all in one percentage-record family, and 52 sorted-number examples across several families. The earlier table-trained evaluation had 382 syntax failures and 67 runtime failures in 768 attempts; 61 runtime failures were `NameError`. Recorded sources visibly switch between incompatible variable families, including `sums`/`counts` and `groups`/`positions`.

The experimental Code memory retains the first ordinary learned unit as a distant anchor and associates it with the latest 0–2 units and the next unit. Its base counts come from the same corpus; successful generated continuations add acquired counts. A finite likelihood ratio adjusts existing candidate probabilities, with strength 1 and smoothing 2. It supplies no Python rules, source templates, repairs, token exclusions or additional corpus programs. The corpus produces 2,381 sparse anchor contexts; each context has at most three ordinary units.

## Frozen protocol

Development: 128 training attempts per arm, then 128 frozen evaluation attempts per arm and task. Confirmation: three replicas, each with 256 training and 256 fresh evaluation attempts. Both tasks start from the same published Code snapshot, SHA-256 `8a3d638578f1e0748c6311a29c685990ae77dbf8327ceda09f167187462ffed6`. Baseline and candidate receive identical seeds and budgets. A third evaluation disables the anchor on the exact candidate-trained checkpoint. Task thresholds, eligibility rules, source tokens and runtime are unchanged.

The prospective promotion rule was table-count improvement without numeric-performance loss. The fixed candidate was tested once; no parameter sweep followed development. Development gave numeric passes 63 → 78 /128 and table passes 0 → 0, while table productive attempts increased 29 → 38. Confirmation therefore measured the coherence improvement with more fresh seeds.

## Confirmation results

Each cell counts all 768 original evaluation attempts; failures and rejected copies stay in the denominator.

| Task / outcome | Baseline | Anchor | Same trained state, anchor disabled |
|---|---:|---:|---:|
| Table task passes | 0 | 1 | 0 |
| Table productive executions | 233 | 271 | 217 |
| Table runtime successes | 345 | 385 | 308 |
| Sorted-number task passes | 377 | 422 | 393 |
| Sorted-number productive executions | 427 | 472 | 445 |
| Sorted-number runtime successes | 447 | 499 | 461 |

Numeric passes improved in each replica: 141 → 147, 114 → 120, and 122 → 155. The paired increase is 45/768, or 5.86 percentage points; a 4,000-resample paired bootstrap gives 3.26–8.59 points. Summed within-replica distinct successful numeric sources increased 17 → 28. Table task success occurred once, in replica 1; completing this task reliably remains further work.

Table syntax failures decreased 366 → 322, while `NameError` increased 40 → 48. Numeric syntax failures decreased 273 → 236 and `NameError` decreased 35 → 15. The coarse initial anchor keeps broad continuation families together, but different record-processing programs share the same beginning. Remembering a later learned context is a specific further hypothesis for those variable bindings.

## Verification and integration

Five experimental memory checks passed: disabled-feature generation parity, acquired-memory save/load, per-program transition deduplication, frozen evaluation, and ordinary-unit-only memory. An independent output checker audited 8,960 raw attempts (3,584 training, 5,376 evaluation); 97 separate CPython executions matched the recorded exact-source stdout. A separate agent independently recounted all attempts, checked 116 frozen checkpoint replays and executed 25 selected sources with matching outputs.

Two completed-run logs had absent tails despite per-row flush/fsync: 8 development rows and 14 confirmation rows. Original bytes remain untouched. Full 128- and 256-seed frozen replays matched all 362 retained records exactly, regenerated the missing 22 separately, and reproduced both contemporaneous summaries. Recovery receipts carry source/state/file hashes.

The experiment passes its numerical promotion rule. The measured benefit is strongest for execution coherence and sorted-number output. The production integration is assembled into Code/general only, with explicit activation and persisted acquired counts. Old snapshots lacking the new field retain strength zero and their previous generation; Lee retains its present memory. The experiment does not replace any published checkpoint.

The build-time `code_memory_build.py` helper emits a standalone Code body. `configure_anchor_memory()` and `--anchor-memory` on `init`, `play`, or learning `ask` enable it. Learning `ask` requires an explicit `--save` destination; frozen `ask` cannot activate the feature. Existing enabled snapshots run normally without the flag. Production parity checks cover 64 fresh enabled generations, eight complete executed records, 64 disabled generations, original snapshot byte-identical roundtrip, active learning/save-load, explicit CLI destination handling, and preservation of enabled architecture when acquired experience is erased. Replica 0 is used for these integration checks; no prospective exported checkpoint was designated in the experiment protocol.

Private evidence: `historical_diagnosis.json`, `corpus_profile.json`, `development/protocol.json`, `confirmation/protocol.json`, `confirmation_aggregate.json`, `measurement_audit.json`, both `recovery/receipt.json` files. Implementation proposal: `anchor_candidate.patch` and `integration_notes.json`.
