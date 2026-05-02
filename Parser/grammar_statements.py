from .ast_nodes import Node


def p_statement(p):
    r"""
    statement : label_opt declaration
              | label_opt assignment
              | label_opt print_stmt
              | label_opt write_stmt
              | label_opt read_stmt
              | label_opt if_stmt
              | label_opt arithmetic_if_stmt
              | label_opt do_stmt
              | label_opt continue_stmt
              | label_opt goto_stmt
              | label_opt computed_goto_stmt
              | label_opt call_stmt
              | label_opt return_stmt
              | label_opt stop_stmt
              | label_opt pause_stmt
              | label_opt dimension_stmt
              | label_opt parameter_stmt
              | label_opt data_stmt
    """
    p[0] = Node("Statement", value=p[1], children=[p[2]], lineno=getattr(p[2], "lineno", None))


def p_stop_stmt(p):
    r"""
    stop_stmt : STOP INT_CONST
              | STOP STRING_CONST
              | STOP
    """
    p[0] = Node("Stop", value=p[2] if len(p) > 2 else None, lineno=p.lineno(1))


def p_pause_stmt(p):
    r"""
    pause_stmt : PAUSE INT_CONST
               | PAUSE STRING_CONST
               | PAUSE
    """
    p[0] = Node("Pause", value=p[2] if len(p) > 2 else None, lineno=p.lineno(1))


def p_arithmetic_if_stmt(p):
    r"arithmetic_if_stmt : IF LPAREN expr RPAREN INT_CONST COMMA INT_CONST COMMA INT_CONST"
    p[0] = Node("ArithmeticIf", value=[p[5], p[7], p[9]], children=[p[3]], lineno=p.lineno(1))


def p_computed_goto_stmt(p):
    r"computed_goto_stmt : GOTO LPAREN label_list RPAREN comma_opt expr"
    p[0] = Node("ComputedGoto", value=p[3], children=[p[6]], lineno=p.lineno(1))


def p_label_list(p):
    r"""
    label_list : label_list COMMA INT_CONST
               | INT_CONST
    """
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


def p_label_opt(p):
    r"""
    label_opt : INT_CONST
              | empty
    """
    p[0] = p[1]


def p_assignment(p):
    r"""
    assignment : ID ASSIGN expr
               | ID LPAREN arg_list RPAREN ASSIGN expr
    """
    if len(p) == 4:
        p[0] = Node("Assignment", value=p[1], children=[p[3]], lineno=p.lineno(1))
    else:
        p[0] = Node("ArrayAssignment", value=p[1], children=[p[3], p[6]], lineno=p.lineno(1))


def p_comma_opt(p):
    r"""
    comma_opt : COMMA
              | empty
    """
    pass


def p_print_stmt(p):
    r"""
    print_stmt : PRINT STAR comma_opt print_list
               | PRINT STAR
    """
    if len(p) == 5:
        p[0] = Node("Print", children=p[4], lineno=p.lineno(1))
    else:
        p[0] = Node("Print", children=[], lineno=p.lineno(1))


def p_print_list(p):
    r"""
    print_list : print_list COMMA expr
               | expr
    """
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


def p_write_stmt(p):
    r"""
    write_stmt : WRITE LPAREN io_unit COMMA io_format RPAREN print_list
               | WRITE LPAREN io_unit COMMA io_format RPAREN
    """
    if len(p) == 8:
        p[0] = Node("Write", value={"unit": p[3], "fmt": p[5]}, children=p[7], lineno=p.lineno(1))
    else:
        p[0] = Node("Write", value={"unit": p[3], "fmt": p[5]}, lineno=p.lineno(1))


def p_io_unit(p):
    r"""
    io_unit : STAR
            | INT_CONST
            | ID
    """
    p[0] = p[1]


def p_io_format(p):
    r"""
    io_format : STAR
              | INT_CONST
              | ID
    """
    p[0] = p[1]


def p_read_list(p):
    r"""
    read_list : read_list COMMA read_item
              | read_item
    """
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


def p_read_item(p):
    r"""
    read_item : ID
              | ID LPAREN arg_list RPAREN
    """
    if len(p) == 2:
        p[0] = Node("ID", value=p[1], lineno=p.lineno(1))
    else:
        p[0] = Node("ArrayAccess", value=p[1], children=p[3], lineno=p.lineno(1))


def p_read_stmt(p):
    r"""
    read_stmt : READ STAR comma_opt read_list
              | READ LPAREN io_unit COMMA io_format RPAREN read_list
              | READ LPAREN io_unit COMMA io_format RPAREN
    """
    if len(p) == 5:
        p[0] = Node("Read", children=p[4], lineno=p.lineno(1))
    elif len(p) == 8:
        p[0] = Node("Read", value={"unit": p[3], "fmt": p[5]}, children=p[7], lineno=p.lineno(1))
    else:
        p[0] = Node("Read", value={"unit": p[3], "fmt": p[5]}, lineno=p.lineno(1))


def p_if_stmt(p):
    r"""
    if_stmt : IF LPAREN expr RPAREN THEN statement_list ELSE statement_list ENDIF
            | IF LPAREN expr RPAREN THEN statement_list ENDIF
            | IF LPAREN expr RPAREN statement
    """
    if len(p) == 10:
        p[0] = Node("If", children=[p[3], p[6], p[8]], lineno=p.lineno(1))
    elif len(p) == 8:
        p[0] = Node("If", children=[p[3], p[6]], lineno=p.lineno(1))
    else:
        p[0] = Node("LogicalIf", children=[p[3], p[5]], lineno=p.lineno(1))


def p_do_stmt(p):
    r"""
    do_stmt : DO INT_CONST comma_opt ID ASSIGN expr COMMA expr
            | DO INT_CONST comma_opt ID ASSIGN expr COMMA expr COMMA expr
    """
    if len(p) == 9:
        p[0] = Node("Do", value={"label": p[2], "var": p[4]}, children=[p[6], p[8]], lineno=p.lineno(1))
    else:
        p[0] = Node("Do", value={"label": p[2], "var": p[4]}, children=[p[6], p[8], p[10]], lineno=p.lineno(1))


def p_continue_stmt(p):
    r"continue_stmt : CONTINUE"
    p[0] = Node("Continue", lineno=p.lineno(1))


def p_goto_stmt(p):
    r"goto_stmt : GOTO INT_CONST"
    p[0] = Node("Goto", value=p[2], lineno=p.lineno(1))


def p_call_stmt(p):
    r"call_stmt : CALL ID LPAREN arg_list_opt RPAREN"
    p[0] = Node("Call", value=p[2], children=p[4], lineno=p.lineno(1))


def p_return_stmt(p):
    r"return_stmt : RETURN"
    p[0] = Node("Return", lineno=p.lineno(1))
