from tulip.symbol import sym
import tulip.lexer as L

class MalformedValue(ValueError):
    pass

def malformed(message):
    raise MalformedValue(message)

class Value(object):
    def dump(self):
        assert False, 'abstract'

    def dump_nested(self):
        return self.dump()

    def matches_tag(self, tag, arity):
        return False

    def matches_type(self, name):
        return False

    def is_list(self):
        return self.matches_tag(nil_sym, 0) or self.matches_tag(cons_sym, 2)

int_sym = sym(u'int')
class Int(Value):
    def __init__(self, value):
        self.value = value

    def matches_type(self, name):
        return name == int_sym

    def dump(self):
        return unicode(str(self.value))

string_sym = sym(u'str')
class String(Value):
    def __init__(self, value):
        self.value = value

    def matches_type(self, name):
        return name == string_sym

    def dump(self):
        return u"'{%s}" % self.value

class Bang(Value):
    def __init__(self):
        pass

    def dump(self):
        return u'!'

bang = Bang()

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

def cons_list(elements):
    i = len(elements)
    out = tag(u'nil', [])
    while i > 0:
        i -= 1
        out = tag(u'cons', [elements[i], out])

    return out

def rpy_list(value):
    out = []
    for e in cons_each(value):
        out.append(e)
    return out

def cons_each(value):
    while True:
        if value.matches_tag(cons_sym, 2):
            yield value.args[0]
            value = value.args[1]
        elif value.matches_tag(nil_sym, 0):
            return
        else:
            raise MalformedValue(u'rpy_list: bad cons-list')

def tag(name, values):
    return Tagged(sym(name), values)

class Tagged(Callable):
    def __init__(self, symbol, args):
        self.symbol = symbol
        self.args = args

    def matches_tag(self, tag, arity):
        return self.symbol == tag and len(self.args) == arity

    def dump(self):
        if self.is_list():
            return self.inspect_cons_list()

        if len(self.args) == 0:
            return u'.%s' % self.symbol.name
        else:
            args = u' '.join([a.dump_nested() for a in self.args])
            return u'.%s %s' % (self.symbol.name, args)

    def inspect_cons_list(self):
        els = [e.dump() for e in rpy_list(self)]

        return u'/[%s]' % u'; '.join(els)

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
