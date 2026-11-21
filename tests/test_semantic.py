"""Semantic stage: converted from the original run_semantic_tests.py."""
from pathlib import Path

import pytest

from shinobi.lexer import tokenize
from shinobi.parser import parse
from shinobi.semantic import analyze, build_dfa, simulate

FIXTURES = Path(__file__).parent / "fixtures"

# file name -> text that must appear in an error message (None = no errors allowed)
EXPECTED = {
    "valid_example.shinobi": None,
    "valid_brief_example.shinobi": None,
    "valid_02_numeric_symbols.shinobi": None,
    "valid_03_comments_and_trap.shinobi": None,
    "valid_04_sugar.shinobi": None,
    "valid_05_empty_awakened.shinobi": None,
    "valid_06_one_line_format.shinobi": None,
    "sem_duplicate_clan.shinobi": "CLAN is declared more than once",
    "sem_missing_origin.shinobi": "ORIGIN is missing",
    "sem_wrong_order.shinobi": "JUTSU uses CHAKRA before it is declared",
    "sem_duplicate_state.shinobi": "'q0' is repeated in CLAN",
    "sem_origin_undeclared.shinobi": "ORIGIN state 'q9' is not declared in CLAN",
    "sem_awakened_undeclared.shinobi": "AWAKENED state 'q7' is not declared in CLAN",
    "sem_symbol_undeclared.shinobi": "symbol 'c' is not declared in CHAKRA",
    "sem_conflicting_transition.shinobi": "more than one transition for (q0, a)",
    "sem_repeated_transition.shinobi": "more than one transition for (q0, a)",
    "sem_missing_transition.shinobi": "missing transition for (q1, b)",
    "sem_12_state_symbol_clash.shinobi": "'a' is used as both a state and a symbol",
    "sem_target_undeclared.shinobi": "transition target 'q9' is not declared in CLAN",
    "sem_duplicate_symbol.shinobi": "'a' is repeated in CHAKRA",
    "sem_epsilon_symbol.shinobi": "epsilon 'ε' cannot be in CHAKRA",
    "sem_epsilon_transition.shinobi": "epsilon transition (q0, epsilon) is not allowed",
}


def errors_for(name):
    source = (FIXTURES / name).read_text(encoding="utf-8")
    return [e["message"] for e in analyze(parse(tokenize(source, name)))]


@pytest.mark.parametrize("name,expected", EXPECTED.items(), ids=list(EXPECTED))
def test_semantic_errors(name, expected):
    messages = errors_for(name)
    if expected is None:
        assert messages == []
    else:
        assert any(expected in m for m in messages), messages


@pytest.mark.parametrize("text,accepted", [("aa", True), ("ab", False), ("bb", True)])
def test_simulate_brief_example(text, accepted):
    source = (FIXTURES / "valid_brief_example.shinobi").read_text(encoding="utf-8")
    dfa = build_dfa(parse(tokenize(source)))
    assert simulate(dfa, text)[0] is accepted


def test_epsilon_gives_no_follow_on_errors():
    """One epsilon mistake should give one error, not a cascade."""
    assert len(errors_for("sem_epsilon_symbol.shinobi")) == 1
    assert len(errors_for("sem_epsilon_transition.shinobi")) == 1


def test_dfa_keeps_its_name():
    source = (FIXTURES / "valid_06_one_line_format.shinobi").read_text(encoding="utf-8")
    assert build_dfa(parse(tokenize(source)))["name"] == "M"
