# Eighth engineering pass — when experience can change the next choice

Baseline: `e67b23a828b549c62a04f430f705c5f8e2bab817`. This pass gives the two standalone organisms different optional ways to consult acquired experience. Lee can admit an experienced continuation that her longest local context excluded. Code can distinguish execution outcomes attached to longer histories that share the same short continuation key. Both mechanisms are off in existing lives; generated source, indentation, execution court, islands and caller routes retain their contracts.

## The diagnosis came before the mechanism

Lee's two saved provenance runs reproduced all 128 original evaluation sources. Of 9,094 unit steps, 8,149 had a single continuation; the median program contained only seven actual choices. No credited alternative was lost through the existing top-24 cutoff. Ordinary execution experience did contain missing alternatives in shorter contexts of at least three units at 227 positions across 117 programs. The decision-credit lookup itself was correct: disabling it changed 12/128 sources, while replacing provenance credit with the coverage control changed only 2/128. Most of the program already had no choice for that credit to affect.

Code's historical evaluation reproduced 512 sources and isolated 20 `NameError` outcomes. Nine penalized local associations also appeared in successful programs, all inside the same first-unit anchor. Eight-unit histories separated two of these conflicts, including the dominant `for column` / `for row` case: the eventual `canvas[row]` access shared its short context, but the relevant earlier unit was seven positions back. These observations selected one fixed mechanism for each body, before their new development outcomes were examined. [Lee diagnosis](lee-diagnosis.json), [Code diagnosis](code-diagnosis.json).

## Installed optional capabilities

**Lee — experienced suffix support.** `--experience-support 0.10` preserves the original candidate list, then examines the nearest strictly shorter available suffix of at least three units with missing alternatives that have actually received ordinary execution credit. Corridor vetoes still apply. Up to 24 additional alternatives share ten percent of the continuation-count prior, proportionally to that shorter suffix's counts; the original counts are unchanged. Reward values do not determine membership. Existing learned heads and credit then score the whole choice. The finite mass is restricted to [0, 0.25] and persists in the saved life. Zero or absent eligible evidence follows the previous source and RNG behavior exactly. Available on Lee `init`, `play`, task-learning `ask`, and `2048.py play`.

**Code — acquired eight-unit outcome residual.** `--context-memory` creates a separate sparse association between the preceding eight units and a sampled continuation. It starts empty. The unchanged general runtime/novelty reward updates eligible choices once per long key per program, including distinct long keys that share one short association. There is no new corpus prior. The next-unit logit receives:

```
2.5 * n8/(n8+4) * ((w8+1)/(n8+2) - (w3+1)/(n3+2))
```

Here `w` and `n` are acquired reward sums and trial counts. Long counts use the existing 0.95 decay at 64 trials. The three-unit ordinary credit and first-unit anchor retain their roles. Source histories in learning choices are validated before mutation. `--no-context-memory` stops readout and acquisition while preserving counts. The option is available on Code `init`, `play`, and `ask --learn-task --save`. Configuration survives save/resume; erasing experience keeps configuration and clears acquired counts in both bodies.

The emitted standalone bodies match the fixed experimental candidates outside their CLI functions. CLI additions expose configuration and inspect output; the 2048 bridge also records explicit overrides in its run protocol. Both organisms remain single Python files using the standard library. [Release assembly](release-assembly.json), [compatibility](compatibility.json).

## Fixed Code comparison

Two replicas per task, with 128 learning attempts for baseline and context memory, then 128 fresh task-conditioned evaluations per arm. A third evaluation disables only the residual on the candidate-trained state. Another 128 no-task generations evaluate each final state independently. Every arm retains first-unit anchor strength 1. Total: **4,096 attempts**, including **1,024 training updates**, in 32 closed streams.

| Measurement | First-anchor baseline | Context memory | Same context state, readout off |
|---|---:|---:|---:|
| Table-request corpus-novel execution / 256 | 83 | 97 | 83 |
| Table-request distinct productive behaviors | 67 | 84 | 68 |
| Complete table contracts / 256 | 0 | 0 | 0 |
| Table-request source replay / 256 | 45 | 44 | 44 |
| Numbers task passes / 256 | 146 | 142 | 145 |
| Numbers source replay / 256 | 10 | 18 | 15 |
| No-task corpus-novel execution / 512 | 200 | 181 | 197 |
| No-task distinct productive behaviors | 124 | 99 | 121 |

“Productive” is the existing runtime-success plus corpus-novelty field. It can include repetition of a behavior discovered in previous experience; accepted outcomes, experience replay and distinct behavior counts are reported separately in the [comparison](code-comparison.json). The table request's increase is **+8 and +6** across the two replicas, but none of these programs fulfills the table contract. Numeric task performance, numeric source replay and no-task productivity fail the registered advancement conditions. No confirmation or public-state promotion follows. [Protocol](code-protocol.json), [decision](code-decision.json).

Independent reconstruction regenerates every training source, applies its preserved execution receipt and reaches all eight final trained snapshots exactly. It independently reconciles 4,077 long-context association updates across 960 stored entries in the four candidate states. A separate 1,536-generation assay holds these states frozen: disabling the residual changes 134/512 task-conditioned sources, and rotating counts among long keys changes 152/512. All 512 genuine sources match the original evaluation journals and all intervention memories remain unchanged. These interventions demonstrate that acquired associations affect generation; the fixed task and free-play comparisons determine whether that effect helps. [Mechanism audit](code-mechanism.json).

