"""Corpus admission: a candidate enters the island only if her own court accepts it.

Law (Don, brief supplement 2026-09-25): every candidate runs the same pipeline
as her generated code — <=8192 bytes, stdlib-only by the judge's AST policy,
self-contained, and judge() must accept it. The island is not a dataset we
approved; it is a world that passed the same court as her own speech.

Usage:
    python3 tools/admit.py SRC_DIR --license LICENSE --family FAMILY \
        --out-island OUT.txt --out-manifest OUT.jsonl [--separator '# === PROGRAM ==='] [--timeout 1.5]

Writes accepted programs to OUT.txt (separator-joined) and one manifest row per
candidate to OUT.jsonl. Dedup is by program_key; the first accepted wins.
Run one source family at a time; balance families when assembling the island.
"""
import argparse, ast, hashlib, json, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import nettalee as core  # judge(), program_key(), RUNTIME_SOURCE_LIMIT

CAP = 8192  # Organism per-program byte limit (nettalee.py: Organism.__init__)


def sha256(text):
    return hashlib.sha256(text.encode()).hexdigest()


def admit_one(source, timeout):
    """Return (ok, status, key). ok True only if the court accepts it."""
    if len(source.encode()) > CAP:
        return False, "over_cap", None
    if not source.strip():
        return False, "empty", None
    # Fast reject: her court rejects any import outright, so skip the judge on
    # anything that carries one (saves a subprocess per import-based file).
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False, "syntax_error", None
    if any(isinstance(n, (ast.Import, ast.ImportFrom)) for n in ast.walk(tree)):
        return False, "has_import", None
    r = core.judge(source, timeout=timeout, mode="general")
    if not r.get("accepted"):
        return False, r.get("status", "rejected"), None
    return True, "accepted", core.program_key(source)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src_dir")
    ap.add_argument("--license", required=True)
    ap.add_argument("--family", required=True)
    ap.add_argument("--out-island", required=True)
    ap.add_argument("--out-manifest", required=True)
    ap.add_argument("--separator", default="# === PROGRAM ===")
    ap.add_argument("--timeout", type=float, default=1.5)
    ap.add_argument("--limit", type=int, default=0, help="cap candidates scanned (0 = all)")
    args = ap.parse_args()

    files = sorted(Path(args.src_dir).rglob("*.py"))
    if args.limit:
        files = files[: args.limit]

    accepted, seen_keys = [], set()
    counts = {"accepted": 0, "over_cap": 0, "empty": 0, "has_import": 0,
              "syntax_error": 0, "duplicate": 0, "other": 0}
    with open(args.out_manifest, "w") as mf:
        for path in files:
            try:
                source = path.read_text(errors="replace")
            except Exception as exc:
                counts["other"] += 1
                mf.write(json.dumps({"path": str(path), "status": "read_error",
                                     "reason": str(exc)[:120]}) + "\n")
                continue
            ok, status, key = admit_one(source, args.timeout)
            row = {"path": str(path.relative_to(args.src_dir)), "bytes": len(source.encode()),
                   "sha256": sha256(source), "license": args.license, "family": args.family,
                   "status": status}
            if ok and key in seen_keys:
                ok, status, row["status"] = False, "duplicate", "duplicate"
            if ok:
                row["program_key"] = key
                seen_keys.add(key)
                accepted.append(source)
                counts["accepted"] += 1
            else:
                counts[status if status in counts else "other"] += 1
            mf.write(json.dumps(row) + "\n")

    island = ("\n" + args.separator + "\n").join(accepted)
    Path(args.out_island).write_text(island)
    summary = {"family": args.family, "license": args.license, "scanned": len(files),
               "accepted": len(accepted), "island_bytes": len(island.encode()),
               "counts": counts, "island_sha256": sha256(island)}
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
