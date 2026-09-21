```
███╗   ██╗ ███████╗ ████████╗ ████████╗  █████╗       ██████╗  ██████╗  ██████╗  ███████╗
████╗  ██║ ██╔════╝ ╚══██╔══╝ ╚══██╔══╝ ██╔══██╗     ██╔════╝ ██╔═══██╗ ██╔══██╗ ██╔════╝
██╔██╗ ██║ █████╗      ██║       ██║    ███████║     ██║      ██║   ██║ ██║  ██║ █████╗  
██║╚██╗██║ ██╔══╝      ██║       ██║    ██╔══██║     ██║      ██║   ██║ ██║  ██║ ██╔══╝  
██║ ╚████║ ███████╗    ██║       ██║    ██║  ██║ ██╗ ╚██████╗ ╚██████╔╝ ██████╔╝ ███████╗
╚═╝  ╚═══╝ ╚══════╝    ╚═╝       ╚═╝    ╚═╝  ╚═╝ ╚═╝  ╚═════╝  ╚═════╝  ╚═════╝  ╚══════╝
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

**Netta Lee** lives differently. Each specialization has its own island and its own saved life: art, strings, records, 2048, Doom and whatever comes next. A small caller named `select_state()` reads ordinary language, weighs declared lexical evidence and wakes the state whose experience belongs to the request, so she can spend one life learning one family of movements instead of asking one memory to vaguely contain every craft at once.

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

`nettalee.py` is the specialist body. Her published lives now cover **art**, **strings**, **records**, **2048** and **Doom**, with each island keeping its own corpus, acquired continuation memory and saved state.

The caller configuration lives in `tools.json`. Each route declares words, phrases and examples associated with a specialization; `select_state()` ranks that evidence, abstains when the signal is weak or competing, and returns the saved life that belongs to the request. The same file now routes the mixed Netta Code state too, so one ordinary-language front door can choose between a specialist island, the mixed coding body and the two game environments.

Declared commands add another layer of experience. `ask --learn-task --save SNAPSHOT` gives a matched command its own **545-parameter outcome head** and continuation credit, and actual execution decides what that memory reinforces. The TXT islands stay code-only; the command is not smuggled into the corpus as a prompt/answer lesson. A normal `ask` keeps the saved state frozen and simply uses what was already acquired.

A request for a compact drawing wakes the art life, a request for sorted records wakes another, `play 2048` routes into a policy world, and Doom wakes something with worse manners. The caller opens the right door and gets out of the way while the coding behavior comes from the experience behind it.

This is where the Bruce Lee joke stops being decoration and turns into architecture: separate lives let one state spend thousands of games inside one family of movements while another life learns an entirely different environment. Bruce Lee probably meant martial arts, but this repository saved the dojo to JSON and kept going.

---

## Netta Code

`nettacode.py` keeps the same general organism while living in `corpora/mixed.txt`, where different program families share one world. Its default continuation context is shorter and its corridor escape is more frequent, giving heterogeneous structures more room to meet inside a single experience.

The two bodies therefore ask different questions with almost the same anatomy. Netta Lee asks what deep local experience becomes when each domain keeps its own life, while Netta Code asks what happens when executable habits from different domains are allowed to occupy the same memory and collide.

One practices the same kick ten thousand times. The other has wandered into several dojos and is taking notes.

Netta Code can also acquire declared task memory through the same execution loop. In the current mixed state, the numeric-list command became a particularly sharp example: the same general island learned a narrow executable demand without being rebuilt into a separate language model or given a TASK → CODE corpus.

---

## what experience changed

The first free-play courts established that accumulated experience changes productive generation. The current pass pushes the same idea into declared executable tasks: three independent runs per command, **512 learning attempts** followed by **256 fresh evaluation attempts** each. “Memory erased” keeps the rest of the same saved organism and removes only the acquired task memory.

| organism / command | task memory | task memory erased | ordinary training |
|---|---:|---:|---:|
| Netta Lee — compact art | **427 / 768** | 308 / 768 | 343 / 768 |
| Netta Lee — records table | **250 / 768** | 80 / 768 | 65 / 768 |
| Netta Code — sorted numeric values | **407 / 768** | 8 / 768 | 5 / 768 |
| Netta Code — table | 3 / 768 | 0 / 768 | 0 / 768 |

The Code numeric task is the cleanest current example of command-shaped experience: 407 completed evaluations with task memory against 8 after removing that memory from the same checkpoints. The separate table task barely moved at all and was not promoted, which is useful because the court gets to keep saying no even when another command has just produced a spectacular number.

The earlier free-play result still matters underneath this layer: experience had already raised productive execution strongly across art, strings, records and the mixed Code island. The newer mechanism narrows that pressure toward a declared result while leaving ordinary no-task trajectories unchanged.

The shared release suite now passes **166 tests**. Technical changes and measured runs live in [NETTALEELOG.md](NETTALEELOG.md) and [NETTACODELOG.md](NETTACODELOG.md); the README follows the current organisms while Astra keeps the receipts in the logs.

---

## a small gallery of consequences

The gallery has become the public window into what the code actually did. It keeps selected art outputs beside their exact generated Python and SHA-256, the current task-comparison table, an interactive move-by-move 2048 episode and a real Doom combat frame produced while a generated Netta Lee policy was driving the game.

A few exact art stdout examples remain pleasantly unnecessary:

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

The complete selected set lives in **[gallery.html](gallery.html)**. ASCII art was supposed to be the harmless demonstration island; it is now sharing a gallery with Doom and a 2048 trajectory because scope control went very well.

---

## 2048

`netta2048.py` is a standard-library game host built around **64 code-only policies in eight families**. A generated program receives the real sixteen-cell board together with four legal-move flags and chooses `left`, `right`, `up` or `down`; board transitions, spawning, score and reward belong to the host, so the organism has to live with the move its own code selected.

After **800 raw learning attempts**, the saved state produced **156 played episodes out of 256 fresh generation attempts**, compared with **13 / 256** after removing learned experience. Score per raw attempt rose from **41.17** to **589.59**. Uniform random legal play scored **949.42**, which gives the next court a wonderfully impolite baseline to chase rather than a victory lap.

The selected fixed-evaluation episode in the gallery reached **1,348 points** and a **128 tile**. Its generated policy is shown beside the complete real trajectory, and independent accounting reconciled all **96,029 recorded transitions** from training and evaluation.

The game is useful for the same reason the compiler is useful: it does not care how persuasive the code looks. The board moves or it does not.

---

## Doom

The Doom body is now `nettadoomer.py`, with `nettadoom.py` kept as the compatible entry point. The default path uses a pinned, locally buildable **Doom Generic** engine from `doom/` and an external IWAD; the published run used **Freedoom 2, MAP02**.

A generated policy receives a compact observation of health, ammunition and scene position, then chooses among six actions:

```
turn_left
turn_right
move_forward
strafe_left
strafe_right
shoot
```

Before play, the exact generated source is executed across the compact observation space and turned into the action table that the game will actually use. The environment then returns combat consequences through Netta's `observe()` path, with kills, damage and ammunition expenditure entering the episode reward.

The first real Doom pass used **24 generation attempts**. Twelve reached the game, representing **11 distinct generated programs** and **24 actual episodes**; the engine's total killcount was **88**, including monster infighting counted by Doom itself. A later frozen paired check over 16 shared generation/game seeds produced 11 played attempts with learned experience and 9 from the initial state, with a mean reward difference of **+0.0921** and bootstrap 95% interval **[-0.1267, 0.3128]**.

One archived generated policy was replayed with the same engine seed and reproduced the trajectory and PNG hashes exactly. Saved Doom experience binds the backend, IWAD hash, map and difficulty to the state, because a life acquired in one Hell should at least remember which Hell it was.

The combat frame and exact Python policy are in **[gallery.html](gallery.html)**. WOLFE learned to play Doom by choosing functions; Netta Lee now writes the policy that chooses among them, which was apparently the calm and proportionate next experiment.

---

## the caller

`select_state()` is the small Wolfe-inspired front door shared by the standalone organisms. It tokenizes an ordinary request, compares it with the declarations in `tools.json`, ranks evidence across the saved states and returns a route when one has earned a clear enough lead. The current table includes Lee specializations, the mixed Code state, 2048 and Doom.

Its job is narrow on purpose: the caller chooses **which experience becomes active** and, when a declared command matches, which task contract is being asked for. Generation, execution and acquisition still belong to the organism that wakes behind that route.

That separation is what makes the design interesting inside larger systems. An upstream LLM can remain a language body, express an ordinary instruction and hand the executable part to a much smaller learned state without having to carry every tool policy inside its own training. WOLFE already showed how far a small neural caller can go when its vocabulary is functions; here the door can lead to a whole saved coding life.

A caller and a specialist walk into a bar. The caller points at the right bottle and leaves; the specialist has been practicing that drink for two thousand games and has somehow returned with Python.

---

## run it

Grow a specialist state from a code island and let it accumulate ordinary experience:

```bash
python3 nettalee.py init --island corpora/art.txt --state states/my-art.json
python3 nettalee.py play --state states/my-art.json --games 100
```

Use the editable caller without changing the saved life:

```bash
python3 nettalee.py ask "draw a compact picture" \
  --tools tools.json --attempts 32 --out out/
