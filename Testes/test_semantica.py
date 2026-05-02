import unittest

from Lexer.lexer import LexError, lexer
from Parser import ParseError, parse_code
from Semantic import SemanticAnalyzer, SemanticError


EXAMPLE_FILES = [
    "exemplos/exemplo1.f",
    "exemplos/exemplo2.f",
    "exemplos/exemplo3.f",
    "exemplos/exemplo4.f",
    "exemplos/exemplo5.f",
]


TABLE_CASES = [
    {
        "name": "programa_minimo",
        "code": """
PROGRAM P
END
""",
        "checks": [
            ("global_symbol", "P", "program"),
            ("child_scope", "P"),
        ],
    },
    {
        "name": "declaracoes_tipos_basicos",
        "code": """
PROGRAM TIPOS
INTEGER I
REAL R
LOGICAL L
      CHARACTER C
      COMPLEX Z
DOUBLE PRECISION D
END
""",
        "checks": [
            ("symbol", "TIPOS", "I", "variable", "INTEGER"),
            ("symbol", "TIPOS", "R", "variable", "REAL"),
            ("symbol", "TIPOS", "L", "variable", "LOGICAL"),
            ("symbol", "TIPOS", "C", "variable", "CHARACTER"),
            ("symbol", "TIPOS", "Z", "variable", "COMPLEX"),
            ("symbol", "TIPOS", "D", "variable", "DOUBLE PRECISION"),
        ],
    },
    {
        "name": "arrays_e_dimension",
        "code": """
PROGRAM ARR
INTEGER A(5), B(1:10), N
REAL X
REAL Y
DIMENSION X(3)
DIMENSION Y(4)
END
""",
        "checks": [
            ("symbol", "ARR", "A", "array", "INTEGER"),
            ("symbol", "ARR", "B", "array", "INTEGER"),
            ("symbol", "ARR", "X", "array", "REAL"),
            ("symbol_kind", "ARR", "Y", "array"),
            ("dimensions_len", "ARR", "A", 1),
            ("dimensions_len", "ARR", "B", 1),
            ("dimensions_len", "ARR", "Y", 1),
        ],
    },
    {
        "name": "labels_do_goto",
        "code": """
PROGRAM LABS
INTEGER I
DO 10 I = 1, 5
10 CONTINUE
GOTO 10
END
""",
        "checks": [
            ("labels", "LABS", [10]),
            ("label_ref", "LABS", "DO", 10),
            ("label_ref", "LABS", "GOTO", 10),
        ],
    },
    {
        "name": "function_subroutine_e_parametros",
        "code": """
      PROGRAM MAIN
INTEGER F
      CALL S(1)
END

INTEGER FUNCTION F(X)
INTEGER X
F = X
RETURN
END

SUBROUTINE S(Y)
INTEGER Y
RETURN
END
""",
        "checks": [
            ("global_symbol", "F", "function"),
            ("global_symbol", "S", "subroutine"),
            ("symbol_kind", "MAIN", "F", "function"),
            ("symbol", "F", "X", "parameter", "INTEGER"),
            ("symbol", "S", "Y", "parameter", "INTEGER"),
        ],
    },
    {
        "name": "intrinseca_mod",
        "code": """
      PROGRAM M
INTEGER A, B, C
A = 7
B = 3
      C = MOD(A, B)
END
""",
        "checks": [
            ("global_symbol", "MOD", "intrinsic"),
        ],
    },
]


INVALID_SYNTAX_CASES = [
    {
        "name": "sem_end",
        "code": """
PROGRAM A
INTEGER X
""",
    },
    {
        "name": "token_ilegal",
        "code": """
PROGRAM A
@
END
""",
    },
]


