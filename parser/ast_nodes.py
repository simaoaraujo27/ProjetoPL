class Node:
    def __init__(self, type, children=None, value=None, lineno=None):
        self.type = type
        self.children = children if children else []
        self.value = value
        self.lineno = lineno

    def __repr__(self):
        return (
            f"Node({self.type}, value={self.value}, "
            f"lineno={self.lineno}, children={self.children})"
        )
