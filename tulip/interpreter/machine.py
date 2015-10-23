# interface to evaluation

from tulip.code import *
from tulip.interpreter.representation import preprocess

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
lambdaTest = Apply([Lambda([Name("x")], Builtin("print", 1, Name("x"))), Constant("lambda-test")])


class MachineContext():
    """
    single-threaded tulip execution context
    wraps an AST and incrementally reduces it
    """

    def __init__(self, ast):
        # DEBUG: hardcoded program
        self.cycle   = 0
        self.symbols = None
        self.program = None

        print "program in: " + bindingTest.dump()
        print

        d = preprocess(bindingTest)
        print d.show()

    def step(self, n):
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
