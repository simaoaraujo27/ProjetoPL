ARITHMETIC_OPS = {"+", "-", "*", "/", "**"}
RELATIONAL_OPS = {".EQ.", ".NE.", ".GT.", ".GE.", ".LT.", ".LE."}
LOGICAL_OPS = {".AND.", ".OR."}
NUMERIC_TYPES = {"INTEGER", "REAL", "DOUBLE PRECISION", "COMPLEX"}
REAL_TYPES = {"REAL", "DOUBLE PRECISION"}

SUPPORTED_EXPRESSION_NODES = {
    "BinOp",
    "UnOp",
    "ID",
    "Literal",
    "ArrayAccess",
    "CallOrArrayAccess",
}


class IRExpressionMixin:
    def _generate_expression(self, expression):
        if expression is None or not hasattr(expression, "type"):
            raise self.error_class("Expressao invalida para geracao de IR")

        if expression.type not in SUPPORTED_EXPRESSION_NODES:
            raise self.error_class(
                f"Tipo de expressao ainda nao suportado na primeira iteracao: {expression.type}"
            )

        if expression.type == "Literal":
            return self._generate_literal(expression)
        if expression.type == "ID":
            return self._generate_identifier(expression)
        if expression.type == "BinOp":
            return self._generate_binop(expression)
        if expression.type == "UnOp":
            return self._generate_unop(expression)
        if expression.type == "ArrayAccess":
            return self._generate_array_access(expression)
        if expression.type == "CallOrArrayAccess":
            return self._generate_call_or_array_access(expression)

        raise self.error_class(
            f"Geracao de IR para expressao '{expression.type}' ainda nao implementada"
        )

    def _generate_literal(self, expression):
        return self._make_constant(expression.value)

    def _generate_identifier(self, expression):
        symbol = self._lookup_symbol(expression.value)
        if symbol is None:
            raise self.error_class(
                f"Identificador '{expression.value.upper()}' nao encontrado na tabela de simbolos"
            )

        if symbol.kind not in {"variable", "parameter", "function"}:
            raise self.error_class(
                f"Identificador '{expression.value.upper()}' nao pode ser usado como valor simples"
            )

        return self._make_variable(expression.value)

    def _generate_binop(self, expression):
        left = self._generate_expression(expression.children[0])
        right = self._generate_expression(expression.children[1])
        folded = self._try_fold_binop(expression.value, left, right)
        if folded is not None:
            return folded
        result_type = self._infer_expression_type(expression)
        result = self.new_temp(result_type)
        self.current_program.emit("BINOP", expression.value, left, right, result=result)
        return result

    def _generate_unop(self, expression):
        operand = self._generate_expression(expression.children[0])
        folded = self._try_fold_unop(expression.value, operand)
        if folded is not None:
            return folded
        result_type = self._infer_expression_type(expression)
        result = self.new_temp(result_type)
        self.current_program.emit("UNOP", expression.value, operand, result=result)
        return result

    def _generate_array_access(self, expression):
        array_symbol = self._require_array_symbol(expression.value)
        index_values = self._generate_array_indices(expression.children)
        result = self.new_temp(array_symbol.type)
        self.current_program.emit(
            "LOAD_ARRAY",
            self._make_variable(expression.value),
            *index_values,
            result=result,
        )
        return result

    def _generate_call_or_array_access(self, expression):
        symbol = self._lookup_symbol(expression.value)
        if symbol is None:
            raise self.error_class(
                f"Identificador '{expression.value.upper()}' nao encontrado na tabela de simbolos"
            )

        if symbol.kind == "array":
            return self._generate_array_access(expression)
        if symbol.kind in {"function", "intrinsic"}:
            return self._generate_function_call(expression, symbol)

        raise self.error_class(
            f"CallOrArrayAccess para '{expression.value.upper()}' ainda nao suportado fora de arrays"
        )

    def _generate_function_call(self, expression, symbol):
        args = [self._generate_expression(argument) for argument in expression.children]
        result_type = getattr(symbol, "return_type", None) or getattr(symbol, "type", None)
        result = self.new_temp(result_type)
        self.current_program.emit(
            "CALL",
            self._make_label_from_unit_name(symbol.name),
            *args,
            result=result,
        )
        return result

    def _infer_expression_type(self, expression):
        if expression is None or not hasattr(expression, "type"):
            return None

        if expression.type == "Literal":
            return self._infer_literal_type(expression.value)

        if expression.type == "ID":
            symbol = self._lookup_symbol(expression.value)
            if symbol is None:
                raise self.error_class(
                    f"Identificador '{expression.value.upper()}' nao encontrado na tabela de simbolos"
                )
            return getattr(symbol, "return_type", None) or getattr(symbol, "type", None)

        if expression.type == "ArrayAccess":
            return self._require_array_symbol(expression.value).type

        if expression.type == "CallOrArrayAccess":
            symbol = self._lookup_symbol(expression.value)
            if symbol is None:
                raise self.error_class(
                    f"Identificador '{expression.value.upper()}' nao encontrado na tabela de simbolos"
                )
            if symbol.kind == "array":
                return symbol.type
            if symbol.kind in {"function", "intrinsic"}:
                return getattr(symbol, "return_type", None) or getattr(symbol, "type", None)
            raise self.error_class(
                f"CallOrArrayAccess para '{expression.value.upper()}' ainda nao suportado fora de arrays"
            )

        if expression.type == "UnOp":
            operand_type = self._infer_expression_type(expression.children[0])
            if expression.value == ".NOT.":
                return "LOGICAL"
            if expression.value == "-":
                return operand_type

        if expression.type == "BinOp":
            left_type = self._infer_expression_type(expression.children[0])
            right_type = self._infer_expression_type(expression.children[1])
            operator = expression.value

            if operator in RELATIONAL_OPS or operator in LOGICAL_OPS:
                return "LOGICAL"
            if operator in ARITHMETIC_OPS:
                return self._promote_numeric_type(left_type, right_type)

        raise self.error_class(
            f"Nao foi possivel inferir o tipo da expressao '{expression.type}'"
        )

    def _promote_numeric_type(self, left_type, right_type):
        if left_type in REAL_TYPES or right_type in REAL_TYPES:
            return "REAL"
        if left_type in NUMERIC_TYPES and right_type in NUMERIC_TYPES:
            return "INTEGER"

        raise self.error_class(
            f"Tipos numericos invalidos para promocao: {left_type} e {right_type}"
        )

    def _require_array_symbol(self, name):
        symbol = self._lookup_symbol(name)
        if symbol is None:
            raise self.error_class(
                f"Array '{name.upper()}' nao encontrado na tabela de simbolos"
            )
        if symbol.kind != "array":
            raise self.error_class(
                f"Identificador '{name.upper()}' nao e array"
            )
        return symbol

    def _generate_array_indices(self, indices):
        return [self._generate_expression(index) for index in indices]

    def _try_fold_binop(self, operator, left, right):
        if not self._is_constant(left) or not self._is_constant(right):
            return None

        left_value = self._constant_runtime_value(left)
        right_value = self._constant_runtime_value(right)

        try:
            if operator == "+":
                result = left_value + right_value
            elif operator == "-":
                result = left_value - right_value
            elif operator == "*":
                result = left_value * right_value
            elif operator == ".EQ.":
                result = left_value == right_value
            elif operator == ".NE.":
                result = left_value != right_value
            elif operator == ".GT.":
                result = left_value > right_value
            elif operator == ".GE.":
                result = left_value >= right_value
            elif operator == ".LT.":
                result = left_value < right_value
            elif operator == ".LE.":
                result = left_value <= right_value
            elif operator == ".AND.":
                result = bool(left_value) and bool(right_value)
            elif operator == ".OR.":
                result = bool(left_value) or bool(right_value)
            else:
                return None
        except Exception:
            return None

        return self._constant_from_runtime_value(result, left.type, right.type)

    def _try_fold_unop(self, operator, operand):
        if not self._is_constant(operand):
            return None

        operand_value = self._constant_runtime_value(operand)

        try:
            if operator == "-":
                result = -operand_value
            elif operator == ".NOT.":
                result = not bool(operand_value)
            else:
                return None
        except Exception:
            return None

        return self._constant_from_runtime_value(result, operand.type)

    def _is_constant(self, value):
        return getattr(value, "__class__", None).__name__ == "IRConstant"

    def _constant_runtime_value(self, constant):
        value = constant.value
        if constant.type == "LOGICAL":
            if isinstance(value, str):
                normalized = value.upper()
                if normalized in {".TRUE.", "TRUE"}:
                    return True
                if normalized in {".FALSE.", "FALSE"}:
                    return False
            return bool(value)
        return value

    def _constant_from_runtime_value(self, value, *source_types):
        if isinstance(value, bool):
            return self._make_constant(".TRUE." if value else ".FALSE.")

        if any(type_name in REAL_TYPES for type_name in source_types if type_name is not None):
            if isinstance(value, (int, float)):
                return self._make_constant(float(value))

        return self._make_constant(value)
