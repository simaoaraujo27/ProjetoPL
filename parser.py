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
    'start : program_unit_list'
    p[0] = p[1]

def p_program_unit_list(p):
    '''program_unit_list : program_unit program_unit_list
                         | program_unit'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

def p_program_unit(p):
    '''program_unit : main_program
                    | subroutine_definition
                    | function_definition'''
    p[0] = p[1]

def p_main_program(p):
    'main_program : PROGRAM ID statement_list END'
    p[0] = Node('MainProgram', value=p[2], children=p[3])

def p_subroutine_definition(p):
    'subroutine_definition : SUBROUTINE ID LPAREN param_list RPAREN statement_list END'
    p[0] = Node('SubroutineDef', value=p[2], children=[p[4], p[6]])

def p_function_definition(p):
    'function_definition : type FUNCTION ID LPAREN param_list RPAREN statement_list END'
    p[0] = Node('FunctionDef', value={'type': p[1], 'name': p[3]}, children=[p[5], p[7]])

def p_param_list(p):
    '''param_list : ID COMMA param_list
                  | ID
                  | empty'''
    if len(p) == 4:
        p[0] = [Node('ID', value=p[1])] + p[3]
    elif len(p) == 2 and p[1] is not None:
        p[0] = [Node('ID', value=p[1])]
    else:
        p[0] = []

def p_statement_list(p):
    '''statement_list : statement statement_list
                      | empty'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []

def p_statement(p):
    '''statement : label_opt declaration
                 | label_opt assignment
                 | label_opt print_stmt
                 | label_opt read_stmt
                 | label_opt if_stmt
                 | label_opt do_stmt
                 | label_opt continue_stmt
                 | label_opt goto_stmt
                 | label_opt call_stmt
                 | label_opt return_stmt'''
    p[0] = Node('Statement', value=p[1], children=[p[2]])

def p_label_opt(p):
    '''label_opt : INT_CONST
                 | empty'''
    p[0] = p[1]

# --- Declarações ---

def p_declaration(p):
    '''declaration : type id_list_decl'''
    p[0] = Node('Declaration', value=p[1], children=p[2])

def p_type(p):
    '''type : INTEGER
            | REAL
            | LOGICAL
            | CHARACTER'''
    p[0] = p[1]

def p_id_list_decl(p):
    '''id_list_decl : id_decl COMMA id_list_decl
                    | id_decl'''
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = [p[1]]

def p_id_decl(p):
    '''id_decl : ID LPAREN INT_CONST RPAREN
               | ID'''
    if len(p) == 5:
        p[0] = Node('ArrayID', value=p[1], children=[p[3]])
    else:
        p[0] = Node('ID', value=p[1])

# --- Comandos ---

def p_assignment(p):
    '''assignment : ID ASSIGN expr
                  | ID LPAREN expr RPAREN ASSIGN expr'''
    if len(p) == 4:
        p[0] = Node('Assignment', value=p[1], children=[p[3]])
    else:
        p[0] = Node('ArrayAssignment', value=p[1], children=[p[3], p[6]])

def p_print_stmt(p):
    'print_stmt : PRINT STAR COMMA print_list'
    p[0] = Node('Print', children=p[4])

def p_print_list(p):
    '''print_list : expr COMMA print_list
                  | expr'''
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = [p[1]]

def p_read_stmt(p):
    '''read_stmt : READ STAR COMMA ID
                 | READ STAR COMMA ID LPAREN expr RPAREN'''
    if len(p) == 5:
        p[0] = Node('Read', value=p[4])
    else:
        p[0] = Node('ArrayRead', value=p[4], children=[p[6]])

def p_if_stmt(p):
    '''if_stmt : IF LPAREN expr RPAREN THEN statement_list ELSE statement_list ENDIF
               | IF LPAREN expr RPAREN THEN statement_list ENDIF'''
    if len(p) == 10:
        p[0] = Node('If', children=[p[3], p[6], p[8]])
    else:
        p[0] = Node('If', children=[p[3], p[6]])

def p_do_stmt(p):
    'do_stmt : DO INT_CONST ID ASSIGN expr COMMA expr'
    p[0] = Node('Do', value={'label': p[2], 'var': p[3]}, children=[p[5], p[7]])

def p_continue_stmt(p):
    'continue_stmt : CONTINUE'
    p[0] = Node('Continue')

def p_goto_stmt(p):
    'goto_stmt : GOTO INT_CONST'
    p[0] = Node('Goto', value=p[2])

def p_call_stmt(p):
    'call_stmt : CALL ID LPAREN arg_list RPAREN'
    p[0] = Node('Call', value=p[2], children=p[4])

def p_return_stmt(p):
    'return_stmt : RETURN'
    p[0] = Node('Return')

# --- Expressões ---

def p_expr_binop(p):
    '''expr : expr PLUS expr
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
            | expr OR expr'''
    p[0] = Node('BinOp', value=p[2], children=[p[1], p[3]])

def p_expr_uminus(p):
    'expr : MINUS expr %prec UMINUS'
    p[0] = Node('UnOp', value='-', children=[p[2]])

def p_expr_not(p):
    'expr : NOT expr'
    p[0] = Node('UnOp', value='.NOT.', children=[p[2]])

def p_expr_group(p):
    'expr : LPAREN expr RPAREN'
    p[0] = p[2]

def p_expr_func_call(p):
    '''expr : ID LPAREN arg_list RPAREN
            | MOD LPAREN arg_list RPAREN'''
    p[0] = Node('FuncCall', value=p[1], children=p[3])

def p_expr_primary(p):
    '''expr : ID
            | INT_CONST
            | REAL_CONST
            | STRING_CONST
            | TRUE
            | FALSE'''
    p[0] = Node('Literal', value=p[1])

def p_arg_list(p):
    '''arg_list : expr COMMA arg_list
                | expr
                | empty'''
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    elif len(p) == 2 and p[1] is not None:
        p[0] = [p[1]]
    else:
        p[0] = []

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    if p:
        print(f"Erro sintático em '{p.value}', linha {p.lineno}")
    else:
        print("Erro sintático no fim do ficheiro")

parser = yacc.yacc()

def parse_code(data):
    return parser.parse(data)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            result = parse_code(f.read())
            print(result)
    else:
        data = "PROGRAM HELLO\nPRINT *, 'Ola, Mundo!'\nEND"
        result = parse_code(data)
        print(result)
