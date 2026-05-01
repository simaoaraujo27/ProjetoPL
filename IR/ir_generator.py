from .ir import IRProgram

from .ir_do import IRDoMixin
from .ir_expr import IRExpressionMixin
from .ir_stmt import IRStatementMixin
from .ir_utils import IRUtilsMixin


SUPPORTED_PROGRAM_NODES = {"MainProgram", "FunctionDef", "SubroutineDef"}


class IRGenerationError(Exception):
    pass


class IRGenerator(IRDoMixin, IRStatementMixin, IRExpressionMixin, IRUtilsMixin):
    error_class = IRGenerationError

    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.temp_counter = 0
        self.label_counter = 0
        self.current_program = None
        self.current_scope = symbol_table
        self.current_unit = None

    def generate(self, ast):
        program_units = self._normalize_program_units(ast)
        if not program_units:
            raise IRGenerationError("Nao existe nenhuma unidade de programa para traduzir")

        main_name = None
        for node in program_units:
            if getattr(node, "type", None) == "MainProgram":
                main_name = node.value
                break

        self.current_program = IRProgram(name=main_name or self._unit_name(program_units[0]))

        for program_node in program_units:
            if program_node.type not in SUPPORTED_PROGRAM_NODES:
                raise IRGenerationError(
                    f"Tipo de unidade de programa ainda nao suportado: {program_node.type}"
                )
            self._generate_program_unit(program_node)

        return self.current_program

    def _generate_program_unit(self, node):
        unit_name = self._unit_name(node)
        self.current_unit = node
        self.current_scope = self.symbol_table.children.get(
            unit_name.upper(),
            self.symbol_table,
        )

        if node.type != "MainProgram":
            self.current_program.emit("LABEL", self._make_label_from_unit_name(unit_name))

        self._generate_statement_list(self._unit_body(node))
        self._ensure_unit_return(node)

    def _ensure_unit_return(self, node):
        instructions = self.current_program.instructions
        if not instructions:
            return

        if node.type == "MainProgram":
            return

        last_opcode = instructions[-1].opcode
        if last_opcode == "RETURN":
            return

        if node.type == "FunctionDef":
            self.current_program.emit("RETURN", self._make_variable(node.value["name"]))
            return

        if node.type == "SubroutineDef":
            self.current_program.emit("RETURN")
