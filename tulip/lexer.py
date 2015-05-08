from rpython.rlib.rarithmetic import r_uint

class Token:
    TOKENS = [
      u"LPAREN",
      u"RPAREN",

      u"LBRACE",
      u"RBRACE",

      u"GT",
      u"DOLLAR",
      u"NL",
      u"RARROW",
      u"EQ",
      u"PLUS",
      u"TILDE",
      u"BANG",

      u"CHECK",
      u"TAGGED",
      u"ANNOT",
      u"SLASH",
      u"INT",
      u"NAME",

      u"EOF"
    ]


for i in range(len(Token.TOKENS)):
    setattr(Token, Token.TOKENS[i], r_uint(i))

class LexError(StandardError):
    def __init__(self, lexer):
        self.lexer = lexer

class Lexer(object):
    def __init__(self, reader):
        self.reader = reader
        self.index = r_uint(0)
        self.line = r_uint(0)
        self.col = r_uint(0)
        self.head = None
        self.tape = None
        self.recording = False
        self.uninitialized = True

    def setup(self):
        assert self.head is None
        self.advance()
        self.uninitialized = False

    def reset(self):
        self.recording = False
        self.tape = None

    def recorded_value(self):
        if self.tape is None:
            return None
        else:
            return u''.join(self.tape)

    def advance(self):
        assert self.uninitialized or self.head is not None

        if self.recording:
            self.tape.append(self.head)

        self.head = self.reader.next()
        print u'advance<%s>' % self.head

        self.index += 1
        if self.head == u'\n':
            print 'line advance'
            self.line += 1
            self.col = r_uint(0)
        else:
            print u'column advance on <%s>' % self.head
            self.col += 1

    def record(self):
        self.recording = True
        self.tape = []

    def end_record(self):
        self.recording = False

    def next(self):
        self.reset()
        token = self.process_root()
        value = self.recorded_value()
        return (token, value)

    def skip_ws(self):
        while is_ws(self.head):
            self.advance()

    def skip_lines(self):
        while True:
            self.skip_ws()
            if self.head == u'#':
                while self.head != u'\n' and self.head is not None:
                    self.advance()
            elif self.head in [u'\r', u'\n']:
                self.advance()
            else:
                self.skip_ws()
                break

    def record_ident(self):
        if not is_alpha(self.head):
            raise LexError(self)

        self.record()
        self.advance()

        while is_ident_char(self.head):
            self.advance()

        self.end_record()

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
            return Token.LBRACE

        if self.head == u']':
            self.advance()
            self.skip_lines()
            return Token.LBRACE

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

        raise LexError(self)


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
