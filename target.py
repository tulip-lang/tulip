from tulip.symbol import Symbol, SymbolTable
def entry_point(argv):
    table = SymbolTable()

    for arg in argv:
        symbol = table.sym(arg)
        print "arg: %s / %d" % (symbol.name, symbol.id)

    return 0

def target(*args):
    return (entry_point, None)
