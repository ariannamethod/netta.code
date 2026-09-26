# Physics stage 1: single-underscore names + assert

2026-09-25, Don. Frozen before any judge edit. Baseline: the frozen "before"
in ../physics_baseline_pre_stage1/baseline.md (HEAD f2deef0, baseline commit
9887912), receipts pinned there.

## Question

Does the first allowlist widening — single-underscore names and the assert
statement — raise the world's compatibility (external corpus yield through
her own court) without degrading her existing crafts?

## The law change — exact, and nothing else

Both judges receive the IDENTICAL hunks: nettalee.py (the `_runtime_tree`
policy, lines 1480–1542 region) and its twin in nettacode.py (same policy at
its own offsets, `_ALLOWED_AST` at nettacode.py:1612). The report shows the
two diffs side by side; any divergence between the bodies is a defect.

1. `_ALLOWED_AST` gains one name: `Assert`.
2. The name gate narrows from all-underscore to dunder-only: the refusal
   `name.startswith('_')` (Name/arg, nettalee.py:1517) and
   `node.name.startswith('_')` (FunctionDef, nettalee.py:1520) both become
   `startswith('__')`, message `'dunder names unavailable'`. Single
   underscore becomes lawful for variables, arguments and function names —
   including the bare `_` throwaway.
3. Nothing else moves: `_SAFE_FUNCTIONS`, `_SAFE_METHODS`, every RUNTIME
   limit, the attribute gate (so `x._private` stays refused — no
   single-underscore method is in `_SAFE_METHODS`), the decorator refusal,
   and Raise/Try/Import/ClassDef/Lambda/With stay out. The runner's flags
   are untouched and `-O` is never added — asserts stay live.

Why dunder stays a wall: the execution namespace holds `__builtins__` as a
bare name (nettalee.py:2112); the parse-time name gate is what keeps
namespace introspection out of her world. A failed assert is an
AssertionError at runtime — the run fails in court like any error. Assert
makes self-checking code expressible; refusal remains the judge's.

## Axis A — crafts (no degradation)

Re-run the baseline's exact frozen method after the edit:
`python3 <body>.py sample --state states/<island>.json --attempts 256 --seed
4242` — art/records/strings via nettalee.py, code via nettacode.py.
Tolerance declared now: ZERO. Per island, each of accepted / productive /
unique_accepted / new_shapes must be >= its baseline value (art 16/122/15/16,
code 21/78/20/21, records 7/52/6/7, strings 23/81/20/23). Stated expectation:
frozen state + same seed + a strictly wider judge = identical candidates,
admission can only widen, so equality is the null and any fall is a DEFECT
to diagnose, not a tolerance to spend. Game islands re-snapped and reported
against their baseline numbers (2048 count arm 587/1024, score_per_raw
589.21; Doom MAP02 kills 4 / reward 0.911); same determinism expectation.

## Axis B — corpus yield (the point of the step)

tools/admit.py over the SAME external corpus snapshot that measured 4/1604,
its file list and digest pinned in the report. Before-yield confirmed at the
pre-edit commit, after-yield at the post-edit commit, same command. Gate:
yield strictly rises (> 4). The report names every new citizen and the exact
refusal it used to die on (private names / unsupported syntax: Assert) —
attribution measured, not assumed.

## Integrity teeth — both polarities, machine verdicts

- t1: a probe file using a single `_name` and an `assert` — refused BY NAME
  pre-edit, accepted post-edit.
- t2: probes with a `__dunder` name, `import`, `try`, `raise`, `class`, a
  decorator, and an `x._private` attribute — each still refused BY NAME
  post-edit, one probe per refusal, zero collateral.
- t3: `__builtins__` as a bare Name — refused (`dunder names unavailable`).
- t4: assert liveness — a file whose assert must fail fails at run time
  (proves nothing strips asserts).

## Gate and FAIL semantics

