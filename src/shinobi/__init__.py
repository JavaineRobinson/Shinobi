"""Shinobi: a spell-themed language for describing deterministic finite automata.

Stages, in order:
    lexer.tokenize   source text  -> tokens
    parser.parse     tokens       -> AST
    semantic.analyze AST          -> list of semantic errors
    semantic.build_dfa AST        -> validated DFA (and semantic.simulate runs it)
    render.to_dot / to_svg  DFA   -> state diagram
pipeline.run(source) runs them all and returns one result; cli and app are built on it.
"""

__version__ = "0.2.0"

from .pipeline import run  # noqa: E402,F401  (the one-call API)
