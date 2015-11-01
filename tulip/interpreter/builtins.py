from tulip.code import *

builtins = {}

# *shrugs* i wanted to fold a predicate but
def allNumbers(list):
    for i in list:
        if isinstance(i, Constant) and isinstance(i.value, (int, long, float)):
            continue
        else:
            return False
    return True

builtins["+"] = {"arity": 2, "definition": (lambda xs: xs[0].value + xs[1].value), "check": allNumbers}
builtins["-"] = {"arity": 2, "definition": (lambda xs: xs[0].value - xs[1].value), "check": allNumbers}
