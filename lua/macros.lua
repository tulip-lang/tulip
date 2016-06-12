local Stubs = require 'lua/stubs'
local Lexer = require 'lua/lexer'
local Skeleton = require 'lua/skeleton'
local List = require 'lua/list'
local Lexer = require 'lua/lexer'

local tag = Stubs.tag
local tag_get = Stubs.tag_get

local function synthetic_token(name, value)
  return Stubs.Token(Lexer.token_ids[name], value, '<synthetic>')
end

local tok = synthetic_token

local macro_registry = {}

local function define_builtin_macro(name, impl)
  if macro_registry[name] then error('macro ' .. name .. ' already exists!') end

  macro_registry[name] = impl
end

local function is_token(skel, toktype)
  if not matches_tag(skel, 'skeleton/token', 1) then return false end
  return tag_get(skel, 0).tokid == Lexer.token_ids[toktype]
end

local function brace(items)
  return tag('skeleton/nested', tok('LBRACE', nil), tok('RBRACE', nil), items)
end

define_builtin_macro('list', function(skels)
  return List.foldr(skels, tag('token', tok('TAGGED', 'nil')), function(el, next)
    return tag('skeleton/nested', tok('LBRACE', nil), tok('RBRACE', nil),
              List.list{tag('token', tok('TAGGED', 'cons')),
                        el,
                        next})
  end)
end)

local function macro_use(skel)
  if not matches_tag(skel, 'skeleton/nested', 3) then return nil end
  local open_tok = tag_get(skel, 0)

  if open_tok.tokid == Lexer.token_ids.MACRO then
    return open_tok.value
  else
    return nil
  end
end

local found_macro_state = {}

local function replace_macros(skels)
  return List.map(skels, function(skel)
    local macro_name = macro_use(skel)

    if macro_name then
      found_macro_state.value = true
      return macro_registry[macro_name](tag_get(skel, 2))
    elseif skel.tag == 'skeleton/nested' then
      return tag('skeleton/nested', tag_get(skel, 0),
                                    tag_get(skel, 1),
                                    replace_macros(tag_get(skel, 2)))
    elseif skel.tag == 'skeleton/item' then
      return tag('skeleton/item', replace_macros(tag_get(skel, 0)),
                                  replace_macros(tag_get(skel, 1)))
    elseif skel.tag == 'skeleton/annotation' then
      return tag('skeleton/annotation', replace_macros(tag_get(skel, 0)))
    else
      return skel
    end
  end)
end

-- forward decl
local macro_expand

local function macro_expand_1(skels)
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

return {
  macro_expand_1 = macro_expand_1,
  macro_expand = macro_expand,
}
