from .semantic_table_builder import SymbolTableBuilder
from .validator_core import SemanticValidator


class SemanticAnalyzer:
    def __init__(self):
        self.builder = SymbolTableBuilder()
        self.validator = SemanticValidator()
        self.global_scope = self.builder.global_scope
        self.current_scope = self.builder.current_scope
        self.unit_scopes = self.builder.unit_scopes

    def analyze(self, ast):
        global_scope = self.builder.build(ast)
        self.validator.validate(ast, global_scope)
        self.global_scope = self.builder.global_scope
        self.current_scope = self.builder.current_scope
        self.unit_scopes = self.builder.unit_scopes
        return global_scope
