from rpython.rlib.rarithmetic import r_uint
from rpython.rlib.rstring import UnicodeBuilder

class ParseState(object):
    def __init__(self, reader):
        self.reader = reader
        self.index = 0
        self.error_index = -1
        self.error_messages = [u'hello']
        self.bt_marks = []
        self.head = None
        self.ahead = []
        self.behind = []
        self.lineno = 0
        self.colno = 0

    def dump(self):
        # this is dumb
        ahead_copy = [x for x in self.ahead]
        ahead_copy.reverse()
        return u"<st %d [%s] %s [%s]>" % (
                self.index,
                u''.join(self.behind),
                self.head,
                u''.join(ahead_copy)
        )

    def mark(self):
        self.bt_marks.append(self.index)

    def clear_mark(self):
        mark_count = len(self.bt_marks)
        assert mark_count > 0, "imbalanced mark release"
        if mark_count == 1:
            self.behind = []
        return self.bt_marks.pop()

    def backtrack(self):
        index = self.bt_marks[-1]
        self.rewind_to(index)

    def error(self, message):
        if self.error_index < self.index:
            self.error_index = self.index
            self.error_messages = [message]
        elif self.index == self.error_index:
            self.error_messages.append(message)

        # otherwise pass, we're backtracked

    def advance_pos(self):
        self.index += 1
        if self.head == u"\n":
            self.lineno += 1
            self.colno = 0
        else:
            self.colno += 1

    def rewind_pos(self):
        self.index -= 1
        if self.head == u"\n":
            self.lineno -= 1
            self.colno = -1 # counts backwards? i guess?
        else:
            self.colno -= 1

    def advance1(self):
        self.advance_pos()
        if len(self.bt_marks) > 0: self.behind.append(self.head)
        if len(self.ahead) == 0:
            self.head = self.reader.next()
        else:
            self.head = self.ahead.pop()
        print u"adv: %s" % self.dump()

    def rewind1(self):
        assert len(self.behind) > 0, "can't rewind anymore!"
        self.ahead.append(self.head)
        self.head = self.behind.pop()
        self.rewind_pos()
        print u"rew: %s" % self.dump()

    def advance(self, steps=1):
        assert steps > 0, "can't advance a negative number of times"
        for _ in range(steps):
            self.advance1(steps)

    def rewind(self, steps=1):
        assert steps > 0, "can't rewind a negative number of times"
        for _ in range(steps):
            self.rewind1(steps)

    def rewind_to(self, idx):
        steps = self.index - idx
        self.rewind(steps)

class Box(object):
    class Base(object):
        def dump(self):
            assert False, "abstract"

        def get_list(self):
            assert False, "not a list!"

        def get_string(self):
            assert False, "not a string!"

        def get_ast(self):
            assert False, "not an AST!"

    class String(Base):
        def __init__(self, s):
            self.value = u'thing'
            self.value = s

        def dump(self):
            return u"<Box.String \"%s\">" % self.value

        def get_string(self):
            return self.value

    class List(Base):
        def __init__(self, l):
            self.values = l

        def get_list(self):
            return self.values

        def dump(self):
            els = u" ".join([box.dump() for box in self.values])
            return u"<Box.List [%s]>" % els

class Result(object):
    pass

class Success(Result):
    def __init__(self, box):
        self.box = box

class Failure(Result):
    pass

class ParseError(Exception):
    def __init__(self, lineno, colno, messages):
        self.lineno = lineno
        self.colno = colno
        self.messages = messages

    def __str__(self):
        return u"parse error at %d:%d - expected one of %s" % \
          (self.lineno, self.colno, ", ".join(self.messages))

class Parser(object):
    def perform(self, st):
        assert False, "abstract"

    def parse(self, reader):
        reader.setup()
        try:
            state = ParseState(reader)
            state.advance1()
            result = self.perform(state)
            if isinstance(result, Failure):
                raise ParseError(state.lineno, state.colno, state.error_messages)
            elif isinstance(result, Success):
                if state.head is None:
                    return result.box
                else:
                    raise ParseError(state.lineno, state.colno, [u'EOF'])

            assert False, "impossible"
        finally:
            reader.teardown()

    def desc(self, desc):
        return Desc(self, desc)

    def many(self):
        return Many(self)

    def many1(self):
        return seq(self, Many(self)).map(_many1_map)

    def scan(self):
        return Scan(self)

    def scan1(self):
        return seq(self, Scan(self)).map(_scan1_map)

    def map(self, fn):
        return Map(self, fn)

    def skip(self, other):
        return seq(self, other).map(_skip_map)

    def then(self, other):
        return seq(self, other).map(_then_map)

def _skip_map(box):
    return box.get_list()[0]

def _then_map(box):
    return box.get_list()[1]

def _many1_map(box):
    first, rest = box.get_list()
    aggregate = rest.get_list()
    aggregate.insert(0, first)
    return Box.List(aggregate)

def _scan1_map(box):
    first, rest = box.get_list()
    return Box.String(first.get_string() + rest.get_string())

