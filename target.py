from tulip.symbol import Symbol, SymbolTable
from tulip.syntax import *

def entry_point(argv):
    table = SymbolTable()

    for arg in argv:
        symbol = table.sym(arg)
        print "arg: %s / %d" % (symbol.name, symbol.id)

    print Lazy(Chain([ \
        Apply([Tag(table.sym("add")), Int(1), Int(2)]), \
        Apply([Tag(table.sym("mul")), Var(table.sym("x"))]), \
    ])).dump()

    return 0

def target(*args):
    return (entry_point, None)

if __name__ == '__main__':
    from sys import argv
    entry_point(argv)
