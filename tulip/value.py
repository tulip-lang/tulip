from tulip.symbol import sym
import tulip.lexer as L

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
        tok_name = L.Token.TOKENS[self.value.tokid]
        if self.value.value is None:
            return u'(*Token %s)' % tok_name
        else:
            return u'(*Token %s %s)' % (tok_name, self.value.value)

class Func(Callable):
    def __init__(self, bytecode, arity):
        self._arity = arity
        self.bytecode = bytecode

    def arity(self):
        return self._arity

    def invoke(self, frame, argv):
        frame = frame.rt.make_frame(self.bytecode, self.arity, argv)
        frame.rt.push(self.bytecode, frame)

cons_sym = sym(u'cons')
nil_sym = sym(u'nil')

class Tagged(Callable):
    def __init__(self, symbol, args):
        self.symbol = symbol
        self.args = args

    def dump(self):
        if self.is_list():
            return self.inspect_cons_list()

        if len(self.args) == 0:
            return u'.%s' % self.symbol.name
        else:
            args = u' '.join([a.dump_nested() for a in self.args])
            return u'.%s %s' % (self.symbol.name, args)

    def inspect_cons_list(self):
        current = self
        inspected = []

        try:
            while True:
                if current.symbol == cons_sym:
                    inspected.append(current.args[0].dump())
                    current = current.args[1]
                elif current.symbol == nil_sym:
                    break
                else:
                    assert False, 'bad cons-list'
        except KeyError as e:
            assert False, 'bad cons-list'

        return u'/[%s]' % u'; '.join(inspected)



    def is_list(self):
        return self.symbol == nil_sym or self.symbol == cons_sym

    def dump_nested(self):
        if self.is_list():
            return self.inspect_cons_list()

        return u'(%s)' % self.dump()

    def invoke(self, rt, argv):
        assert False, 'TODO'

# TODO
class Pattern(Value):
    def __init__(self, bytecode):
        self.bytecode = bytecode
