# Per-decision continuation credit

Both standalone organisms now expose an optional source-bound decision-credit
mechanism. The host computes the targets from actual transitions; the core maps
those targets to generation choices on the executed source lines. The core has
no Python grammar rules, game actions, board rules or action substitution.

## Contract and learning

```python
model.configure_decision_credit(
    enabled=True, strength=2.5, contract="2048-action-advantage-v1")
model.observe(
    generated, episode_reward, runtime_ok,
    environment_observed=True,
    executed_lines=actual_episode_lines,
    decision_feedback={
        "source_hash": digest(generated["source"]),
        "contract": "2048-action-advantage-v1",
        "decisions": [
            {"executed_lines": actual_step_lines, "target": bounded_target},
        ],
    },
)
```

Each actual decision supplies a target in `[0, 1]` and the lines executed while
choosing its action. A generation association counts once within that decision,
including when a loop executes its line repeatedly. Across the episode, the
association receives the arithmetic mean of targets from decisions in which it
participated, followed by one credit trial. Repeating an entire sequence of
decisions therefore does not multiply the accumulated credit.

The separate credit table weights existing generation candidates with strength
2.5, the same coefficient as ordinary local credit. Episode credit, runtime and
syntax heads, search updates, acquisition and source generation are preserved.
An empty decision table has zero influence on generation or RNG consumption.

The 2048 bridge supplies two explicit contracts. `2048-uniform-v1` assigns the
terminal normalized episode reward to every actual decision, providing an
exposure control. `2048-action-advantage-v1` normalizes the selected move's
immediate merge gain between the minimum and maximum gain among the current
board's legal moves; equal gains receive 0.5. These target definitions belong
to the bridge. Generated code remains the actor selecting every move.

## Receipts and persistence

The complete receipt is validated before any ordinary counters, search tables
or learned state change. Validation binds exact-source SHA-256 and named host
contract, requires a real observed episode, checks finite bounded targets, and
requires each decision's integer line numbers to belong to the separately
validated episode trace. Empty decision lists are rejected. Invalid late rows
cannot leave a partial update.

Completed observed episodes require a receipt when the feature is enabled.
Unplayed replay rejections retain ordinary negative credit. A failed partial
episode retains ordinary failure learning and contributes no decision-credit
update, even when it supplies a valid receipt for earlier steps.

The additive `decision_credit` snapshot field stores configuration, acquired
associations and episode/decision counts. Defaults omit this field, preserving
old snapshots byte for byte. Disabling the feature retains acquired memory for
ablation. Experience erasure preserves the selected contract and strength while
clearing acquired associations and counts. A new host contract requires a
separate acquired history. The Code assembly helper remains compatible.

## Verification

Thirteen focused contracts pass on both standalone species. They cover frozen
baseline generation/learning and snapshot parity, fresh-feature neutrality,
actual Python branch traces, distinct branch targets with a common-line mean,
loop and episode-length normalization, unchanged ordinary learning, isolated
influence on sampling, partial failures, atomic malformed receipts, snapshot
resume and experience erasure. Snapshot consistency checks reject learned
history without its host contract or observation counts.

Independent probes additionally exercised 18 malformed receipt scenarios per
species, direct target/mean accounting and five implicit-RNG save/resume cycles.
The final counter-consistency validation differs from the initial frozen game
bundle only when loading malformed snapshots; valid sampling and learning are
unchanged. Source hashes are in `manifest.json`. Gameplay comparisons are
reported with the 2048 experiment.
