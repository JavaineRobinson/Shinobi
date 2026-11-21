# Shinobi grammar (EBNF)

Notation: ISO/IEC 14977 EBNF. `,` = followed by, `|` = or, `{ }` = zero or more,
`[ ]` = optional, `(* *)` = comment, quoted text = a literal token.

The **syntactic grammar** below is what `src/shinobi/parser.py` implements, one
function per rule. The **lexical grammar** is what `src/shinobi/lexer.py` implements.

## Syntactic grammar

```ebnf
program       = dfa_name , "=" , ( long_form | short_form ) ;
dfa_name      = IDENTIFIER ;

(* Format 1: a named block holding one declaration per part *)
long_form     = "{" , declaration , { declaration } , "}" , ";" ;

(* Format 2: the whole 5-tuple on one line, transitions given afterwards *)
short_form    = "(" , state_set , "," , symbol_set , "," , "JUTSU" , "," ,
                      state , "," , accept_set , ")" , ";" ,
                jutsu ;

declaration   = clan | chakra | jutsu | origin | awakened ;
clan          = "CLAN"     , "=" , state_set  , ";" ;
chakra        = "CHAKRA"   , "=" , symbol_set , ";" ;
jutsu         = "JUTSU"    , "=" , "{" , transition , { "," , transition } , "}" , ";" ;
origin        = "ORIGIN"   , "=" , state , ";" ;
awakened      = "AWAKENED" , "=" , accept_set , ";" ;

state_set     = "{" , state  , { "," , state  } , "}" ;
symbol_set    = "{" , symbol , { "," , symbol } , "}" ;
accept_set    = "{" , [ state , { "," , state } ] , "}"   (* F may be empty *)
              | state ;                                   (* syntactic sugar *)

transition    = "(" , state , "," , symbol , ")" , "->" , state ;
state         = IDENTIFIER ;
symbol        = IDENTIFIER | NUMBER | EPSILON ;            (* EPSILON is accepted here so
                                                              the semantic stage can give a
                                                              clear "not allowed" error *)
```

## Lexical grammar (tokens)

```ebnf
IDENTIFIER    = letter , { letter | digit | "_" } ;      (* that is not a KEYWORD or EPSILON *)
NUMBER        = digit , { digit } ;
KEYWORD       = "CLAN" | "CHAKRA" | "JUTSU" | "ORIGIN" | "AWAKENED" ;
EPSILON       = "ε" | "eps" | "epsilon" ;                 (* reserved, always an error *)
punctuation   = "=" | "{" | "}" | "(" | ")" | "," | ";" | "->" ;
letter        = "A" | "B" | … | "Z" | "a" | "b" | … | "z" ;
digit         = "0" | "1" | … | "9" ;
comment       = "#" , { ? any character except a line break ? } ;   (* skipped *)
whitespace    = " " | ? tab ? | ? carriage return ? | ? line feed ? ;  (* skipped *)
```

**Longest match:** at each position the lexer tries every token rule and keeps the
longest match; on a tie, keywords and EPSILON win over IDENTIFIER. So `CLAN` is a
keyword, `CLANS` is an identifier, `eps` is EPSILON, `epsilon2` is an identifier.

## Design decisions

- **Declarations may appear in any order in the grammar.** "Each part exactly once" and
  "nothing used before it is defined" (e.g. JUTSU before CHAKRA) are checked by the
  semantic stage, which gives clearer messages than a syntax error would.
- **A program is a named DFA**, `M = { … };`, so it starts with an identifier and `=` as the
  brief requires. The one-line format follows the brief's `M = (Q, Σ, δ, q₀, F)` exactly.
- **CLAN, CHAKRA and JUTSU must be non-empty** (Q is non-empty, and a DFA needs transitions).
- **A name cannot be both a state and a symbol** (semantic check).
- **The accept set may be empty**, because F ⊆ Q allows F = ∅.
- **Epsilon is reserved**, so it can never be mistaken for an ordinary symbol.

## Syntactic sugar

| Sugar | Means exactly | Why it's sugar |
|---|---|---|
| `AWAKENED = q1;` | `AWAKENED = {q1};` | Same AST; a one-state set could already be written |
| One-line format `M = ({…}, {…}, JUTSU, q0, {…});` | The `M = { … };` format with the same five parts | The parser turns it into the same five declarations, so it adds no expressive power |

## Examples

```shinobi
# Format 1
M = {
    CLAN = {q0, q1};
    CHAKRA = {a, b};
    JUTSU = { (q0, a) -> q1, (q0, b) -> q0, (q1, a) -> q0, (q1, b) -> q1 };
    ORIGIN = q0;
    AWAKENED = {q1};
};

# Format 2 (one line) - the same DFA
M = ({q0, q1}, {a, b}, JUTSU, q0, {q1});
JUTSU = { (q0, a) -> q1, (q0, b) -> q0, (q1, a) -> q0, (q1, b) -> q1 };
```
