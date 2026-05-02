from .symbol_table import SemanticError


class ValidatorStatementsMixin:
    def _validate_statement(self, statement):
        if statement is None or not hasattr(statement, "type"):
            return

        node = self._unwrap_statement(statement)
        if node is None:
            return

        if node.type == "Declaration":
            self._require_declaration_section(node.type)
            self._mark_declaration_available(node)
            return
        if node.type == "Dimension":
            self._require_declaration_section(node.type)
            self._mark_dimension_available(node)
            return
        if node.type in ("Parameter", "Data"):
            self._require_declaration_section(node.type)
            self._validate_children(node)
            return

        self.seen_executable_statement = True

        if node.type == "Assignment":
            target = self._require_assignable_available(node.value)
            value_type = self._infer_expression_type(node.children[0])
            self._require_assignment_compatible(target.return_type or target.type, value_type)
            self._mark_initialized(node.value)
            self._mark_function_assignment(node.value)
        elif node.type == "ArrayAssignment":
            array_symbol = self._require_array_available(node.value)
            self._validate_array_arity(array_symbol, node.children[0])
            self._validate_array_indices(node.children[0])
            value_type = self._infer_expression_type(node.children[1])
            self._require_assignment_compatible(array_symbol.type, value_type)
            self._mark_initialized(node.value)
        elif node.type == "Call":
            subroutine = self.current_scope.require_subroutine(node.value)
            self._validate_call_signature(subroutine, node.children)
        elif node.type == "Do":
            self._require_do_label_continue(node.value["label"])
            control_var = self._require_variable_available(node.value["var"])
            self._require_numeric(control_var.type, "Variável de controlo do DO")
            self._require_numeric_expressions(node.children, "Limites do DO")
            self._validate_do_step(node)
            self._mark_initialized(node.value["var"])
        elif node.type == "Goto":
            self.current_scope.require_label(node.value)
        elif node.type == "ComputedGoto":
            for label in node.value:
                self.current_scope.require_label(label)
            self._require_type(self._infer_expression_type(node.children[0]), "INTEGER", "Índice do computed GOTO")
        elif node.type == "ArithmeticIf":
            for label in node.value:
                self.current_scope.require_label(label)
            self._require_numeric(self._infer_expression_type(node.children[0]), "Expressão do arithmetic IF")
        elif node.type == "If":
            self._validate_if(node)
        elif node.type == "LogicalIf":
            self._require_type(self._infer_expression_type(node.children[0]), "LOGICAL", "Condição do IF")
            self._validate_statement(node.children[1])
        elif node.type == "Read":
            self._validate_read_items(node.children)
        elif node.type in ("Print", "Write"):
            self._infer_expression_list_types(getattr(node, "children", []))
        else:
            self._validate_children(node)

    def _validate_children(self, node):
        for child in getattr(node, "children", []):
            if isinstance(child, list):
                for item in child:
                    self._validate_node(item)
            else:
                self._validate_node(child)

    def _validate_node(self, node):
        if node is None or not hasattr(node, "type"):
            return
        statement_types = {
            "Statement", "Declaration", "Dimension", "Assignment", "ArrayAssignment",
            "Print", "Write", "Read", "If", "LogicalIf", "ArithmeticIf", "Do",
            "Continue", "Goto", "ComputedGoto", "Call", "Return", "Stop", "Pause",
            "Parameter", "Data",
        }
        if node.type in statement_types:
            self._validate_statement(node)
        else:
            self._validate_expression(node)

    def _validate_read_items(self, items):
        for item in items:
            if item.type == "ID":
                self._require_variable_available(item.value)
                self._mark_initialized(item.value)
            elif item.type == "ArrayAccess":
                array_symbol = self._require_array_available(item.value)
                self._validate_array_arity(array_symbol, item.children)
                self._validate_array_indices(item.children)
                self._mark_initialized(item.value)
            else:
                raise SemanticError("READ só pode receber variáveis ou posições de arrays")

    def _validate_unit_contracts(self, node):
        if node.type not in ("FunctionDef", "SubroutineDef"):
            return

        for param_name in self._param_names(node):
            param_symbol = self.current_scope.lookup_current(param_name)
            if param_symbol is None:
                self.errors.append(
                    self._format_error(
                        node,
                        f"Parâmetro formal '{param_name}' não declarado no scope '{self.current_scope.name}'",
                    )
                )
                continue
            if self._symbol_type(param_symbol) is None:
                self.errors.append(
                    self._format_error(
                        node,
                        f"Parâmetro formal '{param_name}' sem tipo no scope '{self.current_scope.name}'",
                    )
                )

        if node.type == "FunctionDef" and not self.function_assigned:
            self.errors.append(
                self._format_error(
                    node,
                    f"FUNCTION '{self._unit_name(node).upper()}' não atribui valor ao próprio nome",
                )
            )

    def _collect_label_targets(self, statements):
        targets = {}
        for statement in statements:
            self._collect_statement_label_targets(statement, targets)
        return targets

    def _collect_statement_label_targets(self, statement, targets):
        if statement is None or not hasattr(statement, "type"):
            return
        if statement.type == "Statement" and statement.value is not None:
            targets[statement.value] = self._unwrap_statement(statement).type
        for child in getattr(statement, "children", []):
            if isinstance(child, list):
                for item in child:
                    self._collect_statement_label_targets(item, targets)
            else:
                self._collect_statement_label_targets(child, targets)

    def _require_do_label_continue(self, label):
        self.current_scope.require_label(label)
        target_type = self.label_targets.get(label)
        if target_type != "Continue":
            raise SemanticError(f"DO usa label {label}, mas a label não corresponde a CONTINUE")

    def _validate_do_step(self, node):
        if len(node.children) < 3:
            return
        step_value = self._constant_numeric_value(node.children[2])
        if step_value == 0:
            raise SemanticError("Passo do DO não pode ser zero")

    def _validate_if(self, node):
        condition_type = self._infer_expression_type(node.children[0])
        self._require_type(condition_type, "LOGICAL", "Condição do IF")
        for child in node.children[1:]:
            if isinstance(child, list):
                for statement in child:
                    self._validate_statement(statement)
            else:
                self._validate_statement(child)
