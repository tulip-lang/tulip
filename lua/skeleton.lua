local Lexer = require('lua/lexer')
local Errors = require('lua/errors')
local List = require('lua/list')

token_ids   = Lexer.token_ids
token_names = Lexer.token_names

eats_preceding_newline = {
  [token_ids.GT]       = true,
  [token_ids.RARROW]   = true,
  [token_ids.EQ]       = true,
  [token_ids.COMMA]    = true,
  [token_ids.PIPE]     = true,
  [token_ids.QUESTION] = true,
  [token_ids.RBRACK]   = true,
  [token_ids.RBRACE]   = true,
}

function parse_skeleton(lexer)
  lexer.setup()
  local parsed = _parse_sequence(lexer, nil, 0)
  lexer.teardown()
  return parsed
end

function is_closing(tok)
  return tok.tokid == token_ids.RBRACK or
         tok.tokid == token_ids.RBRACE or
         tok.tokid == token_ids.RPAREN
end

function unexpected(token, matching, message)
  print('unexpected', token, message)
  return tag('error', Errors.error('parse/unexpected', token, matching, message))
end

function unmatched(token, message)
  print('unmatched', token, message)
  return tag('error', Errors.error('parse/unmatched', token, message))
end

Stubs.impl_inspect_tag('skeleton/nested', 3, function(open, close, body)
  return '\\skel[' .. inspect_value(open) .. ': ' .. inspect_value(body) .. ' :' .. inspect_value(close) .. ']'
end)

Stubs.impl_inspect_tag('skeleton/token', 1, function(tok)
  return inspect_value(tok)
end)

function _parse_sequence(lexer, open_tok, expected_close_id)
  local elements = {}

  while true do
    local tok = lexer.next()

    if not tok then
      return -- the lexer had an error
    elseif tok.tokid == token_ids.EOF then
      if open_tok then
        return unmatched(open_tok, token_names[expected_close_id])
      else
        return List.list(elements)
      end
    elseif open_tok and tok.tokid == expected_close_id then
      return tag('skeleton/nested', open_tok, tok, List.list(elements))
    elseif is_closing(tok) then
      if open_tok then
        return unexpected(tok, tag('some', open_tok), 'invalid nesting')
      else
        return unexpected(tok, tag('none'), 'invalid nesting')
      end
    elseif tok.tokid == token_ids.LT then
      table.insert(elements, _parse_sequence(lexer, tok, token_ids.GT))
    elseif tok.tokid == token_ids.LPAREN then
      table.insert(elements, _parse_sequence(lexer, tok, token_ids.RPAREN))
    elseif tok.tokid == token_ids.LBRACK or tok.tokid == token_ids.MACRO then
      table.insert(elements, _parse_sequence(lexer, tok, token_ids.RBRACK))
    elseif tok.tokid == token_ids.LBRACE then
      table.insert(elements, _parse_sequence(lexer, tok, token_ids.RBRACE))
    elseif tok.tokid == token_ids.NL and expected_close_id == token_ids.RPAREN then
      -- pass
    elseif tok.tokid == token_ids.NL and eats_preceding_newline[lexer.peek().tokid] then
      -- pass
    else
      table.insert(elements, tag('skeleton/token', tok))

      if tok.tokid == token_ids.GT then
        -- manually skip NL tokens here, since the lexer can't for <...>
        while lexer.peek().tokid == token_ids.NL do lexer.next() end
      end
    end
  end
end

return {
  parse_skeleton = parse_skeleton,
  inspect = inspect_skeletons
}
