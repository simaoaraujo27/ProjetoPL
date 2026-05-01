class IRDoMixin:
    def _generate_do(self, statements, index):
        statement = statements[index]
        node = self._unwrap_statement(statement)
        terminal_label_value = node.value["label"]
        terminal_index = self._find_do_terminal_index(
            statements,
            index + 1,
            terminal_label_value,
        )

        control_var = self._make_variable(node.value["var"])
        start_value = self._generate_expression(node.children[0])
        limit_value = self._generate_expression(node.children[1])
        step_value = self._generate_do_step_value(node, control_var.type)

        test_label = self.new_label("DO_TEST")
        negative_step_label = self.new_label("DO_NEG")
        body_label = self.new_label("DO_BODY")
        end_label = self.new_label("DO_END")

        self.current_program.emit("ASSIGN", control_var, start_value)
        self.current_program.emit("LABEL", test_label)

        step_non_negative = self.new_temp("LOGICAL")
        self.current_program.emit(
            "BINOP",
            ".GE.",
            step_value,
            self._zero_constant_for_type(step_value.type),
            result=step_non_negative,
        )
        self.current_program.emit("JUMP_IF_FALSE", step_non_negative, negative_step_label)

        positive_condition = self.new_temp("LOGICAL")
        self.current_program.emit(
            "BINOP",
            ".LE.",
            control_var,
            limit_value,
            result=positive_condition,
        )
        self.current_program.emit("JUMP_IF_FALSE", positive_condition, end_label)
        self.current_program.emit("JUMP", body_label)

        self.current_program.emit("LABEL", negative_step_label)
        negative_condition = self.new_temp("LOGICAL")
        self.current_program.emit(
            "BINOP",
            ".GE.",
            control_var,
            limit_value,
            result=negative_condition,
        )
        self.current_program.emit("JUMP_IF_FALSE", negative_condition, end_label)

        self.current_program.emit("LABEL", body_label)
        self._generate_statement_list(statements[index + 1:terminal_index])
        self.current_program.emit("LABEL", self._make_label_from_fortran(terminal_label_value))

        incremented_value = self.new_temp(control_var.type)
        self.current_program.emit(
            "BINOP",
            "+",
            control_var,
            step_value,
            result=incremented_value,
        )
        self.current_program.emit("ASSIGN", control_var, incremented_value)
        self.current_program.emit("JUMP", test_label)
        self.current_program.emit("LABEL", end_label)

        return terminal_index + 1

    def _find_do_terminal_index(self, statements, start_index, label_value):
        for index in range(start_index, len(statements)):
            statement = statements[index]
            if getattr(statement, "type", None) != "Statement":
                continue

            node = self._unwrap_statement(statement)
            if statement.value == label_value and node is not None and node.type == "Continue":
                return index

        raise self.error_class(
            f"Nao foi encontrada a label terminal {label_value} do ciclo DO"
        )

    def _generate_do_step_value(self, node, control_type):
        if len(node.children) >= 3:
            return self._generate_expression(node.children[2])
        return self._one_constant_for_type(control_type)
