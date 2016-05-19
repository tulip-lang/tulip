-- TODO: pass this into the compile function as a
-- file or string reader
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

-- TODO implement in C
function tag(name, ...)
  return { tag = name, values = {...} }
end

-- TODO implement in C
function tag_get(obj, index)
  return obj.values[index+1]
end

local tag_inspectors = {}

function tag_key(name, arity) return name .. '@' .. tostring(arity) end

function impl_inspect_tag(name, arity, impl)
  tag_inspectors[tag_key(name, arity)] = impl
end

function inspect_tag(t)
  local dyn_impl = tag_inspectors[tag_key(t.tag, #t.values)]
  if dyn_impl then return dyn_impl(unpack(t.values)) end

  local out = '(.' .. t.tag

  for _,v in pairs(t.values) do
    out = out .. ' ' .. inspect_value(v)
  end

  return out .. ')'
end

-- TODO implement in C
function matches_tag(t, name, arity)
  if not (type(t) == 'table') then return false end
  if not (t.tag == name) then return false end
  if not (#t.values == arity) then return false end
  return true
end

-- TODO implement in C
function inspect_value(t)
  if type(t) == 'table' and t.tag then return inspect_tag(t)
  elseif type(t) == 'table' and t.tokid then return inspect_token(t)
  elseif type(t) == 'string' then return '\'{' .. t .. '}'
  else
    return tostring(t)
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
  if range == '<synthetic>' then return '' end

  return '<' .. range.start.input .. ':' ..
          inspect_loc(range.start) .. '-' ..
          inspect_loc(range.final) .. '>'
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
  matches_tag = matches_tag,
  tag = tag,
  tag_get = tag_get,
  Token = Token,
  impl_inspect_tag = impl_inspect_tag,
}
