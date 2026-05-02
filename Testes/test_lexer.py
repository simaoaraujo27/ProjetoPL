import unittest

from Lexer.lexer import LexError, lexer


def lex_all(code):
    lexer.lineno = 1
    lexer.input(code)
    tokens = []

    while True:
        token = lexer.token()
        if not token:
            break
        tokens.append(token)

    return tokens


class TestLexer(unittest.TestCase):
    def test_reconhece_keywords_e_identificadores(self):
        tokens = lex_all("PROGRAM teste\nINTEGER x\nEND\n")
        self.assertEqual(
            [token.type for token in tokens],
            ["PROGRAM", "ID", "NEWLINE", "INTEGER", "ID", "NEWLINE", "END", "NEWLINE"],
        )
        self.assertEqual(tokens[1].value, "TESTE")
        self.assertEqual(tokens[4].value, "X")

    def test_reconhece_end_if_e_go_to_compostos(self):
        tokens = lex_all("END IF\nGO TO 10\n")
        self.assertEqual(
            [token.type for token in tokens],
            ["ENDIF", "NEWLINE", "GOTO", "INT_CONST", "NEWLINE"],
        )

    def test_reconhece_constantes_inteiras_reais_e_string(self):
        tokens = lex_all("1 2.5 1.0D+2 'O''LA'\n")
        self.assertEqual(
            [token.type for token in tokens],
            ["INT_CONST", "REAL_CONST", "REAL_CONST", "STRING_CONST", "NEWLINE"],
        )
        self.assertEqual(tokens[0].value, 1)
        self.assertEqual(tokens[1].value, 2.5)
        self.assertEqual(tokens[2].value, 100.0)
        self.assertEqual(tokens[3].value, "O'LA")

    def test_reconhece_operadores_relacionais_e_logicos(self):
        tokens = lex_all(".EQ. .NE. .GT. .GE. .LT. .LE. .AND. .OR. .NOT. .TRUE. .FALSE.\n")
        self.assertEqual(
            [token.type for token in tokens],
            [
                "EQ",
                "NE",
                "GT",
                "GE",
                "LT",
                "LE",
                "AND",
                "OR",
                "NOT",
                "TRUE",
                "FALSE",
                "NEWLINE",
            ],
        )

    def test_reconhece_simbolos_basicos(self):
        tokens = lex_all("A = (B + C) * 2, D: E / F ** 3\n")
        self.assertEqual(
            [token.type for token in tokens],
            [
                "ID",
                "ASSIGN",
                "LPAREN",
                "ID",
                "PLUS",
                "ID",
                "RPAREN",
                "STAR",
                "INT_CONST",
                "COMMA",
                "ID",
                "COLON",
                "ID",
                "DIVIDE",
                "ID",
                "POW",
                "INT_CONST",
                "NEWLINE",
            ],
        )

    def test_ignora_comentarios(self):
        tokens = lex_all("PRINT *, 1 ! comentario\nEND\n")
        self.assertEqual(
            [token.type for token in tokens],
            ["PRINT", "STAR", "COMMA", "INT_CONST", "NEWLINE", "END", "NEWLINE"],
        )

    def test_atualiza_numero_de_linha(self):
        tokens = lex_all("PROGRAM A\nINTEGER X\nEND\n")
        self.assertEqual(tokens[0].lineno, 1)
        self.assertEqual(tokens[3].lineno, 2)
        self.assertEqual(tokens[6].lineno, 3)

    def test_lanca_erro_em_caractere_ilegal(self):
        lexer.lineno = 1
        lexer.input("PROGRAM A\n@\nEND\n")

        with self.assertRaises(LexError):
            while lexer.token():
                pass


if __name__ == "__main__":
    unittest.main()
