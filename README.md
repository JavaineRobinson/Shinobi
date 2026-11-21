# Shinobi — a DFA formal description language

UTech CIT4004 Analysis of Programming Languages, Semester 1 2026/2027 group project.
Group: Lashawn Green (2305250), Kimberly Bruce (1909007), Javaine Robinson (2304749).

Shinobi describes a deterministic finite automaton (DFA), checks it for lexical, syntax
and semantic errors, draws its state diagram, and runs input strings through it.

```shinobi
EvenAs = {
    CLAN     = {q0, q1};                          # Q  – states
    CHAKRA   = {a, b};                            # Σ  – alphabet
    JUTSU    = { (q0, a) -> q1, (q0, b) -> q0,    # δ  – transitions
                 (q1, a) -> q0, (q1, b) -> q1 };
    ORIGIN   = q0;                                # q₀ – start state
    AWAKENED = {q0};                              # F  – accept states
};
```

The same DFA on one line, as in the brief's `M = (Q, Σ, δ, q₀, F)` (syntactic sugar for the form above):

```shinobi
EvenAs = ({q0, q1}, {a, b}, JUTSU, q0, {q0});
JUTSU  = { (q0, a) -> q1, (q0, b) -> q0, (q1, a) -> q0, (q1, b) -> q1 };
```

Full grammar: [docs/grammar.md](docs/grammar.md).

## Setup (macOS, once)

```bash
brew install graphviz                       # draws the diagrams
cd ~/Documents/VsCode_Projects/APL/shinobi-dfa
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt         # installs shinobi + flask, graphviz, pytest
```

Open the folder in VS Code (`code .`) and pick the `.venv` interpreter if asked.

## Usage

**Web IDE (Shinobi DFA Studio)** — editor, error highlighting, diagram and a test-a-string box:

```bash
shinobi studio            # then open http://localhost:5000
```

**Command line:**

```bash
shinobi check  examples/even_as.shinobi           # print the DFA, or every error with line:column
shinobi run    examples/brief_example.shinobi aa  # ACCEPTED / REJECTED
shinobi render examples/brief_example.shinobi     # saves out/brief_example.svg (--dot for DOT text)
shinobi tokens examples/even_as.shinobi           # lexical stage only
shinobi ast    examples/even_as.shinobi           # syntax stage only (JSON)
```

Without the venv activated, use `python -m shinobi <command>` with `PYTHONPATH=src`.
Exit codes: `0` valid, `1` errors in the program, `2` bad usage or unreadable file.

**In VS Code:** open a `.shinobi` file → Run and Debug → pick a *Shinobi: …* configuration → F5.

## Project layout

```
shinobi-dfa/
├── src/shinobi/                 the compiler (installable Python package)
│   ├── lexer.py                 stage 1  lexical analysis   source -> tokens
│   ├── parser.py                stage 2  syntax analysis    tokens -> AST
│   ├── semantic.py              stage 3  semantic analysis  AST -> errors / validated DFA, simulate()
│   ├── render.py                stage 4  rendering          DFA -> Graphviz DOT -> SVG
│   ├── pipeline.py              runs all stages, returns one result (used by the CLI and the IDE)
│   ├── cli.py                   the `shinobi` command
│   ├── app.py                   the web IDE (Flask)
│   └── templates/studio.html    the web IDE page
├── tests/                       pytest suite, one file per stage + pipeline, CLI, sugar
│   └── fixtures/                48 test programs (see fixtures/README.md)
├── examples/                    sample programs
├── docs/
│   ├── grammar.md               formal grammar (EBNF), tokens, design decisions, sugar
│   ├── tasks.md                 remaining work, owners, status
│   ├── images/                  diagrams for the report
│   ├── reference/               example AST output
│   ├── reports/                 report drafts (group draft, proposal, Kimberly's semantic section)
│   └── brief/                   assignment brief (not committed)
├── .github/workflows/tests.yml  runs the tests on every push / pull request
├── .vscode/                     interpreter, test and run/debug settings
├── pyproject.toml               package metadata, dependencies, `shinobi` command, pytest config
└── requirements-dev.txt
```

## Tests

```bash
pytest          # or the Testing panel in VS Code
```

Test programs are named by what they must produce: `valid_*` pass every stage,
`lex_*` fail in the lexer, `syn_*` fail in the parser, `sem_*` fail semantic analysis.
Add a new case by dropping a file in `tests/fixtures/` with the right prefix; `sem_*` files
also need their expected message in `tests/test_semantic.py`.

## Working as a team

1. Pick a task in [docs/tasks.md](docs/tasks.md) and put your name on it.
2. `git switch -c t17-grammar-section` (branch named after the task).
3. Commit, `git push -u origin <branch>`, open a pull request.
4. GitHub runs the tests on the pull request; merge when they pass.
