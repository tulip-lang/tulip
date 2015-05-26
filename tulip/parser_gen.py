from tulip.debug import debug
from tulip.lexer import Token

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

        def get_token(self):
            assert False, "not a token!"

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

    class Token(Base):
        def __init__(self, t):
            self.token = t

        def get_token(self):
            return self.token

        def dump(self):
            return u"<Box.Token %s>" % self.token.dump()

class ParseState(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.index = 0
        self.head = None
        self.error_token = None
        self.ahead = []
        self.behind = []
        self.bt_marks = []
        self.debug = debug.check('parser')

    def dump(self):
        behind = [t.dump() for t in self.behind]
        ahead = [t.dump() for t in self.ahead]
        if self.head is None:
            head = u'None'
        else:
            head = self.head.dump()
        ahead.reverse()
        return u"(st %d <<%s>> %s <<%s>>)" % (
          self.index,
          u''.join(behind),
          head,
          u''.join(ahead)
        )

    def advance(self):
        self.index += 1
        if self.debug:
            print u'advance: %s' % self.dump()
        if len(self.bt_marks) > 0:
            self.behind.append(self.head)

        if len(self.ahead) > 0:
            self.head = self.ahead.pop()
        else:
            self.head = self.lexer.next()

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
        if self.error_token is self.head:
            self.error_messages.append(message)
        elif self.error_token is None or self.error_token.is_before(self.head):
            self.error_token = self.head
            self.error_messages = [message]

    def rewind(self):
        assert len(self.behind) > 0, "can't rewind anymore!"
        self.index -= 1
        self.ahead.append(self.head)
        self.head = self.behind.pop()
        if self.debug:
            print u"rew: %s" % self.dump()

    def rewind_to(self, idx):
        assert idx <= self.index, "can't rewind forwards"
        while idx < self.index:
            self.rewind()
        # otherwise pass, we're backtracked

    def assert_eof(self):
        if self.head.tokid == Token.EOF:
            raise ParseError(self.head, [u'EOF'])




class Result(object):
    pass

class Success(Result):
    def __init__(self, box):
        self.box = box

class Failure(Result):
    pass

failure = Failure()

class ParseError(Exception):
    def __init__(self, token, messages):
        self.token = token
        self.messages = messages

    def dump(self):
        return u"parse error at %s - expected one of %s" % \
          (self.token.loc_range.start.dump(), u", ".join(self.messages))

    def __str__(self):
        return self.dump()

class Parser(object):
    def perform(self, st):
        assert False, "abstract"

    def parse(self, lexer):
        lexer.setup()
        try:
            state = ParseState(lexer)
            state.advance()
            result = self.perform(state)

            if result is failure:
                raise ParseError(state.error_token, state.error_messages)
            elif isinstance(result, Success):
                print 'head:'
                print state.head.dump()
                if state.head.tokid is Token.EOF:
                    return result.box
                else:
                    state.error(u'EOF')
                    raise ParseError(state.error_token, state.error_messages)

            assert False, "impossible"
        finally:
            lexer.teardown()

    def desc(self, desc):
        return Desc(self, unicode(desc))

    def many(self):
        return Many(self)

    def many1(self):
        return seq(self, Many(self)).map(_many1_map)

    def map(self, fn):
        return Map(self, fn)

    def skip(self, other):
        return seq(self, other).map(_skip_map)

    def then(self, other):
        return seq(self, other).map(_then_map)

    def backtracking(self):
        return Backtracking(self)

    def opt(self):
        return Opt(self)

def _then_map(box):
    return box.get_list()[1]

def _skip_map(box):
    return box.get_list()[0]

def _many1_map(box):
    first, rest = box.get_list()
    aggregate = rest.get_list()
    aggregate.insert(0, first)
    return Box.List(aggregate)

class _GenFail(Exception):
    pass

class Generated(Parser):
    class ParseGen(object):
        def __init__(self, st):
            self.st = st

        def parse(self, parser):
            result = parser.perform(self.st)

            if isinstance(result, Success):
                return result.box
            else:
                raise _GenFail()

        def fail(self, message):
            self.st.error(message)
            raise _GenFail()

        def run(self, gen_fn):
            try:
                return Success(gen_fn(self))
            except _GenFail:
                return failure

    def __init__(self, gen_fn):
        self.gen_fn = gen_fn

    def perform(self, st):
        return Generated.ParseGen(st).run(self.gen_fn)

def generate(desc_or_fn):
    if isinstance(desc_or_fn, str):
        def decorator(fn):
            return Generated(fn).desc(desc_or_fn)
        return decorator
    else:
        return Generated(desc_or_fn)

class Opt(Parser):
    def __init__(self, parser):
        self.parser = parser

    def perform(self, st):
        result = self.parser.perform(st)
        if result is failure:
            return Success(None)
        else:
            return result

class Desc(Parser):
    def __init__(self, parser, desc):
        self.parser = parser
        self._desc = desc

    def perform(self, st):
        head = st.head
        result = self.parser.perform(st)
        if result is failure:
            st.error_token = head
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

class Backtracking(Parser):
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
            if result is failure:
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

class Map(Parser):
    def __init__(self, parser, fn):
        self.parser = parser
        self.fn = fn

    def perform(self, st):
        result = self.parser.perform(st)
        if isinstance(result, Success):
            result.box = self.fn(result.box)

        return result

class tok(Parser):
    def __init__(self, tokid):
        self.tokid = tokid
        self.name = Token.TOKENS[tokid]

    def perform(self, st):
        head = st.head
        if head.tokid == self.tokid:
            if head.tokid != Token.EOF:
                st.advance()
            return Success(Box.Token(head))
        else:
            st.error(self.name)
            return failure

class Any(Parser):
    def perform(self, st):
        head = st.head
        if head.tokid == Token.EOF:
            st.error(u'any token')
            return failure
        else:
            st.advance()
            return Success(Box.Token(head))

any = Any()
