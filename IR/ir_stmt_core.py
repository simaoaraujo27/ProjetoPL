class IRStatementCoreMixin:
    def _generate_assignment(self, node):
        source = self._generate_expression(node.children[0])
        target = self._make_variable(node.value)
        self.current_program.emit("ASSIGN", target, source)

    def _generate_array_assignment(self, node):
        array_symbol = self._require_array_symbol(node.value)
        index_values = self._generate_array_indices(node.children[0])
        source = self._generate_expression(node.children[1])
        self.current_program.emit(
            "STORE_ARRAY",
            self._make_variable(node.value),
            *index_values,
            source,
            comment=f"type={array_symbol.type}",
        )

    def _generate_declaration(self, node):
        for identifier in node.children:
            if getattr(identifier, "type", None) != "ArrayID":
                continue
            bounds = self._array_bounds_from_symbol(identifier.value)
            self.current_program.emit(
                "ARRAY_DECL",
                self._make_variable(identifier.value),
                *bounds,
            )

    def _array_bounds_from_symbol(self, name):
        symbol = self._require_array_symbol(name)
        bounds = []
        for dimension in symbol.dimensions:
            if hasattr(dimension, "type") and dimension.type == "Range":
                lower_value, upper_value = dimension.value
                bounds.append(self._dimension_bound_to_ir(lower_value))
                bounds.append(self._dimension_bound_to_ir(upper_value))
            else:
                bounds.append(self._make_constant(1))
                bounds.append(self._dimension_bound_to_ir(dimension))

        return bounds

    def _dimension_bound_to_ir(self, bound):
        if isinstance(bound, int):
            return self._make_constant(bound)
        if isinstance(bound, float):
            return self._make_constant(bound)
        if isinstance(bound, str):
            return self._make_variable(bound)
        if hasattr(bound, "type") and bound.type == "Literal":
            return self._make_constant(bound.value)
        raise self.error_class(f"Limite de array ainda nao suportado: {bound}")
