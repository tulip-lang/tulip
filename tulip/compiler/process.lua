local dyn = require('tulip/compiler/dyn')
local skeleton = require('tulip/compiler/skeleton')

local function compile(skeleton)
  if #skeletons == 0 then return nil end
  dyn.bind({errors={}}, function() process_expr(skeleton) end)
end

local function report_error(loc, msg)
  table.insert(dyn.errors, {loc, msg})
end

local function compile_expr(skeletons)
  assert(#skeletons > 0)


end

return { compile = compile }

