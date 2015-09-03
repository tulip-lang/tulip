# simple abstract machine rules, see vm docs for more formal description

def branch(node, context):
    return

def reduce(node, context):
    print("performing reduction on %s" % node.dump())
    return

def expand(node, context):
    print("performing name expansion on %s" % node.dump())
    return

def concur(node, context):
    assert False, "DNI"

def confer(node, context):
    assert False, "DNI"
