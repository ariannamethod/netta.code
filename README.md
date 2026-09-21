```
 _ __   ___| |_| |_ __ _   ___ ___   __| | ___
| '_ \\ / _ \\ __| __/ _` | / __/ _ \\ / _` |/ _ \\
| | | |  __/ |_| || (_| || (_| (_) | (_| |  __/
|_| |_|\\___|\\__|\\__\\__,_(_)___\\___/ \\__,_|\\___|
```

# netta.code

*it plays. it acts. it codes.*

> “I fear not the man who has practiced 10,000 kicks once, but I fear the man who has practiced one kick 10,000 times.”
> — Bruce Lee

---

## THESIS

A coding model can begin with agency already inside the architecture. Give it a world made of executable programs, let it grow structure from what it has actually lived, make every generated attempt run, and let the consequences of execution alter what it will try next; the result is a small coding agent whose education happens by playing with code, while language can remain an interface rather than the place where agency has to be manufactured afterward.

That is the experiment in **netta.code**. Programs are the habitat, CPython is part of the environment, and experience survives the game. A candidate can compile, fail, execute, produce something useful, repeat old behavior, discover a new behavior or find a loophole in the court and embarrass everybody involved, and each of those outcomes can become part of the next move.

The repository contains two organisms built around the same idea.

**Netta Code** lives in a mixed island where different kinds of programs occupy the same world, so unrelated structures can collide and recombine inside one acquired experience.

**Netta Lee** lives differently. Each specialization has its own island and its own saved life: art, strings, records, Doom and whatever comes next. A small caller named `select_state()` reads ordinary language, weighs declared lexical evidence and wakes the state whose experience belongs to the request, so she can spend one life learning one family of movements instead of asking one memory to vaguely contain every craft at once.

Bruce Lee probably meant martial arts. The repository chose Python.

The same arrangement can sit inside larger AI systems because the agent loop already exists before another model arrives. A person can address it directly, another program can address it, and an LLM can hand ordinary-language intent to the caller while Netta carries the executable experience, which makes the system an interesting action layer for models whose own job is language rather than the mechanics of every tool they may ever need.

The important part comes first: **agency is the training regime**. She plays, execution answers, experience changes the next play.

---

## the game

An island is a text file containing complete Python programs separated by:

```
# === PROGRAM ===
```

The framing disappears when the island is read; every byte inside each program remains part of the world. From those bytes Netta grows deterministic byte-pair units, builds local continuation tables and begins sampling programs from structures she has actually lived through, with the continuation order and search behavior differing between the two organisms.

Generation is only the opening move. Every candidate is parsed, compiled and executed inside a bounded CPython worker, and the runtime records what actually happened: executed lines and spans, computational operations, retained values, visible output and a behavior signature. The organism then updates acquired continuation memory, learned outcome machinery and its search behavior from the result.

The education loop therefore lives inside the activity itself. Netta does not leave the world, enter a separate classroom, memorize a target answer and return later with a certificate; she keeps playing the same executable environment until the history of what worked begins to bend what she tries.

This is also why the environment can become more interesting without changing the basic idea. A text-processing island, a drawing island, a game controller and a future automation island all present different surfaces, but they share the same essential law: generated code meets consequences.

The main bodies are ordinary Python files. `nettalee.py` and `nettacode.py` each carry their own organism, execution judge and caller; the core runs on the Python standard library, while Doom keeps its optional dependency separate because Hell, apparently, still has packaging requirements.

---

## the court learns too

The first interesting thing an execution-trained organism does after you build a court is discover what the court forgot.

An early novelty rule could be satisfied by taking an old program and attaching dead lines to it. The source looked different, the behavior did not, and Netta quite reasonably accepted the legal advice offered by our own metric. The loophole survived until the generated programs were inspected and the judge was taught to care about execution rather than decorative source acreage.

Novelty is now projected through execution evidence. Dead branches, inert expressions, unused literal stores, uncalled functions and no-op mutations are removed before a candidate receives credit for being new, while whole-source replay, concatenations of known programs and equivalent behavior have their own checks.

