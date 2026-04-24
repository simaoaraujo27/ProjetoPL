# semantic.py

from symbol_table import Symbol, SymbolTable


class SemanticError(Exception):
    pass


class SemanticAnalyzer:
    def __init__(self):
        self.global_scope = SymbolTable("global")
        self.current_scope = self.global_scope

    def analyze(self, ast):
        """
        Ponto de entrada da análise semântica.
        Para já só percorre a AST.
        Depois vamos dividir em fases:
        1. recolher símbolos e labels
        2. validar usos, tipos, labels, arrays, funções
        """
        if isinstance(ast, list):
            for node in ast:
                self.visit(node)
        else:
            self.visit(ast)

        return self.global_scope

    def visit(self, node):
        if node is None:
            return None

        if not hasattr(node, "type"):
            return None

        method_name = f"visit_{node.type}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)

    def generic_visit(self, node):
        for child in node.children:
            if isinstance(child, list):
                for item in child:
                    self.visit(item)
            else:
                self.visit(child)

    def visit_MainProgram(self, node):
        previous_scope = self.current_scope
        self.current_scope = previous_scope.create_child(node.value)

        for stmt in node.children:
            self.visit(stmt)

        self.current_scope = previous_scope

    def visit_FunctionDef(self, node):
        name = node.value["name"]
        return_type = node.value["type"]

        self.current_scope.define(
            Symbol(name, kind="function", return_type=return_type)
        )

        previous_scope = self.current_scope
        self.current_scope = previous_scope.create_child(name)

        params = node.children[0]
        body = node.children[1]

        for param in params:
            self.current_scope.define(
                Symbol(param.value, kind="parameter")
            )

        for stmt in body:
            self.visit(stmt)

        self.current_scope = previous_scope

    def visit_SubroutineDef(self, node):
        name = node.value

        self.current_scope.define(
            Symbol(name, kind="subroutine")
        )

        previous_scope = self.current_scope
        self.current_scope = previous_scope.create_child(name)

        params = node.children[0]
        body = node.children[1]

        for param in params:
            self.current_scope.define(
                Symbol(param.value, kind="parameter")
            )

        for stmt in body:
            self.visit(stmt)

        self.current_scope = previous_scope

    def visit_Statement(self, node):
        # node.value é a label opcional
        # node.children[0] é o statement real
        self.visit(node.children[0])

    def visit_Declaration(self, node):
        var_type = node.value

        for var in node.children:
            if var.type == "ID":
                self.current_scope.define(
                    Symbol(var.value, kind="variable", type=var_type)
                )

            elif var.type == "ArrayID":
                self.current_scope.define(
                    Symbol(
                        var.value,
                        kind="array",
                        type=var_type,
                        dimensions=var.children
                    )
                )