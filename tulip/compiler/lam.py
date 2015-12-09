from .util import split_at, get_tok, seq_contains, list_contains, is_tok, underscore_sym import tulip.value as v
import tulip.code as c
from tulip.lexer import Token

class Dispatch(object):
    pass

class Body(Dispatch):
    def __init__(self, body):
        self.body = body

    def compile(self, context):
        print 'self.body', self.body
        return context.compile_expr(self.body)

class Guard(Dispatch):
    def __init__(self, clauses):
        self.clauses = clauses

    def compile(self, context):
        return c.Branch([
            (context.compile_expr(cond), context.compile_expr(body)) \
              for (cond, body) in self.clauses
        ] + [(v.TRUE, match_error)]

def detect_arity(pattern):
    if is_tok(pattern[0], Token.TAGGED):
        return 1
    else:
        return len(pattern)

def check_arities(clauses, context):
    arities = set([detect_arity(c[0]) for c in clauses])
    if len(arities) != 1:
        context.error(clauses[0][0][0], u'unmatched pattern arities')
        return -1
    else:
        return list(arities)[0]


def split_clause(clause_toks):
    return split_at(clause_toks, Token.RARROW, max=2, err=u'empty clause')

def split_section(clause_toks):
    if list_contains(clause_toks, Token.QUESTION):
        parts = split_at(clause_toks, Token.QUESTION)
        pat = parts[0]
        clauses = parts[1:]
        return (pat, Guard(map(split_clause, clauses)))
    else:
        pat, clause = split_clause(clause_toks)
        return (pat, Body(clause))

match_error = c.Builtin(u'match-error', 0, [])

def compile_lambda(body, context):
    clauses = map(split_section, split_at(body, Token.NL))
    arity = check_arities(clauses, context)
    if arity <= 0: return

    clauses = map(split_section, split_at(body, Token.NL))
    arity = check_arities(clauses, context)
    if arity <= 0: return

    binders = [context.gensym(u'arg') for _ in xrange(0, arity)]

    defs = []
    last_out_sym = context.gensym(u'next')

    defs.append(c.Let(last_out_sym, c.Lambda(underscore_sym, match_error)))

    clauses.reverse()

    for clause in clauses:
        pattern = clause[0]
        dispatch = clause[1]
        last_out = c.Apply([c.Name(last_out_sym), c.Constant(v.bang)])
        compiled = context.compile_pattern(pattern, binders, dispatch.compile(context), last_out)
        last_out_sym = context.gensym(u'clause')
        defs.append(c.Let(last_out_sym, c.Lambda(underscore_sym, compiled)))

    return c.nested_lambda(binders, c.Block(defs + [c.Apply([c.Name(last_out_sym), c.Constant(v.bang)])]))


def compile_autolam(expr, context):
    assert False, u'TODO'