She is allowed to search for loopholes. The court is expected to survive meeting her.

This adversarial little relationship is useful because a compiler and a runtime make unusually stubborn teachers. They do not care whether a continuation sounds plausible, and they are unimpressed by confidence. A colon is either where Python needs it or everybody goes home.

---

## Netta Lee

`nettalee.py` is the specialist body. Her published states currently cover **art**, **strings**, **records** and **Doom**, with each island keeping its own corpus and its own saved experience.

The caller configuration lives in `tools.json`. Each state declares words, phrases and examples associated with the specialization; `select_state()` ranks that evidence, abstains when the signal is too weak or competing, and returns the saved state that belongs to the request. Some states also declare output contracts for particular commands, so the same ordinary-language front door can route toward a constrained executable result.

A request for a compact drawing wakes the art life. A request about sorted words wakes the strings life. Doom wakes something with worse manners.

The mechanism is intentionally small. The caller opens the right door and then gets out of the way, while the actual coding behavior comes from the experience stored behind that door.

This is where the Bruce Lee joke stops being decoration and turns into architecture. Separate lives make specialization explicit: one state can spend thousands of games inside drawings, another inside record processing, another inside a control policy, and each gets to keep what happened there without requiring every other state to absorb the same history.

---

## Netta Code

`nettacode.py` keeps the same general organism while living in `corpora/mixed.txt`, where different program families share one world. Its default continuation context is shorter and its corridor escape is more frequent, giving heterogeneous structures more room to meet inside a single experience.

The two bodies therefore ask different questions with almost the same anatomy. Netta Lee asks what deep local experience becomes when each domain keeps its own life, while Netta Code asks what happens when executable habits from different domains are allowed to occupy the same memory and collide.

One practices the same kick ten thousand times. The other has wandered into several dojos and is taking notes.

---

## what experience changed

The first published memories each completed **2,000 games**, followed by **600 fresh frozen attempts** per evaluation. The current measurements compare those lived states with the same organisms after their acquired experience has been removed.

| organism / island | productive with experience | without acquired experience | new behaviors beyond final memory |
|---|---:|---:|---:|
| Netta Lee — art | **271** | 46 | 52 / 32 |
| Netta Lee — strings | **180** | 45 | 39 / 40 |
| Netta Lee — records | **136** | 24 | 13 / 13 |
| Netta Code — mixed | **205** | 19 | 26 / 12 |

The pattern is already useful to watch: acquired experience sharply raises productive execution, while expansion into behavior genuinely new beyond the final memory grows much less uniformly. Netta is becoming better at doing what her life has taught her before she becomes equally better at discovering things her life has never contained, which turns practice-versus-discovery into a concrete pressure inside the next experiments rather than an abstract discussion about exploration.

The shared release suite at this stage passes **123 tests**. Technical changes and measured runs live in [NETTALEELOG.md](NETTALEELOG.md) and [NETTACODELOG.md](NETTACODELOG.md); the README describes the current organisms while the logs keep the trail of what changed underneath them.

---

## a small gallery of consequences

The art island is convenient because its results can be seen without asking a loss curve to develop a personality. After 2,000 games, the fixed 600-attempt evaluation produced 271 productive executions and 153 distinct results, and the selected generated sources were re-executed by independent CPython.

A few exact stdout examples:

```
 .----.
|^    ^|
|  UU  |
 `----`
```

```
+-----------------+ +-----------------+
|       O O       | |       O O       |
|        --       | |       --        |
+-----------------+ +-----------------+
```

```
       /|
      /XX|
     /XXXX|
    /XXXXXX|
   /XXXXXXXX|
  /XXXXXXXXXX|
 /XXXXXXXXXXXX|
/XXXXXXXXXXXXXX|
|              X
|             XXX
|            XXXXX
|           XXXXXXX
|          XXXXXXXXX
|         XXXXXXXXXXX
|        XXXXXXXXXXXXX
```

