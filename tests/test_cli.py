"""The `shinobi` command line: exit codes and output."""
from pathlib import Path

import pytest

from shinobi.cli import main

ROOT = Path(__file__).parent.parent
FIXTURES = Path(__file__).parent / "fixtures"


def exit_code(*argv):
    with pytest.raises(SystemExit) as info:
        main(list(argv))
    return info.value.code


def test_check_valid_program(capsys):
    main(["check", str(ROOT / "examples" / "even_as.shinobi")])
    assert "Valid DFA: EvenAs" in capsys.readouterr().out


def test_check_reports_errors_with_file_line_and_column(capsys):
    path = FIXTURES / "sem_origin_undeclared.shinobi"
    assert exit_code("check", str(path)) == 1
    assert f"{path}:8:10: semantic error: ORIGIN state 'q9'" in capsys.readouterr().err


def test_run_prints_the_verdict(capsys):
    main(["run", str(FIXTURES / "valid_brief_example.shinobi"), "aa"])
    assert "ACCEPTED" in capsys.readouterr().out


def test_render_dot_writes_a_file(tmp_path):
    out = tmp_path / "m.dot"
    main(["render", str(FIXTURES / "valid_example.shinobi"), "--dot", "-o", str(out)])
    assert out.read_text(encoding="utf-8").startswith("digraph DFA {")


def test_missing_file_is_a_usage_error():
    assert exit_code("check", "no_such_file.shinobi") == 2
