import tulip.interpreter.lang as core
import tulip.interpreter.scope as scope
from tulip.interpreter.state import MachineState

# this file contains the "real" program evaluation logic
# it is a translation of abstract machine rules, originally implemented in haskell, to rpython
# it's a little simplistic, and its control flow is very explicit for rpython's sake
# it will be worked into a set of coroutines to permit multithreaded evaluation

def expand(node, state):

    program = state.program
    bindings = state.bindings
    register = state.register

    ########################################
    # expressions

    # if isinstance(program[node], core.Block):
        # todo find names referenced within the block, and cache their values in the block's scope

    # apply expansion expands each term sequentially
    if isinstance(program[node], core.Apply):
        for v in program[node].chain:
            state = expand(v, state)

    # let expansion does not perform any binding
    if isinstance(program[node], core.Let):
        state = expand(program[node].body, state)

    # a lambda's argument can only be expanded during reduction
    # todo figured out how name expansion can be avoided in this case
    if isinstance(program[node], core.Lambda):
        state = expand(program[node].body, state)

    # xxx [question] do branch predicates need expansion?
    if isinstance(program[node], core.Branch):
        for v in program[node].consequences:
            state = expand(v, state)

    ########################################
    # values

    # literals cannot be expanded

    if isinstance(program[node], core.Name):
        v = scope.lookup(program[node].name, program[node].scope, bindings)
        if v is not None:
            program[node] = program[v]

    if isinstance(program[node], core.Tag):
        for v in program[node].contents:
            state = expand(v, state)

    if isinstance(program[node], core.Builtin):
        for v in program[node].args:
            bindings, program = expand(v, bindings, program)
            state = expand(v, state)

    return MachineState(bindings, program, register)

def reduce(node, state):

    program = state.program
    bindings = state.bindings
    register = state.register

    ########################################
    # expressions

    if isinstance(program[node], core.Block):
        # sequentially expand then reduce contents
        for v in program[node].sequence:
            state = expand(v, state)
            state = reduce(v, state)

        # xxx [question] is destructive reduction ever relevent for blocks?

        # destructive reduction
        # program[node] = program[v]

        # nondestructive evaluation
        # return value should already be in register from last apply

    if isinstance(program[node], core.Apply):
        # single-argument apply does not perform evaluation
        if len(program[node].chain) == 1:
            # destructive reduction
            # program[node] = program[program[node].chain[0]]
            register = program[program[node].chain[0]]
        else:
            # set the register to n+1, then reduce n
            for n in range(0, len(program[node].chain) - 1):
                # state = reduce(program[node].chain[n + 1])
                # xxx [question] how do i implement eager semantics? im worried a forward reduction will break with higher-order functions
                register = program[program[node].chain[n + 1]]
                state = reduce(program[node].chain[n], state)

    if isinstance(program[node], core.Let):
        state = reduce(program[node].body, state)
        bindings[program[node].scope].update({program[node].bind.name: program[node].body})

    # lambda reduction coordinates with apply, binds the apply argument to the lambda name, expands & reduces the lambda body with that name bound
    if isinstance(program[node], core.Lambda):
        return

    if isinstance(program[node], core.Branch):
        bindings, program = branch(program[node], bindings, program);

    ########################################
    # values

    # cannot reduce a literal

    # if a name makes it to reduction, the name wasn't found, nor was part of a pending bind
    if isinstance(program[node], core.Name):
        assert True, "name not found@" + program[node].name

    # if isinstance(program[node], Tag):

    # todo builtin dispatch

    # if isinstance(program[node], Builtin):

    return MachineState(bindings, program, register)

def branch(node, state):
    return (bindings, program)

# def concur(node, state):
#     return

# def confer(node, state):
#     return
