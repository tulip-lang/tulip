from tulip.symbol import Symbol, SymbolTable
from tulip.syntax import *
from tulip.parser import parser
from tulip.parser_gen import StringReader

def entry_point(argv):
    print parser.parse(StringReader(u'1 2 > [ x => .h (.cons 2 [ .nil $ ]) [ $ ]]')).dump()

    return 0

def target(*args):
    return (entry_point, None)

if __name__ == '__main__':
    from sys import argv
    entry_point(argv)
