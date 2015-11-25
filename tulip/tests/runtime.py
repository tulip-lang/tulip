from tulip.code import *

# should return <literal 2>
binding = Block([ Let(Name("x"), Constant(2)), Name("x")])

# should print "print-test"
builtin = Apply([Lambda(Name("x"), Builtin("print", 1, [Name("x")])), Constant("print-test")])

apply = Apply([Lambda(Name("x"), Name("x")), Constant(5)])

branch = Branch([(Tag("t"), Constant(5))])
