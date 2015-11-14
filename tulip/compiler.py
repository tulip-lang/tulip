from rpython.rlib.rarithmetic import r_uint
from tulip.lexer import Token, DummyToken
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
nil_sym = sym(u'nil')

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
        elif tok.tokid == Token.FLAG:
            assert tok.value is not None
            return c.Flag(sym(tok.value))
        elif tok.tokid == Token.BANG:
            context.error(tok, u'improper ! in term position')
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
            if body.matches_tag(nil_sym, 0):
                context.error(open_tok, u'empty block!')
            else:
                return compile_block(body, context)
        elif open_tok.tokid == Token.LBRACK:
            if seq_contains(body, Token.RARROW):
                return compile_lam(body, context)
            return compile_autolam(body, context)
        else:
            context.error(open_tok, u'TODO: unsupported nesting')

chain_sym = sym(u'#chain#')
autovar_sym = sym(u'$')
t_sym = sym(u't')
f_sym = sym(u'f')

def test_match(arg, tag, arity):
    return c.Builtin(u'test-match', 3, [arg, c.Tag(sym(tag)), c.Constant(v.Int(arity))])

def compile_pattern(pattern, arg, body, next, context):
    return compile_pattern_term(pattern[0]) # TODO

def compile_pattern_term(term, arg, body, next, context):
    tok = get_token(term)

    if tok:
        if tok.tokid == Token.NAME:
            return c.Block([c.Let(sym(tok.value), arg), body])
        elif tok.tokid == Token.TAGGED:
            return c.Branch([
                (test_match(arg, tok.value, 0), body),
                (c.Tag(t_sym), next)
            ])
    elif pattern.matches_tag(nested_sym, 3):
        open = pattern.args[0]
        close = pattern.args[1]
        sub_pat = pattern.args[2]

        if open.tok_id == Token.LPAREN:
            return compile_pattern(pattern, arg, rpy_list(sub_pat), body, next, context)
        else:
            context.error(open, u'unexpected token in pattern')




def compile_lam(body, context):
    assert False, 'TODO'
    # clauses = [split_at(line, Token.RARROW, max=2) for line in split_lines(body)]

    # last = c.Name(sym('todo-crash!'))
    # i = len(clauses)
    # while i > 0:
    #     i -= 1
    #     clause = clauses[i]
    #     last = clause

    # for i in xrange(len(body) 

def compile_segment(is_first, segment, context):
    print 'compile_segment', [t.dump() for t in segment]
    assert len(segment) > 0, u'TODO: gracefully handle >>'

    add_dash(is_first, segment, context)

    code_segment = []
    i = 0
    while i < len(segment):
        e = segment[i]

        tok = get_tok(e)

        if tok is not None and tok.tokid == Token.BANG:
            if len(code_segment) == 0:
                context.error(tok, u'`!` must appear only in argument position')
            elif isinstance(code_segment[0], c.Tag):
                context.error(tok, u'`!` can\'t be passed to a tag constructor')
            else:
                code_segment.append(c.Constant(v.bang))
        elif tok is not None and tok.tokid == Token.FLAGKEY:
            key = tok
            pairs = []

            while True:
                i += 1
                if i >= len(segment):
                    context.error(key, u'flagkey needs a value!')
                    break

                if is_tok(segment[i], Token.DASH):
                    compiled = c.Name(chain_sym)
                else:
                    compiled = compile_term(segment[i], context)

                pairs.append((sym(key.value), compiled))

                if i + 1 >= len(segment):
                    break

                next = get_tok(segment[i+1])
                if next is not None and next.tokid == Token.FLAGKEY:
                    key = next
                    i += 1
                else:
                    break

            code_segment.append(c.FlagMap(pairs))
        elif tok is not None and tok.tokid == Token.DASH:
            code_segment.append(c.Name(chain_sym))
        else:
            code_segment.append(compile_term(e, context))

        i += 1

    return code_segment

