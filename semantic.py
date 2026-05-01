# semantic.py

from semantic_table_builder import SymbolTableBuilder
from symbol_table import SemanticError


NUMERIC_TYPES = {"INTEGER", "REAL", "DOUBLE PRECISION", "COMPLEX"}
RELATIONAL_OPS = {".EQ.", ".NE.", ".GT.", ".GE.", ".LT.", ".LE."}
ARITHMETIC_OPS = {"+", "-", "*", "/", "**"}
LOGICAL_OPS = {".AND.", ".OR."}


class SemanticValidator:
    def validate(self, ast, global_scope):
        """
        Ponto central para validacoes semanticas.

        Segue o mesmo estilo do exemplo da aula: as procuras passam por
        metodos da SymbolTable que lancam SemanticError quando encontram uso
        invalido.
        """
        self.global_scope = global_scope
        self.current_scope = global_scope
        self.errors = []

        for program_unit in self._normalize_program_units(ast):
            self._validate_program_unit(program_unit)

        if self.errors:
            raise SemanticError("\n".join(self.errors))

        return []

    def _normalize_program_units(self, ast):
        if ast is None:
            return []
        if isinstance(ast, list):
            return ast
        return [ast]

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
            self._require_numeric(
                self._infer_expression_type(node.children[0]),
                "Expressão do arithmetic IF",
            )
        elif node.type == "If":
            self._validate_if(node)
        elif node.type == "LogicalIf":
            self._require_type(
                self._infer_expression_type(node.children[0]),
                "LOGICAL",
                "Condição do IF",
            )
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
            "Statement",
            "Declaration",
            "Dimension",
            "Assignment",
            "ArrayAssignment",
            "Print",
            "Write",
            "Read",
            "If",
            "LogicalIf",
            "ArithmeticIf",
            "Do",
            "Continue",
            "Goto",
            "ComputedGoto",
            "Call",
            "Return",
            "Stop",
            "Pause",
            "Parameter",
            "Data",
        }

        if node.type in statement_types:
            self._validate_statement(node)
        else:
            self._validate_expression(node)

    def _validate_expression(self, expression):
        self._infer_expression_type(expression)

    def _infer_expression_type(self, expression):
        if expression is None or not hasattr(expression, "type"):
            return None

        if expression.type == "ID":
            symbol = self._require_variable_available(expression.value)
            self._require_initialized(expression.value)
            return self._symbol_type(symbol)
        elif expression.type == "ArrayAccess":
            array_symbol = self._require_array_available(expression.value)
            self._validate_array_arity(array_symbol, expression.children)
            self._validate_array_indices(expression.children)
            self._require_initialized(expression.value)
            return array_symbol.type
        elif expression.type == "CallOrArrayAccess":
            symbol = self._require_symbol_available(expression.value)
            if symbol.kind == "array":
                self._validate_array_arity(symbol, expression.children)
                self._validate_array_indices(expression.children)
                self._require_initialized(expression.value)
                return symbol.type
            elif symbol.kind in ("function", "intrinsic"):
                self._validate_call_signature(symbol, expression.children)
                return symbol.return_type
            else:
                raise SemanticError(
                    f"Identificador '{expression.value.upper()}' não é array nem função"
                )
        elif expression.type == "BinOp":
            return self._infer_binop_type(expression)
        elif expression.type == "UnOp":
            return self._infer_unop_type(expression)
        elif expression.type == "Slice":
            self._validate_array_indices(expression.children)
            return "INTEGER"
        elif expression.type == "RepeatValue":
            self._require_type(
                self._literal_repeat_count_type(expression.value),
                "INTEGER",
                "Repetição do DATA",
            )
            return self._infer_expression_type(expression.children[0])
        elif expression.type == "Literal":
            return self._literal_type(expression.value)
        else:
            self._validate_children(expression)
            return None

    def _validate_expression_list(self, expressions):
        for expression in expressions:
            self._validate_expression(expression)

    def _infer_expression_list_types(self, expressions):
        return [self._infer_expression_type(expression) for expression in expressions]

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

    def _mark_function_assignment(self, name):
        if self.current_unit is None or self.current_unit.type != "FunctionDef":
            return

        if name.upper() == self._unit_name(self.current_unit).upper():
            self.function_assigned = True

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
            raise SemanticError(
                f"DO usa label {label}, mas a label não corresponde a CONTINUE"
            )

    def _validate_do_step(self, node):
        if len(node.children) < 3:
            return

        step_value = self._constant_numeric_value(node.children[2])
        if step_value == 0:
            raise SemanticError("Passo do DO não pode ser zero")

    def _initial_available_symbols(self):
        available = set(self.global_scope.symbols.keys())
        for name, symbol in self.current_scope.symbols.items():
            if symbol.kind == "parameter":
                available.add(name)
        return available

    def _initial_initialized_symbols(self):
        initialized = set(self.global_scope.symbols.keys())
        for name, symbol in self.current_scope.symbols.items():
            if symbol.kind == "parameter":
                initialized.add(name)
        return initialized

    def _mark_declaration_available(self, declaration):
        for identifier in declaration.children:
            self.available_symbols.add(identifier.value.upper())

    def _mark_dimension_available(self, dimension):
        for identifier in dimension.children:
            name = identifier.value.upper()
            if name not in self.available_symbols:
                raise SemanticError(
                    f"DIMENSION aplicado antes da declaração de '{name}'"
                )
            self.available_symbols.add(name)

    def _require_declaration_section(self, statement_type):
        if self.seen_executable_statement:
            raise SemanticError(
                f"{statement_type} aparece depois de comandos executáveis"
            )

    def _mark_initialized(self, name):
        self.initialized_symbols.add(name.upper())

    def _require_initialized(self, name):
        upper_name = name.upper()
        if upper_name not in self.initialized_symbols:
            raise SemanticError(f"Variável '{upper_name}' usada antes de ser inicializada")

    def _require_symbol_available(self, name):
        upper_name = name.upper()
        if upper_name not in self.available_symbols:
            raise SemanticError(f"Símbolo '{upper_name}' usado antes de ser declarado")
        return self.current_scope.require_symbol(name)

    def _require_variable_available(self, name):
        upper_name = name.upper()
        if upper_name not in self.available_symbols:
            raise SemanticError(f"Variável '{upper_name}' usada antes de ser declarada")
        return self.current_scope.require_variable(name)

    def _require_assignable_available(self, name):
        upper_name = name.upper()
        if upper_name not in self.available_symbols:
            raise SemanticError(f"Variável '{upper_name}' usada antes de ser declarada")
        return self.current_scope.require_assignable(name)

    def _require_array_available(self, name):
        upper_name = name.upper()
        if upper_name not in self.available_symbols:
            raise SemanticError(f"Array '{upper_name}' usado antes de ser declarado")
        return self.current_scope.require_array(name)

    def _validate_if(self, node):
        condition_type = self._infer_expression_type(node.children[0])
        self._require_type(condition_type, "LOGICAL", "Condição do IF")

        for child in node.children[1:]:
            if isinstance(child, list):
                for statement in child:
                    self._validate_statement(statement)
            else:
                self._validate_statement(child)

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
                raise SemanticError(
                    f"Comparação incompatível: {left_type} com {right_type}"
                )
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
                self._require_type(
                    self._infer_expression_type(index),
                    "INTEGER",
                    "Índice de array",
                )

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

    def _require_numeric(self, type_name, context):
        if type_name not in NUMERIC_TYPES:
            raise SemanticError(f"{context} deve ser numérico, recebeu {type_name}")

    def _require_type(self, found_type, expected_type, context):
        if found_type != expected_type:
            raise SemanticError(
                f"{context} deve ser {expected_type}, recebeu {found_type}"
            )

    def _types_compatible_for_comparison(self, left_type, right_type):
        if left_type in NUMERIC_TYPES and right_type in NUMERIC_TYPES:
            return True
        return left_type == right_type

    def _promote_numeric_type(self, left_type, right_type):
        priority = ["INTEGER", "REAL", "DOUBLE PRECISION", "COMPLEX"]
        return max((left_type, right_type), key=priority.index)

    def _symbol_type(self, symbol):
        return symbol.return_type or symbol.type

    def _literal_type(self, value):
        if isinstance(value, bool):
            return "LOGICAL"
        if isinstance(value, int):
            return "INTEGER"
        if isinstance(value, float):
            return "REAL"
        if isinstance(value, str):
            if value.upper() in (".TRUE.", ".FALSE."):
                return "LOGICAL"
            return "CHARACTER"
        return None

    def _literal_repeat_count_type(self, value):
        if isinstance(value, int):
            return "INTEGER"
        return None

    def _constant_numeric_value(self, expression):
        if expression is None or not hasattr(expression, "type"):
            return None

        if expression.type == "Literal" and isinstance(expression.value, (int, float)):
            return expression.value

        if expression.type == "UnOp" and expression.value == "-":
            value = self._constant_numeric_value(expression.children[0])
            if value is not None:
                return -value

        return None

    def _format_error(self, node, message):
        if message.startswith("Linha "):
            return message

        lineno = getattr(node, "lineno", None)
        if lineno is None and getattr(node, "type", None) == "Statement":
            unwrapped = self._unwrap_statement(node)
            lineno = getattr(unwrapped, "lineno", None)

        if lineno is None:
            return message

        return f"Linha {lineno}: {message}"

    def _unwrap_statement(self, statement):
        if statement.type == "Statement" and statement.children:
            return statement.children[0]
        return statement

    def _unit_name(self, node):
        if node is None or not hasattr(node, "type"):
            return None
        if node.type == "MainProgram":
            return node.value
        if node.type == "FunctionDef":
            return node.value["name"]
        if node.type == "SubroutineDef":
            return node.value
        return None

    def _unit_body(self, node):
        if node.type == "MainProgram":
            return node.children
        if node.type in ("FunctionDef", "SubroutineDef") and len(node.children) > 1:
            return node.children[1]
        return []

    def _param_names(self, node):
        if node.type not in ("FunctionDef", "SubroutineDef") or not node.children:
            return []
        return [param.value for param in node.children[0]]


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