INVALID_SEMANTIC_CASES = [
    {
        "name": "variavel_nao_declarada",
        "code": """
PROGRAM A
X = 1
END
""",
    },
    {
        "name": "declaracao_duplicada",
        "code": """
PROGRAM A
INTEGER X
INTEGER X
END
""",
    },
    {
        "name": "variavel_usada_antes_declaracao",
        "code": """
PROGRAM A
X = 1
INTEGER X
END
""",
    },
    {
        "name": "variavel_usada_antes_inicializacao",
        "code": """
PROGRAM A
INTEGER X, Y
Y = X
END
""",
    },
    {
        "name": "declaracao_depois_executavel",
        "code": """
PROGRAM A
PRINT *, 'OLA'
INTEGER X
END
""",
    },
    {
        "name": "goto_label_inexistente",
        "code": """
PROGRAM A
GOTO 20
END
""",
    },
    {
        "name": "label_duplicada",
        "code": """
PROGRAM A
10 CONTINUE
10 CONTINUE
END
""",
    },
    {
        "name": "do_label_nao_continue",
        "code": """
PROGRAM A
INTEGER I
DO 10 I = 1, 5
10 PRINT *, I
END
""",
    },
    {
        "name": "do_variavel_nao_numerica",
        "code": """
PROGRAM A
LOGICAL L
DO 10 L = 1, 5
10 CONTINUE
END
""",
    },
    {
        "name": "do_limite_nao_numerico",
        "code": """
PROGRAM A
INTEGER I
DO 10 I = .TRUE., 5
10 CONTINUE
END
""",
    },
    {
        "name": "do_passo_zero",
        "code": """
PROGRAM A
INTEGER I
DO 10 I = 1, 5, 0
10 CONTINUE
END
""",
    },
    {
        "name": "array_numero_indices_errado",
        "code": """
PROGRAM A
INTEGER A(5)
A(1, 2) = 3
END
""",
    },
    {
        "name": "dimension_sem_declaracao",
        "code": """
PROGRAM A
DIMENSION X(3)
END
""",
    },
    {
        "name": "dois_programs_principais",
        "code": """
PROGRAM A
END
PROGRAM B
END
""",
    },
    {
        "name": "atribuicao_tipo_incompativel",
        "code": """
PROGRAM A
INTEGER X
LOGICAL L
X = L
END
""",
    },
    {
        "name": "operador_aritmetico_com_logical",
        "code": """
PROGRAM A
INTEGER X
LOGICAL L
X = L + 1
END
""",
    },
    {
        "name": "if_condicao_nao_logical",
        "code": """
PROGRAM A
INTEGER X
IF (X) THEN
ENDIF
END
""",
    },
    {
        "name": "if_bloco_then_semanticamente_invalido",
        "code": """
PROGRAM A
IF (.TRUE.) THEN
X = 1
ENDIF
INTEGER X
END
""",
    },
    {
        "name": "indice_array_nao_integer",
        "code": """
PROGRAM A
INTEGER A(5)
REAL R
A(R) = 1
END
""",
    },
    {
        "name": "print_variavel_nao_declarada",
        "code": """
PROGRAM A
PRINT *, X
END
""",
    },
    {
        "name": "read_array_como_escalar",
        "code": """
PROGRAM A
INTEGER A(5)
READ *, A
END
""",
    },
    {
        "name": "parametro_formal_repetido",
        "code": """
INTEGER FUNCTION F(X, X)
INTEGER X
F = X
END
""",
    },
    {
        "name": "parametro_formal_sem_tipo",
        "code": """
INTEGER FUNCTION F(X)
F = 1
END
""",
    },
    {
        "name": "function_sem_atribuicao_retorno",
        "code": """
INTEGER FUNCTION F(X)
INTEGER X
RETURN
END
""",
    },
    {
        "name": "call_para_function",
        "code": """
PROGRAM A
      CALL F(1)
END

INTEGER FUNCTION F(X)
INTEGER X
F = X
END
""",
    },
    {
        "name": "call_numero_argumentos_errado",
        "code": """
PROGRAM A
      CALL S(1, 2)
END

SUBROUTINE S(X)
INTEGER X
RETURN
END
""",
    },
    {
        "name": "call_tipo_argumento_errado",
        "code": """
PROGRAM A
LOGICAL L
      CALL S(L)
END

SUBROUTINE S(X)
INTEGER X
RETURN
END
""",
    },
]


MULTI_ERROR_CASE = {
    "name": "varios_erros_semanticos",
    "code": """
PROGRAM A
X = 1
PRINT *, Y
END
""",
    "expected_fragments": ["X", "Y"],
}


LINE_ERROR_CASES = [
    {
        "name": "linha_erro_validador",
        "code": """
PROGRAM A
INTEGER X
PRINT *, X
END
""",
        "expected": "Linha 4:",
    },
    {
        "name": "linha_erro_builder",
        "code": """
PROGRAM A
INTEGER X
INTEGER X
END
""",
        "expected": "Linha 4:",
    },
]


