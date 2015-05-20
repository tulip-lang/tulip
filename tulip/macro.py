from tulip.lexer import ListLexer

class Macro(object):
    def compile(self, lexemes, context):
        assert False, u'abstract'

class ListMacro(Macro):
    def compile(self, lexemes, context):
        lexer = ListLexer(lexemes)
        exprs = expr.many().parse(lexer)
