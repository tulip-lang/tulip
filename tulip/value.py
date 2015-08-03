class Value(object):
    def dump(self):
        assert False, 'abstract'

    def dump_nested(self):
        return self.dump()

class Int(Value):
    def __init__(self, value):
        self.value = value

class String(Value):
    def __init__(self, value):
        self.value = value

class Callable(Value):
    def arity(self):
        raise "abstract"

    def invoke(self, rt, argv):
        raise "abstract"

class Token(Value):
    def __init__(self, value):
        self.value = value

    def dump(self):
        return u'<Token %s>' % self.value.dump()

class Func(Callable):
    def __init__(self, bytecode, arity):
        self._arity = arity
        self.bytecode = bytecode

    def arity(self):
        return self._arity

    def invoke(self, frame, argv):
        frame = frame.rt.make_frame(self.bytecode, self.arity, argv)
        frame.rt.push(self.bytecode, frame)

class Tagged(Callable):
    def __init__(self, symbol, args):
        self.symbol = symbol
        self.args = args

    def dump(self):
        if len(self.args) == 0:
            return u'.%s' % self.symbol.name
        else:
            args = u' '.join([a.dump_nested() for a in self.args])
            return u'.%s %s' % (self.symbol.name, args)

    def dump_nested(self):
        return u'(%s)' % self.dump()

    def invoke(self, rt, argv):
        assert False, 'TODO'

# TODO
class Pattern(Value):
    def __init__(self, bytecode):
        self.bytecode = bytecode
