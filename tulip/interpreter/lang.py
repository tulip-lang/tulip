import tulip.code as ast
from tulip.interpreter.scope import Scope

# CAUTION BIG FILE

########################################
# module exports

def preprocess(program, bindings):
    """recursively descend a program tree, flatten it to a dict, link nodes with keys, and instantiate obvious scope tables"""
    flattened = Program(1)

    s = newScope()
    bindings[s] = Scope(s, None)
    scope = s

    flatten(program, flattened, bindings, scope)
    return (flattened, bindings)

# Node -> [Ref Node] -> [Ref Scope] -> Ref Scope -> Ref
def flatten(node, program, bindings, scope):
    id = newNode()

    if isinstance(node, ast.Block):
        s = newScope()
        bindings[s] = Scope(s, scope)
        scope = s
        program[id] = Block(scope, [flatten(x, program, bindings, scope) for x in node.nodes])
    elif isinstance(node, ast.Apply):
        program[id] = Apply(scope, [flatten(x, program, bindings, scope) for x in node.nodes])
    elif isinstance(node, ast.Let):
        program[id] = Let(scope, Name(scope, node.bind.symbol), flatten(node.body, program, bindings, scope))
    elif isinstance(node, ast.Lambda):
        s = newScope()
        bindings[s] = Scope(s, scope)
        scope = s
        program[id] = Lambda(scope, Name(scope, node.bind.symbol), flatten(node.body, program, bindings, scope))
    elif isinstance(node, ast.Name):
        program[id] = Name(scope, node.symbol)
    elif isinstance(node, ast.Constant):
        program[id] = Literal(node.value)
    elif isinstance(node, ast.Builtin):
        program[id] = Builtin(scope, node.name, node.arity, [flatten(x, program, bindings, scope) for x in node.args])

    return id

########################################
# flattened ast classes

# the table

class Program(dict):
    def __init__(self, id):
        self.id = id
        return

    def __setitem__(self, k, v):
        dict.__setitem__(self, k, v)

    def show(self):
        o =  "----[program table " + str(self.id) + "]---------\n"
        for k,v in self.items():
            o = o + ("%02d" % k) + ": " + v.show() + "\n"
        return o

# abstract node

class Node:
    def __init__(self):
        return

# expressions

class Block(Node):
    def __init__(self, scope, list):
        self.sequence = list # [Ref Node]
        self.scope = scope # Ref Scope

    def show(self):
        return "<block [%s]>" % '; '.join(["@" + str(x) for x in self.sequence]) + " #" + str(self.scope)

class Apply(Node):
    def __init__(self, scope, list):
        self.chain = list # [Ref Node]
        self.scope = scope # Ref Scope

    def show(self):
        return "<apply [%s]>" % ', '.join(["@" + str(x) for x in self.chain]) + " #" + str(self.scope)

class Let(Node):
    def __init__(self, scope, bind, body):
        self.bind = bind # Name
        self.body = body # Ref Node
        self.scope = scope # Ref Scope

    def show(self):
        return "<let " + self.bind.name + " @" + str(self.body) + "> #" + str(self.scope)

class Lambda(Node):
    def __init__(self, scope, bind, body):
        self.bind = bind # Name
        self.body = body # Ref Node
        self.scope = scope # Ref Scope

    def show(self):
        return "<lambda " + self.bind.show() + " @" + str(self.body) + "> #" + str(self.scope)

class Branch(Node):
    def __init__(self, scope, predicates, consequences):
        self.predicates = predicates     # [Ref Node]
        self.consequences = consequences # [Ref Node]
        self.scope = scope # Ref Scope

    def show(self):
        assert True, "not impl"

# values

class Literal(Node):
    def __init__(self, value):
        self.value = value
    def show(self):
        return "<literal %s>" % self.value

class Name(Node):
    def __init__(self, scope, name):
        self.name = name # String
        self.scope = scope # Ref Scope
    def show(self):
        return "<name %s>" % self.name + " #" + str(self.scope)

class Tag(Node):
    def __init__(self, tag):
        self.tag = tag # String
        self.contents = None # [Ref Node], must be constructed by tag application

class Builtin(Node):
    def __init__(self, scope, name, arity, args):
        self.name = name # String
        self.arity = arity # Int
        self.args = args # [Value]
        self.scope = scope # Ref Scope

    def show(self):
        return "<builtin " + self.name + "/" + str(self.arity) + " [" + " ".join([ "@" + str(x) for x in self.args ]) + "]> #" + str(self.scope)


########################################
# internal utilities

# todo make id generation part of a machine context state

id_node = -1
id_scope = -1

def newNode():
    global id_node
    id_node = id_node + 1
    return id_node

def newScope():
    global id_scope
    id_scope = id_scope + 1
    return id_scope
