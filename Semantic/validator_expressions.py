from .symbol_table import SemanticError
from .validator_utils import ARITHMETIC_OPS, LOGICAL_OPS, NUMERIC_TYPES, RELATIONAL_OPS


class ValidatorExpressionsMixin:
    def _validate_expression(self, expression):
        self._infer_expression_type(expression)

    def _infer_expression_type(self, expression):
        if expression is None or not hasattr(expression, "type"):
            return None

        if expression.type == "ID":
            symbol = self._require_variable_available(expression.value)
            self._require_initialized(expression.value)
            return self._symbol_type(symbol)
        if expression.type == "ArrayAccess":
            array_symbol = self._require_array_available(expression.value)
            self._validate_array_arity(array_symbol, expression.children)
            self._validate_array_indices(expression.children)
            self._require_initialized(expression.value)
            return array_symbol.type
        if expression.type == "CallOrArrayAccess":
            symbol = self._require_symbol_available(expression.value)
            if symbol.kind == "array":
                self._validate_array_arity(symbol, expression.children)
                self._validate_array_indices(expression.children)
                self._require_initialized(expression.value)
                return symbol.type
            if symbol.kind in ("function", "intrinsic"):
                self._validate_call_signature(symbol, expression.children)
                return symbol.return_type
            raise SemanticError(
                f"Identificador '{expression.value.upper()}' não é array nem função"
            )
        if expression.type == "BinOp":
            return self._infer_binop_type(expression)
        if expression.type == "UnOp":
            return self._infer_unop_type(expression)
        if expression.type == "Slice":
            self._validate_array_indices(expression.children)
            return "INTEGER"
        if expression.type == "RepeatValue":
            self._require_type(
                self._literal_repeat_count_type(expression.value),
                "INTEGER",
                "Repetição do DATA",
            )
            return self._infer_expression_type(expression.children[0])
        if expression.type == "Literal":
            return self._literal_type(expression.value)

        self._validate_children(expression)
        return None

    def _validate_expression_list(self, expressions):
        for expression in expressions:
            self._validate_expression(expression)

    def _infer_expression_list_types(self, expressions):
        return [self._infer_expression_type(expression) for expression in expressions]

    def _validate_array_arity(self, symbol, indices):
        if symbol.dimensions and len(indices) != len(symbol.dimensions):
            raise SemanticError(
                f"Array '{symbol.name}' usado com {len(indices)} indices, "
                f"mas foi declarado com {len(symbol.dimensions)} dimensao"
            )

    def _validate_call_arity(self, symbol, args):
        if symbol.params and len(args) != len(symbol.params):
            raise SemanticError(
                f"Chamada a '{symbol.name}' com {len(args)} argumentos, "
                f"mas esperava {len(symbol.params)}"
            )

    def _validate_call_signature(self, symbol, args):
        self._validate_call_arity(symbol, args)
        arg_types = self._infer_expression_list_types(args)
        callee_scope = self.global_scope.children.get(symbol.name)
        if callee_scope is None:
            return

        for index, param_name in enumerate(symbol.params):
            param_symbol = callee_scope.lookup_current(param_name)
            if param_symbol is None:
                raise SemanticError(
                    f"Parâmetro formal '{param_name}' de '{symbol.name}' não declarado"
                )
            param_type = self._symbol_type(param_symbol)
            if param_type is None:
                raise SemanticError(
                    f"Parâmetro formal '{param_name}' de '{symbol.name}' sem tipo"
                )
            if index < len(arg_types):
                self._require_assignment_compatible(param_type, arg_types[index])

    def _infer_binop_type(self, expression):
        left_type = self._infer_expression_type(expression.children[0])
        right_type = self._infer_expression_type(expression.children[1])
        operator = expression.value

        if operator in ARITHMETIC_OPS:
            self._require_numeric(left_type, f"Operando esquerdo de '{operator}'")
            self._require_numeric(right_type, f"Operando direito de '{operator}'")
            return self._promote_numeric_type(left_type, right_type)
        if operator in RELATIONAL_OPS:
            if not self._types_compatible_for_comparison(left_type, right_type):
                raise SemanticError(f"Comparação incompatível: {left_type} com {right_type}")
            return "LOGICAL"
        if operator in LOGICAL_OPS:
            self._require_type(left_type, "LOGICAL", f"Operando esquerdo de '{operator}'")
            self._require_type(right_type, "LOGICAL", f"Operando direito de '{operator}'")
            return "LOGICAL"
        raise SemanticError(f"Operador desconhecido: {operator}")

    def _infer_unop_type(self, expression):
        operand_type = self._infer_expression_type(expression.children[0])
        operator = expression.value
        if operator == ".NOT.":
            self._require_type(operand_type, "LOGICAL", "Operando de .NOT.")
            return "LOGICAL"
        if operator == "-":
            self._require_numeric(operand_type, "Operando de '-'")
            return operand_type
        raise SemanticError(f"Operador unário desconhecido: {operator}")

    def _validate_array_indices(self, indices):
        for index in indices:
            if getattr(index, "type", None) == "Slice":
                self._validate_array_indices(index.children)
            else:
                self._require_type(self._infer_expression_type(index), "INTEGER", "Índice de array")

    def _require_numeric_expressions(self, expressions, context):
        for expression in expressions:
            self._require_numeric(self._infer_expression_type(expression), context)

    def _require_assignment_compatible(self, target_type, value_type):
        if target_type is None or value_type is None:
            return
        if target_type == value_type:
            return
        if target_type in NUMERIC_TYPES and value_type in NUMERIC_TYPES:
            return
        raise SemanticError(f"Atribuição incompatível: {target_type} recebe {value_type}")