step_pass = AxisA (no fall, all islands) AND AxisB (yield > 4) AND t1–t4.
AxisB flat while AxisA holds = the step is refuted as useless on this corpus
— recorded with the refusal histogram of the still-rejected files, and the
ladder is re-examined (perhaps `_names`+assert only pay together with
stage 2 Raise/Try). AxisA falling = stop; diagnose before any further
widening. A FAIL with numbers is a result of equal rank.

## Hands

The engine hand edits both judges, runs both axes and all teeth, and commits
with receipts (sha256 of the four re-snapped sample JSONs, the admit.py
before/after outputs, and both diff hunks in the report). Don counter-runs
axis A for at least one island and the full teeth set with his own hand
before the step is called adopted. No learning, no training, no state file
is touched by this step.

— Don (Fable, neo), 2026-09-25

## Results — measured, NOT adopted (engine hand, 2026-09-26)

Judge edit applied to both bodies (identical hunks, see judge-hunks.diff,
twin-diff verified identical): `_ALLOWED_AST` += Assert; name gate
`startswith('_')` -> `startswith('__')` with message `dunder names
unavailable`; FunctionDef gate split so decorator refusal keeps its own name.
Nothing else moved.

**Integrity teeth — all pass (machine verdicts):**
- t1: `_total`/`_i` + assert + real computation -> refused pre-edit
  (`unsupported syntax: Assert`), accepted post-edit (both bodies). A trivial
  `_name`+assert probe correctly returns `trivial` — the productive filter is
  separate and right to cut it.
- t2: `__dunder`->`dunder names unavailable`, import->`Import`, try->`Try`,
  raise->`Raise`, class->`ClassDef`, decorator->`private functions/decorators
  unavailable`, `x._n`->`attribute unavailable: _n`. Each refused BY NAME,
  zero collateral, both bodies identical.
- t3: `__builtins__` bare Name -> `dunder names unavailable`.
- t4: failing assert -> `runtime_error: AssertionError` (asserts stay live; -O
  never added).

**Axis A — PASS, exact equality.** Re-snapped art/records/strings (nettalee)
and code (nettacode), frozen states, seed 4242, N=256. Every sample JSON is
byte-identical to the baseline (sha256 match: art 18f976…, records 40bed4…,
strings dc3ab8…, code 4584fd…). accepted/productive/unique/new_shapes all
equal baseline (16/122/15/16, 7/52/6/7, 23/81/20/23, 21/78/20/21). Frozen
state + same seed + strictly wider judge produced identical candidates, as
preregistered. Zero degradation.

**Axis B — FLAT, step refuted on this corpus.** admit.py over the same
1604-file snapshot: accepted 4 -> 4. counts before -> after: policy_rejected
180->179, trivial 13->14, all else unchanged. No new citizen.

Refusal histogram of the still-rejected (import-free) files, post-edit:
`dunder names unavailable` 115, `Raise` 30, `ClassDef` 14, `Try` 8, others <3.
The dominant private barrier was never single-underscore — it is `__name__`
in the `if __name__ == '__main__':` guard (115 of 179), a dunder the step
deliberately does not touch. single-`_`+assert are lawful widenings but no
file was blocked by them alone; all are multi-barrier.

**Verdict:** step_pass = AxisA AND AxisB AND teeth -> NOT passed (B flat).
Refuted as useless on THIS corpus, exactly as the gate preregistered. The
judge edit is measured, not adopted: reverted in the very next commit so the
stage-2 baseline stays clean. Two follow-ups for Don's next prereg: (a)
stage2-alone (Raise/Try) vs stage1+stage2 combined against this baseline —
does _names+assert only pay together; (b) stage 1b — surgical single-node
allow of `__name__` at the parse gate + `__name__='__main__'` namespace
injection, `__builtins__` wall untouched, to test whether the main-guard is
the real door on this corpus.

Receipts (sha256, this dir): art/records/strings/code-sample.json match
baseline; admit-after.jsonl 6076ab…; admit-before.jsonl (the 4/1604 snapshot);
judge-hunks.diff 840ebc… (the reverted edit, preserved in history).
