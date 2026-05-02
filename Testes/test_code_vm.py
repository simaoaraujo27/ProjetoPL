import tempfile
import unittest
from pathlib import Path

from IR.ir_generator import IRGenerator
from Parser import parse_code
from Semantic import SemanticAnalyzer
from EWVM.vm_codegen import VMCodeGenerator
from compiler import compile_file, compile_to_vm


def build_codegen(code):
    ast = parse_code(code)
    scope = SemanticAnalyzer().analyze(ast)
    ir_program = IRGenerator(scope).generate(ast)
    return VMCodeGenerator(scope), ir_program


class TestVMCodeGenerator(unittest.TestCase):
    def test_builds_global_offsets_from_main_scope(self):
        code = """
PROGRAM T
INTEGER X, Y
REAL R
END
"""
        codegen, ir_program = build_codegen(code)

        layout = codegen.build_memory_layout(ir_program)

        self.assertEqual(
            layout.global_offsets,
            {
                "X": 0,
                "Y": 1,
                "R": 2,
            },
        )

    def test_builds_param_local_and_temp_offsets_for_units(self):
        code = """
PROGRAM MAIN
INTEGER X
X = 1
END

INTEGER FUNCTION DOBRO(A, B)
INTEGER A, B, TMP
TMP = A + B
DOBRO = TMP
RETURN
END
"""
        codegen, ir_program = build_codegen(code)

        layout = codegen.build_memory_layout(ir_program)
        unit_layout = layout.unit_layouts["DOBRO"]

        self.assertEqual(unit_layout.params, {"A": -2, "B": -1})
        self.assertEqual(unit_layout.locals, {"DOBRO": 0, "TMP": 1})
        self.assertEqual(unit_layout.temps, {"T1": 2})

    def test_generates_assignment_expression_and_write(self):
        code = """
PROGRAM MAIN
INTEGER X, Y
X = 1
Y = 2
X = X + Y
PRINT *, X
END
"""
        codegen, ir_program = build_codegen(code)

        vm_code = codegen.generate(ir_program)

        self.assertEqual(
            vm_code,
            "\n".join(
                [
                    "PUSHN 2",
                    "START",
                    "PUSHI 0",
                    "PUSHI 1",
                    "STOREG 0",
                    "PUSHI 2",
                    "STOREG 1",
                    "PUSHG 0",
                    "PUSHG 1",
                    "ADD",
                    "STOREL 0",
                    "PUSHL 0",
                    "STOREG 0",
                    "PUSHG 0",
                    "WRITEI",
                    "WRITELN",
                    "STOP",
                ]
            ),
        )

    def test_generates_conditional_jump(self):
        code = """
PROGRAM T
INTEGER X
X = 0
IF (X .LT. 10) X = 1
END
"""
        codegen, ir_program = build_codegen(code)

        vm_code = codegen.generate(ir_program)

        self.assertEqual(
            vm_code,
            "\n".join(
                [
                    "PUSHI 0",
                    "START",
                    "PUSHI 0",
                    "PUSHI 0",
                    "STOREG 0",
                    "PUSHG 0",
                    "PUSHI 10",
                    "INF",
                    "STOREL 0",
                    "PUSHL 0",
                    "JZ ENDIF1",
                    "PUSHI 1",
                    "STOREG 0",
                    "ENDIF1:",
                    "STOP",
                ]
            ),
        )

    def test_generates_read_and_write(self):
        code = """
PROGRAM T
INTEGER X
READ *, X
WRITE (*,*) X
END
"""
        codegen, ir_program = build_codegen(code)

        vm_code = codegen.generate(ir_program)

        self.assertEqual(
            vm_code,
            "\n".join(
                [
                    "PUSHI 0",
                    "START",
                    "READ",
                    "ATOI",
                    "STOREG 0",
                    "PUSHG 0",
                    "WRITEI",
                    "STOP",
                ]
            ),
        )

    def test_generates_read_into_array_slot(self):
        code = """
PROGRAM T
INTEGER A(5), I
I = 2
READ *, A(I)
END
"""
        codegen, ir_program = build_codegen(code)

        vm_code = codegen.generate(ir_program)

        self.assertEqual(
            vm_code,
            "\n".join(
                [
                    "PUSHN 2",
                    "START",
                    "PUSHI 0",
                    "PUSHI 5",
                    "ALLOCN",
                    "STOREG 0",
                    "PUSHI 2",
                    "STOREG 1",
                    "READ",
                    "ATOI",
                    "STOREL 0",
                    "PUSHG 0",
                    "PUSHG 1",
                    "PUSHI 1",
                    "SUB",
                    "PADD",
                    "PUSHL 0",
                    "STORE 0",
                    "STOP",
                ]
            ),
        )

    def test_generates_string_write(self):
        code = """
PROGRAM HELLO
PRINT *, 'Ola, Mundo!'
END
"""
        codegen, ir_program = build_codegen(code)

        vm_code = codegen.generate(ir_program)

        self.assertEqual(
            vm_code,
            "\n".join(
                [
                    "START",
                    'PUSHS "Ola, Mundo!"',
                    "WRITES",
                    "WRITELN",
                    "STOP",
                ]
            ),
        )

    def test_emits_unit_label_and_declarations_first(self):
        code = """
PROGRAM MAIN
INTEGER X
X = 1
END

SUBROUTINE MOSTRA(V)
INTEGER V, T
T = V + 1
PRINT *, T
RETURN
END
"""
        codegen, ir_program = build_codegen(code)

        vm_code = codegen.generate(ir_program)

        self.assertEqual(
            vm_code,
            "\n".join(
                [
                    "PUSHI 0",
                    "START",
                    "PUSHI 1",
                    "STOREG 0",
                    "STOP",
                    "",
                    "UNITMOSTRA:",
                    "PUSHN 2",
                    "PUSHL -1",
                    "PUSHI 1",
                    "ADD",
                    "STOREL 1",
                    "PUSHL 1",
                    "STOREL 0",
                    "PUSHL 0",
                    "WRITEI",
                    "WRITELN",
                    "RETURN",
                ]
            ),
        )

    def test_generates_array_declaration_assignment_and_access(self):
        code = """
PROGRAM T
INTEGER A(5), I, X
I = 2
A(I) = 7
X = A(I)
END
"""
        codegen, ir_program = build_codegen(code)

        vm_code = codegen.generate(ir_program)

        self.assertEqual(
            vm_code,
            "\n".join(
                [
                    "PUSHN 3",
                    "START",
                    "PUSHI 0",
                    "PUSHI 5",
                    "ALLOCN",
                    "STOREG 0",
                    "PUSHI 2",
                    "STOREG 1",
                    "PUSHG 0",
                    "PUSHG 1",
                    "PUSHI 1",
                    "SUB",
                    "PADD",
                    "PUSHI 7",
                    "STORE 0",
                    "PUSHG 0",
                    "PUSHG 1",
                    "PUSHI 1",
                    "SUB",
                    "PADD",
                    "LOAD 0",
                    "STOREL 0",
                    "PUSHL 0",
                    "STOREG 2",
                    "STOP",
                ]
            ),
        )

    def test_generates_multidimensional_array_access(self):
        code = """
PROGRAM T
INTEGER A(2,3), I, J, X
I = 1
J = 2
A(I,J) = 9
X = A(I,J)
END
"""
        codegen, ir_program = build_codegen(code)

        vm_code = codegen.generate(ir_program)

        self.assertEqual(
            vm_code,
            "\n".join(
                [
                    "PUSHN 4",
                    "START",
                    "PUSHI 0",
                    "PUSHI 2",
                    "PUSHI 3",
                    "MUL",
                    "ALLOCN",
                    "STOREG 0",
                    "PUSHI 1",
                    "STOREG 1",
                    "PUSHI 2",
                    "STOREG 2",
                    "PUSHG 0",
                    "PUSHG 1",
                    "PUSHI 1",
                    "SUB",
                    "PUSHI 3",
                    "MUL",
                    "PUSHG 2",
                    "PUSHI 1",
                    "SUB",
                    "ADD",
                    "PADD",
                    "PUSHI 9",
                    "STORE 0",
                    "PUSHG 0",
                    "PUSHG 1",
                    "PUSHI 1",
                    "SUB",
                    "PUSHI 3",
                    "MUL",
                    "PUSHG 2",
                    "PUSHI 1",
                    "SUB",
                    "ADD",
                    "PADD",
                    "LOAD 0",
                    "STOREL 0",
                    "PUSHL 0",
                    "STOREG 3",
                    "STOP",
                ]
            ),
        )

    def test_generates_do_loop(self):
        code = """
PROGRAM T
INTEGER I, X
DO 10 I = 1, 3
X = I
10 CONTINUE
END
"""
        codegen, ir_program = build_codegen(code)

        vm_code = codegen.generate(ir_program)

        self.assertEqual(
            vm_code,
            "\n".join(
                [
                    "PUSHN 2",
                    "START",
                    "PUSHN 4",
                    "PUSHI 1",
                    "STOREG 0",
                    "DOTEST1:",
                    "PUSHI 1",
                    "PUSHI 0",
                    "SUPEQ",
                    "STOREL 0",
                    "PUSHL 0",
                    "JZ DONEG2",
                    "PUSHG 0",
                    "PUSHI 3",
                    "INFEQ",
                    "STOREL 1",
                    "PUSHL 1",
                    "JZ DOEND4",
                    "JUMP DOBODY3",
                    "DONEG2:",
                    "PUSHG 0",
                    "PUSHI 3",
                    "SUPEQ",
                    "STOREL 2",
                    "PUSHL 2",
                    "JZ DOEND4",
                    "DOBODY3:",
                    "PUSHG 0",
                    "STOREG 1",
                    "PUSHG 0",
                    "PUSHI 1",
                    "ADD",
                    "STOREL 3",
                    "PUSHL 3",
                    "STOREG 0",
                    "JUMP DOTEST1",
                    "DOEND4:",
                    "STOP",
                ]
            ),
        )

    def test_generates_function_and_subroutine_calls(self):
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
        codegen, ir_program = build_codegen(code)

        vm_code = codegen.generate(ir_program)

        self.assertEqual(
            vm_code,
            "\n".join(
                [
                    "PUSHN 2",
                    "START",
                    "PUSHI 0",
                    "PUSHI 5",
                    "STOREG 0",
                    "PUSHG 0",
                    "PUSHA UNITDOBRO",
                    "CALL",
                    "STOREL 0",
                    "PUSHL 0",
                    "STOREG 1",
                    "PUSHG 1",
                    "PUSHA UNITMOSTRA",
                    "CALL",
                    "STOP",
                    "",
                    "UNITDOBRO:",
                    "PUSHN 2",
                    "PUSHL -1",
                    "PUSHL -1",
                    "ADD",
                    "STOREL 1",
                    "PUSHL 1",
                    "STOREL 0",
                    "PUSHL 0",
                    "RETURN",
                    "",
                    "UNITMOSTRA:",
                    "PUSHL -1",
                    "WRITEI",
                    "WRITELN",
                    "RETURN",
                ]
            ),
        )

    def test_generates_intrinsic_mod_without_call_label(self):
        code = """
PROGRAM T
INTEGER A, B, C
A = 7
B = 3
C = MOD(A, B)
END
"""
        codegen, ir_program = build_codegen(code)

        vm_code = codegen.generate(ir_program)

        self.assertEqual(
            vm_code,
            "\n".join(
                [
                    "PUSHN 3",
                    "START",
                    "PUSHI 0",
                    "PUSHI 7",
                    "STOREG 0",
                    "PUSHI 3",
                    "STOREG 1",
                    "PUSHG 0",
                    "PUSHG 1",
                    "MOD",
                    "STOREL 0",
                    "PUSHL 0",
                    "STOREG 2",
                    "STOP",
                ]
            ),
        )


class TestCompilerIntegration(unittest.TestCase):
    def test_compile_to_vm_runs_full_pipeline(self):
        code = """
PROGRAM T
INTEGER X
X = 2 + 3
PRINT *, X
END
"""
        vm_code = compile_to_vm(code)

        self.assertEqual(
            vm_code,
            "\n".join(
                [
                    "PUSHI 0",
                    "START",
                    "PUSHI 5",
                    "STOREG 0",
                    "PUSHG 0",
                    "WRITEI",
                    "WRITELN",
                    "STOP",
                ]
            ),
        )

    def test_compile_file_writes_vm_output(self):
        code = """
PROGRAM T
INTEGER X
X = 1
END
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "programa.f"
            input_path.write_text(code, encoding="utf-8")

            output_path = compile_file(input_path)

            self.assertEqual(output_path, input_path.with_suffix(".vm"))
            self.assertTrue(output_path.exists())
            self.assertEqual(
                output_path.read_text(encoding="utf-8"),
                "\n".join(
                    [
                        "PUSHI 0",
                        "START",
                        "PUSHI 1",
                        "STOREG 0",
                        "STOP",
                    ]
                ),
            )


if __name__ == "__main__":
    unittest.main()
