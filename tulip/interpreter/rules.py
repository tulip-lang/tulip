import tulip.interpreter.lang as core
import tulip.interpreter.scope as scope
import tulip.interpreter.builtins as builtins
from tulip.interpreter.state import MachineState

# this file contains the "real" program evaluation logic
# it is a translation of abstract machine rules, originally implemented in haskell, to rpython
# it's a little simplistic, and its control flow is very explicit for rpython's sake
# it will be worked into a set of coroutines to permit multithreaded evaluation

def expand(node, state):

    ########################################
    # expressions

    # if isinstance(program[node], core.Block):
        # todo block closures

        # find names referenced within the block, and cache their values in the block's scope

    # apply expansion expands each term sequentially
    if isinstance(state.program[node], core.Apply):
        for v in state.program[node].chain:
            expand(v, state)

    # let expansion does not perform any binding
    if isinstance(state.program[node], core.Let):
        expand(state.program[node].body, state)

    # a lambda's argument can only be expanded during reduction
    # todo figured out how name expansion can be avoided in this case
    if isinstance(state.program[node], core.Lambda):
        expand(state.program[node].body, state)

    if isinstance(state.program[node], core.Branch):
        for p in state.program[node].predicates:
            expand(p, state)
        for c in state.program[node].consequences:
            expand(c, state)

    ########################################
    # values

    # literals cannot be expanded

    if isinstance(state.program[node], core.Name):
        v = scope.lookup(state.program[node].name, state.program[node].scope, state.bindings)
        if v is not None:
            state.program[node] = state.program[v]

    # tag contents will already be expanded from their application
    # if isinstance(state.program[node], core.Tag):

    if isinstance(state.program[node], core.Builtin):
        for v in state.program[node].args:
            expand(v, state)

def reduce(node, state):

    ########################################
    # expressions

    if isinstance(state.program[node], core.Block):
        # sequentially expand then reduce contents
        for v in state.program[node].sequence:
            expand(v, state)
            reduce(v, state)

        # nondestructive evaluation returns value of last sequence
        r = state.registers[state.program[node].sequence[len(state.program[node].sequence) - 1]]
        if r is not None:
            state.registers[node] = r
        else:
            state.registers[node] = None

    if isinstance(state.program[node], core.Apply):
        # single-argument apply is precluded by the compiler, and has no semantics
        if len(state.program[node].chain) == 1:
            assert False, "malformed apply"

        # eagerly evaluate arguments
        for v in state.program[node].chain[1:]:
            reduce(v, state)
        for v in state.program[node].chain[1:]:
            state.registers[state.program[node].chain[0]] = state.registers[v]
            reduce(state.program[node].chain[0], state)

        state.registers[node] = state.registers[state.program[node].chain[0]]


    if isinstance(state.program[node], core.Let):
        reduce(state.program[node].body, state)
        state.bindings[state.program[node].scope].update({state.program[node].bind.name: state.program[node].body})

    # lambda argument should already be in register from apply
    if isinstance(state.program[node], core.Lambda):
        state.bindings[state.program[node].scope].update({state.program[node].bind.name: state.registers[node]})
        reduce(state.program[node].body, state)

    if isinstance(state.program[node], core.Branch):
        branch(node, state);

    ########################################
    # values

    if isinstance(state.program[node], core.Literal):
        state.registers[node] = state.program[node]

    # if a name makes it to reduce, the name may be part of a pending bind (lambdas), or is an error
    if isinstance(state.program[node], core.Name):
        v = scope.lookup(state.program[node].name, state.program[node].scope, state.bindings)
        if v is not None:
            state.registers[node] = v
        else:
            assert False, "name not found: " + state.program[node].name

    # todo tag construction
    if isinstance(state.program[node], core.Tag):
        state.registers[node] = state.program[node]

    if isinstance(state.program[node], core.Builtin):
        b = builtins.dispatch[state.program[node].name]
        if b is not None:
            if b["arity"] == state.program[node].arity:
                args = list()
                for v in state.program[node].args:
                    reduce(v, state)
                    args.append(state.registers[v])
                if b["check"](args):
                    state.registers[node] = b["definition"](args)
                else:
                    assert False, "type mismatch in builtin call"
            else:
                assert False, "builtin called with wrong number of arguments"
        else:
            assert False, "builtin not found"


# branch tentatively checks for a boolean tag value
def branch(node, state):
    for p, c in zip(state.program[node].predicates, state.program[node].consequences):
        reduce(p, state)

        if state.registers[p] == core.Tag("t"):
            reduce(c, state)
            state.registers[node] = state.registers[c]
            return

    assert False, "failed branch"

# def concur(node, state):
#     return

# def confer(node, state):
#     return
