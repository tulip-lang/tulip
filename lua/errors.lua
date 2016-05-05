Stubs = require('lua/stubs')

local state = {}

function error_scope(fn)
  local errors = {}
  local orig_errors = state.errors
  state.errors = errors
  local out = fn()
  state.errors = orig_errors

  return errors, out
end

function error(error_tag, ...)
  error_obj = Stubs.tag(error_tag, ...)
  table.insert(state.errors, error_obj)
  return error_obj
end

return {
  error_scope = error_scope,
  error = error,
}