The selected set, together with the exact Python source and SHA-256 for every shown result, lives in **[gallery.html](gallery.html)**.

ASCII art was meant to be the easy island. It has already developed opinions.

---

## Doom

`nettadoom.py` connects a Netta Lee control island to ViZDoom. A generated policy receives a compact observation containing health, ammunition and a coarse scene description, then chooses among six actions:

```
turn_left
turn_right
move_forward
strafe_left
strafe_right
shoot
```

Before a policy enters the game, its exact generated source is executed over the complete compact observation space. The resulting action table is therefore a finite consequence of that program, and a controller that emits the same action everywhere is rejected as unreactive before Doom ever has to suffer it.

Once admitted, real episodes can return kills, damage and ammunition use through Netta's external `observe()` path, allowing game consequences to become acquisition pressure for later policies.

The bridge and repeated-start machinery are already in the repository. The current log records that the first host used for this release hit engine-startup socket EPERM / SIGSEGV before a real episode completed, so the next Doom run begins exactly where the log leaves it.

WOLFE learned to play Doom by choosing functions. Netta Lee gets to write the policy that chooses among them. Apparently this was the next reasonable step.

---

## the caller

`select_state()` is the small Wolfe-inspired front door to Netta Lee. It tokenizes an ordinary request, compares that request with the declarations in `tools.json`, ranks evidence across the saved states and returns a specialization when one state has earned a clear enough lead.

Its job is deliberately narrower than the organism behind it. The caller chooses **which experience becomes active**; it does not generate the program, execute the program or learn from the result. That separation is what makes the same idea useful as a component inside another system: an upstream LLM can remain good at language, emit an ordinary instruction, and let a much smaller learned execution body handle the specialized action that instruction points toward.

WOLFE solves tool selection by living close to functions. Netta Lee adds another room behind the door: a saved coding life.

A router and a specialist walk into a bar. The router points at the right bottle and leaves. The specialist has been practicing that drink for 2,000 games and for reasons nobody fully understands now writes Python.

---

## run it

Grow a specialist state from an island:

```bash
python3 nettalee.py init \
  --island corpora/art.txt \
  --state states/art.json
```

Let her play and keep the experience:

```bash
python3 nettalee.py play \
  --state states/art.json \
  --games 100
```

Sample from a saved life without adding new experience:

```bash
python3 nettalee.py sample \
  --state states/art.json \
  --attempts 32 \
  --out out/
```

Ask the caller to choose a specialization from ordinary language:

```bash
python3 nettalee.py ask \
  "draw a compact picture" \
  --tools tools.json \
  --attempts 32 \
  --out out/
```

Inspect the accumulated state:

```bash
python3 nettalee.py inspect \
  --state states/art.json
```

Netta Code exposes the same basic surface around its mixed state.

---

## files

```
nettalee.py        Netta Lee: specialist organism, judge and select_state() caller
nettacode.py       Netta Code: mixed-island organism
nettadoom.py       ViZDoom execution bridge

tools.json         declarations used by the caller
doom.json          Doom environment configuration
gallery.html       selected exact art outputs + generated sources

NETTALEELOG.md      Lee technical / experiment log
NETTACODELOG.md     Code technical / experiment log

corpora/
  art.txt
  strings.txt
  records.txt
  doom.txt
  mixed.txt

states/
  art.json
  strings.json
  records.json
  doom.json
  code.json
```

---

## lineage

Netta Code and Netta Lee descend from [Netta](https://github.com/ariannamethod/netta), where learned byte units, lived continuations and acquired experience became parts of one organism rather than isolated stages of a conventional pipeline.

The natural-language caller follows the small-field approach of [WOLFE](https://github.com/ariannamethod/wolfe), whose narrow job is to understand which action ordinary language is pointing toward and to do it without dragging a giant general model into every tiny decision.

The rest happened because executable code turned out to be an unusually honest habitat.

---

## license

GPL-3.0-or-later.

---

*Arianna Method.*
