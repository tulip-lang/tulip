from tulip.interpreter.representation import *
from tulip.interpreter.scope import *

# this file contains the "real" program evaluation logic
# it is a translation of abstract machine rules, originally implemented in haskell, to rpython
# it may be a little confusing, and i would advise you look out the abstract machine documentation for more precise details

def expand(node, bindings, program):
    print program.show()
    print 'node', node
    # expressions

    # if isinstance(program[node], Block):
        # build scope table for continuations, do not expand contents
        # this requires some analysis of the block contents, and is todo
    if isinstance(program[node], Apply):
        for v in program[node].chain:
            bindings, program = expand(v, bindings, program)
    if isinstance(program[node], Let):
        bindings, program = expand(program[node].body, bindings, program)
    # if isinstance(program[node], Lambda):
    # if isinstance(program[node], Branch):

    # values

    # if isinstance(program[node], Literal):
        # noop
    if isinstance(program[node], Name):
        v = lookup(program[node].name, program[node].scope, bindings)
        program[node] = program[v]
        assert v is not None, "name not found @" + str(node)
    # if isinstance(program[node], Tag):
        # noop
    # if isinstance(program[node], Builtin):

    return (bindings, program)

def reduce(node, bindings, program):

    # expressions

    if isinstance(program[node], Block):
        # sequentially expand then reduce contents
        for v in program[node].sequence:
            bindings, program = expand(v, bindings, program)
            bindings, program = reduce(v, bindings, program)
            r = v

        # destructive reduction
        program[node] = program[v]

    if isinstance(program[node], Apply):
        if len(program[node].chain) == 1:
            program[node] = program[program[node].chain[0]]
    if isinstance(program[node], Let):
        bindings, program = reduce(program[node].body, bindings, program)
        bindings[program[node].scope].update({program[node].bind.name: program[node].body})
    # if isinstance(program[node], Lambda):
    # if isinstance(program[node], Branch):

    # values

    # if isinstance(program[node], Literal):
    # if isinstance(program[node], Name):
    # if isinstance(program[node], Tag):
    # if isinstance(program[node], Builtin):

    return (bindings, program)

def branch(node):
    return

def concur(node):
    return

def confer(node):
    return
