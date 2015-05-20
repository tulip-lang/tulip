class RT(object):
    def __init__(self, config):
        self.imports = {}
        self.modules = {}
        self.call_stack = []
        self.config = config

    def push(frame):
        self.call_stack.append(frame)

    def push_tail(frame):
        self.call_stack.pop()
        self.push(frame)

    def return_(self, value):

    # annotate inline
    def active_frame(self):
        return self.call_stack[-1]

    def step(self):
        self.active_frame().step()

    # TODO: add jit annotations
    def run(self):
        try:
            while True:
                self.step()
        except ExitProgram:
            return

class Frame(object):
    def __init__(self, bytecode, rt, binding):
        self.rt = rt
        self.binding = binding
        self.pc = r_uint(0)

    def next(self):
        self.pc += 1
        return self.bytecode[self.pc - 1]

    def step(self):
        p = self.next()
        if p == code.LOAD_CONST:
            self.push(rt.load_const(self.next()))
        elif p == code.CALL:
            arity = self.next()
            fn = self.next()
            consumed = fn.accept_args(self, arity)
        pass

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
