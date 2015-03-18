from tulip.symbol import Symbol, SymbolTable

_symbol_table = SymbolTable()
sym = _symbol_table.sym

class Syntax(object):
    def dump_nested(self):
        return self.dump()

    def dump(self):
        assert False, "abstract"

class Expr(Syntax):
    pass

class Pattern(Syntax):
    pass

class ModuleItem(Syntax):
    pass

class Int(Expr):
    def __init__(self, value):
        self.value = value

    def dump(self):
        return u"%d" % self.value

class Var(Expr):
    def __init__(self, symbol):
        self.symbol = symbol

    def dump(self):
        return self.symbol.name

class Autovar(Expr):
    def dump(self):
        return u'$'

class Apply(Expr):
    def __init__(self, exprs):
        self.exprs = exprs

    def dump(self):
        return u" ".join([e.dump_nested() for e in self.exprs])

    def dump_nested(self):
        return u"(%s)" % self.dump()

class Chain(Expr):
    def __init__(self, exprs):
        self.exprs = exprs

    def dump(self):
        return u" > ".join([e.dump() for e in self.exprs])

    def dump_nested(self):
        return u"(%s)" % self.dump()

class Lazy(Expr):
    def __init__(self, expr):
        self.expr = expr

    def dump(self):
        return u"~%s" % self.expr.dump_nested()

class Let(Expr):
    class Clause(Syntax):
        def __init__(self, name, patterns, expr):
            self.name = name
            self.patterns = patterns
            self.expr = expr

    def __init__(self, clauses, expr):
        self.clauses = clauses
        self.expr = expr

class Lam(Expr):
    class Clause(object):
        def __init__(self, pattern, body):
            self.pattern = pattern
            self.body = body

        def dump(self):
            return u'%s => %s' % (self.pattern.dump(), self.body.dump())

    def __init__(self, clauses):
        self.clauses = clauses

    def dump(self):
        body = u'; '.join([c.dump() for c in self.clauses])
        return u'[ %s ]' % body

class Autolam(Expr):
    def __init__(self, body):
        self.body = body

    def dump(self):
        return u'[ %s ]' % self.body.dump()

class Tag(Expr):
    def __init__(self, symbol):
        self.symbol = symbol

    def dump(self):
        return u".%s" % self.symbol.name

class VarPat(Pattern):
    def __init__(self, symbol):
        self.symbol = symbol

    def dump(self):
        return self.symbol.name

class TagPat(Pattern):
    def __init__(self, symbol, patterns):
        self.symbol = symbol
        self.patterns = patterns

    def dump(self):
        patterns = u" ".join([e.dump_nested() for e in self.patterns])
        return u'.%s %s' % (self.symbol.name, patterns)

    def dump_nested(self):
        return u'(%s)' % self.dump()

class NamedPat(Pattern):
    def __init__(self, symbol):
        self.symbol = symbol

    def dump(self):
        return u"%%%s" % self.symbol.name
