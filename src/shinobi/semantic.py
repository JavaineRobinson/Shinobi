"""
Shinobi DFA language - Semantics

Group members / ID numbers:
    Kimberly Bruce(1909007), Lashawn Green(2305250), Javaine Robinson(2304749)
"""

REQUIRED = ["CLAN", "CHAKRA", "JUTSU", "ORIGIN", "AWAKENED"]

NEEDS = {
    "JUTSU": ["CLAN", "CHAKRA"],
    "ORIGIN": ["CLAN"],
    "AWAKENED": ["CLAN"],
}


def analyze(ast):
    errors = []
    seen = {}

    for decl in ast["declarations"]:
        if decl["kind"] in seen:
            errors.append({"message": f"{decl['kind']} is declared more than once", "line": decl["line"], "column": decl["column"]})
        else:
            seen[decl["kind"]] = decl

    for kind in REQUIRED:
        if kind not in seen:
            errors.append({"message": f"{kind} is missing", "line": 1, "column": 1})

    defined = []
    for decl in ast["declarations"]:
        for needed in NEEDS.get(decl["kind"], []):
            if needed in seen and needed not in defined:
                errors.append({"message": f"{decl['kind']} uses {needed} before it is declared", "line": decl["line"], "column": decl["column"]})
        defined.append(decl["kind"])

    for decl in ast["declarations"]:
        if decl["kind"] in ("CLAN", "CHAKRA", "AWAKENED"):
            names_seen = []
            for item in decl["value"]:
                if item["name"] in names_seen:
                    errors.append({"message": f"'{item['name']}' is repeated in {decl['kind']}", "line": item["line"], "column": item["column"]})
                else:
                    names_seen.append(item["name"])

    if "CLAN" in seen:
        states = []
        for item in seen["CLAN"]["value"]:
            states.append(item["name"])

        if "ORIGIN" in seen:
            origin = seen["ORIGIN"]["value"]
            if origin["name"] not in states:
                errors.append({"message": f"ORIGIN state '{origin['name']}' is not declared in CLAN", "line": origin["line"], "column": origin["column"]})

        if "AWAKENED" in seen:
            for item in seen["AWAKENED"]["value"]:
                if item["name"] not in states:
                    errors.append({"message": f"AWAKENED state '{item['name']}' is not declared in CLAN", "line": item["line"], "column": item["column"]})

    if "CLAN" in seen and "CHAKRA" in seen and "JUTSU" in seen:
        alphabet = []
        for item in seen["CHAKRA"]["value"]:
            alphabet.append(item["name"])

        for t in seen["JUTSU"]["value"]:
            if t["state"]["name"] not in states:
                errors.append({"message": f"transition state '{t['state']['name']}' is not declared in CLAN", "line": t["state"]["line"], "column": t["state"]["column"]})
            if t["symbol"]["name"] not in alphabet:
                errors.append({"message": f"symbol '{t['symbol']['name']}' is not declared in CHAKRA", "line": t["symbol"]["line"], "column": t["symbol"]["column"]})
            if t["target"]["name"] not in states:
                errors.append({"message": f"transition target '{t['target']['name']}' is not declared in CLAN", "line": t["target"]["line"], "column": t["target"]["column"]})

    pairs = {}
    if "JUTSU" in seen:
        for t in seen["JUTSU"]["value"]:
            key = (t["state"]["name"], t["symbol"]["name"])
            if key in pairs:
                errors.append({"message": f"more than one transition for ({key[0]}, {key[1]})", "line": t["line"], "column": t["column"]})
            else:
                pairs[key] = t["target"]["name"]

    if "CLAN" in seen and "CHAKRA" in seen and "JUTSU" in seen:
        jutsu = seen["JUTSU"]
        for s in states:
            for a in alphabet:
                if (s, a) not in pairs:
                    errors.append({"message": f"missing transition for ({s}, {a})", "line": jutsu["line"], "column": jutsu["column"]})

    return errors


def build_dfa(ast):
    """Only call this when analyze(ast) found no errors."""
    dfa = {"states": [], "alphabet": [], "transitions": {}, "start": None, "accepting": []}

    for decl in ast["declarations"]:
        if decl["kind"] == "CLAN":
            for item in decl["value"]:
                dfa["states"].append(item["name"])
        elif decl["kind"] == "CHAKRA":
            for item in decl["value"]:
                dfa["alphabet"].append(item["name"])
        elif decl["kind"] == "JUTSU":
            for t in decl["value"]:
                key = (t["state"]["name"], t["symbol"]["name"])
                dfa["transitions"][key] = t["target"]["name"]
        elif decl["kind"] == "ORIGIN":
            dfa["start"] = decl["value"]["name"]
        elif decl["kind"] == "AWAKENED":
            for item in decl["value"]:
                dfa["accepting"].append(item["name"])

    return dfa


def simulate(dfa, text):
    """Run the DFA on text. Returns (accepted, note)."""
    # If every symbol is one character, read the text letter by letter.
    # Otherwise, expect the symbols separated by spaces.
    if all(len(s) == 1 for s in dfa["alphabet"]):
        symbols = list(text)
    else:
        symbols = text.split()

    state = dfa["start"]
    for symbol in symbols:
        if symbol not in dfa["alphabet"]:
            return False, f"symbol '{symbol}' is not in the alphabet"
        state = dfa["transitions"][(state, symbol)]

    return state in dfa["accepting"], f"ended in state {state}"


def main():
    import sys
    from .lexer import tokenize, LexicalError
    from .parser import parse, ShinobiSyntaxError

    if len(sys.argv) < 2:
        print("Usage: python semantic.py <file.shinobi> [input string]")
        return

    path = sys.argv[1]
    source = open(path, encoding="utf-8").read()

    try:
        ast = parse(tokenize(source, path))
    except LexicalError as exc:
        print(f"Lexical error: {exc}")
        return
    except ShinobiSyntaxError as exc:
        print(f"{path}:{exc.line}:{exc.column}: syntax error: {exc.message}")
        return

    errors = analyze(ast)

    if errors:
        errors.sort(key=lambda e: (e["line"], e["column"]))
        for e in errors:
            print(f"{path}:{e['line']}:{e['column']}: semantic error: {e['message']}")
    else:
        dfa = build_dfa(ast)
        print("Valid DFA")
        print("States:", ", ".join(dfa["states"]))
        print("Alphabet:", ", ".join(dfa["alphabet"]))
        print("Start:", dfa["start"])
        print("Accepting:", ", ".join(dfa["accepting"]))
        print("Transitions:")
        for (s, a), target in dfa["transitions"].items():
            print(f"  ({s}, {a}) -> {target}")

        if len(sys.argv) > 2:
            accepted, note = simulate(dfa, sys.argv[2])
            print()
            print(f"Input '{sys.argv[2]}': {'ACCEPTED' if accepted else 'REJECTED'} ({note})")


if __name__ == "__main__":
    main()