"""
Shinobi command-line interface.

    shinobi check  FILE                 check a program; print the DFA or every error
    shinobi run    FILE INPUT           check it, then run INPUT through the DFA
    shinobi render FILE [-o OUT]        check it and save the state diagram (SVG, or DOT with --dot)
    shinobi tokens FILE                 print the token stream (lexical stage only)
    shinobi ast    FILE                 print the abstract syntax tree as JSON (syntax stage only)
    shinobi studio [--port N]           start the web IDE (Shinobi DFA Studio)

Without installing:  python -m shinobi <command> ...
Exit codes:  0 = valid program, 1 = errors in the program, 2 = bad usage or unreadable file.
"""

import argparse
import json
import sys
from pathlib import Path

from .lexer import LexicalError, tokenize
from .parser import ShinobiSyntaxError, parse
from .pipeline import run


def read(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"shinobi: cannot read {path}: {exc.strerror}", file=sys.stderr)
        sys.exit(2)


def print_errors(path, errors):
    for e in errors:
        print(f"{path}:{e['line']}:{e['column']}: {e['stage']} error: {e['message']}", file=sys.stderr)


def print_dfa(dfa):
    print(f"Valid DFA: {dfa['name']}")
    print(f"  States    Q  = {{{', '.join(dfa['states'])}}}")
    print(f"  Alphabet  Σ  = {{{', '.join(dfa['alphabet'])}}}")
    print(f"  Start     q₀ = {dfa['start']}")
    print(f"  Accepting F  = {{{', '.join(dfa['accepting'])}}}")
    print("  Transitions δ:")
    for t in dfa["transitions"]:
        print(f"    ({t['from']}, {t['symbol']}) -> {t['to']}")


def compile_file(path, test_input=None, draw=False):
    result = run(read(path), test_input, draw=draw, filename=str(path))
    if not result["ok"]:
        print_errors(path, result["errors"])
        sys.exit(1)
    return result


def cmd_check(args):
    print_dfa(compile_file(args.file)["dfa"])


def cmd_run(args):
    result = compile_file(args.file, args.input)
    sim = result["simulation"]
    print(f"Input '{sim['input']}': {'ACCEPTED' if sim['accepted'] else 'REJECTED'} ({sim['note']})")
    if args.strict and not sim["accepted"]:
        sys.exit(1)


def cmd_render(args):
    result = compile_file(args.file, draw=not args.dot)
    if not args.dot and result["svg"] is None:
        print("shinobi: Graphviz is not installed, so no SVG can be drawn here.\n"
              "  Install it with:  brew install graphviz\n"
              "  Or save DOT text: shinobi render FILE --dot   (or use: shinobi studio)", file=sys.stderr)
        sys.exit(2)
    suffix = ".dot" if args.dot else ".svg"
    out = Path(args.output) if args.output else Path("out") / (Path(args.file).stem + suffix)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(result["dot"] if args.dot else result["svg"], encoding="utf-8")
    print(f"Diagram saved to {out}")


def cmd_tokens(args):
    try:
        for t in tokenize(read(args.file), args.file):
            print(f"{t['line']:>4}:{t['column']:<4} {t['type']:<11} {t['value']}")
    except LexicalError as exc:
        print_errors(args.file, [{"stage": "lexical", "line": exc.line, "column": exc.column, "message": exc.message}])
        sys.exit(1)


def cmd_ast(args):
    try:
        ast = parse(tokenize(read(args.file), args.file))
    except LexicalError as exc:
        print_errors(args.file, [{"stage": "lexical", "line": exc.line, "column": exc.column, "message": exc.message}])
        sys.exit(1)
    except ShinobiSyntaxError as exc:
        print_errors(args.file, [{"stage": "syntax", "line": exc.line, "column": exc.column, "message": exc.message}])
        sys.exit(1)
    print(json.dumps(ast, indent=2, ensure_ascii=False))


def cmd_studio(args):
    from .app import app   # Flask is only needed for this command
    app.run(host="127.0.0.1", port=args.port, debug=args.debug)


def build_parser():
    cli = argparse.ArgumentParser(prog="shinobi", description="Shinobi DFA language compiler.")
    sub = cli.add_subparsers(dest="command", required=True, metavar="command")

    p = sub.add_parser("check", help="check a program and print the DFA or the errors")
    p.add_argument("file")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("run", help="check a program and run an input string through it")
    p.add_argument("file")
    p.add_argument("input", help="symbols one character at a time (e.g. abba), or space-separated")
    p.add_argument("--strict", action="store_true", help="exit with code 1 if the input is rejected")
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("render", help="check a program and save its state diagram")
    p.add_argument("file")
    p.add_argument("-o", "--output", help="output file (default: out/<name>.svg)")
    p.add_argument("--dot", action="store_true", help="save Graphviz DOT text instead of SVG")
    p.set_defaults(func=cmd_render)

    p = sub.add_parser("tokens", help="print the token stream")
    p.add_argument("file")
    p.set_defaults(func=cmd_tokens)

    p = sub.add_parser("ast", help="print the abstract syntax tree as JSON")
    p.add_argument("file")
    p.set_defaults(func=cmd_ast)

    p = sub.add_parser("studio", help="start the web IDE")
    p.add_argument("--port", type=int, default=5000)
    p.add_argument("--debug", action="store_true", help="auto-reload on code changes")
    p.set_defaults(func=cmd_studio)
    return cli


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
