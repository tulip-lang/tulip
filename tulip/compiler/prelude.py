### [jneen] XXX HACK TODO: actually make a prelude ###
import tulip.interpreter.builtins as b
import tulip.code as c
from tulip.symbol import sym

sym_counter = [0]
def builtin_sym():
    sym_counter[0] += 1
    return sym('##builtin##%d' % sym_counter[0])

def builtin_let(builtin):
    vars = [builtin_sym() for _ in xrange(0, builtin['arity'])]
    names = [c.Name(v) for v in vars]
    builtin_call = c.Builtin(builtin['name'], builtin['arity'], names)

    return c.Let(sym(builtin['name']), c.nested_lambda(vars, builtin_call))

prelude = map(builtin_let, b.dispatch.values())

def with_prelude(expr):
    return c.Block(prelude + [expr])

### [jneen] END HACK ###
