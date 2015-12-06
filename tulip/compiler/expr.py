import tulip.value as v
import tulip.code as c
from tulip.lexer import Token
from tulip.symbol import sym

from .util import split_at, get_tok, is_tok, find_token, nested_sym

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
                code_segment[-1] = c.Apply([code_segment[-1], c.Constant(v.bang)])
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
            if body.matches_tag(nil_sym, 0):
                context.error(open_tok, u'empty expression!')
                return

            return context.compile_expr(rpy_list(body))
        elif open_tok.tokid == Token.LBRACE:
            if body.matches_tag(nil_sym, 0):
                context.error(open_tok, u'empty block!')
            else:
                return context.compile_block(body)
        elif open_tok.tokid == Token.LBRACK:
            return context.compile_lambda(v.rpy_list(body))
        else:
            context.error(open_tok, u'TODO: unsupported nesting')


def compile_expr(skeletons, context):
    assert len(skeletons) > 0

    chain_lambda = is_tok(skeletons[0], Token.GT)

    if chain_lambda:
        skeletons.pop(0)

    raw_chain = split_at(skeletons, Token.GT, context, u'empty sequence')

    chain = [compile_segment(i == 0 and not chain_lambda, segment, context) for (i, segment) in enumerate(raw_chain)]

    if len(chain) == 1:
        body = c.make_apply(chain[0])
    else:
        # thread the chain together with let-assignments to the chain var
        elements = [None] * len(chain)
        for i in xrange(0, len(chain)-1):
            elements[i] = c.Let(chain_sym, c.make_apply(chain[i]))

        elements[-1] = c.make_apply(chain[-1])

        body = c.Block(elements)

    if chain_lambda:
        return c.Lambda(chain_sym, body)
    else:
        return body
