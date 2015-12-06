from .util import get_tok, seq_contains, split_at, nested_sym, get_initial_tok, get_body
from tulip.value import rpy_list
from tulip.lexer import Token
from tulip.symbol import sym
import tulip.value as v
import tulip.code as c

def test_match(arg, tag, arity):
    return c.Builtin(u'test-match', 3, [arg, c.Tag(sym(tag)), c.Constant(v.Int(arity))])

def destruct_match(e, i):
    return c.Builtin(u'destruct', 2, [e, c.Constant(v.Int(i))])

def compile_pattern_seq(pattern, arg, body, next, context):
    print 'pattern', pattern
    first_tok = get_tok(pattern[0])

    if first_tok.tokid == Token.TAGGED:
        destructure = body

        for (i, sub_pat) in enumerate(pattern[1:]):
            sub_arg = context.gensym(u'arg')
            destructure = c.let(
                sub_arg,
                destruct_match(c.Name(arg), i),
                compile_pattern_term(sub_pat, sub_arg, destructure, next, context)
            )

        return c.Branch([
            (test_match(arg, first_tok.value, len(pattern) - 1), destructure),
            (v.TRUE, next)
        ])
    elif seq_contains(pattern, Token.QUESTION):
        sub_pat, cond = split_at(pattern, Token.QUESTION, max=2)
    elif len(pattern) > 1:
        context.error(pattern[0], u'more than one expr is not allowed here')
    else:
        return compile_pattern_term(pattern[0]) # TODO


def compile_pattern_term(term, arg, body, next, context):
    tok = get_tok(term)
    if tok:
        if tok.tokid == Token.NAME:
            return c.let(sym(tok.value), arg, body)
        elif tok.tokid == Token.TAGGED:
            return c.Branch([
                (test_match(arg, tok.value, 0), body),
                (v.TRUE, next)
            ])

    sub_pat = get_body(term, Token.LPAREN)
    if sub_pat:
        return compile_pattern_seq(sub_pat, arg, body, next, context)

    context.error(get_initial_tok(term), u'unexpected token in pattern')

def compile_pattern(pattern, binders, body, next, context):
    assert len(pattern) > 0
    first_tok = get_tok(pattern[0])

    if first_tok.tokid == Token.TAGGED:
        # should be guaranteed by check_arities
        assert len(binders) == 1

        return compile_pattern_seq(pattern, binders[0], body, next, context)
    else:
        last_body = body

        for (i, sub_pat) in enumerate(pattern):
            last_body = compile_pattern_term(sub_pat, binders[i], last_body, next, context)

        return last_body