class Generated(Parser):
    class ParseGen(object):
        class StopParse(Exception):
            def __init__(self, result):
                self.result = result

        def __init__(self, st):
            self.st = st

        def parse(self, parser):
            result = parser.perform(self.st)

            if isinstance(result, Success):
                return result.box
            else:
                raise StopParse(result)

    def run(gen_fn):
        try:
            result = gen_fn(self)
            if isinstance(result, Parser):
                return self.parse(result)
            else:
                return Success(result)
        except StopParse as s:
            return s.result

    def __init__(self, gen_fn):
        self.gen_fn = gen_fn

    def perform(self, st):
        return ParseGen(st).run(self.gen_fn)

class Desc(Parser):
    def __init__(self, parser, desc):
        self.parser = parser
        self._desc = desc

    def perform(self, st):
        index = st.index
        result = self.parser.perform(st)
        if isinstance(result, Failure):
            st.error_index = index
            st.error_messages = [self._desc]

        return result

class Alt(Parser):
    def __init__(self, parsers):
        assert(len(parsers) > 0, "empty alt!")
        self.parsers = parsers

    def perform(self, st):
        index = st.index
        result = None

        for parser in self.parsers:
            result = parser.perform(st)

            if isinstance(result, Success) or index != st.index:
                break

        return result

def alt(*parsers):
    return Alt(list(parsers))

class Backtrack(Parser):
    def __init__(self, parser):
        self.parser = parser

    def perform(self, st):
        st.mark()
        result = self.parser.perform(st)
        if isinstance(result, Success):
            st.clear_mark()
        else:
            st.backtrack()

        return result

class Seq(Parser):
    def __init__(self, parsers):
        assert(len(parsers) > 0, "empty seq!")
        self.parsers = parsers

    def perform(self, st):
        result = None
        aggregate = [None] * len(self.parsers)
        for i in range(0, len(self.parsers)):
            result = self.parsers[i].perform(st)
            if isinstance(result, Failure):
                return result
            aggregate[i] = result.box

        return Success(Box.List(aggregate))

def seq(*parsers):
    return Seq(list(parsers))

class Many(Parser):
    def __init__(self, parser):
        self.parser = parser

    def perform(self, st):
        result = None
        aggregate = []

        while True:
            start_index = st.index
            result = self.parser.perform(st)

            if isinstance(result, Success):
                assert st.index > start_index, "empty many!"
                aggregate.append(result.box)
            else:
                return Success(Box.List(aggregate))

class Scan(Parser):
    def __init__(self, parser):
        self.parser = parser

    def perform(self, st):
        result = None
        aggregate = []
        builder = UnicodeBuilder()

        while True:
            start_index = st.index
            result = self.parser.perform(st)

            if isinstance(result, Success):
                assert st.index > start_index, "empty scan!"
                builder.append(result.box.get_string())
            else:
                return Success(Box.String(builder.build()))

class Map(Parser):
    def __init__(self, parser, fn):
        self.parser = parser
        self.fn = fn

    def perform(self, st):
        result = self.parser.perform(st)
        if isinstance(result, Success):
            result.box = self.fn(result.box)

        return result

class string(Parser):
    def __init__(self, string):
        self.string = string

    def perform(self, st):
        for i in range(0, len(self.string)):
            if st.head != self.string[i]:
                st.error(self.string)
                return Failure()
            else:
                st.advance1()

        return Success(Box.String(self.string))

class Test(Parser):
    def __init__(self, pred):
        self.pred = pred

    def perform(self, st):
        head = st.head
        if self.pred(head):
            st.advance1()
            return Success(Box.String(head))
        else:
            st.error(u'predicate')
            return Failure()

def generate(desc_or_fn):
    if isinstance(desc_or_fn, str):
        def decorator(fn):
            return Generated(fn).desc(desc_or_fn)
        return decorator
    else:
        return Generated(desc_or_fn)

def char_range(start, end):
    return Test(lambda x: x is not None and start <= x <= end)

def one_of(string):
    return Test(lambda x: x is not None and x in string)

def none_of(string):
    return Test(lambda x: x is not None and not x in string)

class Eof(Parser):
    def perform(self, st):
        if st.head is None:
            return Success(None)
        else:
            return Failure()

eof = Eof()

class Reader(object):
    def setup(self):
        pass

    def next(self):
        raise "abstract"

    def teardown(self):
        pass

class FileReader(Reader):
    def __init__(self, fname, bufsize=20):
        self.fname = fname
        self.fdesc = None
        self.isEof = False
        self.buf = u''
        self.bufIndex = r_uint(0)

    def setup(self):
        self.fdesc = open(self.fname)
        self.fdesc.encoding = 'UTF-8'

    def next(self):
        if self.bufIndex >= len(self.buf):
            if self.isEof:
                return None
            else:
                self.buf = unicode(self.fdesc.read(self.bufsize))
                self.bufIndex = 0

        out = self.buf[self.bufIndex]
        self.bufIndex += 1
        return out

    def teardown(self):
        self.fdesc.close()

class StringReader(Reader):
    def __init__(self, string):
        self.string = string
        self.index = r_uint(0)

    def next(self):
        if self.index >= len(self.string):
            return None

        out = self.string[self.index]
        self.index += 1
        return out
