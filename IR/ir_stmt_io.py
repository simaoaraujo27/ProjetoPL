class IRStatementIOMixin:
    def _generate_read(self, node):
        for item in getattr(node, "children", []) or []:
            if item.type == "ID":
                target = self._make_variable(item.value)
                self.current_program.emit("READ", target)
                continue
            if item.type == "ArrayAccess":
                array_symbol = self._require_array_symbol(item.value)
                index_values = self._generate_array_indices(item.children)
                temp_value = self.new_temp(array_symbol.type)
                self.current_program.emit("READ", temp_value)
                self.current_program.emit(
                    "STORE_ARRAY",
                    self._make_variable(item.value),
                    *index_values,
                    temp_value,
                    comment=f"type={array_symbol.type}",
                )
                continue

            raise self.error_class(
                "A primeira iteracao do IR so suporta READ para variaveis simples ou arrays"
            )

    def _generate_print(self, node):
        for item in getattr(node, "children", []) or []:
            value = self._generate_expression(item)
            self.current_program.emit("WRITE", value)
        self.current_program.emit("WRITE_LN")

    def _generate_write(self, node):
        for item in getattr(node, "children", []) or []:
            value = self._generate_expression(item)
            self.current_program.emit("WRITE", value)
