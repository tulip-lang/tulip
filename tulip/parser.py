from tulip.syntax import *
from tulip.parser_gen import string, generate, char_range, one_of, none_of, seq, alt, Box

class ASTBox(Box.Base):
    def __init__(self, syntax):
        assert isinstance(syntax, Syntax)
        self.syntax = syntax

    def get_ast(self):
        return self.syntax

    def dump(self):
        return u"<Box.AST (%s)>" % self.syntax.dump()

whitespace = one_of(u" \t").many()
nl = alt(string(u"\n"), string(u"\r\n"))
comment = seq(string(u'#'), none_of(u"\n").many(), nl)
lines = seq(alt(nl, comment, string(u";")).many(), whitespace)

lexeme = lambda p: p.skip(whitespace)
lineme = lambda p: p.skip(lines)

NUMBER = lexeme(char_range(u'0', u'9').scan1()).desc(u'number')
IDENT =  lexeme(char_range(u'a', u'z').scan1()).desc(u'ident')
RANGLE = lineme(string('>'))
LPAREN = lineme(string('('))
RPAREN = lexeme(string(')'))
LBRACE = lineme(string('['))
RBRACE = lineme(string(']'))
DOLLAR = lexeme(string('$'))
TAGGED = lexeme(string('.').then(IDENT))

@generate('atom')
def atom(gen):
    return gen.parse(alt(var, number, paren, tag, autovar))

@generate('apply')
def apply(gen):
    atoms = gen.parse(atom.many1()).get_list()
    return ASTBox(Apply([a.get_ast() for a in atoms]))

@generate('chain')
def chain(gen):
    first = gen.parse(apply)
    rest = gen.parse(RANGLE.then(apply).many()).get_list()
    chain_size = len(rest) + 1
    out = [None] * chain_size
    out[0] = first.get_ast()
    for i in range(0, chain_size-1):
        out[i+1] = rest[i].get_ast()

    return ASTBox(Chain(out))


var = IDENT.map(lambda s: ASTBox(Var(sym(s.get_string()))))
number = NUMBER.map(lambda s: ASTBox(Int(int(s.get_string()))))
paren = LPAREN.then(chain).skip(RPAREN)
autovar = DOLLAR.map(lambda _: ASTBox(Autovar()))
tag = TAGGED.map(lambda s: ASTBox(Tag(sym(s.get_string()))))

parser = lines.then(chain)
