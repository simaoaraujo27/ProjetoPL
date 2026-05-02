from IR.ir import IRConstant

from .vm_common import VMCodegenError


class VMArraysMixin:
    def _emit_array_decl(self, instruction):
        array_var = instruction.args[0]
        bounds = list(instruction.args[1:])
        allocation_code = self._emit_total_array_size(bounds) + ["ALLOCN"]
        allocation_code.extend(self._emit_store(array_var))
        return allocation_code

    def _emit_load_array(self, instruction):
        array_var = instruction.args[0]
        indices = list(instruction.args[1:])
        code = self._emit_array_address(array_var, indices)
        code.append("LOAD 0")
        code.extend(self._emit_store(instruction.result))
        return code

    def _emit_store_array(self, instruction):
        array_var = instruction.args[0]
        source = instruction.args[-1]
        indices = list(instruction.args[1:-1])
        code = self._emit_array_address(array_var, indices)
        code.extend(
            self._emit_value(
                source,
                expected_type=self._normalize_type(getattr(array_var, "type", None)),
            )
        )
        code.append("STORE 0")
        return code

    def _emit_total_array_size(self, bounds):
        extents = [
            self._dimension_extent(bounds[index], bounds[index + 1])
            for index in range(0, len(bounds), 2)
        ]

        if not extents:
            return ["PUSHI 0"]

        code = self._emit_extent(extents[0])
        for extent in extents[1:]:
            code.extend(self._emit_extent(extent))
            code.append("MUL")
        return code

    def _emit_array_address(self, array_var, indices):
        bounds = self.current_array_bounds.get(array_var.name.upper())
        if bounds is None:
            raise VMCodegenError(
                f"Bounds do array '{array_var.name.upper()}' nao encontrados para geracao VM"
            )

        code = self._emit_load_from_slot(array_var)
        code.extend(self._emit_linearized_offset(indices, bounds))
        code.append("PADD")
        return code

    def _emit_linearized_offset(self, indices, bounds):
        dimension_count = len(bounds) // 2
        if len(indices) != dimension_count:
            raise VMCodegenError(
                f"Aridade invalida no acesso ao array: esperava {dimension_count}, recebeu {len(indices)}"
            )

        normalized_codes = []
        extents = []
        for position in range(dimension_count):
            lower = bounds[position * 2]
            upper = bounds[position * 2 + 1]
            normalized_codes.append(self._emit_index_minus_lower(indices[position], lower))
            extents.append(self._dimension_extent(lower, upper))

        code = normalized_codes[0]
        for position in range(1, dimension_count):
            code.extend(self._emit_extent(extents[position]))
            code.append("MUL")
            code.extend(normalized_codes[position])
            code.append("ADD")
        return code

    def _emit_index_minus_lower(self, index_value, lower_bound):
        code = self._emit_value(index_value, expected_type="INTEGER")
        code.extend(self._emit_value(lower_bound, expected_type="INTEGER"))
        code.append("SUB")
        return code

    def _dimension_extent(self, lower_bound, upper_bound):
        constant_lower = self._constant_int_or_none(lower_bound)
        constant_upper = self._constant_int_or_none(upper_bound)
        if constant_lower is not None and constant_upper is not None:
            return IRConstant(type="INTEGER", value=constant_upper - constant_lower + 1)
        return ("extent", lower_bound, upper_bound)

    def _emit_extent(self, extent):
        if isinstance(extent, IRConstant):
            return self._emit_constant(extent, "INTEGER")
        _, lower_bound, upper_bound = extent
        code = self._emit_value(upper_bound, expected_type="INTEGER")
        code.extend(self._emit_value(lower_bound, expected_type="INTEGER"))
        code.append("SUB")
        code.append("PUSHI 1")
        code.append("ADD")
        return code

    def _constant_int_or_none(self, value):
        if not isinstance(value, IRConstant):
            return None
        try:
            return self._logical_or_integer_value(value.value)
        except Exception:
            return None
