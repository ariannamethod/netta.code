"""Physics stage 2: measure the seven door-arms against the sealed corpus.

Per Don's prereg (reports/measurements/results/physics_stage2_doors/PROTOCOL.md).
The judge in main is NEVER edited: each arm builds a patched COPY of nettalee.py
and nettacode.py in a scratch dir, and axis B runs admit against that variant.

Doors:
  priv : Assert in _ALLOWED_AST; name gate '_' -> '__' (dunder msg); FunctionDef
         gate split so decorator refusal keeps its name. (stage-1 hunks verbatim)
  name : single dunder __name__ allowed in Load only; namespace gains
         __name__ = '__main__'. Store/Del of __name__ stay refused.
  exc  : Try/ExceptHandler/Raise in _ALLOWED_AST; the eight clean exception
         types enter the call gate and the namespace. No SystemExit, no I/O type.

Usage: python3 tools/measure_doors.py CORPUS_DIR OUT_DIR
"""
import ast, hashlib, importlib.util, json, sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAP = 8192
EXC = ('ValueError', 'TypeError', 'KeyError', 'IndexError', 'ZeroDivisionError',
       'ArithmeticError', 'AssertionError', 'Exception')

# --- anchors (identical in both bodies; asserted present before patching) ---
AST_ANCHOR = 'Continue Pass FunctionDef arguments arg '
NAME_GATE = ("            if name.startswith('_'):\n"
             "                raise RuntimePolicyError('private names unavailable')\n")
FUNC_GATE = ("            if node.name.startswith('_') or node.decorator_list:\n"
             "                raise RuntimePolicyError('private functions/decorators unavailable')\n")
NS_ANCHOR = "    namespace = {'__builtins__': safe}\n"
CALL_ANCHOR = "                if node.func.id not in set(_SAFE_FUNCTIONS) | {'print'} | functions:\n"
SAFE_ANCHOR = "    safe['print'] = bounded_print\n"


def door_patch(text, doors):
    """Return the judge source with exactly the requested doors opened."""
    for anchor in (AST_ANCHOR, NAME_GATE, FUNC_GATE, NS_ANCHOR, CALL_ANCHOR, SAFE_ANCHOR):
        if text.count(anchor) != 1:
            raise SystemExit('anchor not unique/found: %r' % anchor[:40])
    # _ALLOWED_AST additions
    extra = []
    if 'priv' in doors:
        extra.append('Assert')
    if 'exc' in doors:
        extra += ['Try', 'ExceptHandler', 'Raise']
    if extra:
        text = text.replace(AST_ANCHOR, 'Continue Pass ' + ' '.join(extra) + ' FunctionDef arguments arg ')
    # name gate
    base = '__' if 'priv' in doors else '_'
    msg = 'dunder names unavailable' if 'priv' in doors else 'private names unavailable'
    if 'name' in doors:
        cond = ("name.startswith('%s') and not (name == '__name__' and "
                "isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load))" % base)
    else:
        cond = "name.startswith('%s')" % base
    text = text.replace(NAME_GATE,
                        "            if %s:\n"
                        "                raise RuntimePolicyError('%s')\n" % (cond, msg))
    # FunctionDef gate: split only under priv (to preserve decorator attribution)
    if 'priv' in doors:
        text = text.replace(FUNC_GATE,
                            "            if node.name.startswith('__'):\n"
                            "                raise RuntimePolicyError('dunder names unavailable')\n"
                            "            if node.decorator_list:\n"
                            "                raise RuntimePolicyError('private functions/decorators unavailable')\n")
    # name door: inject __name__ into namespace
    if 'name' in doors:
        text = text.replace(NS_ANCHOR, "    namespace = {'__builtins__': safe, '__name__': '__main__'}\n")
    # exc door: exception types into call gate and namespace
    if 'exc' in doors:
        exc_set = '{' + ', '.join(repr(e) for e in EXC) + '}'
        text = text.replace(CALL_ANCHOR,
                            "                if node.func.id not in set(_SAFE_FUNCTIONS) | {'print'} | functions | %s:\n" % exc_set)
        inject = SAFE_ANCHOR + ''.join("    safe[%r] = getattr(builtins, %r)\n" % (e, e) for e in EXC)
        text = text.replace(SAFE_ANCHOR, inject)
    return text


def load_variant(doors, scratch):
    """Write patched twin copies; return the nettalee variant path + twin check."""
    tag = '_'.join(sorted(doors)) or 'none'
    orig, vpath = {}, {}
    for body in ('nettalee', 'nettacode'):
        orig[body] = (ROOT / (body + '.py')).read_text()
        p = scratch / ('%s__%s.py' % (body, tag))
        p.write_text(door_patch(orig[body], doors))
        vpath[body] = p

    def changed(orig_src, patched_src):
        base = set(orig_src.splitlines())
        return [l for l in patched_src.splitlines() if l not in base]

    lee_diff = changed(orig['nettalee'], vpath['nettalee'].read_text())
    code_diff = changed(orig['nettacode'], vpath['nettacode'].read_text())
    return vpath['nettalee'], lee_diff == code_diff, lee_diff


def _import(path):
    spec = importlib.util.spec_from_file_location('judge_' + path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def admit_yield(judge_mod, files):
    accepted, seen, counts = 0, set(), {}
    for path in files:
        src = path.read_text(errors='replace')
        if len(src.encode()) > CAP:
            counts['over_cap'] = counts.get('over_cap', 0) + 1
            continue
        if not src.strip():
            counts['empty'] = counts.get('empty', 0) + 1
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError:
            counts['syntax_error'] = counts.get('syntax_error', 0) + 1
            continue
        if any(isinstance(n, (ast.Import, ast.ImportFrom)) for n in ast.walk(tree)):
            counts['has_import'] = counts.get('has_import', 0) + 1
            continue
        r = judge_mod.judge(src, mode='general')
        if r.get('accepted'):
            key = judge_mod.program_key(src)
            if key in seen:
                counts['duplicate'] = counts.get('duplicate', 0) + 1
                continue
            seen.add(key)
            accepted += 1
            counts['accepted'] = counts.get('accepted', 0) + 1
        else:
            counts[r.get('status', 'rejected')] = counts.get(r.get('status', 'rejected'), 0) + 1
    return accepted, counts


def main():
    corpus, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    scratch = out / 'variants'; scratch.mkdir(exist_ok=True)
    files = sorted(corpus.rglob('*.py'))
    doors_all = ('name', 'exc', 'priv')
    arms = []
    for r in range(1, 4):
        arms += [frozenset(c) for c in combinations(doors_all, r)]
    results = {}
    for arm in arms:
        tag = '_'.join(sorted(arm))
        leath, twin_ok, hunks = load_variant(arm, scratch)
        mod = _import(leath)
        acc, counts = admit_yield(mod, files)
        results[tag] = {'yield': acc, 'twin_ok': twin_ok, 'counts': counts}
        print(json.dumps({'arm': tag, 'yield': acc, 'twin_ok': twin_ok, 'counts': counts}))
    (out / 'arms.json').write_text(json.dumps(results, indent=2))
    print('DOORS_DONE')


if __name__ == '__main__':
    main()
