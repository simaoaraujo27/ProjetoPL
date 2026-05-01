from .symbol_table import SemanticError


NUMERIC_TYPES = {"INTEGER", "REAL", "DOUBLE PRECISION", "COMPLEX"}
RELATIONAL_OPS = {".EQ.", ".NE.", ".GT.", ".GE.", ".LT.", ".LE."}
ARITHMETIC_OPS = {"+", "-", "*", "/", "**"}
LOGICAL_OPS = {".AND.", ".OR."}


class ValidatorUtilsMixin:
    def _normalize_program_units(self, ast):
        if ast is None:
            return []
        if isinstance(ast, list):
            return ast
        return [ast]

    def _mark_function_assignment(self, name):
        if self.current_unit is None or self.current_unit.type != "FunctionDef":
            return
        if name.upper() == self._unit_name(self.current_unit).upper():
            self.function_assigned = True

    def _initial_available_symbols(self):
        available = set(self.global_scope.symbols.keys())
        for name, symbol in self.current_scope.symbols.items():
            if symbol.kind == "parameter":
                available.add(name)
        return available

    def _initial_initialized_symbols(self):
        initialized = set(self.global_scope.symbols.keys())
        for name, symbol in self.current_scope.symbols.items():
            if symbol.kind == "parameter":
                initialized.add(name)
        return initialized

    def _mark_declaration_available(self, declaration):
        for identifier in declaration.children:
            self.available_symbols.add(identifier.value.upper())

    def _mark_dimension_available(self, dimension):
        for identifier in dimension.children:
            name = identifier.value.upper()
            if name not in self.available_symbols:
                raise SemanticError(f"DIMENSION aplicado antes da declaração de '{name}'")
            self.available_symbols.add(name)

    def _require_declaration_section(self, statement_type):
        if self.seen_executable_statement:
            raise SemanticError(f"{statement_type} aparece depois de comandos executáveis")

    def _mark_initialized(self, name):
        self.initialized_symbols.add(name.upper())

    def _require_initialized(self, name):
        upper_name = name.upper()
        if upper_name not in self.initialized_symbols:
            raise SemanticError(f"Variável '{upper_name}' usada antes de ser inicializada")

    def _require_symbol_available(self, name):
        upper_name = name.upper()
        if upper_name not in self.available_symbols:
            raise SemanticError(f"Símbolo '{upper_name}' usado antes de ser declarado")
        return self.current_scope.require_symbol(name)

    def _require_variable_available(self, name):
        upper_name = name.upper()
        if upper_name not in self.available_symbols:
            raise SemanticError(f"Variável '{upper_name}' usada antes de ser declarada")
        return self.current_scope.require_variable(name)

    def _require_assignable_available(self, name):
        upper_name = name.upper()
        if upper_name not in self.available_symbols:
            raise SemanticError(f"Variável '{upper_name}' usada antes de ser declarada")
        return self.current_scope.require_assignable(name)

    def _require_array_available(self, name):
        upper_name = name.upper()
        if upper_name not in self.available_symbols:
            raise SemanticError(f"Array '{upper_name}' usado antes de ser declarado")
        return self.current_scope.require_array(name)

    def _require_numeric(self, type_name, context):
        if type_name not in NUMERIC_TYPES:
            raise SemanticError(f"{context} deve ser numérico, recebeu {type_name}")

    def _require_type(self, found_type, expected_type, context):
        if found_type != expected_type:
            raise SemanticError(f"{context} deve ser {expected_type}, recebeu {found_type}")

    def _types_compatible_for_comparison(self, left_type, right_type):
        if left_type in NUMERIC_TYPES and right_type in NUMERIC_TYPES:
            return True
        return left_type == right_type

    def _promote_numeric_type(self, left_type, right_type):
        priority = ["INTEGER", "REAL", "DOUBLE PRECISION", "COMPLEX"]
        return max((left_type, right_type), key=priority.index)

    def _symbol_type(self, symbol):
        return symbol.return_type or symbol.type

    def _literal_type(self, value):
        if isinstance(value, bool):
            return "LOGICAL"
        if isinstance(value, int):
            return "INTEGER"
        if isinstance(value, float):
            return "REAL"
        if isinstance(value, str):
            if value.upper() in (".TRUE.", ".FALSE."):
                return "LOGICAL"
            return "CHARACTER"
        return None

    def _literal_repeat_count_type(self, value):
        if isinstance(value, int):
            return "INTEGER"
        return None

    def _constant_numeric_value(self, expression):
        if expression is None or not hasattr(expression, "type"):
            return None
        if expression.type == "Literal" and isinstance(expression.value, (int, float)):
            return expression.value
        if expression.type == "UnOp" and expression.value == "-":
            value = self._constant_numeric_value(expression.children[0])
            if value is not None:
                return -value
        return None

    def _format_error(self, node, message):
        if message.startswith("Linha "):
            return message
        lineno = getattr(node, "lineno", None)
        if lineno is None and getattr(node, "type", None) == "Statement":
            unwrapped = self._unwrap_statement(node)
            lineno = getattr(unwrapped, "lineno", None)
        if lineno is None:
            return message
        return f"Linha {lineno}: {message}"

    def _unwrap_statement(self, statement):
        if statement.type == "Statement" and statement.children:
            return statement.children[0]
        return statement

    def _unit_name(self, node):
        if node is None or not hasattr(node, "type"):
            return None
        if node.type == "MainProgram":
            return node.value
        if node.type == "FunctionDef":
            return node.value["name"]
        if node.type == "SubroutineDef":
            return node.value
        return None

    def _unit_body(self, node):
        if node.type == "MainProgram":
            return node.children
        if node.type in ("FunctionDef", "SubroutineDef") and len(node.children) > 1:
            return node.children[1]
        return []

    def _param_names(self, node):
        if node.type not in ("FunctionDef", "SubroutineDef") or not node.children:
            return []
        return [param.value for param in node.children[0]]
