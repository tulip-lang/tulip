local Stubs = require 'lua/stubs'
local Lexer = require 'lua/lexer'
local Skeleton = require 'lua/skeleton'
local Errors = require 'lua/errors'
local Macros = require 'lua/macros'

local function compile(reader)
  local lexer = Lexer.new(reader)
  local out = {}
  local errors, _ = Errors.error_scope(function()
    out.skel = parse_skeleton(lexer)
    out.expanded = Macros.macro_expand(out.skel)
  end)

  return errors, out
end

return {
  compile = compile
}
