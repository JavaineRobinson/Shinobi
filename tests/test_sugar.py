"""Syntactic sugar: each pair below must describe exactly the same DFA.

    1. AWAKENED = q1;        vs  AWAKENED = {q1};
    2. one-line 5-tuple      vs  M = { ... };  format
"""
from pathlib import Path

from shinobi.lexer import tokenize
from shinobi.parser import parse
from shinobi.semantic import build_dfa

FIXTURES = Path(__file__).parent / "fixtures"
HEAD = "M = { CLAN = {q0, q1}; CHAKRA = {a}; JUTSU = {(q0,a)->q1,(q1,a)->q0}; ORIGIN = q0; "


def strip_positions(node):
    if isinstance(node, dict):
        return {k: strip_positions(v) for k, v in node.items() if k not in ("line", "column")}
    if isinstance(node, list):
        return [strip_positions(x) for x in node]
    return node


def dfa_from(name):
    source = (FIXTURES / name).read_text(encoding="utf-8")
    return build_dfa(parse(tokenize(source)))


def test_awakened_sugar_gives_same_ast():
    sugar = strip_positions(parse(tokenize(HEAD + "AWAKENED = q1; };")))
    full = strip_positions(parse(tokenize(HEAD + "AWAKENED = {q1}; };")))
    assert sugar == full


def test_one_line_format_gives_same_dfa_as_long_format():
    assert dfa_from("valid_06_one_line_format.shinobi") == dfa_from("valid_brief_example.shinobi")
