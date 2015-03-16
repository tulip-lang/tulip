from tulip.syntax import *
from tulip.parser_gen import string, generate, char_range, one_of, none_of, seq, alt, Box

class ASTBox(Box.Base):
    def __init__(self, syntax):
        assert isinstance(syntax, Syntax)
        self.syntax = syntax

    def get_ast(self):
        return self.syntax

    def dump(self):
        return u"<Box AST %s>" % self.syntax.dump()

whitespace = one_of(u" \t").many()
nl = alt(string(u"\n"), string(u"\r\n"))
comment = seq(string(u'#'), none_of(u"\n").many(), nl)
lines = alt(nl, comment, string(u";")).many()

@generate('expr')
def expr(gen):
    return gen.parse(alt(e_var, e_number).many())

lexeme = lambda p: p.skip(whitespace)
lineme = lambda p: p.skip(lines)

number = lexeme(char_range(u'0', u'9').scan1()).desc(u'number')
ident = lexeme(char_range(u'a', u'z').scan1()).desc(u'ident')

e_var = ident.map(lambda s: ASTBox(Var(sym(s.get_string()))))
e_number = number.map(lambda s: ASTBox(Int(int(s.get_string()))))

parser = lines.then(expr)
