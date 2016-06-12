local host = {}

host.reader = {}
host.reader.setup = __compiler_reader_setup
host.reader.teardown = __compiler_reader_teardown
host.reader.next = __compiler_reader_next

host.value = {}
host.value.create_tag = __compiler_create_tag
host.value.tag_get = __compiler_tag_get
host.value.matches_tag = __compiler_matches_tag
host.value.inspect_value = __compiler_inspect_value

return host
