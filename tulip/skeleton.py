import tulip.value as v
from tulip.symbol import sym
from tulip.lexer import Token

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
                return v.cons_list(elements)
            else:
                error(tok, u'invalid nesting, expected %s' % Token.TOKENS[expected_close_id])
        elif open_tok is not None and tok.tokid == expected_close_id:
            return v.tag(u'nested', [v.Token(open_tok), v.Token(tok), v.cons_list(elements)])
        elif tok.tokid in [ Token.RPAREN, Token.RBRACK, Token.RBRACE ]:
            if open_tok is not None:
                error(tok, u'invalid nesting from %s' % open_tok.dump())
            else:
                error(tok, u'invalid nesting from the beginning')
        elif tok.tokid == Token.LPAREN:
            elements.append(_parse_sequence(lexer, tok, Token.RPAREN))
        elif tok.tokid == Token.LBRACK or tok.tokid == Token.MACRO:
            elements.append(_parse_sequence(lexer, tok, Token.RBRACK))
        elif tok.tokid == Token.LBRACE:
            elements.append(_parse_sequence(lexer, tok, Token.RBRACE))
        elif tok.tokid == Token.NL and expected_close_id == Token.RPAREN:
            pass
        else:
            elements.append(v.tag(u'token', [v.Token(tok)]))

def parse_from_string(s):
    from tulip.reader import StringReader
    from tulip.lexer import ReaderLexer
    reader = StringReader(u'(parse_from_string)', s)
    lexer = ReaderLexer(reader)
    return parse_skeleton(lexer)
