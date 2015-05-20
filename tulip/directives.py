class ImproperDirective(StandardError):
    pass

class Directive(object):
    ELEMENTS = []

    def __init__(self, name, args):
        self.name = name
        self.args = args

