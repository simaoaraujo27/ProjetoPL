import ply.lex as lex
import re

# 1. Lista de tokens
tokens = (
    'PROGRAM', 'END', 'INTEGER', 'REAL', 'DOUBLE', 'PRECISION', 
    'COMPLEX', 'LOGICAL', 'CHARACTER', 'DIMENSION', 'PARAMETER', 
    'DATA', 'PRINT', 'READ', 'IF', 'THEN', 'ELSE', 'ENDIF', 
    'DO', 'CONTINUE', 'GOTO', 'CALL', 'SUBROUTINE', 'FUNCTION', 
    'RETURN', 'MOD',
    'ID', 'INT_CONST', 'REAL_CONST', 'STRING_CONST',
    'PLUS', 'MINUS', 'DIVIDE', 'POW', 'ASSIGN', 'STAR',
    'EQ', 'NE', 'GT', 'GE', 'LT', 'LE',
    'AND', 'OR', 'NOT', 'TRUE', 'FALSE',
    'LPAREN', 'RPAREN', 'COMMA', 'COLON'
)

# 2. Operadores e Símbolos
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_DIVIDE  = r'/'
t_POW     = r'\*\*'
t_ASSIGN  = r'='
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_COMMA   = r','
t_COLON   = r':'
t_STAR    = r'\*'

# 3. Palavras-chave como funções
def t_PROGRAM(t): r'PROGRAM'; return t
def t_END(t): r'END'; return t
def t_INTEGER(t): r'INTEGER'; return t
def t_REAL(t): r'REAL'; return t
def t_DOUBLE(t): r'DOUBLE'; return t
def t_PRECISION(t): r'PRECISION'; return t
def t_COMPLEX(t): r'COMPLEX'; return t
def t_LOGICAL(t): r'LOGICAL'; return t
def t_CHARACTER(t): r'CHARACTER'; return t
def t_DIMENSION(t): r'DIMENSION'; return t
def t_PARAMETER(t): r'PARAMETER'; return t
def t_DATA(t): r'DATA'; return t
def t_PRINT(t): r'PRINT'; return t
def t_READ(t): r'READ'; return t
def t_IF(t): r'IF'; return t
def t_THEN(t): r'THEN'; return t
def t_ELSE(t): r'ELSE'; return t
def t_ENDIF(t): r'ENDIF'; return t
def t_DO(t): r'DO'; return t
def t_CONTINUE(t): r'CONTINUE'; return t
def t_GOTO(t): r'GOTO'; return t
def t_CALL(t): r'CALL'; return t
def t_SUBROUTINE(t): r'SUBROUTINE'; return t
def t_FUNCTION(t): r'FUNCTION'; return t
def t_RETURN(t): r'RETURN'; return t
def t_MOD(t): r'MOD'; return t

# Operadores de comparação e lógicos do Fortran 77
def t_EQ(t): r'\.EQ\.'; return t
def t_NE(t): r'\.NE\.'; return t
def t_GT(t): r'\.GT\.'; return t
def t_GE(t): r'\.GE\.'; return t
def t_LT(t): r'\.LT\.'; return t
def t_LE(t): r'\.LE\.'; return t
def t_AND(t): r'\.AND\.'; return t
def t_OR(t): r'\.OR\.'; return t
def t_NOT(t): r'\.NOT\.'; return t
def t_TRUE(t): r'\.TRUE\.'; return t
def t_FALSE(t): r'\.FALSE\.'; return t

# 4. Comentários 
def t_COMMENT(t):
    r'^[C\*].*|!.*'
    pass

# 5. Identificadores (Nomes de variáveis, definidos após as keywords)
def t_ID(t):
    r'[a-zA-Z][a-zA-Z0-9]*'
    return t

# 6. Constantes com conversão de valor
def t_REAL_CONST(t):
    r'(\d+\.\d*|\.\d+)([eEdD][-+]?\d+)?|\d+[eEdD][-+]?\d+'
    # Fortran usa 'D' para double precision, Python float() precisa de 'E'
    t.value = float(t.value.replace('D', 'E').replace('d', 'e'))
    return t

def t_INT_CONST(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING_CONST(t):
    r"\'([^\\\']|(\\.))*\'"
    # Remove as plicas e trata escape de plicas duplas ''
    t.value = t.value[1:-1].replace("''", "'")
    return t

# 7. Regras de controlo
t_ignore = ' \t\r'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Carácter ilegal: {t.value[0]}")
    t.lexer.skip(1)


# re.IGNORECASE: Fortran não distingue maiúsculas/minúsculas
# re.MULTILINE: Necessário para o ^ detetar início de linha nos comentários
lexer = lex.lex(reflags=re.IGNORECASE | re.MULTILINE)

# Função para testar o analisador léxico
def test(data):
    lexer.input(data)
    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            test(f.read())
    else:
        # Teste com o exemplo simples do Olá Mundo
        data = "PROGRAM HELLO\nPRINT *, 'Ola, Mundo!'\nEND"
        test(data)
