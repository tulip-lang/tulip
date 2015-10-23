import tulip.code

# CAUTION BIG FILE

########################################
# module exports

def preprocess(program):
    """recursively descend a program tree, flatten it to a dict, link nodes with keys, and instantiate obvious scope tables"""
    flattened = Program(1)
    program = flatten(program, flattened)
    return flattened

# Node -> State -> Ref
def flatten(node, program):
    id = newID()

    if isinstance(node, tulip.code.Block):
        program[id] = Block([flatten(x, program) for x in node.nodes])
    elif isinstance(node, tulip.code.Apply):
        program[id] = Apply([flatten(x, program) for x in node.nodes])
    elif isinstance(node, tulip.code.Let):
        program[id] = Let(Name(node.bind.symbol), flatten(node.body, program))
    elif isinstance(node, tulip.code.Lambda):
        program[id] = Let(Lambda(Name(node.bind.symbols[1]), flatten(node.body, program)))
    elif isinstance(node, tulip.code.Name):
        program[id] = Name(node.symbol)
    elif isinstance(node, tulip.code.Constant):
        program[id] = Literal(node.value)

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
    def __init__(self, list):
        self.sequence = list # [ref]
    def show(self):
        return "<block [%s]>" % '; '.join(["@" + str(x) for x in self.sequence])

class Apply(Node):
    def __init__(self, list):
        self.chain = list # [ref]
    def show(self):
        return "<apply [%s]>" % ', '.join(["@" + str(x) for x in self.chain])

class Let(Node):
    def __init__(self, bind, body):
        self.bind = bind # name
        self.body = body # ref
    def show(self):
        return "<let " + self.bind.name + " @" + str(self.body) + ">"

class Lambda(Node):
    def __init__(self, bind, body):
        self.bind = bind # Name
        self.body = body # ref
    def show(self):
        return "<lambda " + self.bind.show() + " " + self.body.show() + ">"

class Branch(Node):
    def __init__(self, predicates, consequences):
        self.predicates = predicates     # [ref]
        self.consequences = consequences # [ref]
    def show(self):
        assert True, "not impl"

# values

class Literal(Node):
    def __init__(self, value):
        self.value = value
    def show(self):
        return "<literal %s>" % self.value

class Name(Node):
    def __init__(self, name):
        self.name = name
    def show(self):
        return "<name %s>" % self.name

class Tag(Node):
    def __init__(self, tag):
        self.tag = tag

class Builtin(Node):
    def __init__(self, name, arity, args):
        self.name = name # String
        self.arity = arity # Int
        self.args = args # [Value]


########################################
# internal utilities

id = 0

# check out this sweet global state
# ideally this would be replaced with some more sensible method of managing my fake heap
# but that's probably not necessary
def newID():
    global id
    id = id + 1
    return id

