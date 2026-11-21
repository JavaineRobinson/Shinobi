"""
Shinobi DFA language - pipeline (integration of all stages).

Group members / ID numbers:
    Lashawn Green(2305250), Kimberly Bruce(1909007), Javaine Robinson(2304749)

run(source) sends a Shinobi program through every stage in order:

    lexer.tokenize -> parser.parse -> semantic.analyze -> semantic.build_dfa -> render.to_svg

and returns ONE result dictionary, so a user interface never has to know
which stage produced what:

    {
      "ok":         True if the program is a valid DFA and was drawn,
      "errors":     [ {"stage": "lexical"|"syntax"|"semantic"|"internal",
                       "line": int, "column": int, "message": str}, ... ],
      "dot":        the state diagram as Graphviz DOT text (None if there were errors),
      "svg":        the state diagram as SVG text (None if there were errors or draw=False),
      "dfa":        {"name", "states", "alphabet", "start", "accepting",
                     "transitions": [{"from","symbol","to"}, ...]}  (None if errors),
      "simulation": {"input", "accepted", "note", "trace": [{"from","symbol","to"}, ...]}  or None,
      "batch":      [ {"input", "accepted", "note"}, ... ]   (one per test_inputs entry),
      "tokens":     the token list (None if lexing failed),
      "ast":        the syntax tree (None if parsing failed),
      "stage":      where it stopped: "lexical" | "syntax" | "semantic" | "render" | "done",
      "warnings":   notes that are not errors, e.g. Graphviz missing (the IDE then draws the
                    DOT in the browser instead)
    }

Error handling policy:
    lexical / syntax errors  -> the compiler stops at the first one (1 error in the list)
    semantic errors          -> all of them are collected (several errors in the list)
Every error has a line and a column so the interface can highlight the exact place.
"""

from .lexer import LexicalError, tokenize
from .parser import ShinobiSyntaxError, parse
from .render import to_dot, to_svg
from .semantic import analyze, build_dfa, simulate


GRAPHVIZ_MISSING = ("Graphviz is not installed on this computer, so the diagram was drawn in the "
                    "browser instead. To draw SVGs from the command line, run: brew install graphviz")


def make_error(stage, line, column, message):
    return {"stage": stage, "line": line, "column": column, "message": message}


def dfa_for_display(dfa, name):
    """Make the DFA easy to send as JSON (tuple keys are not allowed in JSON)."""
    return {
        "name": name,
        "states": dfa["states"],
        "alphabet": dfa["alphabet"],
        "start": dfa["start"],
        "accepting": dfa["accepting"],
        "transitions": [
            {"from": state, "symbol": symbol, "to": target}
            for (state, symbol), target in dfa["transitions"].items()
        ],
    }


def trace(dfa, text):
    """The path an input takes through the DFA: one step per symbol read.
    Reads symbols the same way semantic.simulate() does; stops at an unknown symbol."""
    symbols = list(text) if all(len(s) == 1 for s in dfa["alphabet"]) else text.split()
    state, steps = dfa["start"], []
    for symbol in symbols:
        if symbol not in dfa["alphabet"]:
            break
        target = dfa["transitions"][(state, symbol)]
        steps.append({"from": state, "symbol": symbol, "to": target})
        state = target
    return steps


def run(source, test_input=None, draw=True, filename="program", test_inputs=None):
    """Run a Shinobi program through every stage and return the result dictionary.

    draw=False skips the SVG (so checking a program does not need Graphviz).
    test_inputs is an optional list of input strings to test in one go."""
    result = {"ok": False, "errors": [], "dot": None, "svg": None, "dfa": None,
              "simulation": None, "batch": [], "tokens": None, "ast": None, "stage": "lexical",
              "warnings": []}

    try:
        # 1. lexical analysis
        try:
            tokens = tokenize(source, filename)
        except LexicalError as exc:
            result["errors"].append(make_error("lexical", exc.line, exc.column, exc.message))
            return result
        result["tokens"] = [t for t in tokens if t["type"] != "EOF"]
        result["stage"] = "syntax"

        # 2. syntax analysis (stops at the first error)
        try:
            ast = parse(tokens)
        except ShinobiSyntaxError as exc:
            result["errors"].append(make_error("syntax", exc.line, exc.column, exc.message))
            return result
        result["ast"] = ast
        result["stage"] = "semantic"

        # 3. semantic analysis (collects every error)
        errors = sorted(analyze(ast), key=lambda e: (e["line"], e["column"]))
        if errors:
            for e in errors:
                result["errors"].append(make_error("semantic", e["line"], e["column"], e["message"]))
            return result

        # 4. the program is a valid DFA: build it, draw it, optionally run an input on it
        result["stage"] = "render"
        dfa = build_dfa(ast)
        name = ast["name"]["name"]
        result["dot"] = to_dot(dfa, name)
        if draw:
            try:
                svg = to_svg(dfa, name)
                result["svg"] = svg[svg.index("<svg"):]   # drop the XML header so it can sit in a web page
            except Exception as exc:
                # Graphviz not installed is not a problem with the program: report it as a
                # warning and keep the DOT, which the web IDE can draw in the browser.
                if type(exc).__name__ not in ("ExecutableNotFound", "ModuleNotFoundError", "ImportError"):
                    raise
                result["warnings"].append(GRAPHVIZ_MISSING)
        result["dfa"] = dfa_for_display(dfa, name)
        result["ok"] = True
        result["stage"] = "done"

        if test_input:
            accepted, note = simulate(dfa, test_input)
            result["simulation"] = {"input": test_input, "accepted": accepted, "note": note,
                                    "trace": trace(dfa, test_input)}
        for text in test_inputs or []:
            accepted, note = simulate(dfa, text)
            result["batch"].append({"input": text, "accepted": accepted, "note": note})

    except Exception as exc:      # a bug or a missing Graphviz must not crash the whole page
        result["ok"] = False
        result["dot"] = result["svg"] = result["dfa"] = None
        result["errors"].append(make_error("internal", 1, 1, f"{type(exc).__name__}: {exc}"))

    return result
