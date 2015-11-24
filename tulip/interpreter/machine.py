# single-threaded execution

import tulip.interpreter.lang  as lang
import tulip.interpreter.rules as rules
from tulip.interpreter.state import MachineState

class MachineContext():
    """
    single-threaded tulip execution context
    wraps an AST and incrementally reduces it
    """

    def __init__(self, ast):
        self.cycle   = 0 # iteration count
        self.state = MachineState.fromProgram(ast)

        print ansi_blue + "input state: "
        self.dump()
        print

    def step(self,n):
        """performs n iterations of the interpreter loop"""
        while n > 0:
            n = n - 1

    def loop(self):
        """runs the interpreter loop until program yields"""

    def run(self):
        """runtime test scaffolding, evaluates some expression until it is fully reduced"""

        self.state = rules.expand(0, self.state)
        self.state = rules.reduce(0, self.state)

        print ansi_green + "output state: "
        self.dump()
        print

        print "execution finished"


    def halt(self):
        """prematurely stops evaluation in this context"""
        assert False, "DO NOT IMPLEMENT CONCURRENCY YET"

    def dump(self):
        """printss all context internal state for debugging"""

        print self.state.program.show()

        for _,v in self.state.bindings.items():
            print v.show()

        if self.state.register is not None:
            print "returned: " + self.state.register.show()

ansi_blue = "\033[94m"
ansi_green = "\033[92m"
