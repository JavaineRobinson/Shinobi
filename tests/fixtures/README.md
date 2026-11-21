# Test programs

The file name prefix says what each program must produce:

| Prefix | Must... | Checked by |
|---|---|---|
| `valid_*` | pass every stage and be drawn | `test_syntax.py`, `test_semantic.py`, `test_render.py` |
| `lex_*` | fail in the lexer | `test_syntax.py` |
| `syn_*` | lex fine, fail in the parser | `test_syntax.py` |
| `sem_*` | parse fine, fail semantic analysis with a specific message | `test_semantic.py` |

## Valid
- `valid_example`, `valid_brief_example` (the brief's DFA, with a Trap state)
- `valid_02_numeric_symbols` (alphabet {0, 1}), `valid_03_comments_and_trap`
- `valid_04_sugar`: `AWAKENED = q1;` (shorthand for `{q1}`)
- `valid_05_empty_awakened`: `AWAKENED = {};` (no accept states, every input rejected)
- `valid_06_one_line_format`: the brief's DFA as `M = ({…}, {…}, JUTSU, q1, {q4});`

## Lexical errors
- `lex_01_illegal_char` (`@`), `lex_02_unicode_arrow` (`→` instead of `->`)

## Syntax errors
- `syn_01`–`syn_13`: punctuation, brackets, empty/trailing lists, keyword as a state, set given for ORIGIN
- `syn_14_missing_name`, `syn_15_missing_equals_after_name`, `syn_16_missing_open_brace`,
  `syn_17_missing_close_brace`, `syn_18_missing_final_semicolon`, `syn_12_stray_token_after_end`
- `syn_19_old_format_without_name`: the old format (no `M = { … };`) is rejected
- `syn_20_empty_program_body`, `syn_21_empty_jutsu`
- `syn_22`–`syn_24`: one-line format mistakes (extra declaration, missing JUTSU block, missing JUTSU slot)

## Semantic errors
Kimberly's report quotes the line:column of the named files below, so keep their line numbers stable.
- Declarations: `sem_duplicate_clan`, `sem_missing_origin`, `sem_wrong_order`
- Names: `sem_duplicate_state`, `sem_duplicate_symbol`, `sem_12_state_symbol_clash`
- References: `sem_origin_undeclared`, `sem_awakened_undeclared`, `sem_symbol_undeclared`, `sem_target_undeclared`
- Determinism and totality: `sem_conflicting_transition`, `sem_repeated_transition`, `sem_missing_transition`
- Epsilon: `sem_epsilon_symbol`, `sem_epsilon_transition`
