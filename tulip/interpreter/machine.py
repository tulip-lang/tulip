# interface to evaluation

from tulip.interpreter.representation import preprocess
from tulip.interpreter.rules import *
from tulip.code import * # has to be last, because the rules import leaks its full import of representation

# should print 1
continuationTest = Block([ Let(Name("foo"), Constant(1))
                         , Let(Name("bar"), Lambda([Name("_")], Block([Apply([Builtin("print", 1, []), Name("foo")])])))
                         , Let(Name("foo"), Constant(3))
                         , Apply([Name("bar"), Constant(3)])
                         ])

# should reduce to <literal 2>
bindingTest = Block([ Let(Name("x"), Constant(2)), Apply([Name("x")])])

# should print "test"
builtinTest = Builtin("print", 1, [Constant("test")])

# should print "lambda-test"
lambdaTest = Apply([Lambda(Name("x"), Builtin("print", 1, [Name("x")])), Constant("lambda-test")])


class MachineContext():
    """
    single-threaded tulip execution context
    wraps an AST and incrementally reduces it
    """

    def __init__(self, ast):
        self.cycle   = 0 # iteration count
        self.program = ast
        self.bindings = dict()

        print ansi_blue + "ast in: "
        print self.program.dump()
        print

        self.program, self.bindings = preprocess(self.program, self.bindings)

        print "program in:"
        print self.program.show()

        self.bindings, self.program = expand(0, self.bindings, self.program)
        self.bindings, self.program = reduce(0, self.bindings, self.program)

        print ansi_green + "program out: "
        print self.program.show()

        for _,v in self.bindings.items():
            print v.show()
            print

    def step(self,n):
        """performs n iterations of the interpreter loop"""
        while n > 0:
            n = n - 1

    def loop(self):
        """runs the interpreter loop until program yields"""

    def halt(self):
        """prematurely stops evaluation in this context"""
        assert False, "DO NOT IMPLEMENT CONCURRENCY YET"

    def dump(self):
        """returns all context internal state for debugging"""
        return

ansi_blue = "\033[94m"
ansi_green = "\033[92m"
