"""
Shinobi DFA language - syntax analysis stage (recursive-descent parser).

Group members / ID numbers:
    Lashawn Green(2305250), Kimberly Bruce(1909007), Javaine Robinson(2304749)

Pipeline:   source text -> lexer.tokenize() -> parse() -> AST -> semantic stage

Grammar implemented (full grammar, including tokens, in docs/grammar.md):

    program      = dfa_name , "=" , ( long_form | short_form ) ;
    dfa_name     = IDENTIFIER ;

    (* Format 1: a named block holding one declaration per part *)
    long_form    = "{" , declaration , { declaration } , "}" , ";" ;

    (* Format 2: the whole 5-tuple on one line, transitions afterwards *)
    short_form   = "(" , state_set , "," , symbol_set , "," , "JUTSU" , "," ,
                         state , "," , accept_set , ")" , ";" ,
                   jutsu ;

    declaration  = clan | chakra | jutsu | origin | awakened ;
    clan         = "CLAN"     , "=" , state_set  , ";" ;
    chakra       = "CHAKRA"   , "=" , symbol_set , ";" ;
    jutsu        = "JUTSU"    , "=" , "{" , transition , { "," , transition } , "}" , ";" ;
    origin       = "ORIGIN"   , "=" , state , ";" ;
    awakened     = "AWAKENED" , "=" , accept_set , ";" ;

    state_set    = "{" , state  , { "," , state  } , "}" ;
    symbol_set   = "{" , symbol , { "," , symbol } , "}" ;
    accept_set   = "{" , [ state , { "," , state } ] , "}"    (* F may be empty *)
                 | state ;                                    (* syntactic sugar *)

    transition   = "(" , state , "," , symbol , ")" , "->" , state ;
    state        = IDENTIFIER ;
    symbol       = IDENTIFIER | NUMBER | EPSILON ;   (* EPSILON parses, then the
                                                        semantic stage rejects it *)

Syntactic sugar (both produce the same DFA, nothing new can be expressed):
    1. AWAKENED = q1;          is shorthand for   AWAKENED = {q1};
    2. the one-line format     is shorthand for   the  M = { ... };  format
       (the parser turns format 2 into the same five declarations)

Division of work between stages:
    This parser checks ONLY the shape (order of tokens, brackets, commas).
    Meaning is checked by the semantic stage: undefined states, duplicates,
    missing or repeated declarations, declaration order, missing transitions,
    epsilon.

Error handling: the parser stops at the first syntax error and raises
ShinobiSyntaxError(message, line, column).

AST (plain dicts so the semantic stage can read them easily):
    {"type": "Program", "name": Name, "format": "long" | "short",
     "declarations": [ Declaration, ... ]}
    Declaration = {"type": "Declaration", "kind": "CLAN"|"CHAKRA"|"JUTSU"|"ORIGIN"|"AWAKENED",
                   "value": <see below>, "line": int, "column": int}
        CLAN / CHAKRA / AWAKENED value -> list of Name   (AWAKENED may be empty)
        ORIGIN value                   -> a single Name
        JUTSU value                    -> list of Transition
    Name       = {"name": str, "line": int, "column": int}
    Transition = {"state": Name, "symbol": Name, "target": Name, "line": int, "column": int}
"""

import argparse
import json
import sys
from pathlib import Path

from .lexer import KEYWORDS, LexicalError, tokenize

STATE_TYPES = ("IDENTIFIER",)
SYMBOL_TYPES = ("IDENTIFIER", "NUMBER", "EPSILON")

# How each token type is named inside error messages.
EXPECTED_NAMES = {
    "EQUALS": "'='", "LBRACE": "'{'", "RBRACE": "'}'",
    "LPAREN": "'('", "RPAREN": "')'", "COMMA": "','",
    "SEMICOLON": "';'", "ARROW": "'->'",
    "IDENTIFIER": "an identifier", "NUMBER": "a number",
}


class ShinobiSyntaxError(Exception):
    """Raised on the first syntax error; carries the message and position."""

    def __init__(self, message, line, column):
        super().__init__(f"{line}:{column}: {message}")
        self.message = message
        self.line = line
        self.column = column