```

Acquire a declared command into a new snapshot from actual executed outcomes:

```bash
python3 nettalee.py ask "draw a compact picture" \
  --tools tools.json --attempts 512 --learn-task \
  --save states/my-art-task.json --out runs/art-task
```

Run a frozen 2048 comparison:

```bash
python3 netta2048.py evaluate \
  --state states/2048.json --out runs/2048 \
  --attempts 256
```

Run Doom Generic with your own Doom/Freedoom IWAD:

```bash
python3 nettadoomer.py evaluate \
  --state states/doom.json \
  --iwad /path/to/freedoom2.wad --map 2 \
  --output runs/doom
```

`NETTA_DOOM_IWAD` can supply the IWAD path. The engine source lives in `doom/` and builds locally with `make` and a C compiler; game data stays external.

---

## files

```
nettalee.py        Netta Lee: specialist organism, judge, task memory and select_state()
nettacode.py       Netta Code: mixed-island organism
netta2048.py       seeded 2048 host for generated policies
nettadoomer.py     real Doom Generic / optional ViZDoom bridge
nettadoom.py       compatibility entry point

tools.json         language routes + declared command contracts
doom.json          Doom environment configuration
gallery.html       art, task results, interactive 2048 and Doom evidence

NETTALEELOG.md      Lee technical / experiment log
NETTACODELOG.md     Code technical / experiment log

corpora/
  art.txt
  strings.txt
  records.txt
  mixed.txt
  2048.txt
  doom.txt

states/
  art.json
  strings.json
  records.json
  code.json
  2048.json
  doom.json

doom/
  pinned Doom Generic engine sources + host adapter + build recipe
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
