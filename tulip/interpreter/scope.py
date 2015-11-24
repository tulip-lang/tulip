class Scope(dict):
    def __init__(self, id, parent):
        self.id = id # Ref Scope
        self.parent = parent # Ref Scope

    def show(self):
        o = "----[scope table " + str(self.id) + "]-----------\n"
        o = o + "up: #" + str(self.parent) + "\n"
        for k,v in self.items():
            o = o + k + ": @" + str(v) + "\n"
        return o

    # Name -> Node -> ()
    def __setitem__(self, k, v):
        dict.__setitem__(self, k, v)

def lookup(name, scope, bindings):
    v = bindings[scope].get(name)
    if v:
        return v
    elif bindings[scope].parent:
        return lookup(bindings[bindings[scope].parent], name, bindings)
    else:
        return None
