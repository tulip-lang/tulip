class Scope(dict):
    def __init__(self, id, parent):
        self.id = id
        self.parent = parent

    def show(self):
        o = "----[scope table " + str(self.id) + "]-----------\n"
        o = o + "up: #" + str(self.parent) + "\n"
        for k,v in self.items():
            if isinstance(v, int):
                o = o + k + ": @" + str(v) + "\n"
            else:
                o = o + k + ": " + v.show() + "\n"
        return o

    def __setitem__(self, k, v):
        dict.__setitem__(self, k, v)

def lookup(name, scope, bindings):
    try:
        return bindings[scope][name]
    except KeyError:
        print 'name', name
        print 'scope', scope
        print 'bindings', bindings
        print
        if bindings[scope].parent:
            return lookup(bindings[bindings[scope].parent], name, bindings)
        else:
            return None
