# symbol table structure

class SymbolTable():
    def __init__(self, parent):
        self.bindings = []
        self.parent   = parent
        self.children = []
        if parent:
            parent.children.append(self)

    def lookup(self, name):
        for bind in self.bindings:
            if bind.name == name:
                return bind
            else:
                continue
        if parent:
            return self.parent.lookup(name)
        else:
            return None

class Bind():
    def __init__(self, name, value):
        self.name = name
        self.value = value
