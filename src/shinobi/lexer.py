
import argparse
import re
from pathlib import Path

TOKEN_PATTERNS = [
    (re.compile(pattern), token_type)
    for pattern, token_type in [
        (r"CLAN", "CLAN"),
        (r"CHAKRA", "CHAKRA"),
        (r"JUTSU", "JUTSU"),
        (r"ORIGIN", "ORIGIN"),
        (r"AWAKENED", "AWAKENED"),
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
        (r"#[^\r\n]*", None),
        (r"[ \t\r\n]+", None),
    ]
]

class LexicalError(Exception):
    pass

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
                f"{filename}:{line}:{column}: unrecognised input"
            )

        match, token_type = max(matches, key=lambda item: len(item[0].group()))
        token_text = match.group()
        token_line = line
        token_column = column
        if token_type is not None:
            tokens.append({
                "type": token_type, "value": token_text,
                "line": token_line, "column": token_column
            })

        line_breaks = list(re.finditer(r"\r\n|\r|\n", token_text))
        if line_breaks:
            line += len(line_breaks)
            column = len(token_text) - line_breaks[-1].end() + 1
        else:
            column += len(token_text)
        position = match.end()

    tokens.append({
        "type": "EOF", "value": "",
        "line": tokens[-1]["line"] if tokens else 1,
        "column": tokens[-1]["column"] if tokens else 1
    })
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
