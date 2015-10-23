from tulip.interpreter.representation import *
from tulip.interpreter.scope import *

# this file contains the "real" program evaluation logic
# it is a translation of abstract machine rules, originally implemented in haskell, to rpython
# it may be a little confusing, and i would advise you look out the abstract machine documentation for more precise details

def expand(node, program):

    # expressions

    if isinstance(program[node], Block):
        return
    if isinstance(program[node], Apply):
        return
    if isinstance(program[node], Let):
        return
    if isinstance(program[node], Lambda):
        return
    if isinstance(program[node], Branch):
        return

    # values

    if isinstance(program[node], Literal):
        return
    if isinstance(program[node], Name):
        return
    if isinstance(program[node], Tag):
        return
    if isinstance(program[node], Builtin):
        return

def reduce(node, program):

    # expressions

    if isinstance(program[node], Block):
        return
    if isinstance(program[node], Apply):
        return
    if isinstance(program[node], Let):
        return
    if isinstance(program[node], Lambda):
        return
    if isinstance(program[node], Branch):
        branch(node)

    # values

    if isinstance(program[node], Literal):
        return
    if isinstance(program[node], Name):
        return
    if isinstance(program[node], Tag):
        return
    if isinstance(program[node], Builtin):
        return

def branch(node):
    return

def concur(node):
    return

def confer(node):
    return
