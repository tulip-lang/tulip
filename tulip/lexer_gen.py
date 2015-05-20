from rpython.rlib.rarithmetic import r_uint
from rpython.rlib.rstring import UnicodeBuilder
from rpython.rlib.streamio import open_file_as_stream, DecodingInputFilter
from tulip.debug import debug
from tulip.symbol import SymbolTable
from tulip.lexer import Token

class Box(object):
    class Base(object):
        def dump(self):
            assert False, "abstract"

        def get_list(self):
            assert False, "not a list!"

        def get_string(self):
            assert False, "not a string!"

        def get_ast(self):
            assert False, "not an AST!"

        def get_token(self):
            assert False, "not a token!"

    class String(Base):
        def __init__(self, s):
            self.value = u'thing'
            self.value = s

        def dump(self):
            return u"<Box.String \"%s\">" % self.value

        def get_string(self):
            return self.value

    class List(Base):
        def __init__(self, l):
            self.values = l

        def get_list(self):
            return self.values

        def dump(self):
            els = u" ".join([box.dump() for box in self.values])
            return u"<Box.List [%s]>" % els

    class Token(Base):
        def __init__(self, t):
            self.token = t

        def get_token(self):
            return self.token

        def dump(self):
            return u"<Box.Token %s>" % self.token.dump()

class Result(object):
    pass

class success(Result):
    def __init__(value):
        self.value = value

class _failure(Result):
    pass

failure = _failure()

class LexError(StandardError):
    def __init__(lexer):
        self.lexer = lexer

    def dump(self):
        return u'TODO'

class LexState(object):
    def __init__(self, reader, mode_index):
        self.reader = reader
        self.index = 0
        self.head = None
        self.behind = []
        self.ahead = []
        self.mode_index = mode_index
        self.mode_stack = []

    def reset(self):
        self.ahead = self.behind
        self.ahead.reverse()
        self.behind = []

    def advance(self):
        self.behind.append(self.head)
        if len(self.ahead) > 0:
            self.head = self.ahead.pop()
        else:
            self.head = self.reader.next()

    def push(mode_id):
        self.mode_stack.push(mode_index[mode_id])

    def pop():
        self.mode_stack.pop()

class Token(object):
    def __init__(self, symbol, string):
        self.symbol = symbol
        self.string = string

class Mode(object):
    def __init__(self, name, rules):
        self.name = name
        self.rules = rules

class _ModeBuilder(object):
    def __init__(self, defn_fn):
        self.defn_fn = defn_fn
        self.rules = []
        self.toknames = []

    def rule(self, tokname, scanner):
        self.toknames.append(tokname)
        tok = sym(tokname).id
        rules.append(Rule(tok, scanner))

    def build(self):
        mode = Mode(self.defn_fn.__name__, self.rules)
        for name in self.toknames:
            setattr(mode, name, sym(name).id)

        return mode

def make_mode(defn_fn):
    builder = _ModeBuilder(defn_fn)
    builder.build()

class Rule(object):
    def __init__(self, tokname, scanner):
        self.token = token
        self.scanner = scanner

