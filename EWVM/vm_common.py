from dataclasses import dataclass, field


UNIT_LABEL_PREFIX = "UNIT_"
REAL_TYPES = {"REAL", "DOUBLE PRECISION"}
INTEGER_TYPES = {"INTEGER", "LOGICAL"}


class VMCodegenError(Exception):
    pass


@dataclass
class UnitLayout:
    name: str
    params: dict[str, int] = field(default_factory=dict)
    locals: dict[str, int] = field(default_factory=dict)
    temps: dict[str, int] = field(default_factory=dict)

    def lookup(self, name):
        upper_name = name.upper()
        if upper_name in self.params:
            return ("param", self.params[upper_name])
        if upper_name in self.locals:
            return ("local", self.locals[upper_name])
        if upper_name in self.temps:
            return ("temp", self.temps[upper_name])
        return None

    @property
    def local_slot_count(self):
        return len(self.locals) + len(self.temps)


@dataclass
class VMMemoryLayout:
    global_offsets: dict[str, int] = field(default_factory=dict)
    main_layout: UnitLayout | None = None
    unit_layouts: dict[str, UnitLayout] = field(default_factory=dict)
    array_bounds: dict[tuple[str, str], list[object]] = field(default_factory=dict)
