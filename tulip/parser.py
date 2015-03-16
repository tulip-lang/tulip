from tulip.syntax import *
from tulip.parser_gen import string, generate, char_range, oneOf, noneOf, seq, alt, Box

class ASTBox(Box):
    def __init__(self, syntax):
        assert isinstance(syntax, Syntax)
        self.syntax = syntax

    def get_ast(self):
        return self.syntax

    def dump(self):
        return "<Box AST %s>" % self.syntax.dump()

whitespace = oneOf(u" \t").many()
nl = alt(string("\n"), string("\r\n"))
comment = seq(string(u'#'), noneOf("\n").many(), nl)
lines = alt(nl, comment, string(";")).many()

lexeme = lambda p: p.skip(whitespace)
lineme = lambda p: p.skip(lines)

number = lexeme(char_range(u'0', u'9').scan1()).desc('number')
ident = lexeme(char_range(u'a', u'z').scan1()).desc('ident')
expr = alt(number, ident).many()

parser = lines.then(expr)
