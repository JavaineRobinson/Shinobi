"""Syntactic sugar: AWAKENED = q1;  must give the same AST as  AWAKENED = {q1};
(converted from the original sugar_check.py)."""
from shinobi.lexer import tokenize
from shinobi.parser import parse

HEAD = "CLAN = {q0, q1}; CHAKRA = {a}; JUTSU = {(q0,a)->q1,(q1,a)->q0}; ORIGIN = q0; "


def strip_positions(node):
    if isinstance(node, dict):
        return {k: strip_positions(v) for k, v in node.items() if k not in ("line", "column")}
    if isinstance(node, list):
        return [strip_positions(x) for x in node]
    return node


def test_awakened_sugar_gives_same_ast():
    sugar = strip_positions(parse(tokenize(HEAD + "AWAKENED = q1;")))
    full = strip_positions(parse(tokenize(HEAD + "AWAKENED = {q1};")))
    assert sugar == full
