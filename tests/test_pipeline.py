"""pipeline.run(): one call, one result, used by the web IDE."""
import shutil
from pathlib import Path

import pytest

from shinobi.pipeline import run

FIXTURES = Path(__file__).parent / "fixtures"


def source(name):
    return (FIXTURES / name).read_text(encoding="utf-8")


@pytest.mark.parametrize("name,stage", [
    ("lex_01_illegal_char.shinobi", "lexical"),
    ("syn_01_missing_semicolon.shinobi", "syntax"),
    ("sem_missing_transition.shinobi", "semantic"),
])
def test_errors_are_tagged_with_their_stage_and_position(name, stage):
    result = run(source(name))
    assert result["ok"] is False and result["svg"] is None
    assert result["errors"] and all(e["stage"] == stage for e in result["errors"])
    assert all(e["line"] >= 1 and e["column"] >= 1 for e in result["errors"])


def test_semantic_errors_are_all_collected():
    result = run(source("sem_symbol_undeclared.shinobi"))
    assert len(result["errors"]) == 2


@pytest.mark.skipif(shutil.which("dot") is None, reason="Graphviz not installed (brew install graphviz)")
def test_valid_program_is_drawn_and_simulated():
    pytest.importorskip("graphviz")
    result = run(source("valid_brief_example.shinobi"), "aa")
    assert result["ok"] and result["svg"].startswith("<svg")
    assert result["dfa"]["name"] == "M"
    assert result["simulation"]["accepted"] is True


def test_stage_tokens_and_ast_are_reported():
    bad = run(source("syn_01_missing_semicolon.shinobi"), draw=False)
    assert bad["stage"] == "syntax" and bad["tokens"] and bad["ast"] is None
    good = run(source("valid_example.shinobi"), draw=False)
    assert good["stage"] == "done" and good["ast"]["name"]["name"] == "M"
    assert good["dot"].startswith("digraph")


def test_trace_follows_the_input_and_batch_tests_many():
    result = run(source("valid_brief_example.shinobi"), "ab", draw=False, test_inputs=["aa", "bb", "c"])
    assert result["simulation"]["trace"] == [
        {"from": "q1", "symbol": "a", "to": "q2"},
        {"from": "q2", "symbol": "b", "to": "Trap"},
    ]
    assert [b["accepted"] for b in result["batch"]] == [True, True, False]


def test_missing_graphviz_is_a_warning_not_an_error(monkeypatch):
    """Without Graphviz the program is still valid; the IDE draws the DOT in the browser."""
    import shinobi.pipeline as pipeline

    class ExecutableNotFound(Exception):
        pass

    def no_graphviz(dfa, title=None):
        raise ExecutableNotFound("failed to execute 'dot'")

    monkeypatch.setattr(pipeline, "to_svg", no_graphviz)
    result = pipeline.run(source("valid_example.shinobi"))
    assert result["ok"] and result["errors"] == []
    assert result["svg"] is None and result["dot"].startswith("digraph")
    assert "brew install graphviz" in result["warnings"][0]
