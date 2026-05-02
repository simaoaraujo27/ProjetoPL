from .ast_nodes import Node


def p_expr_binop(p):
    r"""
    expr : expr PLUS expr
         | expr MINUS expr
         | expr STAR expr
         | expr DIVIDE expr
         | expr POW expr
         | expr EQ expr
         | expr NE expr
         | expr GT expr
         | expr GE expr
         | expr LT expr
         | expr LE expr
         | expr AND expr
         | expr OR expr
    """
    p[0] = Node("BinOp", value=p[2], children=[p[1], p[3]], lineno=getattr(p[1], "lineno", None))


def p_expr_uminus(p):
    r"expr : MINUS expr %prec UMINUS"
    p[0] = Node("UnOp", value="-", children=[p[2]], lineno=p.lineno(1))


def p_expr_not(p):
    r"expr : NOT expr"
    p[0] = Node("UnOp", value=".NOT.", children=[p[2]], lineno=p.lineno(1))


def p_expr_group(p):
    r"expr : LPAREN expr RPAREN"
    p[0] = p[2]


def p_expr_func_call(p):
    r"""
    expr : ID LPAREN arg_list_opt RPAREN
         | MOD LPAREN arg_list_opt RPAREN
    """
    p[0] = Node("CallOrArrayAccess", value=p[1], children=p[3], lineno=p.lineno(1))


def p_expr_primary_id(p):
    r"""
    expr : ID
    """
    p[0] = Node("ID", value=p[1], lineno=p.lineno(1))


def p_expr_primary_literal(p):
    r"""
    expr : INT_CONST
         | REAL_CONST
         | STRING_CONST
         | TRUE
         | FALSE
    """
    p[0] = Node("Literal", value=p[1], lineno=p.lineno(1))


def p_arg_list_opt(p):
    r"""
    arg_list_opt : arg_list
                 | empty
    """
    p[0] = p[1] if p[1] else []


def p_arg_list(p):
    r"""
    arg_list : arg_list COMMA arg_spec
             | arg_spec
    """
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


def p_arg_spec(p):
    r"""
    arg_spec : expr COLON expr
             | expr
    """
    if len(p) == 4:
        p[0] = Node("Slice", children=[p[1], p[3]], lineno=getattr(p[1], "lineno", None))
    else:
        p[0] = p[1]
