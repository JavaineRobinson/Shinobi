# What's left to do

See the project board for the full plan. Tick these off as you go.

## Fix in the existing code
- [ ] Program must start with `Name = ` followed by a 5-tuple (brief requirement) — parser + AST + semantic
- [ ] Support the second (one-line) 5-tuple format, e.g. `M = ({q0,q1}, {a,b}, JUTSU, q0, {q1});`
- [ ] Reject epsilon (`ε`, `eps`, `epsilon`) with a clear error
- [ ] Optional: `JUTSU = CLAN x CHAKRA -> CLAN;` signature line + use-before-definition check
- [ ] Decide: may a name be both a state and a symbol? Make code and report agree
- [ ] Decide: allow empty accept set `AWAKENED = {};`?
- [ ] Lexer: show the bad character in errors; give `LexicalError` `.line` / `.column`
- [ ] EOF errors should point just past the last token
- [ ] Add `lex_*` and `syn_*` fixtures (bad char, missing `;`, unmatched brackets, missing `->`, missing name)

## Still to build
- [ ] `render.py`: validated DFA -> Graphviz DOT -> SVG
- [ ] `compile(source)` driver that runs every stage and returns a structured result
- [ ] IDE / web UI (editor, Compile button, tokens/AST/errors/diagram tabs, error highlighting, test-a-string)
- [ ] Optional LLM “explain this DFA” button
- [ ] Cloud deployment (bonus)
- [ ] Group report + 10–15 min presentation
