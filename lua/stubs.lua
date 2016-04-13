function string_reader(input)
  local state = {
    index = 0
  }

  function setup() state.index = 0 end
  function teardown() end

  function next()
    if state.index >= #input then return nil end

    state.index = state.index + 1
    return string.sub(input, state.index, state.index)
  end

  function input_name()
    return '{input-string}'
  end

  return {
    setup = setup,
    next = next,
    teardown = teardown,
    input_name = input_name
  }
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

function tag(name, ...)
  return { tag = name, values = {...} }
end

function tag_get(obj, index)
  -- TODO: error handling
  return obj.values[index]
end

function inspect_tag(t)
  out = '(.' .. t.tag

  for _,v in pairs(t.values) do
    out = out .. ' ' .. inspect_value(v)
  end

  return out .. ')'
end

function matches_tag(t, name, arity)
  if not type(t) == 'table' then return false end
  if not t.tag == name then return false end
  if not #t.values == arity then return false end
  return true
end

function inspect_value(t)
  if type(t) == 'table' and t.tag then return inspect_tag(t)
  elseif type(t) == 'table' and t.tokid then return inspect_token(t)
  elseif type(t) == 'string' then return '\'{' .. t .. '}'
  else return t
  end
end

function Token(id, value, range)
  return {
    tokid = id,
    value = value,
    range = range
  }
end

function inspect_loc(loc)
  return loc.line .. ':' .. loc.column
end

function inspect_range(range)
  return '<' .. range.start.input .. ':' ..
          inspect_loc(range.start) .. '-' ..
          inspect_loc(range.final)
end

function inspect_token(token)
  local name = token_names[token.tokid]
  local range = inspect_range(token.range)
  local raw = nil

  if token.value then
    raw = name .. '(' .. token.value .. ')'
  else
    raw = name
  end

  return raw .. '@' .. range
end

return {
  string_reader = string_reader,
  inspect_skeletons = inspect_skeletons,
  inspect_value = inspect_value,
  tag = tag,
  tag_get = tag_get,
  Token = Token,
}
