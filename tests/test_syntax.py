"""Syntax stage: converted from the original run_tests.py.

File prefix says what each fixture should produce at the lexer/parser stage:
    valid_*, sem_*  -> parses fine (sem_ files are rejected later, by semantics)
    lex_*           -> LexicalError
    syn_*           -> ShinobiSyntaxError
"""
from pathlib import Path

import pytest

from shinobi.lexer import LexicalError, tokenize
from shinobi.parser import ShinobiSyntaxError, parse

FIXTURES = Path(__file__).parent / "fixtures"
EXPECTED = {"valid": "ok", "sem": "ok", "lex": "lex", "syn": "syntax"}


def run(path):
    source = path.read_text(encoding="utf-8")
    try:
        tokens = tokenize(source, path.name)
    except LexicalError:
        return "lex"
    try:
        parse(tokens)
    except ShinobiSyntaxError:
        return "syntax"
    return "ok"


@pytest.mark.parametrize("path", sorted(FIXTURES.glob("*.shinobi")), ids=lambda p: p.name)
def test_fixture_stage(path):
    want = EXPECTED[path.name.split("_")[0]]
    assert run(path) == want
