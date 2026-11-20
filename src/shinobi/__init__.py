"""Shinobi: a spell-themed language for describing deterministic finite automata.

Pipeline: source text -> lexer.tokenize() -> parser.parse() -> semantic.analyze()
          -> semantic.build_dfa() -> (rendering, still to be built)
"""

__version__ = "0.1.0"
