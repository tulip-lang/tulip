from rpython.rlib.rarithmetic import r_uint
from tulip.lexer import Token, DummyToken
from tulip.symbol import sym
from tulip.value import rpy_list, cons_list, cons_sym, cons_each, malformed
import tulip.value as v
import tulip.code as c

from .lam import compile_lambda
from .expr import compile_expr
from .pattern import compile_pattern
from .block import compile_block
from .prelude import with_prelude

class CompileError(StandardError):
    def __init__(self, errors):
        self.errors = errors

    def dump(self):
        messages = [_make_message(t, m) for (t, m) in self.errors]
        return u'\n'.join(messages)

def _make_message(token, message):
    return u'compile error at %s: %s' % (token.dump(), message)

class Compiler(object):
    def __init__(self):
        self.macros = {}
        self.modules = {}
        self.errors = []
        self.gensym_counter = r_uint(0)

    def gensym(self, base):
        self.gensym_counter += 1
        return sym(u'#%s-%s#' % (base, unicode(str(self.gensym_counter))))

    def compile_module(self, skeleton):
        mod = ModuleCompiler(self)
        mod.compile(skeleton)
        self.modules[mod.get_name()] = mod.get_module()

    def error(self, tok, message):
        self.errors.append((tok, message))

    def check_errors(self):
        if len(self.errors) > 0:
            raise CompileError(self.errors)

class CompileContext(object):
    def __init__(self, compiler, module):
        self.compiler = compiler
        self.module = module

    def gensym(self, base):
        return self.compiler.gensym(base)

    def error(self, tok, message):
        self.compiler.error(tok, message)

    def compile_expr(self, e):
        return compile_expr(e, self)

    def compile_lambda(self, e):
        return compile_lambda(e, self)

    def compile_pattern(self, pattern, binders, body, next):
        return compile_pattern(pattern, binders, body, next, self)

    def compile_block(self, b):
        return compile_block(b, self)

nil_sym = sym(u'nil')
def compile_base(expr):
    if expr.matches_tag(nil_sym, 0):
        return None

    print u'compile: %s' % expr.dump()
    context = CompileContext(Compiler(), None)
    out = compile_expr(rpy_list(expr), context)
    context.compiler.check_errors()
    return out

chain_sym = sym(u'#chain#')
autovar_sym = sym(u'$')
underscore_sym = sym(u'_')
t_sym = sym(u't')
f_sym = sym(u'f')

