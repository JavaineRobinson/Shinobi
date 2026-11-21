"""Rendering stage: DOT text (always) and SVG (when Graphviz is installed)."""
import shutil
from pathlib import Path

import pytest

from shinobi.lexer import tokenize
from shinobi.parser import parse
from shinobi.render import to_dot, to_svg
from shinobi.semantic import build_dfa

FIXTURES = Path(__file__).parent / "fixtures"


def dfa_from(name):
    return build_dfa(parse(tokenize((FIXTURES / name).read_text(encoding="utf-8"))))


def test_accepting_states_are_double_circles():
    dot = to_dot(dfa_from("valid_brief_example.shinobi"))
    assert '"q4" [shape=doublecircle]' in dot
    assert '"q1" [shape=circle]' in dot


def test_start_state_gets_an_entry_arrow():
    assert '__start -> "q1"' in to_dot(dfa_from("valid_brief_example.shinobi"))


def test_parallel_transitions_are_merged_into_one_arrow():
    dot = to_dot(dfa_from("valid_brief_example.shinobi"))
    assert '"Trap" -> "Trap" [label="a, b, c"]' in dot


def test_numeric_state_and_symbol_names_are_quoted():
    assert '[label="0"]' in to_dot(dfa_from("valid_02_numeric_symbols.shinobi"))


@pytest.mark.skipif(shutil.which("dot") is None, reason="Graphviz not installed (brew install graphviz)")
def test_svg_is_produced():
    pytest.importorskip("graphviz")
    svg = to_svg(dfa_from("valid_brief_example.shinobi"), "M")
    assert "<svg" in svg and "Trap" in svg
