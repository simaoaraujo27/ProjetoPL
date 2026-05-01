from .ir_stmt_call import IRStatementCallMixin
from .ir_stmt_control import IRStatementControlMixin
from .ir_stmt_core import IRStatementCoreMixin
from .ir_stmt_io import IRStatementIOMixin


SUPPORTED_STATEMENT_NODES = {
    "Declaration",
    "Assignment",
    "ArrayAssignment",
    "Print",
    "Write",
    "Read",
    "Call",
    "If",
    "LogicalIf",
    "ArithmeticIf",
    "Goto",
    "ComputedGoto",
    "Do",
    "Continue",
    "Return",
}


class IRStatementMixin(
    IRStatementCoreMixin,
    IRStatementIOMixin,
    IRStatementControlMixin,
    IRStatementCallMixin,
):
    def _generate_statement(self, statement):
        label = None
        if getattr(statement, "type", None) == "Statement":
            label = statement.value

        node = self._unwrap_statement(statement)
        if node is None:
            return

        if node.type not in SUPPORTED_STATEMENT_NODES:
            raise self.error_class(
                f"Tipo de statement ainda nao suportado na primeira iteracao: {node.type}"
            )

        if label is not None:
            self.current_program.emit("LABEL", self._make_label_from_fortran(label))

        if node.type == "Declaration":
            self._generate_declaration(node)
            return
        if node.type == "Assignment":
            self._generate_assignment(node)
            return
        if node.type == "ArrayAssignment":
            self._generate_array_assignment(node)
            return
        if node.type == "Read":
            self._generate_read(node)
            return
        if node.type == "Call":
            self._generate_call(node)
            return
        if node.type == "Print":
            self._generate_print(node)
            return
        if node.type == "Write":
            self._generate_write(node)
            return
        if node.type == "If":
            self._generate_if(node)
            return
        if node.type == "LogicalIf":
            self._generate_logical_if(node)
            return
        if node.type == "ArithmeticIf":
            self._generate_arithmetic_if(node)
            return
        if node.type == "Goto":
            self._generate_goto(node)
            return
        if node.type == "ComputedGoto":
            self._generate_computed_goto(node)
            return
        if node.type == "Continue":
            return
        if node.type == "Return":
            self._generate_return()
            return
        if node.type == "Do":
            raise self.error_class(
                "Os ciclos DO devem ser processados pela travessia da lista de statements"
            )

        raise self.error_class(
            f"Geracao de IR para statement '{node.type}' ainda nao implementada"
        )

    def _generate_statement_block(self, statements):
        self._generate_statement_list(statements)

    def _generate_statement_list(self, statements):
        index = 0
        while index < len(statements):
            statement = statements[index]
            node = self._unwrap_statement(statement)

            if node is not None and node.type == "Do":
                index = self._generate_do(statements, index)
                continue

            self._generate_statement(statement)
            index += 1
