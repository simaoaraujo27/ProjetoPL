from .vm_arrays import VMArraysMixin
from .vm_common import VMCodegenError
from .vm_instructions import VMInstructionMixin
from .vm_layout import VMLayoutMixin
from .vm_values import VMValuesMixin


class VMCodeGenerator(VMInstructionMixin, VMArraysMixin, VMValuesMixin, VMLayoutMixin):
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.layout = None
        self.main_name = None
        self.current_layout = None
        self.current_unit_name = None
        self.current_is_main = False
        self.current_array_bounds = {}


__all__ = ["VMCodeGenerator", "VMCodegenError"]
