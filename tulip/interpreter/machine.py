# interface to evaluation

from tulip.interpreter.dispatch import *
from tulip.code import *
from tulip.symbol import Symbol

class MachineContext():
    """
    single-threaded tulip execution context
    wraps an AST and incrementally reduces it
    """

    def __init__(self, ast):
        # DEBUG: hardcoded program
        ast = Apply([Name(Symbol("f", 0)), Name(Symbol("x", 1))])
        self.program = ast
        self.cycle   = 0
        self.symbols = None
        self.cursor  = ast

    def step(self, n):
        """performs n iterations of the interpreter loop"""
        while n > 0:
            dispatch(self.cursor, self)
            n = n - 1

    def loop(self):
        """runs the interpreter loop until program yields"""
        while(dispatch(self.cursor, self)):
            self.loop()

    def halt(self):
        """prematurely stops evaluation in this context"""
        assert False, "DO NOT IMPLEMENT CONCURRENCY YET"

    def dump(self):
        """returns all context internal state"""
        return