def add_dash(is_first, segment, context):
    dash = find_token(segment, Token.DASH)

    if dash is not None and is_first:
        context.error(dash, u'dash can\'t appear in the first segment of a chain')
    elif dash is None and not is_first:
        segment.append(v.tag(u'token', [v.Token(DummyToken(Token.DASH, None))]))

def dummy_token(type, value=None):
    return v.tag(u'token', [v.Token(DummyToken(type, value))])

def compile_expr(expr, context):
    skeletons = rpy_list(expr)

    chain_lambda = len(skeletons) > 0 and is_tok(skeletons[0], Token.GT)

    if chain_lambda:
        skeletons.pop(0)

    raw_chain = split_at(skeletons, Token.GT, context, u'empty sequence')

    chain = [compile_segment(i == 0 and not chain_lambda, segment, context) for (i, segment) in enumerate(raw_chain)]

    if len(chain) == 1:
        body = make_apply(chain[0])
    else:
        # thread the chain together with let-assignments to the chain var
        elements = [None] * len(chain)
        for i in xrange(0, len(chain)-1):
            elements[i] = c.Let(chain_sym, make_apply(chain[i]))

        elements[-1] = make_apply(chain[-1])

        body = c.Block(elements)

    if chain_lambda:
        return c.Lambda([chain_sym], body)
    else:
        return body

def make_apply(segments):
    if len(segments) == 1:
        return segments[0]
    else:
        return c.Apply(segments)

def compile_autolam(expr, context):
    assert False, u'TODO'


def compile_block(expr, context):
    parts = []
    last_let_run = []
    lines = split_lines(expr)

    for (i, line) in enumerate(lines):
        assert len(line) > 0, u'empty line!'

        (equal_sign, before, after) = try_split(line, Token.EQ)
        is_let = equal_sign is not None

        if is_let and i == len(lines) - 1:
            context.error(equal_sign, u'block can\'t end with assignment!')
            return

        if is_let:
            last_let_run.append(before, after)
        else:
            if len(last_let_run) > 0:
                parts.extend(compile_let_run(last_let_run, context))
                last_let_run = []

            parts.append(compile_expr(cons_list(line), context))

    if len(last_let_run) > 0:
        parts.extend(compile_let_run(last_let_run, context))

    if len(parts) == 1:
        return parts[0]
    else:
        return c.Block(parts)

def compile_let_run(let_run, context):
    # TODO: recursion
    assert False, u'TODO: compile let runs'

def split_lines(seq):
    return split_at(rpy_list(seq), Token.NL)

def split_at(skeletons, toktype, context=None, err=None, max=0):
    out = [[]]
    last_tok = None
    assert len(skeletons) > 0

    for i in xrange(0, len(skeletons)):
        tok = get_tok(skeletons[i])

        if tok is None or tok.tokid != toktype or (max > 0 and len(out) >= max):
            print 'appending', tok.dump()
            out[-1].append(skeletons[i])
        else:
            if err is not None and len(out[-1]) == 0:
                context.error(tok, err)
                out.pop()

            out.append([])

        last_tok = tok

    if err is not None and len(out[-1]) == 0:
        context.error(last_tok, err)
        out.pop()

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
        if tok is not None and tok.tokid == toktype:
            return True

    return False

def list_contains(list, toktype):
    for e in list:
        tok = get_tok(e)
        if tok is not None and tok.tokid == toktype:
            return True

    return False

def find_token(list, toktype):
    (_, token) = find_token_indexed(list, toktype)
    return token

def find_token_indexed(list, toktype):
    for (i, e) in enumerate(list):
        tok = get_tok(e)
        if tok is not None and tok.tokid == toktype:
            return (i, tok)

    return (-1, None)

def try_split(list, toktype):
    (index, token) = find_token_indexed(list, toktype)

    if token is not None:
        return (token, list[0:index], list[index:len(list)])
    else:
        return (None, None, None)

def is_tok(skel, toktype):
    tok = get_tok(skel)
    return tok is not None and tok.tokid == toktype
