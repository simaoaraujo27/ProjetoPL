import ply.yacc as yacc
from lexer import tokens

# --- Árvore de Sintaxe Abstrata (AST) ---

class Node:
    def __init__(self, type, children=None, value=None):
        self.type = type
        self.children = children if children else []
        self.value = value

    def __repr__(self):
        return f"Node({self.type}, value={self.value}, children={self.children})"

# --- Regras da Gramática ---

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
    ('left', 'EQ', 'NE', 'GT', 'GE', 'LT', 'LE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'STAR', 'DIVIDE'),
    ('right', 'POW'),
    ('right', 'UMINUS'),
)


def p_start(p):
    r"start : optional_newlines program_unit_list optional_newlines"
    p[0] = p[2]

# linhas vazias no inicio ou final do ficheiro, para permitir ficheiros com linhas em branco no inicio ou final
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
    r"main_program : PROGRAM ID NEWLINE statement_list END optional_newlines"
    p[0] = Node('MainProgram', value=p[2], children=p[4])

def p_subroutine_definition(p):
    r"subroutine_definition : SUBROUTINE ID LPAREN param_list_opt RPAREN NEWLINE statement_list END"
    p[0] = Node('SubroutineDef', value=p[2], children=[p[4], p[7]])

def p_function_definition(p):
    r"function_definition : type FUNCTION ID LPAREN param_list_opt RPAREN NEWLINE statement_list END"
    p[0] = Node('FunctionDef', value={'type': p[1], 'name': p[3]}, children=[p[5], p[8]])

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
        p[0] = p[1] + [Node('ID', value=p[3])]
    else:
        p[0] = [Node('ID', value=p[1])]

def p_statement_list(p):
    r"""
    statement_list : statement_list statement_entry
                   | empty
    """
    if len(p) == 3:
        if p[1] is None: p[1] = []
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
    p[0] = Node('Statement', value=p[1], children=[p[2]])

def p_stop_stmt(p):
    r"""
    stop_stmt : STOP INT_CONST
              | STOP STRING_CONST
              | STOP
    """
    p[0] = Node('Stop', value=p[2] if len(p) > 2 else None)

def p_pause_stmt(p):
    r"""
    pause_stmt : PAUSE INT_CONST
               | PAUSE STRING_CONST
               | PAUSE
    """
    p[0] = Node('Pause', value=p[2] if len(p) > 2 else None)

def p_arithmetic_if_stmt(p):
    r"arithmetic_if_stmt : IF LPAREN expr RPAREN INT_CONST COMMA INT_CONST COMMA INT_CONST"
    p[0] = Node('ArithmeticIf', value=[p[5], p[7], p[9]], children=[p[3]])

def p_computed_goto_stmt(p):
    r"computed_goto_stmt : GOTO LPAREN label_list RPAREN comma_opt expr"
    p[0] = Node('ComputedGoto', value=p[3], children=[p[6]])

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

# --- Declarações ---

def p_declaration(p):
    r"declaration : type id_list_decl"
    p[0] = Node('Declaration', value=p[1], children=p[2])

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
        p[0] = Node('ArrayID', value=p[1], children=p[3])
    else:
        p[0] = Node('ID', value=p[1])

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
        p[0] = Node('Range', value=(p[1], p[3]))
    else:
        p[0] = p[1]

# --- Comandos Extras ---

def p_dimension_stmt(p):
    r"dimension_stmt : DIMENSION id_list_decl"
    p[0] = Node('Dimension', children=p[2])

def p_parameter_stmt(p):
    r"parameter_stmt : PARAMETER LPAREN param_assign_list RPAREN"
    p[0] = Node('Parameter', children=p[3])

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
    p[0] = Node('ParamAssign', value=p[1], children=[p[3]])

def p_data_stmt(p):
    r"data_stmt : DATA data_set_list"
    p[0] = Node('Data', children=p[2])

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
    p[0] = Node('DataSet', children=[p[1], p[3]])

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
        p[0] = Node('RepeatValue', value=p[1], children=[p[3]])
    else:
        p[0] = p[1]

def p_constant_id(p):
    r"constant : ID"
    p[0] = Node('ID', value=p[1])

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
        p[0] = Node('Literal', value=p[1])
    else:
        p[0] = Node('UnOp', value=p[1], children=[p[2]])

# --- Comandos Base ---

