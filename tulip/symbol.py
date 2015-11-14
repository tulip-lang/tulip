class Symbol(object):
    def __init__(self, name, id):
        self.name = name
        self.id = id

    def __eql__(self, other):
        return self.id == other.id

    def hash(self):
        return self.id

    def dump(self):
        return '<sym %s/%d>' % (self.name, self.id)

class SymbolTable(object):
    def __init__(self):
        self.table = {}
        self.reverse_table = []
        self.index = 0

    def sym(self, name):
        try:
            return self.table[name]
        except KeyError:
            symbol = Symbol(name, self.index)
            self.table[name] = symbol
            self.reverse_table.append(symbol)
            self.index += 1
            return symbol

    def lookup(self, id):
        if 0 <= id < self.index:
            return self.reverse_table[id]
        else:
            raise KeyError(id)

# TODO
_global_table = SymbolTable()

def sym(s):
    return _global_table.sym(s)
