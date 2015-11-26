# this file is extraneous
# if you can guess why it's here, thank you for understanding my pain

import tulip.interpreter.lang as core

class MachineState():
    """
    wraps the current thread execution state
    """

    def __init__(self, bindings, program, registers):
        self.bindings = bindings   # map of strings to nodes (not references)
        self.program = program     # tree of core lang nodes
        self.registers = registers # sparse map of node refs to intermediate results

def fromProgram(program):
    s = MachineState(dict(), None, RegisterTable())
    s.program, s.bindings = core.preprocess(program, s.bindings)
    return s

class RegisterTable(dict):
    def __init__(self):
        return

    def __setitem__(self, k, v):
        dict.__setitem__(self, k, v)

    def show(self):
        o = "----[registers]------------\n"
        for k,v in self.items():
            o = o + ("%02d" % k) + ": " + v.show() + "\n"
        return o
