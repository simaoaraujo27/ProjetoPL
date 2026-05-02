class IRStatementControlMixin:
    def _generate_if(self, node):
        condition = self._generate_expression(node.children[0])
        constant_condition = self._constant_boolean_value(condition)
        if constant_condition is not None:
            if constant_condition:
                self._generate_statement_block(node.children[1])
            elif len(node.children) == 3:
                self._generate_statement_block(node.children[2])
            return

        else_label = self.new_label("ELSE")
        end_label = self.new_label("ENDIF")

        self.current_program.emit("JUMP_IF_FALSE", condition, else_label)
        self._generate_statement_block(node.children[1])

        if len(node.children) == 3:
            self.current_program.emit("JUMP", end_label)
            self.current_program.emit("LABEL", else_label)
            self._generate_statement_block(node.children[2])
            self.current_program.emit("LABEL", end_label)
        else:
            self.current_program.emit("LABEL", else_label)

    def _generate_logical_if(self, node):
        condition = self._generate_expression(node.children[0])
        constant_condition = self._constant_boolean_value(condition)
        if constant_condition is not None:
            if constant_condition:
                self._generate_statement(node.children[1])
            return

        end_label = self.new_label("ENDIF")
        self.current_program.emit("JUMP_IF_FALSE", condition, end_label)
        self._generate_statement(node.children[1])
        self.current_program.emit("LABEL", end_label)

    def _generate_goto(self, node):
        self.current_program.emit("JUMP", self._make_label_from_fortran(node.value))

    def _generate_computed_goto(self, node):
        index_value = self._generate_expression(node.children[0])
        end_label = self.new_label("CGOTO_END")

        for position, label_value in enumerate(node.value, start=1):
            condition = self.new_temp("LOGICAL")
            self.current_program.emit(
                "BINOP",
                ".EQ.",
                index_value,
                self._make_constant(position),
                result=condition,
            )
            next_label = self.new_label("CGOTO_NEXT")
            self.current_program.emit("JUMP_IF_FALSE", condition, next_label)
            self.current_program.emit("JUMP", self._make_label_from_fortran(label_value))
            self.current_program.emit("LABEL", next_label)

        self.current_program.emit("LABEL", end_label)

    def _generate_arithmetic_if(self, node):
        value = self._generate_expression(node.children[0])
        constant_value = self._constant_numeric_runtime_value(value)
        value_type = self._infer_expression_type(node.children[0])
        zero = self._zero_constant_for_type(value_type)
        negative_label, zero_label, positive_label = [
            self._make_label_from_fortran(label_value)
            for label_value in node.value
        ]

        if constant_value is not None:
            if constant_value < 0:
                self.current_program.emit("JUMP", negative_label)
            elif constant_value == 0:
                self.current_program.emit("JUMP", zero_label)
            else:
                self.current_program.emit("JUMP", positive_label)
            return

        is_negative = self.new_temp("LOGICAL")
        self.current_program.emit(
            "BINOP",
            ".LT.",
            value,
            zero,
            result=is_negative,
        )
        check_zero_label = self.new_label("ARIF_ZERO")
        self.current_program.emit("JUMP_IF_FALSE", is_negative, check_zero_label)
        self.current_program.emit("JUMP", negative_label)
        self.current_program.emit("LABEL", check_zero_label)

        is_zero = self.new_temp("LOGICAL")
        self.current_program.emit(
            "BINOP",
            ".EQ.",
            value,
            zero,
            result=is_zero,
        )
        positive_check_label = self.new_label("ARIF_POS")
        self.current_program.emit("JUMP_IF_FALSE", is_zero, positive_check_label)
        self.current_program.emit("JUMP", zero_label)
        self.current_program.emit("LABEL", positive_check_label)
        self.current_program.emit("JUMP", positive_label)

    def _constant_boolean_value(self, value):
        if not self._is_constant(value):
            return None
        if value.type != "LOGICAL":
            return None
        return bool(self._constant_runtime_value(value))

    def _constant_numeric_runtime_value(self, value):
        if not self._is_constant(value):
            return None
        if value.type not in {"INTEGER", "REAL", "DOUBLE PRECISION"}:
            return None
        runtime_value = self._constant_runtime_value(value)
        if isinstance(runtime_value, (int, float)):
            return runtime_value
        return None
