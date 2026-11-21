# Shinobi DFA — Remaining Tasks

Put your name next to a task before you start it, and work on a branch named after
the task ID (e.g. `t01-program-header`). Open a pull request when "Done when" is true
and `pytest` passes.

✅ = done (Nov 20). Rendering, pipeline and web IDE (T12–T14) built by Lashawn; name-clash rule (T05) by Kimberly. Roles (from the brief's grading table, group of 3):
- **Lexer/Grammar** = Member 1 · **Parser** = Member 2 · **Semantic** = Member 3 (Kimberly)
- **Shared** = all three (rendering, IDE, report, presentation = 40% shared grade)

> ⚠️ **T00 — Confirm the deadline first.** The brief says "week of November 5". Someone email Mr. White today about an extension.

## A. Fix the language (critical path)

| ID | Task | Role | Needs | Done when |
|----|------|------|-------|-----------|
| ~~T01~~ ✅ | Program shape `M = { declarations };` (team decision); add `name` to the AST | Parser | – | All fixtures updated with a header; missing header gives a syntax error |
| ~~T02~~ ✅ | One-line 5-tuple format: `M = ({q0,q1}, {a,b}, JUTSU, q0, {q1});` + JUTSU block | Parser | T01 | Both formats give the same AST |
| ~~T03~~ ✅ | Reject epsilon (`ε`, `eps`, `epsilon`) with a clear message | Lexer/Grammar + Semantic | – | "epsilon is not allowed in a DFA" error with line:col |
| T04 | *(Optional, probably drop)* δ signature line `JUTSU = CLAN x CHAKRA -> CLAN;` | Parser + Semantic | T01 | Signature before CLAN/CHAKRA gives a semantic error |
| ~~T05~~ ✅ | Decide whether a name can be both a state and a symbol; make code and report agree | Semantic | – | Code and report say the same thing |
| ~~T06~~ ✅ | Decide whether `AWAKENED = {};` (empty F) is allowed; implement or justify | Parser | – | Test + one line in report |
| ~~T07~~ ✅ | Lexer errors: show the bad character, give `LexicalError` `.line`/`.column`, EOF errors point past last token | Lexer/Grammar | – | Error reads e.g. `1:24: unexpected character '@'` |
| ~~T08~~ ✅ | Update `analyze()` and `build_dfa()` for the new AST (name, inline tuple) | Semantic | T01, T02 | All semantic tests pass on both formats |

## B. Tests

| ID | Task | Role | Needs | Done when |
|----|------|------|-------|-----------|
| ~~T09~~ ✅ | `lex_*` fixtures: bad character, ε | Lexer/Grammar | T03, T07 | ≥3 lex fixtures pass |
| ~~T10~~ ✅ | `syn_*` fixtures: missing `;`, unmatched/misnested brackets, missing `->`, missing header | Parser | T01 | ≥5 syntax fixtures pass |
| ~~T11~~ ✅ | Fixtures for new semantic rules (epsilon, name clash) | Semantic | T03–T05 | Tests pass |

## C. Build the back end (shared)

| ID | Task | Role | Needs | Done when |
|----|------|------|-------|-----------|
| ~~T12~~ ✅ | `compile(source)` driver in `src/shinobi/compiler.py`: runs all stages, returns `{tokens, ast, errors:[{stage,line,column,message}], dfa}` | Shared | – | One call used by CLI and UI |
| ~~T13~~ ✅ | `render.py`: DFA → Graphviz DOT → SVG (double circle = accept, arrow into start, merged edge labels `a,b`) | Shared | T12 | Brief example renders like the brief's diagram |
| ~~T14~~ ✅ | IDE / web UI (Flask or Streamlit): editor, Compile button, tokens/AST/errors/diagram tabs, error-line highlighting, test-a-string box | Shared | T12, T13 | Whole pipeline usable in one page |
| T15 | *(Optional)* LLM "Explain this DFA" button | Shared | T14 | Returns plain-English description of the language accepted |
| T16 | *(Bonus)* Deploy to Azure App Service / Render / Streamlit Cloud | Shared | T14 | Public URL works |

## D. Report & presentation

| ID | Task | Role | Needs | Done when |
|----|------|------|-------|-----------|
| T17 | Grammar section of the report: start from `docs/grammar.md`, then explain the lexer and lexical errors | Lexer/Grammar | T01–T03 | Section drafted |
| T18 | Parsing method, syntactic sugar vs feature multiplicity, syntax error detection/reporting | Parser | T01, T02 | Section drafted |
| T19 | Update semantic section (header, epsilon, name clash) + IDE error screenshot. Report examples use `M = { … };` already. Add: epsilon errors, one-line format, `sem_target_undeclared`, `sem_duplicate_symbol` | Semantic | T08, T14 | Section updated |
| T20 | Shared sections: design rationale & theme, comparison with Python/Java/C/SQL, good-language characteristics, rendering & IDE (screenshots), deployment, AI-use statement | Shared | T13, T14 | Sections drafted |
| T21 | Merge report, format, proofread | Shared | T17–T20 | Final PDF |
| T22 | 10–15 min slides (all 3 speak) + live demo script; rehearse once | Shared | T14 | Rehearsed |
| T23 | Submit: report, clean source zip (no `.venv`, `.DS_Store`), app link; peer evaluations | Shared | all | Uploaded to portal |
