# Preregistration — 2048 organ-ablation batch 1

Frozen before running, per BRIEF v2 priority 1. Builder: Opus (neo). Auditor:
Don (counter-run on results). HEAD at declaration: 4939992. Date: 2026-09-25.
Runtime: CPython 3.14 / darwin. No reruns after results are seen; rc taken
directly (never through a pipe); every arm's summary.json is hashed.

## Question

Re-measure the 2048 compass (NETTALEELOG: learned 589.59 vs random-legal
949.42 per raw attempt) UNDER the new organs, and decide, per Don's doctrine
(gradients may be an ORGAN, never the ORGANISM): does each organ pay for
itself? Split the two gaps the brief names — has outcome conditioning closed
the WANT-SCORE gap (score per attempt), or only the PLAY-MORE gap (attempts
completed)?

## Fixed setup

- Island: corpora/2048.txt (64 policies). One init, seed 71, then copied so
  every arm starts from byte-identical experience.
- Train (play): 800 raw attempts. Eval (evaluate): 256 attempts. max-moves 128.
- Shared seeds across ALL arms (paired by construction): play --seed 3100000
  --episode-seed 3200000; evaluate --seed 3500000 --episode-seed 3600000
  (2048.py defaults). Per-attempt seed = base + index.
- Built-in baselines in every eval on the same episode seeds: random_legal
  (the 949.42 compass) and fixed_greedy.

## Arms (leave-one-out around FULL)

1. count   — all organs OFF (the counting body; sanity vs historical 589.59)
2. full    — --sequence-memory --experience-support 0.10 --decision-credit temporal --control-learning both
3. head-off       — full minus --no-sequence-memory
4. credit-off     — full minus --decision-credit off
5. support-off    — full minus --experience-support 0.0

## Metrics (from summary.json)

- score_per_raw_attempt   (compass; want-score, per raw attempt)
- mean_played_score       (want-score isolated from completion rate)
- played / raw_attempts   (play-more gap)
- completed, max_tile, distinct_played_sources

## Gate (frozen)

- G1 compass: report full.score_per_raw_attempt against random_legal (949.42
  class). The hostile number stays in the log until beaten.
- G2 gap split: if full raises played/raw but mean_played_score(full) is not
  above mean_played_score(count), the organs closed only the PLAY-MORE gap —
  say so plainly.
- G3 organ pays for itself: an organ is retained ONLY IF its leave-one-out arm
  degrades vs full on the shared seeds — paired difference with a bootstrap
  95% interval that does not cross zero. sequence-memory (the BPTT reflex) is
  kept only if head-off degrades; otherwise it is a removal candidate.

A FAIL with numbers is a result. No arm is promoted on this batch alone;
Don counter-runs before any "organ pays" verdict.

## Results (run at 4939992, CPython 3.14 / darwin, 2026-09-25)

One init (seed 71), five byte-identical copies. Each arm: play 800 (rc=0),
evaluate 256 (rc=0). Aggregate eval metrics (trained arm):

| arm         | score/raw | mean_played | played/256 | max_tile | distinct |
|-------------|----------:|------------:|-----------:|---------:|---------:|
| count       |    608.86 |     1046.1  |        149 |      128 |       64 |
| full        |    652.53 |     1121.1  |        149 |      128 |       59 |
| head_off    |    587.52 |     1066.7  |        141 |      128 |       66 |
| credit_off  |    593.02 |     1084.4  |        140 |      256 |       48 |
| support_off |    657.00 |     1064.5  |        158 |      128 |       74 |
| random_legal|    965.06 |             |            |          |          |
| fixed_greedy|   1265.55 |             |            |          |          |

Paired bootstrap on reward, matched by episode_seed (256 shared seeds,
10000 resamples, seed 20260925), full minus each arm:

| comparison         | mean diff | 95% CI              |
|--------------------|----------:|---------------------|
| full - count       |  +0.01460 | [-0.03421, +0.06392]|
| full - head_off    |  +0.03135 | [-0.00075, +0.06336]|
| full - credit_off  |  +0.03025 | [-0.00757, +0.06873]|
| full - support_off |  -0.01303 | [-0.06076, +0.03323]|

### Verdict against the frozen gate

- G1 compass: NOT beaten. full 652.53 < random_legal 965.06 per raw attempt.
  fixed_greedy 1265.55 is the harder ceiling. The hostile number stays.
- G2 gap split: aggregate mean_played rose (full 1121.1 vs count 1046.1) with
  identical played (149=149) — reads as want-score, not play-more — BUT the
  paired full-count reward CI [-0.034, +0.064] crosses zero, so even this is
  not separable from noise at N=256.
- G3 organ pays for itself: NONE cleared it. Every leave-one-out CI crosses
  zero. head_off is closest (lower bound -0.00075) but does not pass. Per
  doctrine, no organ is retained on this batch; none is condemned either —
  the batch cannot separate an organ worth ~0.03 reward from noise at N=256.

Not a failure of the organs, a failure of resolution. Next batch: N>=1024 on
the same shared-seed design before any keep/remove call. Non-improving result
logged per brief priority 5.

Receipts (sha256, this directory):
- count-summary.json      de52cc62ba2ea2c1e9216d59d0965a11f97c3765e0c5480864d29049bd294b7e
- full-summary.json       f88696ee963f89618f09a8bdce7f6ff0d054f1600159bc5427e500fdb57affb6
- head_off-summary.json   92bd0c1162cb53e3cd30601787343195307a7d48d95d31aba052d84b0fabb687
- credit_off-summary.json a6dcf2a0e590b61bac1f7616989d25dd1291e504f8ec9ae8468f0304941944cc
- support_off-summary.json e6ae5338409820b01b5d08aa4122c4afdb40c99fcc15459ad8764b80e8e39744
- bootstrap.py            8e33f2e58b595f5ab448a1495d3aeeabb4127c9834e6df0de7253c5dbd01175b

Reproduce (rc direct):
  python3 2048.py init --state B/init.json                      # seed 71
  cp B/init.json B/<arm>.json                                   # per arm
  python3 2048.py play --state B/<arm>.json --out B/<arm>_play --attempts 800 <arm flags>
  python3 2048.py evaluate --state B/<arm>.json --out B/<arm>_eval --attempts 256
Arm flags: count=(none); full=--sequence-memory --experience-support 0.10
--decision-credit temporal --control-learning both; head_off=full with
--no-sequence-memory; credit_off=full with --decision-credit off;
support_off=full with --experience-support 0.0.
