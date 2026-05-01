class SemanticError(Exception):
    pass


class Symbol:
    def __init__(
        self,
        name,
        kind,
        type=None,
        dimensions=None,
        params=None,
        return_type=None,
    ):
        self.name = name.upper()
        self.kind = kind
        self.type = type
        self.dimensions = dimensions or []
        self.params = params or []
        self.return_type = return_type

    def __repr__(self):
        parts = [f"name={self.name}", f"kind={self.kind}"]
        if self.type:
            parts.append(f"type={self.type}")
        if self.return_type:
            parts.append(f"return_type={self.return_type}")
        if self.params:
            parts.append(f"params={self.params}")
        if self.dimensions:
            parts.append(f"dimensions={self.dimensions}")
        return f"<Symbol {', '.join(parts)}>"


class SymbolTable:
    def __init__(self, name="global", parent=None):
        self.name = name
        self.parent = parent
        self.symbols = {}
        self.labels = {}
        self.label_references = []
        self.children = {}

    def define(self, symbol):
        name = symbol.name
        if name in self.symbols:
            raise SemanticError(f"Símbolo '{name}' já declarado no scope '{self.name}'")
        self.symbols[name] = symbol

    def declare_program(self, name):
        self.define(Symbol(name, kind="program"))

    def declare_function(self, name, return_type=None, params=None):
        self.define(
            Symbol(
                name,
                kind="function",
                return_type=return_type,
                params=params or [],
            )
        )

    def declare_subroutine(self, name, params=None):
        self.define(Symbol(name, kind="subroutine", params=params or []))

    def declare_intrinsic(self, name, return_type=None, params=None):
        self.define(
            Symbol(
                name,
                kind="intrinsic",
                return_type=return_type,
                params=params or [],
            )
        )

    def declare_variable(self, name, type=None):
        self.define(Symbol(name, kind="variable", type=type))

    def declare_parameter(self, name, type=None):
        self.define(Symbol(name, kind="parameter", type=type))

    def declare_array(self, name, type=None, dimensions=None):
        self.define(Symbol(name, kind="array", type=type, dimensions=dimensions or []))

    def require_symbol(self, name):
        found = self.lookup(name)
        if found is None:
            raise SemanticError(f"Símbolo '{name.upper()}' não declarado")
        return found

    def require_variable(self, name):
        found = self.require_symbol(name)
        if found.kind not in ("variable", "parameter"):
            raise SemanticError(f"Identificador '{name.upper()}' não é variável")
        return found

    def require_assignable(self, name):
        found = self.require_symbol(name)
        if found.kind not in ("variable", "parameter", "function"):
            raise SemanticError(f"Identificador '{name.upper()}' não pode receber valor")
        return found

    def require_array(self, name):
        found = self.require_symbol(name)
        if found.kind != "array":
            raise SemanticError(f"Identificador '{name.upper()}' não é array")
        return found

    def require_function(self, name):
        found = self.require_symbol(name)
        if found.kind not in ("function", "intrinsic"):
            raise SemanticError(f"Identificador '{name.upper()}' não é função")
        return found

    def require_subroutine(self, name):
        found = self.require_symbol(name)
        if found.kind != "subroutine":
            raise SemanticError(f"Identificador '{name.upper()}' não é subrotina")
        return found

    def lookup(self, name):
        name = name.upper()
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

    def lookup_current(self, name):
        return self.symbols.get(name.upper())

    def define_label(self, label):
        if label in self.labels:
            raise SemanticError(f"Label '{label}' já existe no scope '{self.name}'")
        self.labels[label] = True

    def require_label(self, label):
        if not self.lookup_label(label):
            raise SemanticError(f"Label '{label}' não declarada no scope '{self.name}'")
        return True

    def lookup_label(self, label):
        return self.labels.get(label)

    def add_label_reference(self, label, kind):
        self.label_references.append({"label": label, "kind": kind})

    def create_child(self, name):
        child = SymbolTable(name=name, parent=self)
        self.children[name.upper()] = child
        return child

    def format_tree(self, indent=0):
        prefix = " " * indent
        lines = [f"{prefix}<SymbolTable {self.name}>"]

        if self.symbols:
            lines.append(f"{prefix}  symbols:")
            for symbol in self.symbols.values():
                lines.append(f"{prefix}    {symbol}")
        else:
            lines.append(f"{prefix}  symbols: []")

        if self.labels:
            lines.append(f"{prefix}  labels: {list(self.labels.keys())}")
        else:
            lines.append(f"{prefix}  labels: []")

        if self.label_references:
            lines.append(f"{prefix}  label_references:")
            for reference in self.label_references:
                lines.append(f"{prefix}    {reference['kind']} -> {reference['label']}")
        else:
            lines.append(f"{prefix}  label_references: []")

        if self.children:
            lines.append(f"{prefix}  children:")
            for child in self.children.values():
                lines.append(child.format_tree(indent + 4))
        else:
            lines.append(f"{prefix}  children: []")

        return "\n".join(lines)

    def __repr__(self):
        return self.format_tree()
