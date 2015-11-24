# this file is extraneous
# if you can guess why it's here, thank you for understanding my pain

import tulip.interpreter.lang as core

class MachineState():
    """
    wraps the current thread execution state
    """

    def __init__(self, bindings, program, register):
        self.bindings = bindings
        self.program = program
        self.register = register

    @staticmethod
    def fromProgram(program):
        s = MachineState(dict(), None, None)
        s.program, s.bindings = core.preprocess(program, s.bindings)
        return s
