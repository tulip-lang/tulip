function bind(tbl, fn)
  local saves = {}

  for k,v in ipairs(tbl) do
    saves[k] = _G[k]
    _G[k] = v
  end

  local status, ret = pcall(fn)

  for k,v in ipairs(saves) do
    _G[k] = saves[k]
  end

  if status then return ret else error(ret) end
end
