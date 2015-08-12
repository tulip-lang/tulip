from rpython.rlib.rarithmetic import r_uint
from tulip.debug import debug

class Token:
    TOKENS = [
      u"LPAREN",
      u"RPAREN",

      u"LBRACK",
      u"RBRACK",

      u"GT",
      u"DOLLAR",
      u"NL",
      u"RARROW",
      u"EQ",
      u"PLUS",
      u"TILDE",
      u"BANG",
      u"PIPE",
      u"COLON",
      u"STAR",
      u"COMMA",
      u"UNDERSCORE",
      u"QUESTION",
      u"DASH",

      u"AMP",
      u"FLAG",
      u"FLAGKEY",
      u"CHECK",
      u"TAGGED",
      u"MACRO",
      u"ANNOT",
      u"SLASH",
      u"INT",
      u"NAME",
      u"STRING",

      u"EOF"
    ]

    def __init__(self, tokid, value, loc_range):
        self.tokid = tokid
        self.value = value
        self.loc_range = loc_range

    def is_before(self, other):
        return self.loc_range.start.index < other.loc_range.start.index

    def dump(self):
        if self.value is None:
            return u'%s%s' % (self.loc_range.dump(), Token.TOKENS[self.tokid])
        else:
            return u'%s%s(%s)' % (self.loc_range.dump(), Token.TOKENS[self.tokid], self.value)

    def is_eof(self):
        return self.tokid == Token.EOF

for i in range(len(Token.TOKENS)):
    setattr(Token, Token.TOKENS[i], r_uint(i))

