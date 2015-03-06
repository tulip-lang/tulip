from tulip.symbol import Symbol, SymbolTable

class Syntax(object):
    def dump_nested(self)
        return self.dump()

class Int(Syntax):
    def __init__(self, value):
        self.value = value

    def dump(self):
        return "%i" % self.value

class Var(Syntax):
    def __init__(self, symbol):
        return self.symbol = symbol

    def dump(self):
        return symbol.name

class Apply(Syntax):
    def __init__(self, exprs)
        self.exprs = exprs

    def dump(self):
        return " ".join(e.dump_nested() for e in self.exprs)

    def dump_nested(self):
        return "(%s)" % self.dump()

class Chain(Syntax):
    def __init__(self, exprs)
        self.exprs = exprs

    def dump(self):
        return " > ".join(e.dump_nested() for e in self.exprs)

    def dump_nested(self):
        return "(%s)" % self.dump()


class Tag(Syntax):
    def __init__(self, symbol):
        self.symbol = symbol

    def dump(self):
        return ".%s" % symbol.name
