# Corpus expansion V3

The four ordinary islands now contain 1,056 training programs. Every TXT file still contains only executable Python and the exact `# === PROGRAM ===` boundary line. Programs retain their original indentation. No requests, class labels, task descriptions, or family names enter the learner's input.

| Island | Training programs | Construction families | Held-out programs | Held-out families |
| --- | ---: | ---: | ---: | ---: |
| art | 256 | 32 | 16 | 4 |
| strings | 264 | 33 | 16 | 4 |
| records | 264 | 33 | 16 | 4 |
| mixed | 272 | 34 | 16 | 4 |

Each training family has eight parameter variants. Each held-out family has four. The expansion adds control-flow and data-construction families, in addition to varying dimensions, symbols, words, records, and numeric inputs. The mixed island intentionally shares some families with specialized islands; it is not a separate cross-domain generalization test.

## What changed

Art adds coordinate and mutable-canvas faces, filled and hollow silhouettes, tiered trees, roofs, a turning spiral walker, nested frames, mirrored masks, lattices, horizontal histograms, paired face panels, profiles, ribbons, woven blocks, and arrows. Programs expose different ways of producing a visible result: concatenation, comprehensions, character decisions, mutable grids, and coordinate updates.

Strings adds run-length encoding, neighboring-character counts, interleaving, rotation, common-prefix extraction, length ordering, vowel runs, wrapping, character positions, cumulative initials, column transposition, frequency ordering, anagram grouping, repeated-substring search, alternating case, mirrored words, and a sorted unique list of words.

Records adds grouped means, ranks with ties, pairwise differences, lookup joins, initial-based pivots, moving means, running extrema, field transposition, percentage shares, chunk summaries, histograms, all maxima, medians, inverse indexes, duplicate pruning, baseline deltas, and a sorted list of numeric values.

Mixed combines arithmetic, selected specialist families, and four families that retain computed results without printing. It contains 32 no-stdout examples; stdout is not required for those programs to perform actual work.

## Held-out families

`corpora/heldout/` contains entirely different construction families:

- Art: integer line stepping, flood filling, a cellular row update, and sprite rotation.
- Strings: dynamic-programming edit distance, nesting depth, trie construction, and shortest unique prefixes.
- Records: a Pareto frontier, greedy budget selection, a pairwise distance matrix, and weighted sampling along a fixed grid.
- Mixed: Pascal rows, Horner polynomial evaluation, a prime sieve, and balanced partitioning.

The builder checks that no held-out program has a whole-program AST shape occurring in any training island, after replacing literal values with their types. Family exclusion is the principal split rule; this AST check is an additional guard. Common Python syntax and subexpressions naturally occur across both splits.

Held-out files must remain outside training, archive updates, sampling feedback, and parameter selection. They support evaluation of unfamiliar program families, for example frozen continuation likelihood and controlled acquisition experiments with a declared new training stage. Merely executing these reference programs successfully does not measure model generalization.

`corpora/families_v3.json` is developer-only metadata: family membership, variant identifiers, paths, hashes, and split provenance. Neither learner imports this manifest. Any future evaluation that uses its labels must keep them outside model input.

## Validation

`results/corpus_v3_validation.json` records **1,120/1,120 accepted programs** through the real `runtime_part.worker_entry` judge in fresh isolated CPython subprocesses: all 1,056 training programs and all 64 held-out programs. Art uses the art judge; other domains use the general judge. Each program is passed to the judge unchanged. The report includes source hashes, status, instruction counts, output hashes, and the runtime hash before and after validation. The runtime was unchanged during the recorded run.

The runtime's conservative provenance checker currently does not recognize one nested-container mutation pattern used in a preliminary field-transposition example. The final corpus expresses that same operation using explicit intermediate lists. This changes the example program itself and does not repair generated learner output or weaken the judge.

Expected utility: more construction patterns and overlapping local continuations give the learner a broader set of executable combinations; family holdouts make it possible to separate familiar-family continuation from unfamiliar-family acquisition. Whether this improves accepted novel generation must be measured on newly initialized V3 states. Existing saved-state results describe their original islands.

## Reproduction and preserved data

From the project directory:

```sh
python3 tools/build_corpora_v3.py
python3 tools/validate_corpora_v3.py
```

The original four islands and Doom island are preserved byte-for-byte under `corpora/v1/`. The four original corpus hashes match the earlier `results/corpus_validation.json`. Existing states were not modified. The current `corpora/doom.txt` was not changed by this expansion.

`tools/build_corpora.py` remains the original V1 builder and supplies its template definitions to the V3 builder. Running that old script directly rebuilds V1 files in the top-level corpus directory; use the explicit V3 command above for this version. The V3 builder never writes `corpora/v1/` or any saved state.

## Fixed-budget release training

`tools/train_expanded.py` trains four fresh birth snapshots from `results/v3_birth/`. The declared release budget is 2,000 raw games per island, with explicit per-game seeds starting at 2,100,000 plus 10,000 times the domain index (`art`, `strings`, `records`, `code`). It retains the final checkpoint, without choosing a best intermediate checkpoint. Training attempts, including failures and replays, are streamed to `results/v3_expanded/<domain>/training.jsonl`.

Each final checkpoint then receives 600 frozen evaluation attempts, starting at seed 2,500,000 plus the same domain offset, paired against its own `without_experience()` state. That control resets the two neural heads, acquired transitions, transition credit, and both learned search settings. It retains the same corpus, units, judge reference, source and behavior exclusions, visit history, statistics, RNG state, and fixed exploration configuration. The trainer exhaustively classifies every snapshot field, so a new field cannot silently escape the ablation definition.

Both arms are evaluated by `compare_v3.evaluate` under the preserved V2 judge and novelty rules. Every admitted productive source is additionally executed unchanged by ordinary CPython, with matching stdout required. Evaluation records full sources, hashes, exclusions, and before/after state hashes. This is a secondary expanded-island comparison; the separate matched old-island protocol remains the primary V2/V3 comparison.

```sh
python3 tools/train_expanded.py
```

The output paths must not already exist. Final states are written under `states/v3_expanded/`; experiment summaries are under `results/v3_expanded/`. Running again requires distinct output directories or deliberately archiving the previous run first.

### Recorded release results

All four trajectories completed their declared 2,000 raw training games. Each evaluation arm used exactly 600 fresh seeds. Values below are **trained / without experience**; the last column excludes all behavior already present in the final trained memory for both arms.

| Island | Training admissions | Productive attempts / 600 | Unique productive behaviors | Unique behaviors beyond final memory |
| --- | ---: | ---: | ---: | ---: |
| art | 351 | 271 / 46 | 153 / 45 | 52 / 32 |
| strings | 193 | 180 / 45 | 90 / 44 | 39 / 40 |
| records | 117 | 136 / 24 | 64 / 22 | 13 / 13 |
| code | 148 | 205 / 19 | 62 / 19 | 26 / 12 |

Across all four islands, the trained states produced more executable, corpus-novel results. Further discovery improved for art and code; strings yielded 39 versus 40 behaviors beyond final memory, and records yielded 13 versus 13. The secondary run therefore supports acquired productive capability across these islands, with uneven improvement in subsequent discovery. It does not establish a universal discovery gain.

The run contains 8,000 training attempts and 4,800 frozen evaluation attempts, with no independent execution failures, stdout disagreements, or independently detected corpus replay admissions. Every in-memory evaluation hash and saved checkpoint hash remained unchanged. The full paired counts and per-program evidence are in `results/v3_expanded/summary.json` and its domain reports.
