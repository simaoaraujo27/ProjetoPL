from .ast_nodes import Node


def p_declaration(p):
    r"declaration : type id_list_decl"
    p[0] = Node("Declaration", value=p[1], children=p[2], lineno=getattr(p[2][0], "lineno", None))


def p_type(p):
    r"""
    type : INTEGER
         | REAL
         | LOGICAL
         | CHARACTER
         | COMPLEX
         | DOUBLE PRECISION
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = "DOUBLE PRECISION"


def p_id_list_decl(p):
    r"""
    id_list_decl : id_list_decl COMMA id_decl
                 | id_decl
    """
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


def p_id_decl(p):
    r"""
    id_decl : ID LPAREN dim_list RPAREN
            | ID
    """
    if len(p) == 5:
        p[0] = Node("ArrayID", value=p[1], children=p[3], lineno=p.lineno(1))
    else:
        p[0] = Node("ID", value=p[1], lineno=p.lineno(1))


def p_dim_list(p):
    r"""
    dim_list : dim_list COMMA dim_spec
             | dim_spec
    """
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


def p_dim_spec(p):
    r"""
    dim_spec : INT_CONST COLON INT_CONST
             | INT_CONST
             | ID
    """
    if len(p) == 4:
        p[0] = Node("Range", value=(p[1], p[3]), lineno=p.lineno(1))
    else:
        p[0] = p[1]


def p_dimension_stmt(p):
    r"dimension_stmt : DIMENSION id_list_decl"
    p[0] = Node("Dimension", children=p[2], lineno=p.lineno(1))


def p_parameter_stmt(p):
    r"parameter_stmt : PARAMETER LPAREN param_assign_list RPAREN"
    p[0] = Node("Parameter", children=p[3], lineno=p.lineno(1))


def p_param_assign_list(p):
    r"""
    param_assign_list : param_assign_list COMMA param_assign
                      | param_assign
    """
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


def p_param_assign(p):
    r"param_assign : ID ASSIGN expr"
    p[0] = Node("ParamAssign", value=p[1], children=[p[3]], lineno=p.lineno(1))


def p_data_stmt(p):
    r"data_stmt : DATA data_set_list"
    p[0] = Node("Data", children=p[2], lineno=p.lineno(1))


def p_data_set_list(p):
    r"""
    data_set_list : data_set data_set_list_tail
    """
    p[0] = [p[1]] + p[2]


def p_data_set_list_tail(p):
    r"""
    data_set_list_tail : COMMA data_set data_set_list_tail
                       | empty
    """
    if len(p) == 4:
        p[0] = [p[2]] + p[3]
    else:
        p[0] = []


def p_data_set(p):
    r"data_set : id_list_decl DIVIDE val_list DIVIDE"
    p[0] = Node("DataSet", children=[p[1], p[3]], lineno=getattr(p[1][0], "lineno", None))


def p_val_list(p):
    r"""
    val_list : val_list COMMA data_val
             | data_val
    """
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


def p_data_val(p):
    r"""
    data_val : INT_CONST STAR constant
             | constant
    """
    if len(p) == 4:
        p[0] = Node("RepeatValue", value=p[1], children=[p[3]], lineno=p.lineno(1))
    else:
        p[0] = p[1]


def p_constant_id(p):
    r"constant : ID"
    p[0] = Node("ID", value=p[1], lineno=p.lineno(1))


def p_constant(p):
    r"""
    constant : INT_CONST
             | REAL_CONST
             | STRING_CONST
             | TRUE
             | FALSE
             | PLUS constant
             | MINUS constant
    """
    if len(p) == 2:
        p[0] = Node("Literal", value=p[1], lineno=p.lineno(1))
    else:
        p[0] = Node("UnOp", value=p[1], children=[p[2]], lineno=p.lineno(1))
