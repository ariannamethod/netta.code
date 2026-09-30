# Physics stage 2: three doors against a measured wall

2026-09-27, Don. Frozen before any judge edit. Baseline unchanged: the
stage-1 "before" (baseline commit 9887912; judge at HEAD == original,
verified diff 9887912..687494d over both bodies = 0 lines). The wall map is
sealed: stage-1 measurement b8a71e2 plus Don's counter-run (zero mismatches
over 1604 rows, refusal histogram reproduced digit for digit) — of 179
policy_rejected files: `dunder names unavailable` 115 (the
`if __name__ == '__main__':` guard), `Raise` 30, `ClassDef` 14, `Try` 8,
others ≤2.

## Question

Which minimal set of doors raises corpus yield through her own court —
and does stage 1 pay only in combination, as its FAIL left open?

## The doors — exact

- **D-name**: the parse gate allows exactly one dunder, the bare Name
  `__name__` in Load context only (Store/Del stay refused; every other
  dunder stays refused, `__builtins__` included), and the execution
  namespace gains one entry: `__name__ = '__main__'`. Main-guard bodies
  therefore execute — the court then judges what they do.
- **D-exc**: `_ALLOWED_AST` gains `Try`, `ExceptHandler`, `Raise` (with
  finally/orelse/bare-except/`raise..from` as those nodes carry them), and
  the declared exception set E = {ValueError, TypeError, KeyError,
  IndexError, ZeroDivisionError, ArithmeticError, AssertionError,
  Exception} enters both the call gate and the namespace. Provenance of E,
  measured on the sealed 1604-file snapshot 2026-09-27: raised ValueError
  996, TypeError 150, Exception 56, IndexError 28, AssertionError 20,
  ZeroDivisionError 7, ArithmeticError 6, KeyError 5; caught ValueError 54,
  IndexError 18, TypeError 13. SystemExit and every I/O or system type
  (OSError, ImportError, FileNotFoundError, AttributeError) stay out — no
  door to the process or the filesystem.
- **D-priv**: stage 1 verbatim — `Assert` + single-underscore names — the
  exact hunks preserved at b8a71e2 (judge-hunks.diff).

Both bodies receive identical hunks per arm; twin divergence is a defect.
Nothing else moves: `_SAFE_FUNCTIONS`, `_SAFE_METHODS`, limits, attribute
gate, decorators, Import/ClassDef/Lambda/With, `-O` never added.

## Arms

Axis B (tools/admit.py, the same pinned 1604-file snapshot, same command)
runs for all seven door combinations: {name}, {exc}, {priv}, {name,exc},
{name,priv}, {exc,priv}, {name,exc,priv}. Each arm's report carries yield,
the full status counts, the refusal histogram of its still-rejected files,
and every new citizen named with the refusal it previously died on.
Ceiling stated honestly: these doors address only the 179 policy_rejected
files; has_import 1094 is out of scope until a stage that touches imports.

Axis A (crafts, zero tolerance, the stage-1 frozen method and numbers) runs
for the union arm {name,exc,priv} and for the adoption nominee. Stage-1
evidence (byte-identical sample JSONs under a strictly wider judge) says
equality is the null; any fall is a defect.

## Integrity teeth — per arm, both polarities

- Each door's accept-probe passes exactly in the arms containing that door
  and is refused BY NAME in every arm without it (one probe per door:
  a main-guarded file; a raise/try file using only E; a `_name`+assert
  file with real computation).
- Wall probes refused in ALL arms: `__import__`, `__builtins__`, a
  non-`__name__` dunder, `import`, `class`, a decorator, `x._private`
  attribute; in D-name arms additionally `__name__ = ...` (Store) refused.
- In D-exc arms: `raise SystemExit(0)` refused (`call unavailable`);
  an exception type outside E refused by the call gate.
- In D-priv arms: assert-liveness (a failing assert fails at runtime).
- Twin identity across both bodies for every arm's hunks.

## Gate and adoption law

An arm is USEFUL if axis B yield > 4 strictly, with teeth green. Adoption:
among useful arms whose axis A holds, adopt the arm with the highest
yield; tie broken by fewer doors. Adoption of an arm containing D-priv
retroactively adopts stage 1 as part of a paying combination — the clean
answer to stage 1's open question. If NO arm is useful, all three doors
are refuted on this corpus, the ladder stops, and the open question
becomes the corpus itself (structurally main-guarded and import-heavy:
1094/1604 has_import). A FAIL with numbers is a result of equal rank.

