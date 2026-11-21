"""
Shinobi DFA language - web interface (Shinobi DFA Studio).

Group members / ID numbers:
    Lashawn Green(2305250), Kimberly Bruce(1909007), Javaine Robinson(2304749)

Run:   python -m shinobi.app        then open  http://localhost:5000

The page has an editor, a Run button, an error list (click an error to jump to
its line; the offending lines are highlighted in red) and the rendered diagram.
All the real work is done by pipeline.run(), so this file only moves text in
and results out. The page itself is templates/studio.html.
"""

from flask import Flask, jsonify, render_template, request

from .pipeline import run

app = Flask(__name__)

EXAMPLES = {
    "Valid: brief example (with Trap state)": """M = {
  CLAN = {q1, q2, q3, q4, Trap};
  CHAKRA = {a, b, c};
  JUTSU = {
    (q1, a) -> q2, (q1, b) -> q3, (q1, c) -> Trap,
    (q2, a) -> q4, (q2, b) -> Trap, (q2, c) -> q2,
    (q3, a) -> Trap, (q3, b) -> q4, (q3, c) -> q3,
    (q4, a) -> Trap, (q4, b) -> Trap, (q4, c) -> Trap,
    (Trap, a) -> Trap, (Trap, b) -> Trap, (Trap, c) -> Trap
  };
  ORIGIN = q1;
  AWAKENED = {q4};
};
""",
    "Valid: two states": """M = {
  CLAN = {q0, q1};
  CHAKRA = {a, b};
  JUTSU = {
    (q0, a) -> q1, (q0, b) -> q0,
    (q1, a) -> q0, (q1, b) -> q1
  };
  ORIGIN = q0;
  AWAKENED = q1;
};
""",
    "Valid: no accepting states": """M = {
  CLAN = {q0, q1};
  CHAKRA = {a};
  JUTSU = { (q0, a) -> q1, (q1, a) -> q0 };
  ORIGIN = q0;
  AWAKENED = {};
};
""",
    "Valid: one-line 5-tuple (same DFA as the brief)": """M = ({q1, q2, q3, q4, Trap}, {a, b, c}, JUTSU, q1, {q4});
JUTSU = {
  (q1, a) -> q2, (q1, b) -> q3, (q1, c) -> Trap,
  (q2, a) -> q4, (q2, b) -> Trap, (q2, c) -> q2,
  (q3, a) -> Trap, (q3, b) -> q4, (q3, c) -> q3,
  (q4, a) -> Trap, (q4, b) -> Trap, (q4, c) -> Trap,
  (Trap, a) -> Trap, (Trap, b) -> Trap, (Trap, c) -> Trap
};
""",
    "Lexical error (illegal character)": """M = {
  CLAN = {q0, q1};
  CHAKRA = {a, b};
  JUTSU = { (q0, a) -> q1, (q0, b) -> q0, (q1, a) -> q0, (q1, b) => q1 };
  ORIGIN = q0;
  AWAKENED = {q1};
};
""",
    "Semantic error (epsilon transition)": """M = {
  CLAN = {q0, q1};
  CHAKRA = {a, b};
  JUTSU = { (q0, a) -> q1, (q0, b) -> q0, (q0, ε) -> q0, (q1, a) -> q0, (q1, b) -> q1 };
  ORIGIN = q0;
  AWAKENED = {q1};
};
""",
    "Syntax error (missing semicolon)": """M = {
  CLAN = {q0, q1}
  CHAKRA = {a, b};
  JUTSU = {
    (q0, a) -> q1, (q0, b) -> q0,
    (q1, a) -> q0, (q1, b) -> q1
  };
  ORIGIN = q0;
  AWAKENED = {q1};
};
""",
    "Semantic errors (several at once)": """M = {
  CLAN = {q0, q1};
  CHAKRA = {a, b};
  JUTSU = {
    (q0, a) -> q1, (q0, c) -> q0,
    (q1, a) -> q0
  };
  ORIGIN = q9;
  AWAKENED = {q1};
};
""",
}

@app.route("/")
def index():
    return render_template("studio.html", examples=list(EXAMPLES.items()))   # a list keeps the order


@app.route("/api/run", methods=["POST"])
def api_run():
    data = request.get_json(silent=True) or {}
    inputs = [str(x) for x in (data.get("inputs") or [])][:200]
    return jsonify(run(data.get("source", ""), data.get("input") or None, test_inputs=inputs))


def main():
    app.run(host="127.0.0.1", port=5000, debug=True)


if __name__ == "__main__":
    main()