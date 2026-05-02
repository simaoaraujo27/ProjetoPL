import unittest

from Parser import ParseError, parse_code


class TestParser(unittest.TestCase):
    def assert_parses(self, code):
        ast = parse_code(code)
        self.assertIsNotNone(ast)
        return ast

    def test_programa_minimo(self):
        ast = self.assert_parses(
            """
PROGRAM A
END
"""
        )
        if isinstance(ast, list):
            self.assertEqual(len(ast), 1)
            ast = ast[0]
        self.assertEqual(getattr(ast, "type", None), "MainProgram")

    def test_declaracoes_e_tipos(self):
        self.assert_parses(
            """
PROGRAM TIPOS
INTEGER I
REAL R
LOGICAL L
CHARACTER C
DOUBLE PRECISION D
END
"""
        )

    def test_if_logico(self):
        self.assert_parses(
            """
PROGRAM A
LOGICAL L
L = .TRUE.
IF (L) PRINT *, 1
END
"""
        )

    def test_if_then_else_endif(self):
        self.assert_parses(
            """
PROGRAM A
INTEGER X
X = 1
IF (X .LT. 10) THEN
PRINT *, X
ELSE
PRINT *, 0
ENDIF
END
"""
        )

    def test_do_continue(self):
        self.assert_parses(
            """
PROGRAM A
INTEGER I
DO 10 I = 1, 5
10 CONTINUE
END
"""
        )

    def test_arrays_e_mod(self):
        self.assert_parses(
            """
PROGRAM A
INTEGER X, Y(5), Z
X = 1
Y(1) = 2
Z = MOD(X, Y(1))
END
"""
        )

    def test_computed_goto(self):
        self.assert_parses(
            """
PROGRAM A
INTEGER I
I = 2
GOTO (10,20,30), I
10 CONTINUE
20 CONTINUE
30 CONTINUE
END
"""
        )

    def test_arithmetic_if(self):
        self.assert_parses(
            """
PROGRAM A
INTEGER X
X = 1
IF (X) 10, 20, 30
10 CONTINUE
20 CONTINUE
30 CONTINUE
END
"""
        )

    def test_function_e_subroutine(self):
        ast = self.assert_parses(
            """
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
        )
        self.assertIsInstance(ast, list)
        self.assertEqual(len(ast), 3)

    def test_read_write_print_stop(self):
        self.assert_parses(
            """
PROGRAM IO
INTEGER X
READ *, X
PRINT *, X
WRITE (*,*) X
STOP
END
"""
        )

    def test_falha_sem_end(self):
        with self.assertRaises(ParseError):
            parse_code(
                """
PROGRAM A
INTEGER X
"""
            )

    def test_falha_em_if_mal_formado(self):
        with self.assertRaises(ParseError):
            parse_code(
                """
PROGRAM A
IF (.TRUE.) THEN
PRINT *, 1
END
"""
            )


if __name__ == "__main__":
    unittest.main()
