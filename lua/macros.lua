local Stubs = require 'lua/stubs'
local Lexer = require 'lua/lexer'
local Skeleton = require 'lua/skeleton'
local List = require 'lua/list'

local tag = Stubs.tag
local tag_get = Stubs.tag_get

function synthetic_token(name, value)
  return Stubs.Token(Lexer.token_ids[name], value, '<synthetic>')
end

local tok = synthetic_token

local macro_registry = {}

function define_builtin_macro(name, impl)
  if macro_registry[name] then error('macro ' .. name .. ' already exists!') end

  macro_registry[name] = impl
end

-- TODO: actually separate by ;
define_builtin_macro('list', function(skels)
  local out = tag('token', tok('TAGGED', 'nil'))

  List.each(skels, function(skel)
    out = tag('skeleton/nested', tok('LPAREN', nil), tok('RPAREN', nil),
              List.list{tag('token', tok('TAGGED', 'cons')),
                        skel,
                        out})
  end)

  return out
end)

function macro_use(skel)
  if not matches_tag(skel, 'skeleton/nested', 3) then return nil end
  local open_tok = tag_get(skel, 0)

  if open_tok.tokid == Lexer.token_ids.MACRO then
    return open_tok.value
  else
    return nil
  end
end

local found_macro_state = {}

function macro_expand_1(skels)
  found_macro_state.value = false
  local out = replace_macros(skels)
  return found_macro_state.value, out
end

function macro_expand(skels)
  local modified = true

  while modified do
    modified, skels = macro_expand_1(skels)
  end

  return skels
end

function replace_macros(skels)
  return List.map(skels, function(skel)
    local macro_name = macro_use(skel)

    if macro_name then
      found_macro_state.value = true
      return macro_registry[macro_name](tag_get(skel, 2))
    elseif skel.tag == 'nested' then
      return tag('nested', tag_get(skel, 0),
                           tag_get(skel, 1),
                           replace_macros(tag_get(skel, 2)))
    else
      return skel
    end
  end)
end

return {
  macro_expand_1 = macro_expand_1,
  macro_expand = macro_expand,
}
