# Island-productivity baseline — frozen before physics stage 1

Snapped at 4939992..f2deef0 (HEAD f2deef0), CPython 3.14 / darwin, 2026-09-25,
BEFORE any allowlist change to the judge. This is the "before" against which
every physics step (allowlist widening) must be measured: a widening may not
degrade her existing crafts. Second axis (corpus yield) is measured by
tools/admit.py.

Method: `python3 <body>.py sample --state states/<island>.json --attempts 256
--seed 4242` (frozen state, no learning, deterministic). art/records/strings
via nettalee.py; code (mixed) via nettacode.py.

| island  | attempts | accepted | productive | unique_accepted | new_shapes |
|---------|---------:|---------:|-----------:|----------------:|-----------:|
| art     |      256 |       16 |        122 |              15 |         16 |
| code    |      256 |       21 |         78 |              20 |         21 |
| records |      256 |        7 |         52 |               6 |          7 |
| strings |      256 |       23 |         81 |              20 |         23 |

Game islands carry their own productivity measure (played-rate), snapped this
session: 2048 count arm played 587/1024 (score_per_raw 589.21); Doom MAP02
generated-policy kills 4 / reward 0.911. Those are the game-side "before".

Gate for a physics step: re-snap these exact commands after the allowlist
change; accepted/productive per island must not fall (declare tolerance in the
step protocol). Don writes the stage-1 protocol (private `_names` + assert)
against these numbers.

Receipts (sha256):
- art-sample.json     18f9762546650b2b7be4e9078494f793fe90818c14ed79ebb99e8af625627f49
- code-sample.json    4584fde36237fe4c1db2ef8fea6e4287bab8c503e6405b9c3d748a43d94e0c9a
- records-sample.json 40bed4143e99e342f9ba427b1d89ed0c29c1a3823e705f9e9118a1460b4f3db8
- strings-sample.json dc3ab855139247c1e9b483335520bd106930afe7d2bbe0ab9ae79abc7e165f64
