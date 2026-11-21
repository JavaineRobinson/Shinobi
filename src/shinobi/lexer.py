"""
Shinobi DFA language - lexical analysis stage.

Group members / ID numbers:
    Lashawn Green(2305250), Kimberly Bruce(1909007), Javaine Robinson(2304749)

Turns source text into a list of tokens:
    {"type": ..., "value": ..., "line": int, "column": int}

Matching rule: at each position every pattern is tried and the LONGEST match
wins. On a tie the pattern listed first wins, which is how the keywords
(CLAN, CHAKRA, ...) and EPSILON beat IDENTIFIER: "CLAN" is a keyword, while
"CLANS" is an identifier because it is the longer match.

The token rules are written out in EBNF in docs/grammar.md.
"""

import argparse
import re
from pathlib import Path

KEYWORDS = {"CLAN", "CHAKRA", "JUTSU", "ORIGIN", "AWAKENED"}

# Spellings of epsilon. They are reserved so nobody can use them as an
# ordinary symbol; the semantic stage reports them as an error, because
# epsilon may never appear in a DFA.
EPSILON_SPELLINGS = {"ε", "eps", "epsilon"}

TOKEN_PATTERNS = [
    (re.compile(pattern), token_type)
    for pattern, token_type in [
        (r"CLAN", "CLAN"),
        (r"CHAKRA", "CHAKRA"),
        (r"JUTSU", "JUTSU"),
        (r"ORIGIN", "ORIGIN"),
        (r"AWAKENED", "AWAKENED"),
        (r"ε|epsilon|eps", "EPSILON"),
        (r"->", "ARROW"),
        (r"=", "EQUALS"),
        (r"\{", "LBRACE"),
        (r"\}", "RBRACE"),
        (r"\(", "LPAREN"),
        (r"\)", "RPAREN"),
        (r",", "COMMA"),
        (r";", "SEMICOLON"),
        (r"[0-9]+", "NUMBER"),
        (r"[A-Za-z][A-Za-z0-9_]*", "IDENTIFIER"),
        (r"#[^\r\n]*", None),        # comment: skipped
        (r"[ \t\r\n]+", None),       # whitespace: skipped
    ]
]


class LexicalError(Exception):
    """Raised on the first character that starts no token."""

    def __init__(self, message, line, column, filename="<input>"):
        super().__init__(f"{filename}:{line}:{column}: {message}")
        self.message = message
        self.line = line
        self.column = column
        self.filename = filename


def tokenize(source: str, filename: str = "<input>"):
    tokens = []
    position = 0
    line = 1
    column = 1

    while position < len(source):
        matches = [
            (match, token_type)
            for pattern, token_type in TOKEN_PATTERNS
            if (match := pattern.match(source, position)) is not None
        ]
        if not matches:
            raise LexicalError(
                f"unexpected character {source[position]!r}", line, column, filename
            )

        # longest match wins; max() keeps the first pattern on a tie
        match, token_type = max(matches, key=lambda item: len(item[0].group()))
        token_text = match.group()
        if token_type is not None:
            tokens.append({
                "type": token_type, "value": token_text,
                "line": line, "column": column,
            })

        line_breaks = list(re.finditer(r"\r\n|\r|\n", token_text))
        if line_breaks:
            line += len(line_breaks)
            column = len(token_text) - line_breaks[-1].end() + 1
        else:
            column += len(token_text)
        position = match.end()

    # EOF sits just after the last token, so "expected ';' but found end of
    # file" points at the place where the ';' is missing.
    if tokens:
        last = tokens[-1]
        eof_line, eof_column = last["line"], last["column"] + len(last["value"])
    else:
        eof_line, eof_column = 1, 1
    tokens.append({"type": "EOF", "value": "", "line": eof_line, "column": eof_column})
    return tokens


def main():
    cli = argparse.ArgumentParser(description="Tokenize a Shinobi source file.")
    cli.add_argument("file", type=Path, help="Shinobi source file")
    args = cli.parse_args()

    try:
        source = args.file.read_text(encoding="utf-8")
        for token in tokenize(source, str(args.file)):
            print(token)
    except (OSError, LexicalError) as exc:
        cli.error(str(exc))


if __name__ == "__main__":
    main()
