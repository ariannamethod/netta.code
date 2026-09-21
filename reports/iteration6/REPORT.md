# Sixth engineering pass — temporal credit and branching context

Experimental baseline: `e8b0f78ef507ca89b155d7c66e9e130d78a19a2a`. The author's updated NETTA title is preserved. Exact generated source, independent saved island lives and standard-library model bodies remain the foundation.

## Installed capabilities

`2048.py play --decision-credit temporal` adds the explicit `2048-temporal-return-v1` contract. For each actual decision, the host computes the discounted mean of merge gains over the current move and up to seven following moves, with discount 0.9. Let those returns be `Q`, their mean `m`, the maximum absolute deviation `d`, and the existing episode reward `r`. The target is `r + min(r, 1-r) * (Q-m)/d`; constant returns receive `r`. Targets remain bounded and preserve the episode mean. Each encountered generation association still receives one averaged credit trial per episode.

The calculation uses the completed real trajectory. The generated program selects every move unchanged. Constant integer-gain sequences and endpoint rounding have focused regression checks. Settings, learned tables and named contracts survive save/resume; existing modes and published defaults retain their behavior.

The README now shows exact generated Code, 2048 and Doom programs plus three original Doom frames. PNGs and their [provenance](../../doom/assets/provenance.json) live in `doom/assets/`. The frames show a pistol shot, incoming projectile and ammunition pickup. The accepted Code example independently reproduces `[12, 15]` in CPython.

## Python requirements

`requirements.txt` contains comments and no installable package. Both model bodies, 2048 and the default Doom Generic Python bridge use the standard library. The vendored engine needs a C compiler, `make` and an external IWAD. `requirements-doom.txt` retains `vizdoom==1.3.0` for the explicitly selected `--backend vizdoom` implementation, which imports that package lazily. No dependency was added or removed.

## 2048 fixed comparison

Two replicas per arm, each with 128 learning attempts and 64 fresh evaluation attempts. The fixed arms were existing learning, uniform decision credit and one temporal candidate.

| Learning | Played / raw | Completed score / raw | Mean played score |
|---|---:|---:|---:|
| Existing | 76/128 | 568.15625 | 956.89474 |
| Uniform | 80/128 | 606.6875 | 970.7 |
| Temporal | 80/128 | 606.6875 | 970.7 |

Uniform and temporal gained 38.53125 points per raw attempt over existing learning; paired bootstrap 95% interval [-5.125, 84.09375]. All 128 generated sources and play outcomes matched between uniform and temporal, with 80 played episodes per arm. Across 256 training attempts, one source differed in an unplayed rejection; the actual training episodes matched. The prospective rule required temporal to beat uniform in each replica and by at least 25 pooled points/raw. It failed, so no confirmation sweep or snapshot replacement followed.

The temporal memory did receive distinct feedback: 21 of its 153 credited training episodes contained an affected generated-choice association, with 22 affected episode/key pairs out of 1,047. Maximum key-level target difference from uniform was 0.0229352. That narrow influence changed saved credit but did not change held-out behavior in this comparison.

Uniform random legal and fixed greedy controls scored 932.6875 and 1259.1875 per raw attempt over the same 128 starts. All rejected, failed and incomplete generated attempts remain in the primary denominator. [Protocol](protocol-2048.json), [comparison](2048-comparison.json), [decision](2048-decision.json).

## Code fixed comparison

The private candidate combined the existing first-anchor prior with a later context only when the later context supported multiple available continuations. Its fixed weight was `min(1, Gini_later/Gini_first)`, or 1 when first-context impurity was zero; unary later support returned exactly to the first-anchor law. The two separately smoothed probabilities were mixed arithmetically before the existing finite log weighting. Candidate support, source bytes, indentation and the judge stayed unchanged.

Two replicas per task, each with 128 learning and 128 fresh evaluation attempts:

| Outcome / 256 attempts | First anchor | Branching later context | Candidate-trained, first-only restored |
|---|---:|---:|---:|
| Table productive execution | 82 | 68 | 73 |
| Complete table task | 0 | 1 | 1 |
| Table source replays | 39 | 58 | 60 |
| Numeric task completion | 141 | 143 | 145 |
| Numeric source replays | 10 | 12 | 13 |

The declared gate required table productive execution to gain at least five, neither task to lose completions, and neither task to increase source replays. It failed. The public first-anchor implementation and saved Code state remain unchanged; the complete candidate is preserved with its 2,560 measured attempts. [Protocol](protocol-code.json), [compact comparison](code-comparison.json).

## Where the learning signal reaches

An exact replay of all 768 fifth-pass training attempts traced the proposed temporal signal back to actual generation choices. Only 44 of 3,519 episode/key pairs changed, across 40 of 519 completed episodes. Many varying runtime lines have a single possible continuation during generation and therefore contribute no sampled-choice association. In the strongest concrete example, the affected choice was the `2` in `score += board[first] * 2`; the subsequent assignment to `action` contained no sampled choice. The current executed-line union also includes computations for directions that the program eventually discards.

This identifies the next architectural question: how to connect the final action to the particular executed computations that produced it, while retaining the exact source and the model's freedom to write it. Code's next memory question is selection of useful relationships across examples: the recent-context variants keep raising corpus replay. The [source-backed diagnosis](credit-diagnosis.json) records counts, definitions and the concrete policy.

## Verification and storage

The full shared suite passes **274 tests**, with zero failures, errors or skips. [Summary](tests.json), [test output](tests.log). Independent verification reconciles all **3,968 measured attempts**, 106,504 board transitions, all 1,152 generated 2048 sources and all 1,792 training updates across the two experiments. It checks 17,100 temporal targets against a rational oracle, six real caller routes, source/novelty receipts, saved-state continuation and all three Doom images. No attempt recovery was needed. [Audit summary](audit-summary.json).

Public reports contain compact protocols, comparisons and verification receipts. Full attempts, frozen source, checkpoints and reproduction tools are kept in the [separate compressed archive](private-archive-inventory.json).
