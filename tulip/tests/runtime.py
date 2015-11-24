from tulip.code import *

# should return <literal 2>
binding = Block([ Let(Name("x"), Constant(2)), Apply([Name("x")])])

# should print "lambda-test"
lambdaTest = Apply([Lambda(Name("x"), Builtin("print", 1, [Name("x")])), Constant("lambda-test")])

apply = Apply([Lambda(Name("x"), Name("x")), Constant(5)])
