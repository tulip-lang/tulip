from os import environ

class _Debug(object):
    def __init__(self):
        try:
            self.debug = unicode(environ['TULIP_DEBUG']).split(u',')
        except KeyError:
            self.debug = []

    def check(self, s):
        return s in self.debug

debug = _Debug()
