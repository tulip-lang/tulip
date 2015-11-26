import tulip.interpreter.lang as core
import tulip.value as v

# *shrugs* i wanted to fold a predicate but
def allNumbers(list):
    for i in list:
        if isinstance(i, core.Literal) and isinstance(i.value, (int, long, float)):
            continue
        else:
            return False
    return True

def literal(list):
    for i in list:
        if isinstance(i, core.Literal):
            continue
        else:
            return False
    return True

def no_check(_):
    return True

dispatch = {}
def builtin(arity, check=no_check):
    def decorator(fn):
        name = fn.__name__.replace('_', '-')
        dispatch[name] = {
          'arity': arity,
          'definition': fn,
          'check': check,
          'name': name
        }
        return fn

    return decorator


@builtin(2, check=allNumbers)
def add(args):
    return c.Constant(v.Int(args[0].value + args[1].value))

@builtin(2, check=allNumbers)
def sub(args):
    return c.Constant(v.Int(args[1].value - args[0].value))

@builtin(1, check=literal)
def p(args):
    print args[0].value.dump()
