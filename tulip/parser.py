from tulip.syntax import *
from tulip.parser_gen import tok, generate, seq, alt, Box, any
from tulip.lexer import Token
from tulip.symbol import sym

# register all the token parsers
for tokname in Token.TOKENS:
    globals()[tokname] = tok(getattr(Token, tokname))

class ASTBox(Box.Base):
    def __init__(self, syntax):
        assert isinstance(syntax, Syntax)
        self.syntax = syntax

    def get_ast(self):
        return self.syntax

    def dump(self):
        return u"<Box.AST (%s)>" % self.syntax.dump()

@generate('atom')
def atom(gen):
    return gen.parse(alt(var, number, paren, lam, tag, autovar))

@generate('apply')
def apply(gen):
    atoms = gen.parse(atom.many1()).get_list()
    if len(atoms) == 1:
        return atoms[0]
    else:
        return ASTBox(Apply([a.get_ast() for a in atoms]))

@generate('chain')
def chain(gen):
    component = apply.skip(NL.opt())
    first = gen.parse(component)
    rest = gen.parse(GT.then(component).many()).get_list()
    gen.parse(NL.opt())

    if len(rest) == 0:
        return first

    chain_size = len(rest) + 1
    out = [None] * chain_size
    out[0] = first.get_ast()
    for i in range(0, chain_size-1):
        out[i+1] = rest[i].get_ast()

    return ASTBox(Chain(out))

@generate
def definition(gen):
    gen.parse(PLUS)
    name = gen.parse(NAME).get_token().value
    args = [a.get_ast() for a in gen.parse(pattern.many()).get_list()]
    gen.parse(EQ)
    body = gen.parse(expr).get_ast()
    return ASTBox(Definition(sym(name), args, body))

@generate
def expr(gen):
    clauses = [c.get_ast() for c in gen.parse(definition.many()).get_list()]
    body = gen.parse(chain).get_ast()

    if len(clauses) == 0:
        return ASTBox(body)
    else:
        return ASTBox(Let(clauses, body))

@generate('pattern')
def pattern(gen):
    return gen.parse(alt(var_pattern, tag_pattern, named_pattern, paren_pattern))

paren_pattern = LPAREN.then(pattern).skip(RPAREN)
var_pattern = NAME.map(lambda s: ASTBox(VarPat(sym(s.get_token().value))))

@generate
def tag_pattern(gen):
    tag = gen.parse(TAGGED).get_token().value
    args = gen.parse(pattern.many()).get_list()
    pats = [p.get_ast() for p in args]
    return ASTBox(TagPat(sym(tag), pats))

named_pattern = CHECK.map(lambda s: ASTBox(NamedPat(sym(s.get_token().value))))


var = NAME.map(lambda b: ASTBox(Var(sym(b.get_token().value))))
number = INT.map(lambda b: ASTBox(Int(int(b.get_token().value or u''))))
paren = LPAREN.then(expr).skip(RPAREN)
autovar = DOLLAR.map(lambda _: ASTBox(Autovar()))
tag = TAGGED.map(lambda s: ASTBox(Tag(sym(s.get_token().value))))
lam_start = LBRACK

def _lam_map(args):
    pat, body = args.get_list()
    clause = Lam.Clause(pat.get_ast(), body.get_ast())
    return ASTBox(Lam([clause]))

# TODO: multiple clauses
@generate
def lam_clause(gen):
    pat = gen.parse(pattern).get_ast()
    gen.parse(NL.opt())
    gen.parse(RARROW)
    body = gen.parse(expr).get_ast()
    return ASTBox(Lam.Clause(pat, body))

@generate
def lam_end(gen):
    clauses = gen.parse(lam_clause.many()).get_list()
    clauses = [c.get_ast() for c in clauses]
    gen.parse(RBRACK)

    return ASTBox(Lam(clauses))

autolam_end = expr.skip(RBRACK).map(lambda c: ASTBox(Autolam(c.get_ast())))

lam = lam_start.then(alt(lam_end.backtracking(), autolam_end))

@generate
def balanced_braces(gen):
    print u'balanced braces start'
    count = 0
    lexemes = []
    while True:
        lexemes.append(gen.parse(alt(any, EOF)))
        tokid = lexemes[-1].get_token().tokid

        if tokid == Token.LBRACK:
            count += 1
            print u'incr count to: %d' % count
        elif tokid == Token.RBRACK:
            if count <= 0:
                gen.fail(u'balanced braces')
            count -= 1
            print u'decr count to: %d' % count
        elif count == 0 and tokid in [Token.NL, Token.EOF]:
            print u'balanced braces end'
            return Box.List(lexemes)

@generate
def unparsed_annotation(gen):
    name = gen.parse(ANNOT).get_token().value
    lexemes = [l.get_token() for l in gen.parse(balanced_braces).get_list()]
    return ASTBox(UnparsedAnnotation(name, lexemes))

@generate
def module_item(gen):
    return gen.parse(alt(definition, unparsed_annotation))

@generate
def module(gen):
    items = [i.get_ast() for i in gen.parse(module_item.many()).get_list()]
    return ASTBox(UnparsedModule(items))

def parse(reader):
    lexer = Lexer(reader)
    return expr.parse(lexer)
