local Stubs = require 'lua/stubs'
local Errors = require 'lua/errors'

local Token = Stubs.Token

local token_names = {
  "LPAREN",
  "RPAREN",

  "LBRACK",
  "RBRACK",

  "LBRACE",
  "RBRACE",

  "GT",
  "LT",
  "DOLLAR",
  "NL",
  "RARROW",
  "EQ",
  "TILDE",
  "BANG",
  "PIPE",
  "COLON",
  "STAR",
  "COMMA",
  "UNDERSCORE",
  "QUESTION",
  "DASH",
  "DOT",

  "AMP",
  "DYNAMIC",
  "FLAG",
  "FLAGKEY",
  "CHECK",
  "TAGGED",
  "TICKED",
  "MACRO",
  "PMACRO",
  "ATMACRO",
  "PATMACRO",
  "STARRED",
  "LOOKUP",
  "ANNOT",
  "PANNOT",
  "INT",
  "NAME",
  "STRING",

  "EOF"
}

local token_ids = {}
for index, name in ipairs(token_names) do
  token_ids[name] = index
end

function new(stream)
  local state = {
    index = 0,
    line = 0,
    column = 0,
    tape = nil,
    last = nil,
    head = nil,
    recording = false,
    uninitialized = true,
    peek = nil,
    final_loc = nil,
  }

  function setup()
    stream.setup()
    advance()
    state.uninitialized = false
    skip_lines()
    reset()
  end

  function teardown()
    stream.teardown()
  end

  function reset()
    state.recording = false
    state.tape = nil
    state.final_loc = nil
  end

  function recorded_value()
    if state.tape then
      return table.concat(state.tape, '')
    else
      return nil
    end
  end

  function current_location()
    return {
      input = stream.input_name(),
      index = state.index,
      line = state.line,
      column = state.column
    }
  end

  function error(...)
    return Errors.error('parse/lexer', ...)
  end

  function advance()
    if not (state.uninitialized or state.head) then
      error('unexpected EOF')
    end

    state.index = state.index + 1
    if state.head == "\n" then
      state.line = state.line + 1
      state.column = 0
    else
      state.column = state.column + 1
    end

    if state.recording then
      table.insert(state.tape, state.head)
    end

    state.last = state.head
    state.head = stream.next()
  end

  function record()
    state.recording = true
    state.tape = {}
  end

  function end_record()
    state.recording = false
    end_loc()
  end

  function end_loc()
    state.final_loc = current_location()
  end

  function final_loc()
    return state.final_loc or current_location()
  end

  function next()
    if state.peek then
      local p = state.peek
      state.peek = nil
      return p
    end

    reset()
    local start = current_location()
    local token = process_root()
    local value = recorded_value()
    local final = final_loc()

    assert(token == token_ids.EOF or state.index ~= start.index, 'must advance the stream! (at ' .. start.index .. ')')

    return Token(token, value, { start = start, final = final })
  end

  function peek()
    if not state.peek then
      state.peek = next()
    end

    return state.peek
  end

  function skip_ws()
    end_loc()
    advance_through_ws()
  end

  function advance_through_ws()
    while is_ws(state.head) do advance() end
  end

  function skip_lines()
    end_loc()
    while true do
      advance_through_ws()
      if state.head == '#' then
        while state.head and state.head ~= "\n" do advance() end
      elseif is_nl(state.head) then
        advance()
      else
        break
      end
    end
  end

  function record_ident()
    if not is_alpha(state.head) then error('expected an identifier') end

    record()

    advance()
    while is_ident_char(state.head) do advance() end

    end_record()
  end

  function advance_through_string()
    local level = 0

    while true do
      if state.head == '\\' then
        advance()
      elseif state.head == '{' then
        level = level + 1
      elseif state.head == '}' then
        level = level - 1
      elseif not state.head then
        error('unmatched close brace')
      end

      advance()

      if level == 0 then break end
    end
  end

  function process_root()
    if not state.head then return token_ids.EOF end

    if state.head == '(' then
      advance()
      skip_lines()
      return token_ids.LPAREN
    end

    if state.head == ')' then
      advance()
      skip_ws()
      return token_ids.RPAREN
    end

    if state.head == '[' then
      advance()
      skip_lines()
      return token_ids.LBRACK
    end

    if state.head == ']' then
      advance()
      skip_ws()
      return token_ids.RBRACK
    end

    if state.head == '{' then
      advance()
      skip_lines()
      return token_ids.LBRACE
    end

    if state.head == '}' then
      advance()
      skip_ws()
      return token_ids.RBRACE
    end

    if state.head == "'" then
      advance()
      if state.head == '{' then
        record()
        advance_through_string()
        end_record()
        skip_ws()
        return token_ids.STRING
      else
        record_ident()
        return token_ids.STRING
      end
    end

    if state.head == '`' then
      advance()
      record_ident()
      skip_lines()
      return token_ids.TICKED
    end

    if state.head == '=' then
      advance()
      if state.head == '>' then
        advance()
        skip_lines()
        return token_ids.RARROW
      else
        skip_lines()
        return token_ids.EQ
      end
    end

    if state.head == '+' then
      advance()
      record_ident()

      if state.head == '{' then
        state.recording = true
        advance_through_string()
        end_record()
        skip_lines()
        return token_ids.PANNOT
      else
        skip_ws()
        return token_ids.ANNOT
      end
    end

    if state.head == '$' then
      advance()
      if is_alpha(state.head) then
        record_ident()
        skip_ws()
        return token_ids.DYNAMIC
      else
        skip_ws()
        return token_ids.DOLLAR
      end
    end

    if state.head == '>' then
      advance()
      skip_ws()
      return token_ids.GT
    end

    if state.head == '<' then
      advance()
      skip_lines()
      return token_ids.LT
    end

    if state.head == '!' then
      advance()
      skip_ws()
      return token_ids.BANG
    end

    if state.head == '?' then
      advance()
      skip_lines()
      return token_ids.QUESTION
    end

    if state.head == '_' then
      advance()
      skip_ws()
      return token_ids.UNDERSCORE
    end

    if state.head == '-' then
      advance()
      if is_alpha(state.head) then
        record_ident()
        if state.head == ':' then
          advance()
          skip_lines()
          return token_ids.FLAGKEY
        else
          skip_ws()
          return token_ids.FLAG
        end
      else
        return token_ids.DASH
      end
    end

    if state.head == ':' then
      advance()
      skip_lines()
      return token_ids.COLON
    end

    if state.head == ',' then
      advance()
      skip_lines()
      return token_ids.COMMA
    end

    if state.head == '*' then
      advance()
      skip_ws()
      return token_ids.STAR
    end

    if state.head == '~' then
      advance()
      skip_ws()
      return token_ids.TILDE
    end

    if state.head == '%' then
      advance()
      record_ident()
      skip_ws()
      return token_ids.CHECK
    end

    if state.head == '@' then
      advance()
      record_ident()

      if state.head == '{' then
        state.recording = true
        advance_through_string()
        end_record()
        skip_lines()
        return token_ids.PATMACRO
      else
        skip_ws()
        return token_ids.ATMACRO
      end
    end

    if state.head == '&' then
      advance()
      record_ident()
      skip_ws()
      return token_ids.AMP
    end

    if state.head == '/' then
      advance()
      record_ident()
      return token_ids.LOOKUP
    end

    if state.head == '\\' then
      advance()
      if is_alpha(state.head) then
        record_ident()
      else
        state.tape = {}
      end

      if state.head == '[' then
        advance()
        skip_lines()
        return token_ids.MACRO
      elseif state.head == '{' then
        state.recording = true
        advance_through_string()
        end_record()
        return token_ids.PMACRO
      else
        error('expected [')
      end
    end

    if state.head == '.' then
      advance()
      if is_alpha(state.head) then
        record_ident()
        skip_ws()
        return token_ids.TAGGED
      else
        skip_ws()
        return token_ids.DOT
      end
    end

    if is_digit(state.head) then
      record()
      while is_digit(state.head) do advance() end
      end_record()
      skip_ws()
      return token_ids.INT
    end

    if is_alpha(state.head) then
      record_ident()
      skip_ws()
      return token_ids.NAME
    end

    if is_nl(state.head) or state.head == '#' then
      skip_lines()
      return token_ids.NL
    end

    error('unexpected character <' .. state.head .. '>')
  end

  return {
    setup = setup,
    teardown = teardown,
    next = next,
    peek = peek
  }
end

function is_nl(char)
  if not char then return false end
  return char == '\r' or char == '\n' or char == ';'
end

function is_ws(char)
  if not char then return false end
  return char == ' ' or char == '\t'
end

function is_alpha(char)
  if not char then return false end
  return ('a' <= char and char <= 'z') or
         ('A' <= char and char <= 'Z')
end

function is_digit(char)
  if not char then return false end
  return ('0' <= char and char <= '9')
end

function is_ident_char(char)
  if not char then return false end

  return is_alpha(char) or
         is_digit(char) or
         char == '-' or
         char == '_' or
         char == '/'
end

function is_immediate(char)
  if is_ws(char) then return false end
  if is_alpha(char) then return true end
  if char == ')' or char == ']' or char == '}' then return true end
  if char == '$' or char == '-' then return true end

  return false
end

return {
  new = new,
  token_ids = token_ids,
  token_names = token_names
}
