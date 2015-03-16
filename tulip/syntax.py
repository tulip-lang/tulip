from tulip.symbol import Symbol, SymbolTable

_symbol_table = SymbolTable()
sym = _symbol_table.sym

class Syntax(object):
    def dump_nested(self):
        return self.dump()

class PatternSyntax(Syntax):
    pass

class ExprSyntax(Syntax):
    pass

class ModuleSyntax(Syntax):
    pass

class Int(Syntax):
    def __init__(self, value):
        self.value = value

    def dump(self):
        return "%d" % self.value

class Var(Syntax):
    def __init__(self, symbol):
        self.symbol = symbol

    def dump(self):
        return self.symbol.name

class Apply(Syntax):
    def __init__(self, exprs):
        self.exprs = exprs

    def dump(self):
        return " ".join([e.dump_nested() for e in self.exprs])

    def dump_nested(self):
        return "(%s)" % self.dump()

class Chain(Syntax):
    def __init__(self, exprs):
        self.exprs = exprs

    def dump(self):
        return " > ".join([e.dump() for e in self.exprs])

    def dump_nested(self):
        return "(%s)" % self.dump()

class Lazy(Syntax):
    def __init__(self, expr):
        self.expr = expr

    def dump(self):
        return "~%s" % self.expr.dump_nested()

class Let(Syntax):
    class Clause(object):
        def __init__(self, name, patterns, expr):
            self.name = name
            self.patterns = patterns
            self.expr = expr

    def __init__(self, clauses, expr):
        self.clauses = clauses
        self.expr = expr

class Tag(Syntax):
    def __init__(self, symbol):
        self.symbol = symbol

    def dump(self):
        return ".%s" % self.symbol.name
