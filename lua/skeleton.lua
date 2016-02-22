Lexer = require('lua/lexer')

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

function tag(name, ...)
  return { tag = name, values = {...} }
end

function parse_skeleton(lexer)
  lexer.setup()
  local parsed = _parse_sequence(lexer, nil, 0)
  lexer.teardown()
  return parsed
end

function inspect_skeletons(skeletons)
  local out = {}
  for k,v in pairs(skeletons) do
    out[k] = inspect_one(v)
  end

  return table.concat(out, ' ')
end

function inspect_one(skel)
  if skel.tag == 'nested' then
    local open, close, body = unpack(skel.values)
     return '[' .. inspect_token(open) .. ': ' .. inspect_skeletons(body) .. ' :' .. inspect_token(close) .. ']'
  elseif skel.tag == 'token' then
    local token = unpack(skel.values)
    return inspect_token(token)
  else
    error('bad skeleton')
  end
end

function inspect_token(token)
  name = token_names[token.tokid]
  if token.value then
    return name .. '(' .. token.value .. ')'
  else
    return name
  end
end

function is_closing(tok)
  return tok.tokid == token_ids.RBRACK or
         tok.tokid == token_ids.RBRACE or
         tok.tokid == token_ids.RPAREN
end

function unexpected(token, message)
  error(tag('parse/unexpected', token, message))
end

function unmatched(token, message)
  error(tag('parse/unmatched', token, message))
end

function _parse_sequence(lexer, open_tok, expected_close_id)
  local elements = {}

  while true do
    local tok = lexer.next()

    if tok.tokid == token_ids.EOF then
      if open_tok then
        unmatched(open_tok, token_names[expected_close_id])
      else
        return elements
      end
    elseif open_tok and tok.tokid == expected_close_id then
      return tag('nested', open_tok, tok, elements)
    elseif is_closing(tok) then
      if open_tok then
        unexpected(tok, 'invalid nesting from ' .. open_tok)
      else
        unexpected(tok, 'invalid nesting from the beginning')
      end
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
      table.insert(elements, tag('token', tok))
    end
  end
end

return {
  parse_skeleton = parse_skeleton,
  inspect = inspect_skeletons
}
