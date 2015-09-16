from rpython.rlib.rarithmetic import r_uint
from tulip.lexer import Token
from tulip.symbol import sym
from tulip.value import rpy_list, cons_list, cons_sym, cons_each, malformed
import tulip.value as v
import tulip.code as c

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

token_sym = sym(u'token')
nested_sym = sym(u'nested')

class CompileContext(object):
    def __init__(self, compiler, module):
        self.compiler = compiler
        self.module = module

    def gensym(self, base):
        return self.compiler.gensym(base)

    def error(self, tok, message):
        self.compiler.error(tok, message)

def compile_base(expr):
    print u'compile: %s' % expr.dump()
    context = CompileContext(Compiler(), None)
    out = compile_expr(expr, context)
    context.compiler.check_errors()
    return out

def compile_term(e, context):
    tok = get_tok(e)
    if tok is not None:
        if tok.tokid == Token.NAME:
            return c.Name(sym(tok.value))
        elif tok.tokid == Token.INT:
            assert tok.value is not None
            return c.Constant(v.Int(int(tok.value)))
        elif tok.tokid == Token.STRING:
            assert tok.value is not None
            return c.Constant(v.String(tok.value))
        elif tok.tokid == Token.TAGGED:
            assert tok.value is not None
            return c.Tag(sym(tok.value))
        else:
            context.error(tok, u'TODO: unsupported token')
    elif e.matches_tag(nested_sym, 3):
        open_val = e.args[0]
        close_val = e.args[1]
        assert isinstance(open_val, v.Token)
        assert isinstance(close_val, v.Token)

        open_tok = open_val.value
        close_tok = close_val.value

        body = e.args[2]

        if open_tok.tokid == Token.LPAREN:
            return compile_expr(body, context)
        elif open_tok.tokid == Token.LBRACE:
            return compile_block(body, context)
        else:
            context.error(open_tok, u'TODO: unsupported nesting')

chain_sym = sym(u'#chain#')

def compile_expr(expr, context):
    chain = [[]]
    found_dash = False

    for e in cons_each(expr):
        tok = get_tok(e)
        if tok is not None and tok.tokid == Token.GT:
            if len(chain) >= 2 and not found_dash:
                chain[-1].append(c.Name(chain_sym))

            chain.append([])
            found_dash = False
        elif tok is not None and tok.tokid == Token.DASH:
            found_dash = True
            if len(chain) < 2:
                context.error(tok, u'dash can\'t appear in the first segment of a chain')

            chain[-1].append(c.Name(chain_sym))
        else:
            chain[-1].append(compile_term(e, context))

    if len(chain) >= 2 and not found_dash:
        chain[-1].append(c.Name(chain_sym))

    if len(chain) == 1:
        return make_apply(chain[0])

    elements = [None] * len(chain)
    for i in xrange(0, len(chain)-1):
        elements[i] = c.Let(chain_sym, make_apply(chain[i]))

    elements[-1] = make_apply(chain[-1])

    return c.Block(elements)

def make_apply(segments):
    if len(segments) == 1:
        return segments[0]
    else:
        return c.Apply(segments)

def compile_autolam(expr, context):
    pass

def compile_block(expr, context):
    # TODO: let runs

    parts = []
    for line in split_lines(expr):
        print line
        is_let = False
        split_index = 0
        last_let_run = []

        for i, el in enumerate(line):
            tok = get_tok(el)
            if tok is not None and tok.tokid == Token.EQ:
                is_let = True
                split_index = i
                break

        if is_let:
            last_let_run.append((line[0:split_index], line[split_index:-1]))
        else:
            if len(last_let_run) > 0:
                parts.concat(compile_let_run(last_let_run, context))
                last_let_run = []

            parts.append(compile_expr(cons_list(line), context))

    if len(last_let_run) > 0:
        parts.concat(compile_let_run(last_let_run, context))

    if len(parts) == 1:
        return parts[0]
    else:
        return c.Block(parts)

def compile_let_run(let_run, context):
    # TODO: recursion
    assert False, u'TODO: compile let runs'

def split_lines(seq):
    out = [[]]

    elements = rpy_list(seq)

    for i in xrange(0, len(elements)):
        tok = get_tok(elements[i])
        if tok is not None and tok.tokid == Token.NL:
            out.append([])
        else:
            out[-1].append(elements[i])

    return out

def get_tok(skel):
    if not skel.matches_tag(token_sym, 1):
        return None

    val = skel.args[0]
    assert isinstance(val, v.Token)

    return val.value

def seq_contains(seq, toktype):
    for e in cons_each(seq):
        tok = get_tok(e)
        if e.tokid == toktype:
            return True

    return False
