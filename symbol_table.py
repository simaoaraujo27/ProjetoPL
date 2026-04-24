# symbol_table.py

class Symbol:
    def __init__(self, name, kind, type=None, dimensions=None, params=None, return_type=None):
        self.name = name.upper()   # Fortran é case-insensitive
        self.kind = kind           # variable, array, function, subroutine, parameter
        self.type = type           # INTEGER, REAL, LOGICAL...
        self.dimensions = dimensions or []
        self.params = params or []
        self.return_type = return_type

    def __repr__(self):
        return f"<Symbol {self.name}, kind={self.kind}, type={self.type}>"


class SymbolTable:
    def __init__(self, name="global", parent=None):
        self.name = name
        self.parent = parent
        self.symbols = {}   # variáveis, funções, etc.
        self.labels = {}    # labels (DO, GOTO, etc.)

    def define(self, symbol):
        name = symbol.name
        if name in self.symbols:
            raise Exception(f"Símbolo '{name}' já declarado no scope '{self.name}'")
        self.symbols[name] = symbol

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
            raise Exception(f"Label '{label}' já existe no scope '{self.name}'")
        self.labels[label] = True

    def lookup_label(self, label):
        return self.labels.get(label)

    def create_child(self, name):
        return SymbolTable(name=name, parent=self)

    def __repr__(self):
        return f"<SymbolTable {self.name}, symbols={list(self.symbols.keys())}, labels={list(self.labels.keys())}>"