## Instrument law (stage-1 gap, closed here)

tools/admit.py enters git BEFORE the measurement commit. Stage 1 committed
the receipts while the instrument stayed untracked — the counter-run had
to take admit.py from the working tree instead of the measured ref. The
axis-B instrument is part of the experiment and lives at the measured
commit, or the measurement is not self-contained.

## Hands

The engine hand implements the seven arms (judge variants applied and
reverted around each measurement, or equivalent parameterization —
whatever form, the judge in main stays the original until adoption), runs
axes and teeth, commits measurement receipts (per-arm manifests sha256,
histograms, twin diffs). Don counter-runs axis B for the adoption nominee
and the full teeth set with his own hand before any arm is called adopted.
No learning, no training, no state file is touched.

— Don (Fable, neo), 2026-09-27

## Results — measured, NOT adopted (engine hand, 2026-10-01)

Instrument: tools/measure_doors.py (sha bc9f1496…). The judge in main is never
edited — each arm builds patched twin COPIES in a scratch dir and axis B runs
against that variant. main untouched throughout: git diff nettalee.py
nettacode.py = 0 lines (main-untouched.diff). Every arm twin_ok = true.

**Axis B — yield over the sealed 1604 corpus (baseline before = 4):**

| arm            | yield | note                         |
|----------------|------:|------------------------------|
| exc_name_priv  |    24 | union, highest yield         |
| name_priv      |    23 | one door fewer, exc's +1 lost|
| name           |    16 | the load-bearing door alone  |
| exc_name       |    16 | exc adds nothing to name     |
| exc            |     4 | flat alone                   |
| priv           |     4 | flat alone                   |
| exc_priv       |     4 | flat without name            |

Reading: **name carries the wall** — 16 alone, the `__name__` main-guard (115
of the 179 refusals). **priv pays only in company** — name 16 -> name_priv 23
(+7), which closes stage 1's open question: single-`_`+assert earn their place
combined with name, never alone (priv alone still 4). **exc barely knocks** —
+1 only in the full triple (name_priv 23 -> exc_name_priv 24), 0 otherwise; it
admits exactly one Raise citizen.

**Axis A — PASS, exact equality.** Nominee/union exc_name_priv re-sampled
art/records/strings (nettalee variant) and code (nettacode variant), frozen
states, seed 4242, N=256: every sample byte-identical to baseline (sha match
art 18f976…, records 40bed4…, strings dc3ab8…, code 4584fd…). Three doors open,
zero degradation of her crafts.

**Teeth — all green, both polarities.** accept-probe matrix: each door's probe
is `ok` in exactly the arms containing that door and refused elsewhere
(name in the 4 name-arms, exc in the 4 exc-arms, priv in the 4 priv-arms).
Walls in the union arm all refuse: `__import__` (call unavailable),
`__builtins__` and any non-`__name__` dunder (dunder names unavailable — the
name door opens only `__name__` in Load), import/class/decorator/`x._private`,
and `__name__ = ...` in Store. exc arms refuse SystemExit and OSError (call
unavailable). priv arms keep assert liveness.

**Attribution — 20 new citizens** (of 24, the other 4 already lawful), by the
refusal they died on under the original judge: `private names` 16 (the
main-guard class), `private functions/decorators` 2, `Assert` 1, `Raise` 1.
Note: first-refusal attribution is coarser than the yield delta for
multi-barrier files — the +7 that priv adds over name-alone is the exact
measure of priv's contribution; several of the 16 `private names` files needed
priv as a second barrier and opened only with both doors.

**Verdict.** All of name / name_priv / exc_name / exc_name_priv are USEFUL
(yield > 4, teeth green, axis A holds on the nominee). By the adoption law
(highest yield, tie to fewer doors) the nominee is exc_name_priv (24). But
exc's marginal +1 (one Raise citizen) against one extra door is Don's call:
name_priv (23) delivers the wall's real gain with two doors. Adoption of any
D-priv arm retroactively adopts stage 1 — its open question is answered: it
pays in company. The judge edits are measured, not adopted; main stays the
original pending Don's counter-run of the nominee's axis B and the teeth.
Ceiling honest: doors touch only the 179 policy_rejected; has_import 1094 waits
for an import stage.

Receipts (sha256, this dir): arms.json 9ed99d73…; axisA-nominee-*.json (match
baseline); main-untouched.diff (0 lines); tools/measure_doors.py bc9f1496….
