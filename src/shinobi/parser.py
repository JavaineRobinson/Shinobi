"""
Shinobi DFA language - syntax analysis stage (recursive-descent parser).

Group members / ID numbers:
    Lashawn Green(2305250), Kimberly Bruce(1909007), Javaine Robinson()

Pipeline:   source text -> lexer.tokenize() -> parse() -> AST -> semantic stage

Grammar implemented (Shape B: a program is a list of separate declarations):

    program      = declaration , { declaration } ;
    declaration  = clan | chakra | jutsu | origin | awakened ;

    clan         = "CLAN"     , "=" , "{" , state , { "," , state } , "}" , ";" ;
    chakra       = "CHAKRA"   , "=" , "{" , symbol , { "," , symbol } , "}" , ";" ;
    jutsu        = "JUTSU"    , "=" , "{" , transition , { "," , transition } , "}" , ";" ;
    origin       = "ORIGIN"   , "=" , state , ";" ;
    awakened     = "AWAKENED" , "=" , ( "{" , state , { "," , state } , "}" | state ) , ";" ;

    transition   = "(" , state , "," , symbol , ")" , "->" , state ;
    state        = IDENTIFIER ;
    symbol       = IDENTIFIER | NUMBER ;

Syntactic sugar:  AWAKENED = q1;   is shorthand for   AWAKENED = {q1};
Both forms produce exactly the same AST (see sugar_check.py).

Division of work between stages:
    This parser checks ONLY the shape (order of tokens, brackets, commas).
    Meaning is checked by the semantic stage: undefined states, duplicates,
    missing or repeated declarations, declaration order, missing transitions.

Error handling: the parser stops at the first syntax error and raises
ShinobiSyntaxError(message, line, column).

AST (plain dicts so the semantic stage can read them easily):
    {"type": "Program", "declarations": [ Declaration, ... ]}
    Declaration = {"type": "Declaration", "kind": "CLAN"|"CHAKRA"|"JUTSU"|"ORIGIN"|"AWAKENED",
                   "value": <see below>, "line": int, "column": int}
        CLAN / CHAKRA / AWAKENED value -> list of Name
        ORIGIN value                   -> a single Name
        JUTSU value                    -> list of Transition
    Name       = {"name": str, "line": int, "column": int}
    Transition = {"state": Name, "symbol": Name, "target": Name, "line": int, "column": int}
"""

import argparse
import json
import sys
from pathlib import Path

from .lexer import tokenize, LexicalError

KEYWORDS = {"CLAN", "CHAKRA", "JUTSU", "ORIGIN", "AWAKENED"}

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
        declarations = []
        while self.peek()["type"] != "EOF":
            declarations.append(self.parse_declaration())
        if not declarations:
            self.error("a declaration (CLAN, CHAKRA, JUTSU, ORIGIN or AWAKENED)")
        return {"type": "Program", "declarations": declarations}

    def parse_declaration(self):
        keyword = self.peek()
        parse_value = self.declaration_parsers.get(keyword["type"])
        if parse_value is None:
            self.error("a declaration keyword (CLAN, CHAKRA, JUTSU, ORIGIN or AWAKENED)")
        self.advance()                 # the keyword
        self.expect("EQUALS")
        value = parse_value()          # right-hand side depends on the keyword
        self.expect("SEMICOLON")
        return {
            "type": "Declaration", "kind": keyword["type"], "value": value,
            "line": keyword["line"], "column": keyword["column"],
        }

    def parse_clan(self):
        return self.parse_name_set(("IDENTIFIER",), "a state name")

    def parse_chakra(self):
        return self.parse_name_set(("IDENTIFIER", "NUMBER"), "an alphabet symbol")

    def parse_jutsu(self):
        self.expect("LBRACE")
        transitions = [self.parse_transition()]
        while self.peek()["type"] == "COMMA":
            self.advance()
            transitions.append(self.parse_transition())
        self.expect("RBRACE", "',' or '}'")
        return transitions

    def parse_origin(self):
        return self.parse_name(("IDENTIFIER",), "a state name")

    def parse_awakened(self):
        # Syntactic sugar: AWAKENED = q1;  means  AWAKENED = {q1};
        if self.peek()["type"] == "LBRACE":
            return self.parse_name_set(("IDENTIFIER",), "a state name")
        if self.peek()["type"] == "IDENTIFIER":
            return [self.parse_name(("IDENTIFIER",), "a state name")]
        self.error("'{' or a state name")

    def parse_name_set(self, allowed_types, what):
        """'{' name { ',' name } '}'  (at least one name)."""
        self.expect("LBRACE")
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
        state = self.parse_name(("IDENTIFIER",), "a state name")
        self.expect("COMMA")
        symbol = self.parse_name(("IDENTIFIER", "NUMBER"), "an alphabet symbol")
        self.expect("RPAREN")
        self.expect("ARROW")
        target = self.parse_name(("IDENTIFIER",), "a state name")
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
        print(json.dumps(parse(tokenize(source, str(args.file))), indent=2))
    except OSError as exc:
        sys.exit(f"Cannot read file: {exc}")
    except LexicalError as exc:
        sys.exit(f"Lexical error: {exc}")
    except ShinobiSyntaxError as exc:
        sys.exit(f"{args.file}:{exc.line}:{exc.column}: syntax error: {exc.message}")


if __name__ == "__main__":
    main()
