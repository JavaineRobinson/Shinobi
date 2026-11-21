"""
Shinobi DFA language - rendering stage.
"""


def quote(name):
    """Wrap a name in double quotes so DOT accepts any name (e.g. 0, 1, Trap)."""
    return '"' + str(name).replace("\\", "\\\\").replace('"', '\\"') + '"'


def to_dot(dfa, title=None):
    """Return the Graphviz DOT text for a DFA."""
    lines = ["digraph DFA {", "  rankdir=LR;"]
    if title:
        lines.append(f"  label={quote(title)}; labelloc=t;")
    lines.append("  node [shape=circle];")

    # invisible start point with an arrow into the start state
    lines.append("  __start [shape=point, label=\"\"];")
    lines.append(f"  __start -> {quote(dfa['start'])};")

    # every state is drawn; accepting states get a double circle
    for state in dfa["states"]:
        shape = "doublecircle" if state in dfa["accepting"] else "circle"
        lines.append(f"  {quote(state)} [shape={shape}];")

    # merge parallel transitions: (q1,a)->q2 and (q1,b)->q2 become one arrow "a, b"
    grouped = {}
    for (state, symbol), target in dfa["transitions"].items():
        grouped.setdefault((state, target), []).append(symbol)

    for (state, target), symbols in grouped.items():
        label = ", ".join(symbols)
        lines.append(f"  {quote(state)} -> {quote(target)} [label={quote(label)}];")

    lines.append("}")
    return "\n".join(lines)


def to_svg(dfa, title=None):
    """Return the diagram as SVG text (needs Graphviz installed)."""
    import graphviz   # imported here so to_dot() works even without the package
    return graphviz.Source(to_dot(dfa, title)).pipe(format="svg").decode("utf-8")