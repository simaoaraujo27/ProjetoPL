import unittest

from IR.ir_generator import IRGenerationError, IRGenerator
from parser import parse_code
from semantic import SemanticAnalyzer


def generate_ir(code):
    ast = parse_code(code)
    scope = SemanticAnalyzer().analyze(ast)
    return IRGenerator(scope).generate(ast)


class TestIRGenerator(unittest.TestCase):
    def test_assignment_with_precedence(self):
        code = """
PROGRAM T
INTEGER X, A, B, C
A = 1
B = 2
C = 3
X = A + B * C
END
"""
        ir = generate_ir(code)

        self.assertEqual(
            ir.render(),
            "\n".join(
                [
                    "PROGRAM T",
                    "ASSIGN A 1",
                    "ASSIGN B 2",
                    "ASSIGN C 3",
                    "t1 = BINOP * B C",
                    "t2 = BINOP + A t1",
                    "ASSIGN X t2",
                ]
            ),
        )

    def test_logical_if_generates_conditional_jump(self):
        code = """
PROGRAM T
INTEGER X
X = 0
IF (X .LT. 10) X = 1
END
"""
        ir = generate_ir(code)

        self.assertEqual(
            ir.render(),
            "\n".join(
                [
                    "PROGRAM T",
                    "ASSIGN X 0",
                    "t1 = BINOP .LT. X 10",
                    "JUMP_IF_FALSE t1 ENDIF1",
                    "ASSIGN X 1",
                    "ENDIF1:",
                ]
            ),
        )

    def test_if_else_generates_else_and_end_labels(self):
        code = """
PROGRAM T
INTEGER X
X = 0
IF (X .LT. 10) THEN
X = 1
ELSE
X = 2
ENDIF
END
"""
        ir = generate_ir(code)

        self.assertEqual(
            ir.render(),
            "\n".join(
                [
                    "PROGRAM T",
                    "ASSIGN X 0",
                    "t1 = BINOP .LT. X 10",
                    "JUMP_IF_FALSE t1 ELSE1",
                    "ASSIGN X 1",
                    "JUMP ENDIF2",
                    "ELSE1:",
                    "ASSIGN X 2",
                    "ENDIF2:",
                ]
            ),
        )

    def test_read_print_write(self):
        code = """
PROGRAM T
INTEGER X
READ *, X
PRINT *, X
WRITE (*,*) X
END
"""
        ir = generate_ir(code)

        self.assertEqual(
            ir.render(),
            "\n".join(
                [
                    "PROGRAM T",
                    "READ X",
                    "WRITE X",
                    "WRITE_LN",
                    "WRITE X",
                ]
            ),
        )

    def test_goto_with_label(self):
        code = """
PROGRAM T
10 GOTO 10
END
"""
        ir = generate_ir(code)

        self.assertEqual(
            ir.render(),
            "\n".join(
                [
                    "PROGRAM T",
                    "LABEL_10:",
                    "JUMP LABEL_10",
                ]
            ),
        )

    def test_do_with_implicit_step(self):
        code = """
PROGRAM T
INTEGER I, X
DO 10 I = 1, 3
X = I
10 CONTINUE
END
"""
        ir = generate_ir(code)

        self.assertEqual(
            ir.render(),
            "\n".join(
                [
                    "PROGRAM T",
                    "ASSIGN I 1",
                    "DO_TEST1:",
                    "t1 = BINOP .GE. 1 0",
                    "JUMP_IF_FALSE t1 DO_NEG2",
                    "t2 = BINOP .LE. I 3",
                    "JUMP_IF_FALSE t2 DO_END4",
                    "JUMP DO_BODY3",
                    "DO_NEG2:",
                    "t3 = BINOP .GE. I 3",
                    "JUMP_IF_FALSE t3 DO_END4",
                    "DO_BODY3:",
                    "ASSIGN X I",
                    "LABEL_10:",
                    "t4 = BINOP + I 1",
                    "ASSIGN I t4",
                    "JUMP DO_TEST1",
                    "DO_END4:",
                ]
            ),
        )

    def test_do_with_negative_step(self):
        code = """
PROGRAM T
INTEGER I, X
DO 10 I = 3, 1, -1
X = I
10 CONTINUE
END
"""
        ir = generate_ir(code)

        self.assertEqual(
            ir.render(),
            "\n".join(
                [
                    "PROGRAM T",
                    "t1 = UNOP - 1",
                    "ASSIGN I 3",
                    "DO_TEST1:",
                    "t2 = BINOP .GE. t1 0",
                    "JUMP_IF_FALSE t2 DO_NEG2",
                    "t3 = BINOP .LE. I 1",
                    "JUMP_IF_FALSE t3 DO_END4",
                    "JUMP DO_BODY3",
                    "DO_NEG2:",
                    "t4 = BINOP .GE. I 1",
                    "JUMP_IF_FALSE t4 DO_END4",
                    "DO_BODY3:",
                    "ASSIGN X I",
                    "LABEL_10:",
                    "t5 = BINOP + I t1",
                    "ASSIGN I t5",
                    "JUMP DO_TEST1",
                    "DO_END4:",
                ]
            ),
        )

    def test_array_declaration_assignment_and_access(self):
        code = """
PROGRAM T
INTEGER A(5), I, X
I = 2
A(I) = 7
X = A(I)
END
"""
        ir = generate_ir(code)

        self.assertEqual(
            ir.render(),
            "\n".join(
                [
                    "PROGRAM T",
                    "ARRAY_DECL A 1 5",
                    "ASSIGN I 2",
                    "STORE_ARRAY A I 7 ; type=INTEGER",
                    "t1 = LOAD_ARRAY A I",
                    "ASSIGN X t1",
                ]
            ),
        )

    def test_array_read_and_print(self):
        code = """
PROGRAM T
INTEGER A(5)
READ *, A(1)
PRINT *, A(1)
END
"""
        ir = generate_ir(code)

        self.assertEqual(
            ir.render(),
            "\n".join(
                [
                    "PROGRAM T",
                    "ARRAY_DECL A 1 5",
                    "READ t1",
                    "STORE_ARRAY A 1 t1 ; type=INTEGER",
                    "t2 = LOAD_ARRAY A 1",
                    "WRITE t2",
                    "WRITE_LN",
                ]
            ),
        )

    def test_multidimensional_array_declaration_and_access(self):
        code = """
PROGRAM T
INTEGER A(2,3), I, J, X
I = 1
J = 2
A(I,J) = 9
X = A(I,J)
END
"""
        ir = generate_ir(code)

        self.assertEqual(
            ir.render(),
            "\n".join(
                [
                    "PROGRAM T",
                    "ARRAY_DECL A 1 2 1 3",
                    "ASSIGN I 1",
                    "ASSIGN J 2",
                    "STORE_ARRAY A I J 9 ; type=INTEGER",
                    "t1 = LOAD_ARRAY A I J",
                    "ASSIGN X t1",
                ]
            ),
        )

    def test_multidimensional_array_with_explicit_ranges(self):
        code = """
PROGRAM T
INTEGER A(1:2,5:7), X
A(1,5) = 4
X = A(1,5)
END
"""
        ir = generate_ir(code)

        self.assertEqual(
            ir.render(),
            "\n".join(
                [
                    "PROGRAM T",
                    "ARRAY_DECL A 1 2 5 7",
                    "STORE_ARRAY A 1 5 4 ; type=INTEGER",
                    "t1 = LOAD_ARRAY A 1 5",
                    "ASSIGN X t1",
                ]
            ),
        )

    def test_function_and_subroutine_generation(self):
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
        ir = generate_ir(code)

        self.assertEqual(
            ir.render(),
            "\n".join(
                [
                    "PROGRAM MAIN",
                    "ASSIGN N 5",
                    "t1 = CALL UNIT_DOBRO N",
                    "ASSIGN R t1",
                    "CALL UNIT_MOSTRA R",
                    "UNIT_DOBRO:",
                    "t2 = BINOP + X X",
                    "ASSIGN DOBRO t2",
                    "RETURN DOBRO",
                    "UNIT_MOSTRA:",
                    "WRITE V",
                    "WRITE_LN",
                    "RETURN",
                ]
            ),
        )

    def test_computed_goto_generation(self):
        code = """
PROGRAM T
INTEGER I
I = 2
GOTO (10,20,30), I
10 CONTINUE
20 CONTINUE
30 CONTINUE
END
"""
        ir = generate_ir(code)

        self.assertEqual(
            ir.render(),
            "\n".join(
                [
                    "PROGRAM T",
                    "ASSIGN I 2",
                    "t1 = BINOP .EQ. I 1",
                    "JUMP_IF_FALSE t1 CGOTO_NEXT2",
                    "JUMP LABEL_10",
                    "CGOTO_NEXT2:",
                    "t2 = BINOP .EQ. I 2",
                    "JUMP_IF_FALSE t2 CGOTO_NEXT3",
                    "JUMP LABEL_20",
                    "CGOTO_NEXT3:",
                    "t3 = BINOP .EQ. I 3",
                    "JUMP_IF_FALSE t3 CGOTO_NEXT4",
                    "JUMP LABEL_30",
                    "CGOTO_NEXT4:",
                    "CGOTO_END1:",
                    "LABEL_10:",
                    "LABEL_20:",
                    "LABEL_30:",
                ]
            ),
        )

    def test_arithmetic_if_generation(self):
        code = """
PROGRAM T
INTEGER X
X = -1
IF (X) 10, 20, 30
10 CONTINUE
20 CONTINUE
30 CONTINUE
END
"""
        ir = generate_ir(code)

        self.assertEqual(
            ir.render(),
            "\n".join(
                [
                    "PROGRAM T",
                    "t1 = UNOP - 1",
                    "ASSIGN X t1",
                    "t2 = BINOP .LT. X 0",
                    "JUMP_IF_FALSE t2 ARIF_ZERO1",
                    "JUMP LABEL_10",
                    "ARIF_ZERO1:",
                    "t3 = BINOP .EQ. X 0",
                    "JUMP_IF_FALSE t3 ARIF_POS2",
                    "JUMP LABEL_20",
                    "ARIF_POS2:",
                    "JUMP LABEL_30",
                    "LABEL_10:",
                    "LABEL_20:",
                    "LABEL_30:",
                ]
            ),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
