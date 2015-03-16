class RT(object):
    def __init__(self, config):
        self.imports = {}
        self.modules = {}

class Value(object):
    pass

class Module(Value):
    pass # TODO

class Int(Value):
    def __init__(self, value):
        self.value = value

class Func(Value):
    def __init__(self, bytecode, curried, remaining):
        self.bytecode = bytecode
        self.curried = curried
        self.remaining = remaining

class Tagged(Value):
    def __init__(self, symbol, args):
        self.symbol = symbol
        self.args = args

# TODO
class Pattern(Value):
    def __init__(self, bytecode):
        self.bytecode = bytecode

class NativeAction(Value):
    def __init__(self, impl):
        self.impl = impl

class NativeFunc(Value):
    def __init__(self, arity, impl):
        self.arity = arity
        self.impl = impl

class Lazy(Value):
    def __init__(self, application):
        self.application = application
