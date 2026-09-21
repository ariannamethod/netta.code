# Ordered sequence memory

The two standalone bodies now include an optional **537-parameter recurrent outcome head**. It consumes the organism's learned byte units in their emitted order, learns from actual execution and keeps eight hidden values during generation. The learned weights belong to each saved life. The implementation, source-bound learning, all analytical gradients and standalone command paths passed their checks. Fixed quality comparisons and frozen interventions determine the release decision below.

## From recurrent networks and actually.life

The research read the actual equations and implementations in five primary sources. Exact URLs, retrieval hashes and inspected sections are in [research-sources.json](research-sources.json).

| Source | Relevant construction | Decision for Netta |
|---|---|---|
| [Cho et al., GRU, §2.3](https://arxiv.org/pdf/1406.1078) | Learned gates interpolate old state and a nonlinear proposal. | Keep an explicit learned write/retention mechanism. |
| [Feng et al., minGRU, §3.1.1](https://arxiv.org/html/2410.01201v3) | Input-only gates and proposals make the recurrence diagonal; this intermediate step retains `tanh`. | Use this bounded intermediate cell and manual backward gradients. |
| [Hochreiter and Schmidhuber, original LSTM](https://www.bioinf.jku.at/publications/older/2604.pdf) | A memory cell with input/output gates controls storage and access. | Treat retention and useful readout as separate questions. |
| [Peng et al., RWKV, §3 and Appendix D](https://arxiv.org/html/2305.13048) | A sequence is accumulated in fixed-size recurrent state. | Keep streaming inference small. |
| [Karpathy, minimal RNN implementation](https://gist.github.com/karpathy/d4dee566867f8291f086) | Explicit reverse-time derivatives and clipping. | Implement and independently check the complete gradients using the standard library. |

The project-specific reference was [`actually.life` at `7f59688`](https://github.com/ariannamethod/actually.life/blob/7f596883baa653c487127f420330b48501f962c9/l.c). Its organisms count ordered adjacent glyph pairs, create compound symbols from frequent pairs and can use existing compounds as parents. A generated glyph enters the recent sequence before the next choice. Pair identity preserves order even though the initial embedding of a new compound averages its parents. Its neural forward path uses causal attention; recurrent organism state also lives in the recent sequence, transition field and other acquired internal variables. Exact source locations and hashes are in [glyphs-sources.json](glyphs-sources.json).

Netta transfers the sequence principle through its existing byte-pair alphabet: composing units changes the state from which the next continuation is chosen. Each generated program has its own hidden trajectory. Lee saves learned parameters separately per island; Code acquires them across its mixed island. The caller selects the saved life, and the recurrent mechanism operates inside that life.

## Exact mechanism

For a unit's deterministic sparse 32-dimensional identity projection `x`:

```
z = sigmoid(Wz*x + bz)
c = tanh(Wc*x + bc)
h_next = (1-z)*h + z*c
outcome = sigmoid(bias + v·h_next)
candidate_logit_delta = 0.8*clip(v·h_next, -4, 4)
```

Two 8×32 matrices, three eight-value vectors and one output bias give 537 trainable parameters. Four signed hashed coordinates encode each unit. A private seeded RNG initializes the matrices; write biases start at −2 and the readout starts at zero. Birth therefore leaves the sampling law unchanged. All transition parameters learn after the readout becomes nonzero.

BOS, deterministic units and the actual emitted EOS all advance the real state. Hypothetical candidates receive provisional states; only the selected unit advances the stream. The hidden state resets for each program. The learned parameters and update count survive save/resume. Disabling the feature retains these weights while stopping readout and learning. Experience erasure resets the acquired head to birth parameters while keeping the selected configuration.

Actual runtime/novelty or game reward supplies the outcome target. The existing failure localization or explicit reward choices determine eligible positions. At most twelve equally spaced distinct eligible choice positions contribute mean binary cross-entropy; one full reverse pass and one SGD update cover the actual generated sequence. The rate is `0.05/sqrt(1+steps/4000)` with global gradient norm clipped to one. There is no extra truncation within the existing generator budget. Exact source, byte spans, tokens, choice history and termination are validated before enabled external learning can mutate state. [Design](design.json).

The memory is exposed as `--sequence-memory` and `--no-sequence-memory` on both models' `init`, `play` and `ask --learn-task --save`, plus `2048.py play` and `doomer.py train`. Omission retains the saved setting. Both model files remain independently runnable with the Python standard library.

## Why state and choice need separate measurements

For two updates, componentwise algebra gives:

```
T_B(T_A(h)) - T_A(T_B(h)) = z_A*z_B*(c_B-c_A)
```

A common suffix attenuates the difference by its retention factors. This establishes an ordered latent trajectory. Its usefulness at a choice depends on the readout:

```
v·h_next = v·h + v·[z_candidate*(c_candidate-h)]
```

The common `v·h` term cancels between candidates before clipping. Candidate-dependent gates carry the remaining history contrast. The frozen assay therefore measures actual candidate probabilities, source changes and exact-prefix controls as well as hidden-state differences.

## Fixed quality comparison

Code uses the existing first-unit anchor and disables the previous eight-unit context option. Each of two replicas per task receives 128 training attempts per baseline/candidate arm, followed by 128 frozen task evaluations and 128 separate no-task evaluations in baseline, candidate and same-candidate-checkpoint OFF conditions. All 4,096 attempts are preserved in 32 sealed streams. OFF changes only the enabled flag and performs no updates. [Protocol](code-protocol.json), [comparison](code-comparison.json), [decision](code-decision.json).

| Code measure | Separately trained baseline | Recurrent ON | Same-checkpoint OFF |
|---|---:|---:|---:|
| Table-request productive /256 | 93 | 95 | 94 |
| Complete table task /256 | 0 | 0 | 0 |
| Numeric productive /256 | 179 | 184 | 184 |
| Numeric task passes /256 | 171 | 172 | 172 |
| Numeric corpus source replay /256 | 6 | 8 | 8 |
| Separate no-task productive /512 | 192 | 191 | 191 |

The table gain is +1 in each replica. Distinct productive table behaviors increase 79→82 and numeric behaviors 35→42. The predeclared gate requires pooled table gain of at least five, no numeric replay increase and no free-play productivity decline; these three conditions fail. Confirmation and state promotion are not performed.

Lee starts from the published 2048 life, with existing provenance credit at strength 2.5 and experienced suffix support zero. Two replicas train baseline and recurrent arms for 128 attempts each, then evaluate baseline, recurrent and same-checkpoint OFF for 64 attempts each. The 896 generated attempts comprise 512 learning attempts and 384 frozen evaluations. Another 256 episodes use random legal and fixed greedy controls on the same evaluation environment seeds. [Protocol](lee-protocol.json), [comparison](lee-comparison.json), [decision](lee-decision.json).

| Lee / 2048 measure | Separately trained baseline | Recurrent ON | Same-checkpoint OFF |
|---|---:|---:|---:|
| Completed /128 | 86 | 87 | 86 |
| Completed score per raw attempt | 658.78125 | 663.34375 | 658.78125 |
| Corpus source replay | 10 | 9 | 10 |
| Corpus probe-behavior replay | 22 | 22 | 22 |
| Distinct completed sources | 46 | 45 | 46 |

The pooled score difference is +4.5625 points per raw attempt, with paired bootstrap 95% interval [−16.125, 29.8125]. Replica differences are −10.75 and +19.875. The gate requires positive gains in both replicas and a pooled gain of at least 25 with no completion loss. It fails, so confirmation and state promotion are not performed. Random legal play scores 986.09375 per attempt and fixed greedy play 1275.5 under the same move cap.

The prospective gallery policy is the first completed candidate in replica zero, seed `173000000`, scoring 1,228. Baseline also completes this seed. A separate first-difference witness at index 20 isolates one generated multiplier: baseline and same-checkpoint OFF use `* 4` and score 1,248; ON uses `* 2` and scores 560. The original generated source is executed in every case. [Gallery receipt](lee-gallery.json), [neural consequence witness](lee-neural-witness.json).

## Frozen interventions

The generation-only assay uses every candidate checkpoint and the original evaluation seeds: **2,560 Code generations and 640 Lee generations**, with five variants per seed. It runs no program workers or games and performs no learning. Genuine and OFF complete generation records match the original closed evaluations. Each state remains byte-equivalent after frozen generation.

1. Genuine acquired head and actual history.
2. OFF: the same acquired checkpoint with only its enabled flag changed.
3. Initial transitions: restore initial gate/proposal matrices and biases; retain the acquired readout and all other memories.
4. Zero prefix: retain all acquired weights and score from zero hidden history at each choice.
5. Permuted prefix: swap adjacent earlier units while preserving BOS, the first ordinary unit, the last eight units, length and multiset. Only the recurrent input changes; emitted code, ordinary local context and candidate support follow the actual sampler.

Five controls were requested before the full quality runs. The shared generation-only protocol was frozen after those runs had started, when root already had partial quality results. It includes every declared checkpoint and evaluation seed and introduces no model selection or parameter sweep. The exact original protocol and chronology are retained with the [transport amendment](sequence-assay-transport-amendment.json) and [event record](sequence-assay-transport-events.json).

| Frozen intervention | Changed Code sources /512 | Code maximum probability TV | Changed Lee sources /128 | Lee maximum probability TV |
|---|---:|---:|---:|---:|
| OFF | 4 | 0.00198531 | 2 | 0.000264684 |
| Initial transitions | 0 | 0.0000258170 | 0 | 0.000000347067 |
| Zero prefix | 0 | 0.0000582003 | 0 | 0.00000610191 |
| Permuted prefix | 0 | 0.00000275864 | 0 | 0.000000244300 |

TV is half the sum of absolute candidate-probability differences at matched genuine prefixes. The protected-order intervention changes probabilities at 10,017 Code and 424 Lee sampled choices, using the declared threshold of 1e−15. All six heads make 128 updates, and all 537 parameters in each differ from initialization. The ordering and trained transitions affect the sampling law; their effect is much smaller than removing the entire learned readout. The observed source changes are therefore principally consistent with the head's learned unit preferences, while the isolated history interventions select the same programs on these fixed seeds. [Code mechanism](code-mechanism.json), [Lee mechanism](lee-mechanism.json), [assay protocol](sequence-assay-protocol.json).

An initial long-open compressed diagnostic stream failed mandatory readback after the first checkpoint. That stream was rejected. The writer was changed to sealed per-seed compressed files with immediate readback; the seven mechanism/measurement functions have identical ASTs. Deterministic generation was replayed with the same fixed inputs, and all 34 recoverable interrupted records match the final records exactly. Actual program/game experiments were not repeated. The interrupted evidence and transport chronology are retained with the full archive.

## Independent verification and selected consequences

All **537 analytical derivatives** agree with finite differences, with maximum absolute error **1.763744713972025e−10**. Independent checks also cover the forward equations, order identity, common-suffix attenuation, cold start, all transition/readout parameter families and global clipping. [Gradient and order receipt](gradient-and-order.json).

The full suite passes **363 tests**. Compatibility reproduces **252 exact generation records**, **20 actual learning updates** and all **six caller routes**, including native Doom. The CLI checks exercise configuration persistence, standalone bodies, cross-species dispatch and real game feedback: two short completed 2048 episodes and one short native Doom episode, alongside rejected attempts. [Tests](tests.json), [complete test log](tests.log), [compatibility](compatibility.json), [CLI](cli.json).

The release bodies are the measured frozen candidate cores with the audited CLI integration. AST comparisons preserve all measured non-CLI code. Public states, corpora, caller contracts and existing source components keep their hashes. [Release assembly](release-assembly.json), [preservation](preservation.json).

The prospective Code gallery seed is `222000039`. It computes `result=[121,9,81,49,121,169]` with empty stdout. The program is corpus-novel and executable, but repeats acquired experience: `experience_replay`, `accepted=false`, `task_passed=false`. Its paired baseline is a corpus source replay. These distinctions remain visible in the [exact receipt](code-gallery.json) and [gallery](../../gallery.html).

Independent reconstruction checks all **1,536 training updates**, including **768 recurrent updates** and **4,977 selected recurrent loss positions**. Lee's audit additionally reconciles **95,916 actual board transitions**, including the 256 controls, and 65,596 source-bound action/temporal-credit receipts. The complete development comparison contains **4,992 generated attempts**; the 3,200 diagnostic generations are counted separately. [Audit summary](audit-summary.json).

The next architectural pressure point is the contrast between a remembered prefix and each candidate. The current linear readout shares a large common history term across candidates, leaving write-gate differences to express most contextual preference. A subsequent fixed experiment can give the candidate a direct learned query into the accumulated state and test that against a zero-history control. The present evidence selects this narrower question: how to make already represented order useful at a choice. The existing optional head and its complete measurements remain available, with defaults and published lives unchanged.

## Evidence storage

This directory contains compact protocols, aggregate comparisons, selected exact programs, verification receipts and source references. Complete attempted programs, choice histories, checkpoints, game trajectories, probability traces, test fixtures and reproduction tools are retained in the separate [archive inventory](private-archive-inventory.json). Downloaded full-paper caches remain outside the archive; the research notes preserve their URLs, hashes and inspected scope.
