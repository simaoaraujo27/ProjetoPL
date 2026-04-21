import ply.lex as lex
import re

# 1. keywords
reserved = {
    'PROGRAM': 'PROGRAM', 'END': 'END', 'INTEGER': 'INTEGER', 'REAL': 'REAL', 
    'DOUBLE': 'DOUBLE', 'PRECISION': 'PRECISION', 'COMPLEX': 'COMPLEX', 
    'LOGICAL': 'LOGICAL', 'CHARACTER': 'CHARACTER', 'DIMENSION': 'DIMENSION', 
    'PARAMETER': 'PARAMETER', 'DATA': 'DATA', 'PRINT': 'PRINT', 'READ': 'READ', 
    'IF': 'IF', 'THEN': 'THEN', 'ELSE': 'ELSE', 'ENDIF': 'ENDIF', 
    'DO': 'DO', 'CONTINUE': 'CONTINUE', 'GOTO': 'GOTO', 'CALL': 'CALL', 
    'SUBROUTINE': 'SUBROUTINE', 'FUNCTION': 'FUNCTION', 'RETURN': 'RETURN', 
    'MOD': 'MOD',
}

# 2. Lista de tokens
tokens = (
    'ID', 'INT_CONST', 'REAL_CONST', 'STRING_CONST',
    'PLUS', 'MINUS', 'DIVIDE', 'POW', 'ASSIGN', 'STAR',
    'EQ', 'NE', 'GT', 'GE', 'LT', 'LE',
    'AND', 'OR', 'NOT', 'TRUE', 'FALSE',
    'LPAREN', 'RPAREN', 'COMMA', 'COLON'
) + tuple(reserved.values())

# 3. Operadores e Símbolos
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

# 4. Comentários (ignorar)
def t_COMMENT(t):
    r'^[C\*c].*|!.*'
    pass

# 5. Identificadores (com verificação de keywords)
def t_ID(t):
    r'[a-zA-Z][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value.upper(), 'ID')
    return t

# 6. Constantes
def t_REAL_CONST(t):
    r'(\d+\.\d*|\.\d+)([eEdD][-+]?\d+)?|\d+[eEdD][-+]?\d+'
    t.value = float(t.value.replace('D', 'E').replace('d', 'e'))
    return t

def t_INT_CONST(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING_CONST(t):
    r"\'([^\\\']|(\\.))*\'"
    t.value = t.value[1:-1].replace("''", "'")
    return t

# 7. Regras de controlo
t_ignore = ' \t\r'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

class LexError(Exception):
    pass

def t_error(t):
    raise LexError(f"Carácter ilegal: {t.value[0]} na linha {t.lexer.lineno}")

# re.IGNORECASE: Fortran não distingue maiúsculas/minúsculas
# re.MULTILINE: Necessário para o ^ detetar início de linha nos comentários
lexer = lex.lex(reflags=re.IGNORECASE | re.MULTILINE)

# Função para testar o analisador léxico
def test(data):
    lexer.input(data)
    while True:
        try:
            tok = lexer.token()
            if not tok:
                break
            print(tok)
        except LexError as e:
            print(e)
            break

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            test(f.read())
    else:
        # Teste com o exemplo simples do Olá Mundo
        data = "PROGRAM HELLO\nPRINT *, 'Ola, Mundo!'\nEND"
        test(data)