## Fixed Lee / 2048 comparison

Two replicas, each with 128 training and 64 fresh evaluation attempts in three arms. Baseline keeps support mass zero; support uses 0.10; the third arm keeps support 0.10 but sets decision-credit strength to zero while still collecting its feedback. All arms observe the same provenance contract and retain ordinary learning. Every generated program has the same 128-move and worker CPU limits.

| Learning arm | Completed / raw evaluations | Completed score / raw attempt |
|---|---:|---:|
| Existing local support | 93 / 128 | 713.5625 |
| Experienced suffix support | 78 / 128 | 607.6250 |
| Support, decision readout zero | 76 / 128 | 580.5000 |
| Random legal control | 128 / 128 | 933.0000 |
| Fixed greedy control | 128 / 128 | 1293.71875 |

Support changes completed score by **−109.0625 and −102.8125** in the two replicas, pooled **−105.9375** points per raw attempt. It fails all three advancement conditions: positive gain in each replica, at least 25 pooled points, and no loss of completed episodes. Confirmation is not run. The complete budget contains **1,152 generated attempts**, including **768 training updates**, plus **256 separately identified control episodes**. Rejections and failed or incomplete execution remain in the denominator. [Protocol](lee-protocol.json), [comparison](lee-comparison.json), [decision](lee-decision.json).

Opening a formerly deterministic continuation consumes a new random draw even if the original token still wins. Whole-program changes therefore do not count how often an admitted alternative was sampled. The frozen mechanism assay records candidate admission, actual extra-token selections, matched-prefix probabilities and source changes separately. Across all seven evaluation programs that actually selected an admitted token, outcomes were four syntax errors, one runtime error, one probe-behavior replay and one completed game scoring 768. [Mechanism](lee-mechanism.json).

## Exact visible outcomes

The [gallery](../../gallery.html#iteration8) follows selection rules registered before the experiments. Code shows the first table-evaluation seed in replica zero where the candidate is productive and baseline is not: seed `152000001`. The candidate prints eight vertical rows and a bottom frame; baseline has a syntax error. The executed drawing is accepted for general novelty and **fails the requested table contract**. Its exact source and stdout are retained in [the receipt](code-gallery.json).

Lee shows the first replica-zero evaluation where support completes a game and baseline does not: seed `133000014`, game seed `134000014`. The generated policy scores **700** while the paired baseline is rejected for probe-behavior replay. Selection does not rank scores. The full actual trajectory and unchanged source appear beside the support mechanism in [the receipt](lee-gallery.json). This individual example is shown together with the weaker aggregate result.

## Verification and preservation

The final emitted sources pass **345 tests in 183.739 seconds**, including 27 new mechanism and CLI checks. Independent numerical tests check 10,240 categorical draws and actual CPython context updates, including saturation. Regression coverage includes default-off parity, empty-memory parity, source-history validation, distinct-long-key deduplication, finite mass validation, saved configuration, count retention and exact continuation after save/resume.

Compatibility checks against the frozen public baseline reproduce **252 exact generation records** and **20 actual CPython learning updates**, and execute all **six caller routes**, including native Doom. All 42 checked state, corpus, configuration, host and shared-core inputs retain their bytes. Public snapshots and default settings are preserved. [Tests](tests.json), [test output](tests.log), [preservation](preservation.json), [independent audit](audit-summary.json).

Independent Lee accounting reconciles all 1,408 game receipts, 109,369 board transitions, 1,152 exact source-and-choice regenerations and 768 complete state-update replays. It also checks 79,421 source/input/action provenance receipts, 79,340 temporal targets with a rational-arithmetic oracle, and 1,359 decision-association updates.

Gallery checks preserve every preceding section byte-for-byte and verify the exact Code stdout, both source hashes, all 93 recorded Lee moves, navigation endpoints and UTF-8 source highlighting. The checks execute JavaScript in Node with a minimal DOM; CSS layout is not browser-rendered. [Gallery verification](gallery-qa.json).

The first tiny plumbing runs stopped on tuple-versus-JSON-list receipt comparisons: six Lee and two Code records. The fix normalized receipt metadata without changing either candidate. These interrupted records are preserved and independently match their repeated tiny runs. The successful plumbing runs are separate from development: 38 Code attempts and 12 generated Lee attempts plus four game controls. They do not supply replacement development observations.

## Next pressure point

The data favor studying **when to consult additional memory**. Lee needs to preserve useful local structure while opening choices where experience supports exploration. Code's longer acquired memory helps the table-conditioned generation measure while hurting a previously strong numeric task and free play. Its same-state readout intervention recovers much of that loss, making selective retrieval a concrete next hypothesis. Candidate admission, learned residual readout and changes in the training trajectory must remain separately measurable.

The mechanisms are available explicitly for new lives and further islands; fixed defaults are retained. Compact public evidence lives here. Complete attempts, frozen candidates, checkpoints, historical diagnosis inputs and reproduction tools remain in the [separate compressed archive](private-archive-inventory.json).
