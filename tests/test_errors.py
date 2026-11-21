"""Error positions and messages that the IDE will rely on for highlighting."""
import pytest

from shinobi.lexer import LexicalError, tokenize
from shinobi.parser import ShinobiSyntaxError, parse


def test_lexical_error_reports_character_and_position():
    with pytest.raises(LexicalError) as info:
        tokenize("M = {\n  @")
    err = info.value
    assert (err.line, err.column) == (2, 3)
    assert "'@'" in err.message


def test_eof_error_points_just_after_last_token():
    source = "M = { ORIGIN = q0; }"
    with pytest.raises(ShinobiSyntaxError) as info:
        parse(tokenize(source))
    assert info.value.column == len(source) + 1
    assert "found end of file" in info.value.message


@pytest.mark.parametrize("word", ["ε", "eps", "epsilon"])
def test_epsilon_spellings_are_reserved(word):
    assert tokenize(word)[0]["type"] == "EPSILON"


@pytest.mark.parametrize("word", ["epsilon2", "CLANS", "q0"])
def test_longer_words_are_identifiers(word):
    assert tokenize(word)[0]["type"] == "IDENTIFIER"