VALID_SEMANTIC_CASES = [
    {
        "name": "read_inicializa_variavel",
        "code": """
PROGRAM A
INTEGER X
READ *, X
PRINT *, X
END
""",
    },
    {
        "name": "atribuicao_inicializa_variavel",
        "code": """
PROGRAM A
INTEGER X, Y
X = 1
Y = X
END
""",
    },
    {
        "name": "read_inicializa_array",
        "code": """
PROGRAM A
INTEGER A(5), I
I = 1
READ *, A(I)
PRINT *, A(I)
END
""",
    },
]


def analyze_code(code):
    ast = parse_code(code)
    return SemanticAnalyzer().analyze(ast)


def child_scope(scope, name):
    return scope.children[name.upper()]


def symbol(scope, name):
    return scope.symbols[name.upper()]


def assert_check(scope, check):
    kind = check[0]

    if kind == "global_symbol":
        _, name, expected_kind = check
        found = symbol(scope, name)
        assert found.kind == expected_kind, (name, found.kind, expected_kind)
    elif kind == "child_scope":
        _, name = check
        assert name.upper() in scope.children, name
    elif kind == "symbol":
        _, scope_name, name, expected_kind, expected_type = check
        found = symbol(child_scope(scope, scope_name), name)
        assert found.kind == expected_kind, (name, found.kind, expected_kind)
        assert found.type == expected_type, (name, found.type, expected_type)
    elif kind == "symbol_kind":
        _, scope_name, name, expected_kind = check
        found = symbol(child_scope(scope, scope_name), name)
        assert found.kind == expected_kind, (name, found.kind, expected_kind)
    elif kind == "dimensions_len":
        _, scope_name, name, expected_len = check
        found = symbol(child_scope(scope, scope_name), name)
        assert len(found.dimensions) == expected_len, (name, found.dimensions)
    elif kind == "labels":
        _, scope_name, expected_labels = check
        found = child_scope(scope, scope_name)
        assert sorted(found.labels.keys()) == sorted(expected_labels), found.labels
    elif kind == "label_ref":
        _, scope_name, ref_kind, label = check
        refs = child_scope(scope, scope_name).label_references
        assert {"kind": ref_kind, "label": label} in refs, refs
    else:
        raise AssertionError(f"Check desconhecido: {check}")


def run_example_files():
    for path in EXAMPLE_FILES:
        with open(path) as source:
            analyze_code(source.read())


def run_table_cases():
    for case in TABLE_CASES:
        scope = analyze_code(case["code"])
        for check in case["checks"]:
            assert_check(scope, check)


def run_invalid_syntax_cases():
    for case in INVALID_SYNTAX_CASES:
        try:
            analyze_code(case["code"])
        except Exception as error:
            assert isinstance(error, ParseError) or "Carácter ilegal" in str(error)
        else:
            raise AssertionError(f"{case['name']} devia falhar sintaticamente")


def run_invalid_semantic_cases():
    for case in INVALID_SEMANTIC_CASES:
        try:
            analyze_code(case["code"])
        except SemanticError:
            pass
        else:
            raise AssertionError(f"{case['name']} devia falhar semanticamente")


def run_valid_semantic_cases():
    for case in VALID_SEMANTIC_CASES:
        analyze_code(case["code"])


def run_multi_error_case():
    try:
        analyze_code(MULTI_ERROR_CASE["code"])
    except SemanticError as error:
        message = str(error)
        for fragment in MULTI_ERROR_CASE["expected_fragments"]:
            assert fragment in message, message
    else:
        raise AssertionError(
            f"{MULTI_ERROR_CASE['name']} devia reportar varios erros"
        )


def run_line_error_cases():
    for case in LINE_ERROR_CASES:
        try:
            analyze_code(case["code"])
        except SemanticError as error:
            assert case["expected"] in str(error), str(error)
        else:
            raise AssertionError(f"{case['name']} devia incluir linha no erro")


class TestSemantica(unittest.TestCase):
    def test_ficheiros_exemplo(self):
        run_example_files()

    def test_construcao_tabela_simbolos(self):
        run_table_cases()

    def test_erros_sintaticos_e_lexicos(self):
        run_invalid_syntax_cases()

    def test_casos_semanticos_validos(self):
        run_valid_semantic_cases()

    def test_erros_semanticos(self):
        run_invalid_semantic_cases()

    def test_varios_erros_semanticos(self):
        run_multi_error_case()

    def test_linhas_nos_erros(self):
        run_line_error_cases()


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
        scope = analyze_code(code)
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
        scope = analyze_code(code)
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
    unittest.main()
