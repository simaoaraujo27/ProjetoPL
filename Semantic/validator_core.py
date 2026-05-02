from .symbol_table import SemanticError
from .validator_expressions import ValidatorExpressionsMixin
from .validator_statements import ValidatorStatementsMixin
from .validator_utils import ValidatorUtilsMixin


class SemanticValidator(ValidatorExpressionsMixin, ValidatorStatementsMixin, ValidatorUtilsMixin):
    def validate(self, ast, global_scope):
        self.global_scope = global_scope
        self.current_scope = global_scope
        self.errors = []

        for program_unit in self._normalize_program_units(ast):
            self._validate_program_unit(program_unit)

        if self.errors:
            raise SemanticError("\n".join(self.errors))
        return []

    def _validate_program_unit(self, node):
        name = self._unit_name(node)
        if name is None:
            return

        previous_scope = self.current_scope
        self.current_scope = self.global_scope.children.get(name.upper(), self.global_scope)
        previous_available_symbols = getattr(self, "available_symbols", None)
        previous_initialized_symbols = getattr(self, "initialized_symbols", None)
        previous_label_targets = getattr(self, "label_targets", None)
        previous_unit = getattr(self, "current_unit", None)
        previous_function_assigned = getattr(self, "function_assigned", None)
        previous_seen_executable = getattr(self, "seen_executable_statement", None)
        self.available_symbols = self._initial_available_symbols()
        self.initialized_symbols = self._initial_initialized_symbols()
        self.label_targets = self._collect_label_targets(self._unit_body(node))
        self.current_unit = node
        self.function_assigned = False
        self.seen_executable_statement = False

        for statement in self._unit_body(node):
            try:
                self._validate_statement(statement)
            except SemanticError as error:
                self.errors.append(self._format_error(statement, str(error)))

        for reference in self.current_scope.label_references:
            try:
                self.current_scope.require_label(reference["label"])
            except SemanticError as error:
                self.errors.append(str(error))

        self._validate_unit_contracts(node)

        self.current_scope = previous_scope
        self.available_symbols = previous_available_symbols
        self.initialized_symbols = previous_initialized_symbols
        self.label_targets = previous_label_targets
        self.current_unit = previous_unit
        self.function_assigned = previous_function_assigned
        self.seen_executable_statement = previous_seen_executable