class LocRange(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def dump(self):
        return u'%s:<%s,%s>' % (self.start.input, self.start.dump(), self.end.dump())

class Location(object):
    def __init__(self, input, index, line, col):
        self.index = index
        self.line = line
        self.col = col
        self.input = input

    def equal(self, other):
        return self.input == other.input and self.index == other.index

    def dump(self):
        return u'%d:%d' % (self.line, self.col)

class LexError(StandardError):
    def __init__(self, lexer, message):
        self.lexer = lexer
        self.message = message

    def dump(self):
        head_ = self.lexer.head or u'EOF'

        return u'lex error: %d:%d: %s\nhead: <%s>' % (
          self.lexer.line,
          self.lexer.col,
          self.message,
          head_
        )

class Lexer(object):
    def setup(self):
        pass

    def next(self):
        assert False, u'abstract'

    def teardown(self):
        pass

class ListLexer(Lexer):
    def __init__(self, lexemes):
        self.lexemes = lexemes
        self.index = 0

    def next(self):
        self.index += 1
        return self.lexemes[self.index - 1]

class ReaderLexer(Lexer):
    def __init__(self, reader):
        self.reader = reader
        self.index = r_uint(0)
        self.line = r_uint(1)
        self.col = r_uint(0)
        self.head = None
        self.tape = None
        self.recording = False
        self.uninitialized = True

    def error(self, message):
        raise LexError(self, message)

    def setup(self):
        assert self.head is None
        self.reader.setup()
        self.advance()
        self.uninitialized = False
        self.skip_lines()
        self.reset()

    def teardown(self):
        self.reader.teardown()

    def reset(self):
        self.recording = False
        self.tape = None
        self._final_loc = None

    def recorded_value(self):
        if self.tape is None:
            return None
        else:
            return u''.join(self.tape)

    def current_location(self):
        return Location(self.reader.input_name(), self.index, self.line, self.col)

    def advance(self):
        assert self.uninitialized or self.head is not None, u"can't advance past the end!"

        self.index += 1
        if self.head == u'\n':
            self.line += 1
            self.col = r_uint(0)
        else:
            self.col += 1

        if self.recording:
            self.tape.append(self.head)

        self.head = self.reader.next()

        if debug.check('lexer'):
            print u'advance<%s>' % self.head

    def record(self):
        self.recording = True
        self.tape = []

    def end_record(self):
        self.recording = False
        self.end_loc()

    def end_loc(self):
        self._final_loc = self.current_location()

    def final_loc(self):
        return self._final_loc or self.current_location()

    def next(self):
        self.reset()
        start = self.current_location()
        token = self.process_root()
        value = self.recorded_value()
        end = self.final_loc()
        assert (token == Token.EOF or self.index != start.index), u'must advance the stream!'
        return Token(token, value, LocRange(start, end))

    def skip_ws(self):
        self.end_loc()
        self._advance_through_ws()

    def _advance_through_ws(self):
        while is_ws(self.head):
            self.advance()

    def skip_lines(self):
        self.end_loc()
        while True:
            self._advance_through_ws()
            if self.head == u'#':
                while self.head != u'\n' and self.head is not None:
                    self.advance()
            elif self.head in [u'\r', u'\n', u';']:
                self.advance()
            else:
                self._advance_through_ws()
                break

    def record_ident(self):
        if not is_alpha(self.head):
            self.error(u'expected an identifier')

        self.record()
        self.advance()

        while is_ident_char(self.head):
            self.advance()

        self.end_record()

    def process_string(self):
        self.advance()

        self.record()
        level = 1
        while True:
            if self.head == u'{':
                level += 1
            elif self.head == u'}':
                level -= 1
            elif self.head is None:
                self.error(u'unmatched close brace }')

            if level == 0:
                self.end_record()
                self.advance()
                break
            else:
                self.advance()

    def process_root(self):
        if self.head is None:
            return Token.EOF

        if self.head == u'(':
            self.advance()
            self.skip_lines()
            return Token.LPAREN

        if self.head == u')':
            self.advance()
            self.skip_ws()
            return Token.RPAREN

        if self.head == u'[':
            self.advance()
            self.skip_lines()
            return Token.LBRACK

        if self.head == u'{':
            self.process_string()
            self.skip_ws()
            return Token.STRING

        if self.head == u'\'':
            self.advance()
            self.record_ident()
            return Token.STRING

        if self.head == u']':
            self.advance()
            self.skip_ws()
            return Token.RBRACK

        if self.head == u'=':
            self.advance()
            if self.head == u'>':
                self.advance()
                self.skip_lines()
                return Token.RARROW
            else:
                self.skip_lines()
                return Token.EQ

        if self.head == u'+':
            self.advance()
            self.skip_ws()
            return Token.PLUS

        if self.head == u'$':
            self.advance()
            self.skip_ws()
            return Token.DOLLAR

        if self.head == u'>':
            self.advance()
            self.skip_lines()
            return Token.GT

        if self.head == u'!':
            self.advance()
            self.skip_ws()
            return Token.BANG

        if self.head == u'?':
            self.advance()
            self.skip_lines()
            return Token.QUESTION

        if self.head == u'_':
            self.advance()
            self.skip_ws()
            return Token.UNDERSCORE

        if self.head == u'-':
            self.advance()
            if is_ws(self.head) or self.head is None:
                self.skip_ws()
                return Token.DASH
            else:
                self.record_ident()
                if self.head == u':':
                    self.advance()
                    self.skip_lines()
                    return Token.FLAGKEY
                else:
                    self.skip_ws()
                    return Token.FLAG

        if self.head == u':':
            self.advance()
            self.skip_lines()
            return Token.COLON

        if self.head == u',':
            self.advance()
            self.skip_lines()
            return Token.COMMA

        if self.head == u'*':
            self.advance()
            self.skip_ws()
            return Token.STAR

        if self.head == u'%':
            self.advance()
            self.record_ident()
            self.skip_ws()
            return Token.CHECK

        if self.head == u'@':
            self.advance()
            self.record_ident()
            self.skip_ws()
            return Token.ANNOT

        if self.head == u'&':
            self.advance()
            self.record_ident()
            self.skip_ws()
            return Token.AMP

        if self.head == u'/':
            self.advance()
            if is_alpha(self.head):
                self.record_ident()
            else:
                self.tape = []

            if self.head == u'[':
                self.advance()
                self.skip_lines()
                return Token.MACRO
            else:
                self.error(u'expected [')

        if self.head == u'.':
            self.advance()
            self.record_ident()
            self.skip_ws()
            return Token.TAGGED

        if is_digit(self.head):
            self.record()
            while is_digit(self.head):
                self.advance()
            self.end_record()
            self.skip_ws()
            return Token.INT

        if is_alpha(self.head):
            self.record_ident()
            self.skip_ws()
            return Token.NAME

        if self.head in [u'\r', u'\n', u'#', u';']:
            self.skip_lines()
            return Token.NL

        self.error(u'unexpected character')


def is_digit(c):
    if c is None:
        return False

    return u'0' <= c <= u'9'

def is_alpha(c):
    if c is None:
        return False

    return u'a' <= c <= u'z' or u'A' <= c <= u'Z'

def is_ident_char(c):
    if c is None:
        return False

    return is_alpha(c) or is_digit(c) or c in [u'-', u'_']

def is_ws(c):
    if c is None:
        return False

    return c in [u' ', u'\t']
