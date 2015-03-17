from tulip.symbol import Symbol, SymbolTable
from tulip.syntax import *
from tulip.parser import parser
from tulip.parser_gen import StringReader, ParseError
from sys import stdin
from tulip.libedit import readline
from os import environ

def entry_point(argv):
    try:
        DEBUG = unicode(environ['TULIP_DEBUG']).split(u',')
    except KeyError:
        DEBUG = []

    debug_parser = (u'parser' in DEBUG)

    while True:
        try:
            line = readline(': ')
            print '=', parser.parse(StringReader(line), debug=debug_parser).dump()
        except EOFError:
            break
        except ParseError as e:
            print e.dump()


    return 0

def target(*args):
    return (entry_point, None)

if __name__ == '__main__':
    from sys import argv
    entry_point(argv)
