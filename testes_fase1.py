import unittest

from lexer import LexError, lexer
from parser import ParseError, parse_code
from semantic import SemanticAnalyzer, SemanticError


def analyze_code(code):
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    scope = analyzer.analyze(ast)
    return ast, analyzer, scope


class TestFase1LexicoSintaticoSemantico(unittest.TestCase):
    def test_lexer_ignora_comentario_inline_com_exclamacao(self):
        code = "PROGRAM A\nPRINT *, 1 ! comentario\nEND\n"
        lexer.lineno = 1
        lexer.input(code)
        token_types = []

        while True:
            token = lexer.token()
            if not token:
                break
            token_types.append(token.type)

        self.assertIn("PRINT", token_types)
        self.assertIn("INT_CONST", token_types)
        self.assertNotIn("COMMENT", token_types)

    def test_lexer_lanca_erro_em_caractere_ilegal(self):
        lexer.lineno = 1
        lexer.input("PROGRAM A\n@\nEND\n")

        with self.assertRaises(LexError):
            while lexer.token():
                pass

    def test_parser_aceita_logical_if(self):
        code = """
PROGRAM A
LOGICAL L
L = .TRUE.
IF (L) PRINT *, 1
END
"""
        ast = parse_code(code)
        self.assertTrue(ast)

    def test_parser_aceita_if_then_else_endif(self):
        code = """
PROGRAM A
LOGICAL L
L = .TRUE.
IF (L) THEN
PRINT *, 1
ELSE
PRINT *, 0
ENDIF
END
"""
        ast = parse_code(code)
        self.assertTrue(ast)

    def test_parser_distingue_chamada_funcao_de_array(self):
        code = """
PROGRAM A
INTEGER X, Y(5), Z
X = 1
Y(1) = 2
Z = MOD(X, Y(1))
END
"""
        ast = parse_code(code)
        self.assertTrue(ast)

    def test_semantica_aceita_do_com_continue(self):
        code = """
PROGRAM A
INTEGER I
DO 10 I = 1, 5
10 CONTINUE
END
"""
        _, _, scope = analyze_code(code)
        self.assertIn("A", scope.children)

    def test_semantica_rejeita_do_sem_continue_na_label(self):
        code = """
PROGRAM A
INTEGER I
DO 10 I = 1, 5
10 PRINT *, I
END
"""
        with self.assertRaises(SemanticError):
            analyze_code(code)

    def test_semantica_rejeita_variavel_nao_inicializada(self):
        code = """
PROGRAM A
INTEGER X, Y
Y = X
END
"""
        with self.assertRaises(SemanticError):
            analyze_code(code)

    def test_semantica_aceita_funcao_e_subrotina(self):
        code = """
PROGRAM MAIN
INTEGER N, R
N = 5
R = DOBRO(N)
CALL MOSTRA(R)
END

INTEGER FUNCTION DOBRO(X)
INTEGER X
DOBRO = X + X
RETURN
END

SUBROUTINE MOSTRA(V)
INTEGER V
PRINT *, V
RETURN
END
"""
        _, _, scope = analyze_code(code)
        self.assertIn("DOBRO", scope.symbols)
        self.assertIn("MOSTRA", scope.symbols)

    def test_semantica_rejeita_dois_programs_principais(self):
        code = """
PROGRAM A
END
PROGRAM B
END
"""
        ast = parse_code(code)
        with self.assertRaises(SemanticError):
            SemanticAnalyzer().analyze(ast)


if __name__ == "__main__":
    unittest.main(verbosity=2)
