import tulip.value as v
from tulip.symbol import sym
from tulip.lexer import Token

def tag(name, values):
    return v.Tagged(sym(name), values)

def parse_skeleton(lexer):
    lexer.setup()
    parsed = _parse_sequence(lexer, None, 0)
    lexer.teardown()
    return parsed

class ParseError(StandardError):
    def __init__(self, token, message):
        self.token = token
        self.message = message

    def dump(self):
        return u'unexpected token %s: %s' % (self.token.dump(), self.message)

def error(tok, message):
    raise ParseError(tok, message)

def _parse_sequence(lexer, open_tok, expected_close_id):
    elements = []

    while True:
        tok = lexer.next()
        if tok.tokid == Token.EOF:
            if open_tok is None:
                return build_cons_list(elements)
            else:
                error(tok, u'invalid nesting, expected %s' % Token.TOKENS[expected_close_id])
        elif open_tok is not None and tok.tokid == expected_close_id:
            return tag(u'nested', [v.Token(open_tok), v.Token(tok), build_cons_list(elements)])
        elif tok.tokid in [ Token.RPAREN, Token.RBRACK ]:
            error(tok, u'invalid nesting from %s' % open_tok.dump())
        elif tok.tokid == Token.LPAREN:
            elements.append(_parse_sequence(lexer, tok, Token.RPAREN))
        elif tok.tokid == Token.LBRACK or tok.tokid == Token.MACRO:
            elements.append(_parse_sequence(lexer, tok, Token.RBRACK))
        else:
            elements.append(tag(u'token', [v.Token(tok)]))

def build_cons_list(elements):
    i = len(elements)
    out = tag(u'nil', [])
    while i > 0:
        i -= 1
        out = tag(u'cons', [elements[i], out])

    return out

def parse_from_string(s):
    from tulip.reader import StringReader
    from tulip.lexer import ReaderLexer
    reader = StringReader(u'(parse_from_string)', s)
    lexer = ReaderLexer(reader)
    return parse_skeleton(lexer)
