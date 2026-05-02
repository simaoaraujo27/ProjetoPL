from IR.ir import IRConstant, IRTemp, IRVariable

from .vm_common import INTEGER_TYPES, REAL_TYPES, VMCodegenError


class VMValuesMixin:
    def _emit_value(self, value, expected_type=None):
        actual_type = self._normalize_type(getattr(value, "type", None))
        expected_type = self._normalize_type(expected_type)
        code = []

        if isinstance(value, IRConstant):
            code.extend(self._emit_constant(value, expected_type))
        elif isinstance(value, (IRVariable, IRTemp)):
            code.extend(self._emit_load_from_slot(value))
        else:
            raise VMCodegenError(f"Valor IR invalido para geracao VM: {value}")

        if expected_type is not None:
            code.extend(self._emit_conversion(actual_type, expected_type))

        return code

    def _emit_constant(self, constant, expected_type=None):
        constant_type = self._normalize_type(expected_type or constant.type)
        value = constant.value

        if constant_type in INTEGER_TYPES:
            return [f"PUSHI {self._logical_or_integer_value(value)}"]
        if constant_type in REAL_TYPES:
            return [f"PUSHF {self._real_value(value)}"]
        if constant_type == "CHARACTER":
            escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
            return [f'PUSHS "{escaped}"']

        raise VMCodegenError(
            f"Tipo de constante ainda nao suportado no backend VM: {constant_type}"
        )

    def _emit_load_from_slot(self, value):
        region, index = self._resolve_slot(value)

        if region == "global":
            return [f"PUSHG {index}"]
        if region in {"local", "param", "temp"}:
            return [f"PUSHL {index}"]

        raise VMCodegenError(f"Regiao de memoria invalida para load: {region}")

    def _emit_store(self, target):
        region, index = self._resolve_slot(target)

        if region == "global":
            return [f"STOREG {index}"]
        if region in {"local", "param", "temp"}:
            return [f"STOREL {index}"]

        raise VMCodegenError(f"Regiao de memoria invalida para store: {region}")

    def _emit_conversion(self, actual_type, expected_type):
        if actual_type is None or expected_type is None or actual_type == expected_type:
            return []
        if actual_type in INTEGER_TYPES and expected_type in REAL_TYPES:
            return ["ITOF"]
        if actual_type in REAL_TYPES and expected_type in INTEGER_TYPES:
            return ["FTOI"]
        return []

    def _write_opcode_for_type(self, value_type):
        normalized = self._normalize_type(value_type)
        if normalized in INTEGER_TYPES:
            return "WRITEI"
        if normalized in REAL_TYPES:
            return "WRITEF"
        if normalized == "CHARACTER":
            return "WRITES"
        raise VMCodegenError(f"Tipo ainda nao suportado para WRITE no backend VM: {normalized}")

    def _expected_operand_types(self, operator, result_type, left_type, right_type):
        normalized_result = self._normalize_type(result_type)

        if operator in {".AND.", ".OR."}:
            return ("LOGICAL", "LOGICAL")
        if operator in {".LT.", ".LE.", ".GT.", ".GE.", ".EQ.", ".NE."}:
            comparison_type = "REAL" if left_type in REAL_TYPES or right_type in REAL_TYPES else None
            return (comparison_type, comparison_type)
        if normalized_result in REAL_TYPES:
            return ("REAL", "REAL")
        return (normalized_result, normalized_result)

    def _resolve_slot(self, value):
        name = value.name.upper()

        if self.current_layout is not None:
            local_slot = self.current_layout.lookup(name)
            if local_slot is not None:
                return local_slot

        if name in self.layout.global_offsets:
            return ("global", self.layout.global_offsets[name])

        raise VMCodegenError(f"Valor '{name}' nao tem offset definido para geracao VM")

    def _emit_slot_allocation(self, count):
        if count <= 0:
            return []
        if count == 1:
            return ["PUSHI 0"]
        return [f"PUSHN {count}"]

    def _emit_unit_prologue(self, layout):
        return self._emit_slot_allocation(layout.local_slot_count)

    def _normalize_type(self, value_type):
        if value_type is None:
            return None
        upper = value_type.upper()
        if upper == "DOUBLE PRECISION":
            return "REAL"
        return upper

    def _logical_or_integer_value(self, value):
        if isinstance(value, bool):
            return 1 if value else 0

        text = str(value).upper()
        if text in {".TRUE.", "TRUE"}:
            return 1
        if text in {".FALSE.", "FALSE"}:
            return 0
        return int(value)

    def _real_value(self, value):
        if isinstance(value, str):
            return float(value)
        return float(value)
