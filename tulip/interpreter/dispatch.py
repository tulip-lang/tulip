# main interpreter loop

from tulip.code import *
from tulip.interpreter.rules import *

def dispatch(node, context):
    """performs a reduction on node, returns True if more evaluation can be done, False if evaluation has reached a return value"""

    # these objects can be reduced
    if isinstance(node, Apply):
        # expand each term individually, then reduce the chain as a whole
        assert isinstance(node.nodes, list), "malformed apply chain"
        for term in node.nodes:
            term = expand(term, context)
            continue
        reduce(node, context)
        return True
    elif isinstance(node, Block):
        # evaluate each apply or let sequentially?
        for line in node.nodes:
            expand(line, context)
            reduce(line, context)
            # or, dispatch(line, context)?
            # not sure where to put scope management
            continue
        return True
    elif isinstance(node, Let):
        # mutate local bindings
        return True
    elif isinstance(node, Branch):
        # perform branch
        branch(node)
        return True
    # elif isinstance(node, Builtin):
    #     return True

    # these objects are reduced as far as possible, and cannot be evaluated any further
    elif isinstance(node, Name):
        return False
    elif isinstance(node, Tag):
        return False
    elif isinstance(node, Constant):
        return False
    elif isinstance(node, Lambda):
        return False

    # catch
    else:
        assert True, "cannot dispatch on node"
