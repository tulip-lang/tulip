# interface to evaluation

class MachineContext():
    """
    single-threaded tulip execution context
    wraps an AST and incrementally reduces it
    """

    def __init__(self, ast):
        self.program = ast
        self.cycle   = 0
        self.symbols = None

    def step(self, n):
        """performs n iterations of the interpreter loop"""
        return

    def loop(self):
        """runs the interpreter loop until program yields"""
        return

    def halt(self):
        """prematurely stops the interpreter"""
        assert False, "DO NOT IMPLEMENT CONCURRENCY YET"

    def dump(self):
        """returns all context internal state"""
        return