def p_assignment(p):
    r"""
    assignment : ID ASSIGN expr
               | ID LPAREN arg_list RPAREN ASSIGN expr
    """
    if len(p) == 4:
        p[0] = Node('Assignment', value=p[1], children=[p[3]])
    else:
        p[0] = Node('ArrayAssignment', value=p[1], children=[p[3], p[6]])

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
        p[0] = Node('Print', children=p[4])
    else:
        p[0] = Node('Print', children=[])

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
        p[0] = Node('Write', value={'unit': p[3], 'fmt': p[5]}, children=p[7])
    else:
        p[0] = Node('Write', value={'unit': p[3], 'fmt': p[5]})

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
        p[0] = Node('ID', value=p[1])
    else:
        p[0] = Node('ArrayAccess', value=p[1], children=p[3])

def p_read_stmt(p):
    r"""
    read_stmt : READ STAR comma_opt read_list
              | READ LPAREN io_unit COMMA io_format RPAREN read_list
              | READ LPAREN io_unit COMMA io_format RPAREN
    """
    if len(p) == 5:
        p[0] = Node('Read', children=p[4])
    elif len(p) == 8:
        p[0] = Node('Read', value={'unit': p[3], 'fmt': p[5]}, children=p[7])
    else:
        p[0] = Node('Read', value={'unit': p[3], 'fmt': p[5]})

def p_if_stmt(p):
    r"""
    if_stmt : IF LPAREN expr RPAREN THEN statement_list ELSE statement_list ENDIF
            | IF LPAREN expr RPAREN THEN statement_list ENDIF
            | IF LPAREN expr RPAREN statement
    """
    if len(p) == 10:
        p[0] = Node('If', children=[p[3], p[6], p[8]])
    elif len(p) == 8:
        p[0] = Node('If', children=[p[3], p[6]])
    else:
        p[0] = Node('LogicalIf', children=[p[3], p[5]])

def p_do_stmt(p):
    r"""
    do_stmt : DO INT_CONST comma_opt ID ASSIGN expr COMMA expr
            | DO INT_CONST comma_opt ID ASSIGN expr COMMA expr COMMA expr
    """
    if len(p) == 9:
        p[0] = Node('Do', value={'label': p[2], 'var': p[4]}, children=[p[6], p[8]])
    else:
        p[0] = Node('Do', value={'label': p[2], 'var': p[4]}, children=[p[6], p[8], p[10]])

def p_continue_stmt(p):
    r"continue_stmt : CONTINUE"
    p[0] = Node('Continue')

def p_goto_stmt(p):
    r"goto_stmt : GOTO INT_CONST"
    p[0] = Node('Goto', value=p[2])

def p_call_stmt(p):
    r"call_stmt : CALL ID LPAREN arg_list_opt RPAREN"
    p[0] = Node('Call', value=p[2], children=p[4])

def p_return_stmt(p):
    r"return_stmt : RETURN"
    p[0] = Node('Return')

# --- Expressões ---

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
    p[0] = Node('BinOp', value=p[2], children=[p[1], p[3]])

def p_expr_uminus(p):
    r"expr : MINUS expr %prec UMINUS"
    p[0] = Node('UnOp', value='-', children=[p[2]])

def p_expr_not(p):
    r"expr : NOT expr"
    p[0] = Node('UnOp', value='.NOT.', children=[p[2]])

def p_expr_group(p):
    r"expr : LPAREN expr RPAREN"
    p[0] = p[2]

def p_expr_func_call(p):
    r"""
    expr : ID LPAREN arg_list_opt RPAREN
         | MOD LPAREN arg_list_opt RPAREN
    """
    p[0] = Node('CallOrArrayAccess', value=p[1], children=p[3])

def p_expr_primary_id(p):
    r"""
    expr : ID
    """
    p[0] = Node('ID', value=p[1])


def p_expr_primary_literal(p):
    r"""
    expr : INT_CONST
         | REAL_CONST
         | STRING_CONST
         | TRUE
         | FALSE
    """
    p[0] = Node('Literal', value=p[1])

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
        p[0] = Node('Slice', children=[p[1], p[3]])
    else:
        p[0] = p[1]

def p_empty(p):
    r"empty :"
    pass

class ParseError(Exception):
    pass

def p_error(p):
    if p:
        raise ParseError(f"Erro sintático em '{p.value}', linha {p.lineno}")
    else:
        raise ParseError("Erro sintático no fim do ficheiro")

parser = yacc.yacc(write_tables=False)

def parse_code(data):
    return parser.parse(data)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            try:
                result = parse_code(f.read())
                print(result)
                print("Parsing succeeded.")
            except ParseError as e:
                print(e)
    else:
        data = "PROGRAM HELLO\nPRINT *, 'Ola, Mundo!'\nEND"
        try:
            result = parse_code(data)
            print(result)
            print("Parsing succeeded.")
        except ParseError as e:
            print(e)
