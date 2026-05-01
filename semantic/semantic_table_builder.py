from .symbol_table import SemanticError, SymbolTable


class SymbolTableBuilder:
    def __init__(self):
        self.global_scope = SymbolTable("global")
        self.current_scope = self.global_scope
        self.unit_scopes = {}
        self._define_intrinsics()

    def build(self, ast):
        program_units = self._normalize_program_units(ast)
        self._validate_program_structure(program_units)
        self._collect_global_units(program_units)
        self._create_unit_scopes(program_units)
        self._collect_unit_symbols(program_units)
        self._collect_unit_labels(program_units)
        self._collect_label_references(program_units)
        self.current_scope = self.global_scope
        return self.global_scope

    def _validate_program_structure(self, program_units):
        if not program_units:
            raise SemanticError("O programa deve ter pelo menos uma unidade")

        main_programs = [
            node
            for node in program_units
            if node is not None and hasattr(node, "type") and node.type == "MainProgram"
        ]
        if len(main_programs) > 1:
            raise SemanticError("Só pode existir um PROGRAM principal")

    def _normalize_program_units(self, ast):
        if ast is None:
            return []
        if isinstance(ast, list):
            return ast
        return [ast]

    def _collect_global_units(self, program_units):
        for node in program_units:
            if node is None or not hasattr(node, "type"):
                continue

            if node.type == "MainProgram":
                self._define_global_symbol(node.value, kind="program")
            elif node.type == "FunctionDef":
                self._define_global_symbol(
                    node.value["name"],
                    kind="function",
                    return_type=node.value["type"],
                    params=self._param_names(node),
                )
            elif node.type == "SubroutineDef":
                self._define_global_symbol(
                    node.value,
                    kind="subroutine",
                    params=self._param_names(node),
                )

    def _create_unit_scopes(self, program_units):
        for node in program_units:
            name = self._unit_name(node)
            if name is None:
                continue

            upper_name = name.upper()
            if upper_name in self.unit_scopes:
                raise SemanticError(f"Scope '{upper_name}' já declarado")
            self.unit_scopes[upper_name] = self.global_scope.create_child(name)

    def _collect_unit_symbols(self, program_units):
        for node in program_units:
            name = self._unit_name(node)
            if name is None:
                continue

            self.current_scope = self.unit_scopes.get(name.upper(), self.global_scope)
            self._define_formal_params(node)
            for statement in self._unit_body(node):
                self._collect_statement_symbols(statement)

    def _collect_unit_labels(self, program_units):
        for node in program_units:
            name = self._unit_name(node)
            if name is None:
                continue

            self.current_scope = self.unit_scopes.get(name.upper(), self.global_scope)
            for statement in self._unit_body(node):
                self._collect_statement_labels(statement)

    def _collect_label_references(self, program_units):
        for node in program_units:
            name = self._unit_name(node)
            if name is None:
                continue

            self.current_scope = self.unit_scopes.get(name.upper(), self.global_scope)
            for statement in self._unit_body(node):
                self._collect_statement_label_references(statement)

    def _collect_statement_symbols(self, statement):
        if statement is None or not hasattr(statement, "type"):
            return

        node = self._unwrap_statement(statement)
        if node is None:
            return

        if node.type == "Declaration":
            try:
                self._define_declaration_symbols(node)
            except SemanticError as error:
                self._raise_at(node, str(error))
            return

        if node.type == "Dimension":
            try:
                self._define_dimension_symbols(node)
            except SemanticError as error:
                self._raise_at(node, str(error))
            return

        for child in getattr(node, "children", []):
            if isinstance(child, list):
                for item in child:
                    self._collect_statement_symbols(item)
            else:
                self._collect_statement_symbols(child)

    def _collect_statement_labels(self, statement):
        if statement is None or not hasattr(statement, "type"):
            return

        if statement.type == "Statement" and statement.value is not None:
            try:
                self._define_current_label(statement.value)
            except SemanticError as error:
                self._raise_at(statement, str(error))

        for child in getattr(statement, "children", []):
            if isinstance(child, list):
                for item in child:
                    self._collect_statement_labels(item)
            else:
                self._collect_statement_labels(child)

    def _collect_statement_label_references(self, statement):
        if statement is None or not hasattr(statement, "type"):
            return

        node = self._unwrap_statement(statement)
        if node is None:
            return

        if node.type == "Do":
            self.current_scope.add_label_reference(node.value["label"], "DO")
        elif node.type == "Goto":
            self.current_scope.add_label_reference(node.value, "GOTO")

        for child in getattr(node, "children", []):
            if isinstance(child, list):
                for item in child:
                    self._collect_statement_label_references(item)
            else:
                self._collect_statement_label_references(child)

    def _define_declaration_symbols(self, declaration):
        var_type = declaration.value
        for identifier in declaration.children:
            if identifier.type == "ID":
                global_symbol = self.global_scope.lookup_current(identifier.value)
                if global_symbol and global_symbol.kind == "function":
                    self._define_current_symbol(
                        identifier.value,
                        kind="function",
                        return_type=var_type,
                        params=global_symbol.params,
                    )
                else:
                    self._define_current_symbol(identifier.value, kind="variable", type=var_type)
            elif identifier.type == "ArrayID":
                self._define_current_symbol(
                    identifier.value,
                    kind="array",
                    type=var_type,
                    dimensions=identifier.children,
                )

    def _define_dimension_symbols(self, dimension):
        for identifier in dimension.children:
            if identifier.type != "ArrayID":
                continue
            existing = self.current_scope.lookup_current(identifier.value)
            if existing:
                if existing.kind not in ("variable", "parameter"):
                    raise SemanticError(
                        f"DIMENSION aplicado a símbolo inválido: {identifier.value.upper()}"
                    )
                existing.kind = "array"
                existing.dimensions = identifier.children
            else:
                raise SemanticError(
                    f"DIMENSION aplicado a variável não declarada: {identifier.value.upper()}"
                )

    def _define_formal_params(self, node):
        for param_name in self._param_names(node):
            self._define_current_symbol(param_name, kind="parameter")

    def _define_intrinsics(self):
        self.global_scope.declare_intrinsic("MOD", return_type="INTEGER", params=["A", "P"])

    def _define_global_symbol(self, name, kind, return_type=None, params=None):
        if kind == "program":
            self.global_scope.declare_program(name)
        elif kind == "function":
            self.global_scope.declare_function(name, return_type=return_type, params=params or [])
        elif kind == "subroutine":
            self.global_scope.declare_subroutine(name, params=params or [])

    def _define_current_symbol(self, name, kind, type=None, dimensions=None, params=None, return_type=None):
        existing = self.current_scope.lookup_current(name)
        if existing:
            if existing.kind == "parameter" and kind in ("variable", "array"):
                existing.type = type
                if kind == "array":
                    existing.kind = "array"
                    existing.dimensions = dimensions or []
                return
            if existing.kind == "variable" and kind == "array":
                existing.kind = "array"
                existing.dimensions = dimensions or []
                return
            raise SemanticError(
                f"Símbolo '{name.upper()}' já declarado no scope '{self.current_scope.name}'"
            )

        if kind == "variable":
            self.current_scope.declare_variable(name, type=type)
        elif kind == "parameter":
            self.current_scope.declare_parameter(name, type=type)
        elif kind == "array":
            self.current_scope.declare_array(name, type=type, dimensions=dimensions or [])
        elif kind == "function":
            self.current_scope.declare_function(name, return_type=return_type, params=params or [])
        elif kind == "subroutine":
            self.current_scope.declare_subroutine(name, params=params or [])

    def _define_current_label(self, label):
        self.current_scope.define_label(label)

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

    def _param_names(self, node):
        if node.type not in ("FunctionDef", "SubroutineDef") or not node.children:
            return []
        return [param.value for param in node.children[0]]

    def _unit_body(self, node):
        if node.type == "MainProgram":
            return node.children
        if node.type in ("FunctionDef", "SubroutineDef") and len(node.children) > 1:
            return node.children[1]
        return []

    def _raise_at(self, node, message):
        if message.startswith("Linha "):
            raise SemanticError(message)
        lineno = getattr(node, "lineno", None)
        if lineno is None:
            raise SemanticError(message)
        raise SemanticError(f"Linha {lineno}: {message}")
