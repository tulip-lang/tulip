class Value(object):
    pass

class Int(Value):
    def __init__(self, value):
        self.value = value

class Callable(Value):
    def arity(self):
        raise "abstract"

    def invoke(self, rt, argv):
        raise "abstract"

class Func(Callable):
    def __init__(self, bytecode, arity)
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

    def invoke(self, rt, argv):

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
