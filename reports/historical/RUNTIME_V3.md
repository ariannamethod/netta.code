# Runtime v3: localized CPython feedback

The judge still executes the original source. It never inserts indentation, repairs syntax, rewrites expressions, or adds an observation prefix. `source_hash` remains the SHA-256 of the exact UTF-8 source submitted to `judge` or `judge_batch`.

## Exception diagnostics

Generated-source exceptions now include these top-level fields alongside the existing `status`, `accepted`, `reason`, output, and metrics:

| Field | Meaning |
| --- | --- |
| `exception_type` | Exact exception class name, including `IndentationError`, `TabError`, `SyntaxError`, `NameError`, or `ZeroDivisionError`. |
| `error_line` | One-based starting source line. |
| `error_column` | Zero-based UTF-8 byte column. |
| `error_end_line` | One-based ending source line. |
| `error_end_column` | Exclusive zero-based UTF-8 byte column on the ending line. |
| `syntax_offset` | Syntax exceptions only: CPython's original one-based character offset. |
| `syntax_end_offset` | Syntax exceptions only: CPython's original ending character offset. |

Unavailable CPython positions remain `null`. Syntax exceptions keep status `syntax_error`, including its indentation and tab subclasses. Runtime exceptions keep status `runtime_error`; resource and instruction exceptions keep their existing `limit` status. An accepted execution has no fabricated exception fields.

Runtime positions come from the innermost traceback frame belonging to the generated source and its exact instruction position, including inline-cache instructions. Thus a failure inside a called function identifies the failing expression in its body rather than the caller's line. Byte columns align with the AST, instruction-span metrics, and byte-based learned source units even when an earlier identifier or string contains non-ASCII characters.

`judge_batch` preserves the same diagnostics as individual execution, with fresh candidate namespaces for each control observation. Existing Doom observation and action contracts are unchanged.

## Scoped no-op correction

Subscript writes now use the same before/after observation already used for mutating methods. For example, `x=[1]; x[0]=x[0]` and `x={'a':1}; x['a']=x['a']` produce no computation credit; `x=[1]; x[0]=x[0]+1` changes retained data and does. The unchanged write's target span appears in `noop_mutation_spans` using its existing `(line, end_line, column, end_column)` convention. No-op method behavior remains unchanged.

## Verification

The runtime suite contains 31 tests. New cases compare parser diagnostics against direct CPython compilation, distinguish missing indentation, inconsistent dedentation, and mixed tabs/spaces, prove that a mixed-indentation program is rejected while a separately supplied normalized program succeeds, inspect the exact failing expression of a nested function, check UTF-8 byte columns, check missing-name and compile-stage errors, compare batch versus individual diagnostics, and reject unchanged subscript writes.

Before assembly, run:

```sh
NETTA_RUNTIME_TEST_MODULE=runtime_part.py python -m unittest discover -s tests -p test_runtime.py
```

After assembly, the default test target is `nettalee.py`; set `NETTA_RUNTIME_TEST_MODULE=nettacode.py` to verify the other standalone build.
