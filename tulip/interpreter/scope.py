class Scope(dict):
    def __init__(self, id, parent):
        self.id = id
        self.parent = parent

    def show(self):
        return "SCOPE TABLE"

    def __setitem__(self, k, v):
        dict.__setitem__(self, k, v)

def lookup(scope, name):
    v = scope.get(name)
    if v:
        return v
    elif scope.parent:
        return lookup(scope.parent, name)
    else:
        return None
