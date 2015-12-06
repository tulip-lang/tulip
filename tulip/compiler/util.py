from tulip.symbol import sym
from tulip.lexer import Token, DummyToken
import tulip.value as v

token_sym = sym(u'token')
nested_sym = sym(u'nested')
nil_sym = sym(u'nil')
underscore_sym = sym(u'_')

def split_lines(seq):
    return split_at(rpy_list(seq), Token.NL)

def split_at(skeletons, toktype, context=None, err=None, max=0):
    out = [[]]
    last_tok = None
    assert len(skeletons) > 0

    for i in xrange(0, len(skeletons)):
        tok = get_tok(skeletons[i])

        if tok is None or tok.tokid != toktype or (max > 0 and len(out) >= max):
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

def get_body(skel, open_type=None):
    if not skel.matches_tag(nested_sym, 3):
        print 'not nested'
        return None

    open = skel.args[0]
    assert isinstance(open, v.Token)

    if open_type is not None and open.value.tokid is not open_type:
        print 'not a token type', Token.TOKENS[open_type]
        print 'got', open.value.get_name()
        return None

    return v.rpy_list(skel.args[2])

def get_initial_tok(skel):
    tok = skel.args[0]
    assert isinstance(tok, v.Token)
    return tok.value

def seq_contains(seq, toktype):
    for e in v.cons_each(seq):
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

