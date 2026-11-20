# Shinobi — a DFA formal description language

UTech CIT4004 Analysis of Programming Languages, Semester 1 2026/2027 group project.
Group: Lashawn Green (2305250), Kimberly Bruce (1909007), Javaine Robinson (2304749).

Shinobi lets you describe a deterministic finite automaton (DFA), checks it for
lexical, syntax and semantic errors, and (once the rendering stage is built)
draws its state diagram.

```shinobi
CLAN     = {q0, q1};                          # Q  – states
CHAKRA   = {a, b};                            # Σ  – alphabet
JUTSU    = { (q0, a) -> q1, (q0, b) -> q0,    # δ  – transitions
             (q1, a) -> q0, (q1, b) -> q1 };
ORIGIN   = q0;                                # q₀ – start state
AWAKENED = {q0};                              # F  – accept states
```

## Project layout

```
shinobi-dfa/
├── src/shinobi/          # the compiler (installable Python package)
│   ├── lexer.py          # stage 1: lexical analysis   -> tokens
│   ├── parser.py         # stage 2: syntax analysis    -> AST
│   ├── semantic.py       # stage 3: semantic analysis  -> validated DFA (+ simulate)
│   └── __main__.py       # `python -m shinobi file.shinobi [input]`
├── tests/                # pytest suite
│   └── fixtures/         # .shinobi test programs (valid_*, sem_*, lex_*, syn_*)
├── examples/             # sample programs to try
├── docs/
│   ├── brief/            # assignment brief (v6)
│   ├── reports/          # report drafts
│   ├── reference/        # AST example, original sugar_check.py
│   └── TODO.md           # what's left / what needs fixing
├── pyproject.toml
└── requirements-dev.txt
```

## Setup (macOS, once)

```bash
cd ~/Documents/VsCode_Projects/APL/shinobi-dfa
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Then open the folder in VS Code (`code .`) and pick the `.venv` interpreter if asked.

## Usage

```bash
python -m shinobi examples/brief_example.shinobi        # check a program
python -m shinobi examples/brief_example.shinobi aa     # ...and run an input string
shinobi examples/language.shinobi                       # same, via the installed command
python -m shinobi.lexer  examples/language.shinobi      # tokens only
python -m shinobi.parser examples/language.shinobi      # AST only
```

In VS Code: open a `.shinobi` file and press **F5** (“Shinobi: compile current .shinobi file”).

## Tests

```bash
pytest            # or use the Testing panel in VS Code
```

Fixture naming: `valid_*` must pass every stage, `sem_*` must parse but fail semantic
analysis, `lex_*` must fail in the lexer, `syn_*` must fail in the parser.
