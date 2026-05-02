from collections import OrderedDict

from IR.ir import IRTemp

from .vm_common import UNIT_LABEL_PREFIX, UnitLayout, VMMemoryLayout, VMCodegenError


class VMLayoutMixin:
    def build_memory_layout(self, ir_program):
        self.main_name = ir_program.name.upper()
        main_scope = self._require_scope(ir_program.name)
        sections = self._split_program_sections(ir_program)
        main_temps = self._collect_section_temps(sections["main"])
        global_offsets = self._build_global_offsets(main_scope)
        main_layout = UnitLayout(
            name=self.main_name,
            temps=self._build_temp_offsets(main_temps, 0),
        )
        unit_layouts = {}
        array_bounds = self._collect_array_bounds(sections)

        for unit_name, scope in self.symbol_table.children.items():
            if unit_name == self.main_name:
                continue
            unit_instructions = sections["units"].get(unit_name, [])
            unit_layouts[unit_name] = self._build_unit_layout(scope, unit_instructions)

        self.layout = VMMemoryLayout(
            global_offsets=global_offsets,
            main_layout=main_layout,
            unit_layouts=unit_layouts,
            array_bounds=array_bounds,
        )
        return self.layout

    def _build_global_offsets(self, scope):
        offsets = {}
        index = 0

        for symbol in scope.symbols.values():
            if symbol.kind not in {"variable", "parameter", "array", "function"}:
                continue
            offsets[symbol.name] = index
            index += 1

        return offsets

    def _build_unit_layout(self, scope, instructions):
        params = {}
        locals_ = {}
        parameter_names = [
            symbol.name for symbol in scope.symbols.values() if symbol.kind == "parameter"
        ]

        parameter_count = len(parameter_names)
        for position, parameter_name in enumerate(parameter_names):
            params[parameter_name] = position - parameter_count

        local_index = 0

        global_symbol = self.symbol_table.lookup_current(scope.name)
        if global_symbol is not None and global_symbol.kind == "function":
            locals_[global_symbol.name] = local_index
            local_index += 1

        for symbol in scope.symbols.values():
            if symbol.kind == "parameter":
                continue

            if symbol.kind in {"variable", "array", "function"}:
                if symbol.name in locals_:
                    continue
                locals_[symbol.name] = local_index
                local_index += 1

        temp_names = self._collect_section_temps(instructions)
        temps = self._build_temp_offsets(temp_names, local_index)
        return UnitLayout(name=scope.name.upper(), params=params, locals=locals_, temps=temps)

    def _build_temp_offsets(self, temp_names, start_index):
        return {
            temp_name.upper(): start_index + offset
            for offset, temp_name in enumerate(temp_names)
        }

    def _collect_section_temps(self, instructions):
        temp_names = []
        seen = set()

        for instruction in instructions:
            values = []
            if instruction.result is not None:
                values.append(instruction.result)
            values.extend(instruction.args)

            for value in values:
                if isinstance(value, IRTemp) and value.name not in seen:
                    temp_names.append(value.name)
                    seen.add(value.name)

        return temp_names

    def _require_scope(self, name):
        scope = self.symbol_table.children.get(name.upper())
        if scope is None:
            raise VMCodegenError(
                f"Scope '{name.upper()}' nao encontrado para geracao de codigo VM"
            )
        return scope

    def _split_program_sections(self, ir_program):
        sections = {"main": [], "units": OrderedDict()}
        current_target = sections["main"]

        for instruction in ir_program.instructions:
            if (
                instruction.opcode == "LABEL"
                and instruction.args
                and str(instruction.args[0]).startswith(UNIT_LABEL_PREFIX)
            ):
                current_unit_name = str(instruction.args[0])[len(UNIT_LABEL_PREFIX):]
                sections["units"][current_unit_name] = [instruction]
                current_target = sections["units"][current_unit_name]
                continue

            current_target.append(instruction)

        return sections

    def _collect_array_bounds(self, sections):
        array_bounds = {}

        for instruction in sections["main"]:
            if instruction.opcode != "ARRAY_DECL":
                continue
            array_name = instruction.args[0].name.upper()
            array_bounds[(self.main_name, array_name)] = list(instruction.args[1:])

        for unit_name, instructions in sections["units"].items():
            for instruction in instructions:
                if instruction.opcode != "ARRAY_DECL":
                    continue
                array_name = instruction.args[0].name.upper()
                array_bounds[(unit_name, array_name)] = list(instruction.args[1:])

        return array_bounds

    def _array_bounds_for_unit(self, unit_name):
        return {
            array_name: bounds
            for (scope_name, array_name), bounds in self.layout.array_bounds.items()
            if scope_name == unit_name
        }
