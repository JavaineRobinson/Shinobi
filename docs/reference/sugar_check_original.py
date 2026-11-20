"""Shows that the sugar form and the full form give the SAME AST (apart from
source positions, which naturally differ)."""
from lexer import tokenize
from parser import parse

def strip_positions(node):
    if isinstance(node, dict):
        return {k: strip_positions(v) for k, v in node.items() if k not in ("line", "column")}
    if isinstance(node, list):
        return [strip_positions(x) for x in node]
    return node

HEAD = "CLAN = {q0, q1}; CHAKRA = {a}; JUTSU = {(q0,a)->q1,(q1,a)->q0}; ORIGIN = q0; "
sugar = strip_positions(parse(tokenize(HEAD + "AWAKENED = q1;")))
full = strip_positions(parse(tokenize(HEAD + "AWAKENED = {q1};")))
print("AWAKENED = q1;    ->", sugar["declarations"][-1]["value"])
print("AWAKENED = {q1};  ->", full["declarations"][-1]["value"])
print("Identical ASTs:", sugar == full)
