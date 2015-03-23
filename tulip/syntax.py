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
    def __init__(self, definitions, expr):
        self.definitions = definitions
        self.expr = expr

    def dump(self):
        clauses_ = u'; '.join([c.dump() for c in self.definitions])
        return u'%s; %s' % (clauses_, self.expr.dump())

    def dump_nested(self):
        return u'(%s)' % self.dump()

class Lam(Expr):
    class Clause(Syntax):
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
        if len(self.patterns) > 0:
            patterns = u" ".join([e.dump_nested() for e in self.patterns])
            return u'.%s %s' % (self.symbol.name, patterns)
        else:
            return u'.%s' % self.symbol.name

    def dump_nested(self):
        return u'(%s)' % self.dump()

class NamedPat(Pattern):
    def __init__(self, symbol):
        self.symbol = symbol

    def dump(self):
        return u"%%%s" % self.symbol.name

class Definition(ModuleItem):
    def __init__(self, symbol, patterns, body):
        assert isinstance(body, Expr)
        self.symbol = symbol
        self.patterns = patterns
        self.body = body

    def __init__(self, symbol, patterns, expr):
        self.symbol = symbol
        self.patterns = patterns
        self.expr = expr

    def dump(self):
        name_ = self.symbol.name
        expr_ = self.expr.dump()
        if len(self.patterns) == 0:
            return u'+ %s = %s' % (name_, expr_)
        else:
            patterns_ = u' '.join([p.dump_nested() for p in self.patterns])
            return u'+ %s %s = %s' % (name_, patterns_, expr_)

class Module(ModuleItem):
    def __init__(self, name, patterns, items):
        self.name = name
        self.patterns = patterns
        self.items = items

    def dump(self):
        if len(self.patterns) > 0:
            patterns_ = u' '.join([p.dump_nested() for p in self.patterns])
            heading = u'%s %s' % (self.name.name, patterns_)
        else:
            heading = u'%s' % self.name.name

        body = u'; '.join([i.dump() for i in self.items])
        return u'@module %s = [ %s ]' % (heading, body)
