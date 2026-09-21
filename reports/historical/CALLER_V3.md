# Declared command outcomes

`tools.json` can attach `commands` to a specialization. Each profile names exact
request phrases and an output contract. `state:command` selects the same profile
directly. Whole-phrase matching normalizes Unicode, case and whitespace while
preserving punctuation and numeric signs.

The six default profiles are:

| Profile | Output checked |
| --- | --- |
| `art:compact_marks` | 3–12 lines; widest line 3–24 characters; contains both `#` and `.` |
| `art:compact_picture` | 3–18 lines; widest line 3–40 characters |
| `strings:unique_sorted_words` | Python literal list, at least two strings, unique, ascending |
| `records:sorted_values` | Python literal list, at least two finite numbers, ascending |
| `records:row_report` | 2–30 lines; widest line 3–120 characters |
| `records:table` | Python literal list of at least two `[name, value]` rows; name is a string and value a finite number |

For example, `нарисуй компактный узор` selects `art:compact_marks`; `нарисуй рожу`
selects the art state and explicitly reports `task.status = "no_match"`. Additional
profiles and aliases are declared in JSON. TXT islands continue to contain only
scripts. The output contract is applied after exact-source execution.

## Profile schema

```json
{
  "name": "sorted_values",
  "requests": ["output sorted numeric values", "выведи отсортированный список чисел"],
  "output": {
    "literal_type": "list",
    "min_items": 2,
    "item_type": "number",
    "sorted": "ascending"
  }
}
```

Supported text constraints: `equals`, `contains`, `min_lines`, `max_lines`,
`min_width`, `max_width`. Width is the longest line, measured in Unicode
characters; line count uses Python `splitlines()`. `equals` retains whitespace
and the terminal newline. Every string in `contains` must occur literally.

List constraints: `literal_type: "list"`, `min_items`, `max_items`,
`item_type: "string" | "number" | "record"`, `unique: true`, and
`sorted: "ascending" | "descending"`. Parsing uses `ast.literal_eval`.
Numbers exclude booleans and nonfinite floats. A `record` must be a list of
exactly two elements: a string name and a finite numeric value. Uniqueness and
sorting require a declared scalar item type; combining either with `record`
fails validation. Unsupported fields, contradictory bounds, empty
contracts and duplicate request aliases fail configuration validation.

Doom control states keep their episode verification in `nettadoom.py`.

## Core integration

The caller returns its ordinary `selection` plus either a matched `task` profile
or an explicit `no_match`. In the `ask` loop, immediately after `model.game(...)`:

```python
record["task_check"] = check_task_output(call, record)
task_statuses[record["task_check"]["status"]] += 1
task_passed += int(record["task_check"]["passed"])
```

For a matched profile, export only candidates whose `productive` flag and
`task_check.passed` are both true. Preserve the raw attempt budget and every
candidate's receipt. Include the profile, `task_statuses` and `task_passed` in the
summary. If a matched profile produces zero passing candidates, return exit 3.
For an unmatched request report `task_status = "no_match"` explicitly.

`check_task_output` requires successful runtime evidence, matching source hashes
and productivity admission. It returns `runtime_failed`, `invalid_receipt`,
`ineligible`, `failed`, `passed`, or `no_match`. Each evaluated constraint carries
its expected value, observed value and pass flag. The receipt also binds the
source hash and output hash. The check leaves generated source and saved
experience untouched.

## Verification

`tests/test_task_output.py` covers passing contracts, successful executions with
wrong outputs, failed execution, excluded source admission, mismatched source
hashes, unsafe literal syntax, configuration errors and unmatched commands.
`results/caller_v3_checks.json` records separately executed verification fixtures
with their runtime and task receipts. The added table cases, including rejected
boolean values, are retained in `results/caller_v3_table_checks.json` together
with reruns of the original fixtures.

```sh
python3 tests/test_task_output.py --receipts results/caller_v3_table_checks.json
```

These are fixed verification programs passed through the production game and
runtime path. The fixture label is retained in every receipt.
