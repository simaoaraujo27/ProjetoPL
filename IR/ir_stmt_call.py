class IRStatementCallMixin:
    def _generate_call(self, node):
        args = [self._generate_expression(argument) for argument in node.children]
        self.current_program.emit(
            "CALL",
            self._make_label_from_unit_name(node.value),
            *args,
        )

    def _generate_return(self):
        if self.current_unit is not None and self.current_unit.type == "FunctionDef":
            function_name = self.current_unit.value["name"]
            self.current_program.emit("RETURN", self._make_variable(function_name))
            return
        self.current_program.emit("RETURN")
