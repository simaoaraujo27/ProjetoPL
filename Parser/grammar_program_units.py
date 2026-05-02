from .ast_nodes import Node


def p_start(p):
    r"start : optional_newlines program_unit_list optional_newlines"
    p[0] = p[2]


def p_optional_newlines(p):
    r"""
    optional_newlines : optional_newlines NEWLINE
                      | empty
    """
    pass


def p_program_unit_list(p):
    r"""
    program_unit_list : program_unit_list optional_newlines program_unit
                      | program_unit
    """
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


def p_program_unit(p):
    r"""
    program_unit : main_program
                 | subroutine_definition
                 | function_definition
    """
    p[0] = p[1]


def p_main_program(p):
    r"main_program : PROGRAM ID NEWLINE statement_list END"
    p[0] = Node("MainProgram", value=p[2], children=p[4], lineno=p.lineno(1))


def p_subroutine_definition(p):
    r"subroutine_definition : SUBROUTINE ID LPAREN param_list_opt RPAREN NEWLINE statement_list END"
    p[0] = Node("SubroutineDef", value=p[2], children=[p[4], p[7]], lineno=p.lineno(1))


def p_function_definition(p):
    r"function_definition : type FUNCTION ID LPAREN param_list_opt RPAREN NEWLINE statement_list END"
    p[0] = Node(
        "FunctionDef",
        value={"type": p[1], "name": p[3]},
        children=[p[5], p[8]],
        lineno=p.lineno(2),
    )


def p_param_list_opt(p):
    r"""
    param_list_opt : param_list
                   | empty
    """
    p[0] = p[1] if p[1] else []


def p_param_list(p):
    r"""
    param_list : param_list COMMA ID
               | ID
    """
    if len(p) == 4:
        p[0] = p[1] + [Node("ID", value=p[3], lineno=p.lineno(3))]
    else:
        p[0] = [Node("ID", value=p[1], lineno=p.lineno(1))]


def p_statement_list(p):
    r"""
    statement_list : statement_list statement_entry
                   | empty
    """
    if len(p) == 3:
        if p[1] is None:
            p[1] = []
        if p[2] is not None:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = p[1]
    else:
        p[0] = []


def p_statement_entry(p):
    r"""
    statement_entry : statement NEWLINE
                    | NEWLINE
    """
    if len(p) == 3:
        p[0] = p[1]
    else:
        p[0] = None
