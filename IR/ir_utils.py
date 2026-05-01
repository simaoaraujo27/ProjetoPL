from .ir import IRConstant, IRLabelRef, IRTemp, IRVariable


REAL_TYPES = {"REAL", "DOUBLE PRECISION"}


class IRUtilsMixin:
    def new_temp(self, value_type=None):
        self.temp_counter += 1
        return IRTemp(name=f"t{self.temp_counter}", type=value_type)

    def new_label(self, prefix="L"):
        self.label_counter += 1
        return IRLabelRef(name=f"{prefix}{self.label_counter}")

    def _normalize_program_units(self, ast):
        if ast is None:
            return []
        if isinstance(ast, list):
            return ast
        return [ast]

    def _unwrap_statement(self, statement):
        if statement is None:
            return None
        if getattr(statement, "type", None) == "Statement":
            return statement.children[0] if statement.children else None
        return statement

    def _lookup_symbol(self, name):
        if self.current_scope is None:
            return None
        return self.current_scope.lookup(name)

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
        if node is None or not hasattr(node, "type"):
            return []
        if node.type == "MainProgram":
            return node.children
        if node.type in {"FunctionDef", "SubroutineDef"}:
            return node.children[1]
        return []

    def _make_variable(self, name):
        symbol = self._lookup_symbol(name)
        symbol_type = None
        if symbol is not None:
            symbol_type = getattr(symbol, "return_type", None) or getattr(symbol, "type", None)
        return IRVariable(name=name.upper(), type=symbol_type)

    def _make_constant(self, value):
        return IRConstant(value=value, type=self._infer_literal_type(value))

    def _make_label_from_fortran(self, value):
        return IRLabelRef(name=f"LABEL_{value}")

    def _make_label_from_unit_name(self, value):
        return IRLabelRef(name=f"UNIT_{value.upper()}")

    def _infer_literal_type(self, value):
        if isinstance(value, bool):
            return "LOGICAL"
        if isinstance(value, int):
            return "INTEGER"
        if isinstance(value, float):
            return "REAL"

        normalized = str(value).upper()
        if normalized in {".TRUE.", "TRUE"}:
            return "LOGICAL"
        if normalized in {".FALSE.", "FALSE"}:
            return "LOGICAL"
        if isinstance(value, str) and (
            value.startswith("'")
            or value.startswith('"')
        ):
            return "CHARACTER"
        return None

    def _one_constant_for_type(self, value_type):
        if value_type in REAL_TYPES:
            return IRConstant(value=1.0, type="REAL")
        return IRConstant(value=1, type="INTEGER")

    def _zero_constant_for_type(self, value_type):
        if value_type in REAL_TYPES:
            return IRConstant(value=0.0, type="REAL")
        return IRConstant(value=0, type="INTEGER")
