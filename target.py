from tulip.symbol import Symbol, SymbolTable
from tulip.syntax import *
# from tulip.parser import expr_parser, module_parser
# from tulip.parser_gen import StringReader, FileReader, ParseError
from sys import stdin
from tulip.libedit import readline
from tulip.debug import debug
from rpython.rlib.objectmodel import we_are_translated
from tulip.lexer import Lexer, Token, LexError
from tulip.reader import StringReader

def entry_point(argv):
    lexer = Lexer(StringReader(unicode(argv[1])))
    lexer.setup()
    try:
        while True:
            (token, value) = lexer.next()
            if value is None:
                print Token.TOKENS[token]
            else:
                print u'%s(%s)' % (Token.TOKENS[token], value)

            if token is Token.EOF:
                break

        return 0
    except LexError as e:
        print u'error: %d:%d' % (e.lexer.line, e.lexer.col)
        print u'head: <%s>' % e.lexer.head
        return 1
    # if len(argv) >= 2:
    #     return run_file(argv[1])
    # elif stdin.isatty:
    #     return run_repl()
    # else:
    #     assert False, u'TODO: actually implement an arg parser'

def run_repl():
    print_logo()

    while True:
        try:
            line = readline(': ')
            print '=', expr_parser.parse(StringReader(line)).dump()
        except EOFError:
            break
        except ParseError as e:
            print e.dump()

    return 0

def print_logo():
    print
    print "    ) ("
    print "   (/ _) tulip"
    print "     |/"
    print

def run_file(fname):
    reader = FileReader(fname)
    try:
        print module_parser.parse(reader).dump()
        return 0
    except ParseError as e:
        print e.dump()
        return 1

def target(*args):
    return (entry_point, None)

if __name__ == '__main__':
    from sys import argv
    entry_point(argv)
