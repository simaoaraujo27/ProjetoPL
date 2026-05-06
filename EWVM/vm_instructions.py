from .vm_common import INTEGER_TYPES, REAL_TYPES, VMCodegenError


class VMInstructionMixin:
    def _vm_label(self, label):
        text = str(label)
        normalized = "".join(char for char in text if char.isalnum())
        if not normalized:
            raise VMCodegenError(f"Label invalida para a VM: {text}")
        return normalized

    def generate(self, ir_program):
        self.build_memory_layout(ir_program)
        code = self._emit_program(ir_program)
        return "\n".join(code)

    def _emit_program(self, ir_program):
        sections = self._split_program_sections(ir_program)
        code = []

        code.extend(self._emit_slot_allocation(len(self.layout.global_offsets)))
        code.append("START")
        code.extend(self._emit_unit_prologue(self.layout.main_layout))
        code.extend(self._emit_instruction_block(sections["main"], self.layout.main_layout, is_main=True))
        code.append("STOP")

        for unit_name, instructions in sections["units"].items():
            code.append("")
            unit_layout = self.layout.unit_layouts[unit_name]
            code.extend(self._emit_instruction_block(instructions, unit_layout, is_main=False))

        return code

    def _emit_instruction_block(self, instructions, layout, is_main):
        previous_layout = self.current_layout
        previous_unit_name = self.current_unit_name
        previous_is_main = self.current_is_main
        previous_array_bounds = self.current_array_bounds

        self.current_layout = layout
        self.current_unit_name = layout.name
        self.current_is_main = is_main
        self.current_array_bounds = self._array_bounds_for_unit(layout.name)

        code = []

        if not is_main and instructions:
            first = instructions[0]
            if first.opcode == "LABEL":
                code.append(f"{self._vm_label(first.args[0])}:")
                code.extend(self._emit_unit_prologue(layout))
                instructions = instructions[1:]

        for instruction in instructions:
            code.extend(self._emit_instruction(instruction))

        self.current_layout = previous_layout
        self.current_unit_name = previous_unit_name
        self.current_is_main = previous_is_main
        self.current_array_bounds = previous_array_bounds
        return code

    def _emit_instruction(self, instruction):
        opcode = instruction.opcode

        if opcode == "ASSIGN":
            return self._emit_assign(instruction)
        if opcode == "BINOP":
            return self._emit_binop(instruction)
        if opcode == "UNOP":
            return self._emit_unop(instruction)
        if opcode == "LABEL":
            return [f"{self._vm_label(instruction.args[0])}:"]
        if opcode == "JUMP":
            return [f"JUMP {self._vm_label(instruction.args[0])}"]
        if opcode == "JUMP_IF_FALSE":
            return self._emit_jump_if_false(instruction)
        if opcode == "WRITE":
            return self._emit_write(instruction)
        if opcode == "WRITE_LN":
            return ["WRITELN"]
        if opcode == "READ":
            return self._emit_read(instruction)
        if opcode == "ARRAY_DECL":
            return self._emit_array_decl(instruction)
        if opcode == "LOAD_ARRAY":
            return self._emit_load_array(instruction)
        if opcode == "STORE_ARRAY":
            return self._emit_store_array(instruction)
        if opcode == "CALL":
            return self._emit_call(instruction)
        if opcode == "RETURN":
            return self._emit_return(instruction)

        raise VMCodegenError(f"Instrucao IR ainda nao suportada no backend VM: {opcode}")

    def _emit_assign(self, instruction):
        target, source = instruction.args
        code = self._emit_value(source, expected_type=getattr(target, "type", None))
        code.extend(self._emit_store(target))
        return code

    def _emit_binop(self, instruction):
        operator, left, right = instruction.args
        result = instruction.result
        result_type = self._normalize_type(getattr(result, "type", None))
        left_expected, right_expected = self._expected_operand_types(
            operator,
            result_type,
            self._normalize_type(getattr(left, "type", None)),
            self._normalize_type(getattr(right, "type", None)),
        )

        code = self._emit_value(left, expected_type=left_expected)
        code.extend(self._emit_value(right, expected_type=right_expected))
        code.extend(self._emit_binop_operator(operator, left_expected))
        code.extend(self._emit_store(result))
        return code

    def _emit_unop(self, instruction):
        operator, operand = instruction.args
        result = instruction.result
        result_type = self._normalize_type(getattr(result, "type", None))
        code = self._emit_value(operand, expected_type=result_type)
        code.extend(self._emit_unop_operator(operator, result_type))
        code.extend(self._emit_store(result))
        return code

    def _emit_jump_if_false(self, instruction):
        condition, label = instruction.args
        code = self._emit_value(condition, expected_type="LOGICAL")
        code.append(f"JZ {self._vm_label(label)}")
        return code

    def _emit_write(self, instruction):
        value = instruction.args[0]
        code = self._emit_value(value)
        code.append(self._write_opcode_for_type(getattr(value, "type", None)))
        return code

    def _emit_read(self, instruction):
        target = instruction.args[0]
        target_type = self._normalize_type(getattr(target, "type", None))
        code = ["READ"]

        if target_type in INTEGER_TYPES:
            code.append("ATOI")
        elif target_type in REAL_TYPES:
            code.append("ATOF")
        elif target_type == "CHARACTER":
            pass
        else:
            raise VMCodegenError(
                f"Tipo ainda nao suportado para READ no backend VM: {target_type}"
            )

        code.extend(self._emit_store(target))
        return code

    def _emit_call(self, instruction):
        label = instruction.args[0]
        args = list(instruction.args[1:])
        vm_label = self._vm_label(label)

        if vm_label == "UNITMOD":
            return self._emit_intrinsic_mod(args, instruction.result)

        code = []

        if instruction.result is not None:
            code.append("PUSHI 0")

        for argument in args:
            code.extend(self._emit_value(argument))

        code.append(f"PUSHA {vm_label}")
        code.append("CALL")

        if instruction.result is not None and args:
            code.append(f"POP {len(args)}")

        if instruction.result is not None:
            code.extend(self._emit_store(instruction.result))

        return code

    def _emit_intrinsic_mod(self, args, result):
        if len(args) != 2:
            raise VMCodegenError("A intrinseca MOD exige exatamente 2 argumentos")

        code = []
        code.extend(self._emit_value(args[0], expected_type="INTEGER"))
        code.extend(self._emit_value(args[1], expected_type="INTEGER"))
        code.append("MOD")

        if result is not None:
            code.extend(self._emit_store(result))

        return code

    def _emit_return(self, instruction):
        code = []
        if instruction.args:
            if self.current_layout is None or self.current_layout.return_slot is None:
                raise VMCodegenError("RETURN com valor fora de uma funcao")
            code.extend(self._emit_value(instruction.args[0]))
            code.append(f"STOREL {self.current_layout.return_slot}")
        code.append("RETURN")
        return code

    def _emit_binop_operator(self, operator, operand_type):
        is_real = operand_type in REAL_TYPES

        arithmetic_map = {
            "+": "FADD" if is_real else "ADD",
            "-": "FSUB" if is_real else "SUB",
            "*": "FMUL" if is_real else "MUL",
            "/": "FDIV" if is_real else "DIV",
        }
        relational_map = {
            ".LT.": "FINF" if is_real else "INF",
            ".LE.": "FINFEQ" if is_real else "INFEQ",
            ".GT.": "FSUP" if is_real else "SUP",
            ".GE.": "FSUPEQ" if is_real else "SUPEQ",
            ".EQ.": "EQUAL",
        }

        if operator in arithmetic_map:
            return [arithmetic_map[operator]]
        if operator == ".NE.":
            return ["EQUAL", "NOT"]
        if operator in relational_map:
            return [relational_map[operator]]
        if operator == ".AND.":
            return ["AND"]
        if operator == ".OR.":
            return ["OR"]

        raise VMCodegenError(f"Operador binario ainda nao suportado no backend VM: {operator}")

    def _emit_unop_operator(self, operator, operand_type):
        if operator == ".NOT.":
            return ["NOT"]
        if operator == "-":
            if operand_type in REAL_TYPES:
                return ["PUSHF -1.0", "FMUL"]
            return ["PUSHI -1", "MUL"]

        raise VMCodegenError(f"Operador unario ainda nao suportado no backend VM: {operator}")
