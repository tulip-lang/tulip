from rpython.rlib.rarithmetic import r_uint
from rpython.rlib.rstring import UnicodeBuilder
from rpython.rlib.streamio import open_file_as_stream, DecodingInputFilter

class Reader(object):
    def setup(self):
        pass

    def next(self):
        assert False, 'abstract!'

    def teardown(self):
        pass

    def input_name(self):
        assert False, 'abstract!'

class FileReader(Reader):
    def __init__(self, fname):
        self.fname = fname
        self.stream = None
        self.done = False

    def setup(self):
        self.stream = open_file_as_stream(self.fname)

    def input_name(self):
        return unicode(self.fname)

    def next(self):
        if self.done:
            return None

        data = ''
        for _ in range(0, 9):
            try:
                data += self.stream.read(1)
                return self.decode(data)
            except UnicodeDecodeError as e:
                pass

        data += self.stream.read(1)
        return self.decode(data)

    def decode(self, data):
        decoded = data.decode('utf-8')
        if len(decoded) == 0:
            self.done = True
            return None
        else:
            return decoded

    def teardown(self):
        self.stream.close()

class StringReader(Reader):
    def __init__(self, name, string):
        self.name = name
        self.string = string
        self.index = r_uint(0)

    def input_name(self):
        return self.name

    def next(self):
        if self.index >= len(self.string):
            return None

        out = self.string[self.index]
        self.index += 1
        return out