def describe(token):
    """Human-readable description of a token, used for the 'found ...' part."""
    kind = token["type"]
    if kind == "EOF":
        return "end of file"
    if kind in KEYWORDS:
        return f"keyword {token['value']}"
    if kind == "EPSILON":
        return f"epsilon '{token['value']}'"
    if kind == "IDENTIFIER":
        return f"identifier '{token['value']}'"
    if kind == "NUMBER":
        return f"number {token['value']}"
    return f"'{token['value']}'"


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0  # index of the current token
        # which function parses the right-hand side of each declaration
        self.declaration_parsers = {
            "CLAN": self.parse_clan,
            "CHAKRA": self.parse_chakra,
            "JUTSU": self.parse_jutsu,
            "ORIGIN": self.parse_origin,
            "AWAKENED": self.parse_awakened,
        }

    # ---------- helper functions ----------

    def peek(self):
        """Look at the current token without consuming it."""
        return self.tokens[self.pos]

    def advance(self):
        """Consume and return the current token (never moves past EOF)."""
        token = self.tokens[self.pos]
        if token["type"] != "EOF":
            self.pos += 1
        return token

    def error(self, expected):
        """Raise a syntax error at the current token."""
        token = self.peek()
        raise ShinobiSyntaxError(
            f"expected {expected} but found {describe(token)}",
            token["line"], token["column"],
        )

    def expect(self, token_type, expected=None):
        """Consume a token of the given type, or raise a syntax error."""
        if self.peek()["type"] != token_type:
            self.error(expected or EXPECTED_NAMES.get(token_type, token_type))
        return self.advance()

    # ---------- grammar rules ----------

    def parse_program(self):
        name = self.parse_name(STATE_TYPES, "the DFA's name (a program starts like  M = { ... };)")
        self.expect("EQUALS")
        kind = self.peek()["type"]
        if kind == "LBRACE":
            fmt, declarations = "long", self.parse_long_form()
        elif kind == "LPAREN":
            self.advance()
            fmt, declarations = "short", self.parse_short_form()
        else:
            self.error("'{' to start the program body (or '(' for the one-line 5-tuple)")
        if self.peek()["type"] != "EOF":
            self.error("end of file")
        return {"type": "Program", "name": name, "format": fmt, "declarations": declarations}

    def parse_long_form(self):
        """'{' declaration { declaration } '}' ';'"""
        self.expect("LBRACE")
        declarations = []
        while self.peek()["type"] != "RBRACE":
            if self.peek()["type"] not in self.declaration_parsers:
                expected = "a declaration keyword (CLAN, CHAKRA, JUTSU, ORIGIN or AWAKENED)"
                self.error(expected + (" or '}' to close the program" if declarations else ""))
            declarations.append(self.parse_declaration())
        if not declarations:
            self.error("a declaration (CLAN, CHAKRA, JUTSU, ORIGIN or AWAKENED)")
        self.expect("RBRACE")
        self.expect("SEMICOLON", "';' after the closing '}' of the program")
        return declarations

    def parse_short_form(self):
        """( {states}, {symbols}, JUTSU, start, {accept} );  then the JUTSU block.

        Produces the same five declarations as the long format, so the
        semantic stage does not need to know which format was used."""
        start = self.peek()
        if start["type"] != "LBRACE":
            self.error("'{' to start the set of states")
        clan = self.make_declaration("CLAN", self.parse_name_set(STATE_TYPES, "a state name"), start)
        self.expect("COMMA")

        start = self.peek()
        chakra = self.make_declaration("CHAKRA", self.parse_name_set(SYMBOL_TYPES, "an alphabet symbol"), start)
        self.expect("COMMA")
        self.expect("JUTSU", "JUTSU (the transitions are written after the tuple)")
        self.expect("COMMA")

        start = self.peek()
        origin = self.make_declaration("ORIGIN", self.parse_name(STATE_TYPES, "the start state"), start)
        self.expect("COMMA")

        start = self.peek()
        awakened = self.make_declaration("AWAKENED", self.parse_accept_set(), start)
        self.expect("RPAREN", "')' to close the 5-tuple")
        self.expect("SEMICOLON")

        if self.peek()["type"] != "JUTSU":
            self.error("the JUTSU block (JUTSU = { ... };) after the one-line tuple")
        jutsu = self.parse_declaration()
        if self.peek()["type"] != "EOF":
            self.error("end of file (in the one-line format only the JUTSU block follows the tuple)")
        return [clan, chakra, origin, awakened, jutsu]

    def make_declaration(self, kind, value, token):
        return {"type": "Declaration", "kind": kind, "value": value,
                "line": token["line"], "column": token["column"]}

    def parse_declaration(self):
        keyword = self.peek()
        parse_value = self.declaration_parsers.get(keyword["type"])
        if parse_value is None:
            self.error("a declaration keyword (CLAN, CHAKRA, JUTSU, ORIGIN or AWAKENED)")
        self.advance()                 # the keyword
        self.expect("EQUALS")
        value = parse_value()          # right-hand side depends on the keyword
        self.expect("SEMICOLON")
        return self.make_declaration(keyword["type"], value, keyword)

    def parse_clan(self):
        return self.parse_name_set(STATE_TYPES, "a state name")

    def parse_chakra(self):
        return self.parse_name_set(SYMBOL_TYPES, "an alphabet symbol")

    def parse_jutsu(self):
        self.expect("LBRACE")
        transitions = [self.parse_transition()]
        while self.peek()["type"] == "COMMA":
            self.advance()
            transitions.append(self.parse_transition())
        self.expect("RBRACE", "',' or '}'")
        return transitions

    def parse_origin(self):
        return self.parse_name(STATE_TYPES, "a state name")

    def parse_awakened(self):
        return self.parse_accept_set()

    def parse_accept_set(self):
        # Syntactic sugar: AWAKENED = q1;  means  AWAKENED = {q1};
        if self.peek()["type"] == "LBRACE":
            return self.parse_name_set(STATE_TYPES, "a state name", allow_empty=True)
        if self.peek()["type"] == "IDENTIFIER":
            return [self.parse_name(STATE_TYPES, "a state name")]
        self.error("'{' or a state name")

    def parse_name_set(self, allowed_types, what, allow_empty=False):
        """'{' name { ',' name } '}'  (at least one name unless allow_empty)."""
        self.expect("LBRACE")
        if allow_empty and self.peek()["type"] == "RBRACE":
            self.advance()
            return []
        names = [self.parse_name(allowed_types, what)]
        while self.peek()["type"] == "COMMA":
            self.advance()
            names.append(self.parse_name(allowed_types, what))
        self.expect("RBRACE", "',' or '}'")
        return names

    def parse_name(self, allowed_types, what):
        token = self.peek()
        if token["type"] not in allowed_types:
            self.error(what)
        self.advance()
        return {"name": token["value"], "line": token["line"], "column": token["column"]}

    def parse_transition(self):
        """'(' state ',' symbol ')' '->' state"""
        start = self.expect("LPAREN", "'(' to start a transition")
        state = self.parse_name(STATE_TYPES, "a state name")
        self.expect("COMMA")
        symbol = self.parse_name(SYMBOL_TYPES, "an alphabet symbol")
        self.expect("RPAREN")
        self.expect("ARROW")
        target = self.parse_name(STATE_TYPES, "a state name")
        return {"state": state, "symbol": symbol, "target": target,
                "line": start["line"], "column": start["column"]}


def parse(tokens):
    """Parse a token list (from lexer.tokenize) and return the AST."""
    return Parser(tokens).parse_program()


def main():
    cli = argparse.ArgumentParser(description="Parse a Shinobi file and print its AST.")
    cli.add_argument("file", type=Path)
    args = cli.parse_args()
    try:
        source = args.file.read_text(encoding="utf-8")
        print(json.dumps(parse(tokenize(source, str(args.file))), indent=2, ensure_ascii=False))
    except OSError as exc:
        sys.exit(f"Cannot read file: {exc}")
    except LexicalError as exc:
        sys.exit(f"{exc.filename}:{exc.line}:{exc.column}: lexical error: {exc.message}")
    except ShinobiSyntaxError as exc:
        sys.exit(f"{args.file}:{exc.line}:{exc.column}: syntax error: {exc.message}")


if __name__ == "__main__":
    main()
