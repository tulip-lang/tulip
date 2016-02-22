local dyn = {}

dyn.bind = function (tbl, fn)
  local saves = {}

  for k,v in ipairs(tbl) do
    saves[k] = dyn[k]
    dyn[k] = v
  end

  local status, ret = pcall(fn)

  for k,v in ipairs(saves) do
    dyn[k] = saves[k]
  end

  if status then return ret else error(ret) end
end

return dyn
