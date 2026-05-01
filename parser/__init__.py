import ply.yacc as yacc

from lexer import lexer, tokens

from .ast_nodes import Node
from .grammar_program_units import *  # noqa: F401,F403
from .grammar_declarations import *  # noqa: F401,F403
from .grammar_statements import *  # noqa: F401,F403
from .grammar_expressions import *  # noqa: F401,F403


precedence = (
    ("left", "OR"),
    ("left", "AND"),
    ("right", "NOT"),
    ("left", "EQ", "NE", "GT", "GE", "LT", "LE"),
    ("left", "PLUS", "MINUS"),
    ("left", "STAR", "DIVIDE"),
    ("right", "POW"),
    ("right", "UMINUS"),
)

start = "start"


def p_empty(p):
    r"empty :"
    pass


class ParseError(Exception):
    pass


def p_error(p):
    if p:
        raise ParseError(f"Erro sintático em '{p.value}', linha {p.lineno}")
    raise ParseError("Erro sintático no fim do ficheiro")


parser = yacc.yacc(write_tables=False, debug=False)


def parse_code(data):
    lexer.lineno = 1
    return parser.parse(data, lexer=lexer)


__all__ = ["Node", "ParseError", "parse_code", "parser"]
