class Code(object):
    def dump(self):
        assert False, 'abstract'

class Constant(Code):
    def __init__(self, value):
        self.value = value

    def dump(self):
        return u'<const %s>' % self.value.dump()

class Apply(Code):
    def __init__(self, nodes):
        self.nodes = nodes

    def dump(self):
        return u'<apply [%s]>' % u' '.join([e.dump() for e in self.nodes])

class Lambda(Code):
    def __init__(self, symbols, body):
        self.symbols = symbols
        self.body = body

    def dump(self):
        symbols = u' '.join([s.name for s in self.symbols])
        return u'<lambda [%s] %s>' % (symbols, self.body.dump())

class Block(Code):
    def __init__(self, nodes):
        self.nodes = nodes

    def dump(self):
        return u'<block [%s]>' % u'; '.join([e.dump() for e in self.nodes])

class Branch(Code):
    def __init__(self, clauses):
        self.clauses = clauses

    def dump(self):
        clauses = u' '.join([u'<cond %s %s>' % (c.dump(), b.dump()) for (c, b) in self.clauses])
        return u'<branch %s>' % clauses

class Name(Code):
    def __init__(self, symbol):
        self.symbol = symbol

    def dump(self):
        return u'<name %s>' % self.symbol.name

class Tag(Code):
    def __init__(self, symbol):
        self.symbol = symbol

    def dump(self):
        return u'<tag .%s>' % self.symbol

class Flag(Code):
    def __init__(self, symbol):
        self.symbol = symbol

    def dump(self):
        return u'<flag -%s>' % self.symbol.name

class FlagMap(Code):
    def __init__(self, pairs):
        self.pairs = pairs

    def dump(self):
        pairs_ = u' '.join([u"-%s: %s" % (s.name, e.dump()) for (s, e) in self.pairs])
        return u'<flag-map %s>' % pairs_

class Let(Code):
    def __init__(self, bind, body):
        self.bind = bind
        self.body = body

    def dump(self):
        return u'<let %(n)s %(b)s>' % {'n': self.bind.dump(), 'b': self.body.dump()}

class Builtin(Code):
    def __init__(self, name, arity, args):
        self.name = name
        self.arity = arity
        self.args = args

    def dump(self):
        return u'<builtin %(n)s/%(a)d %(v)s>' % { 'n': self.name
                                                , 'a': self.arity
                                                , 'v': u' '.join([e.dump() for e in self.args])
                                                }
