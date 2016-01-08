string_reader = function(input)
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
    return 'input string <' .. input .. '>'
  end

  return {
    setup = setup,
    next = next,
    teardown = teardown,
    input_name = input_name
  }
end

return {
  string_reader = string_reader
}
