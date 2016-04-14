## Tulip code server

The tulip code server, available via an api in the dynamic variable `$code`, is the process that manages live updates of code.

When a tulip process is booted, all of the `@import` directives (in scripts) or dependencies (in packages) are resolved statically, and exactly one version of each module is loaded into the runtime.  When the compilation code needs to look up an import or other dependency, it grabs the current version from `$code`.  In normal runtime behavior, `$code` is not consulted at all.  However, processes are allowed to dynamically update and register code with `$code`.  Consider the following example:

``` tulip
# module foo
server-loop state = receive [
  ... => { ...; server-loop new-state }
  .refresh-code => $code/refresh 'foo/server-loop state
]

# thread 2
new-module = compile-code /q[...]
$code/register 'foo new-module
some-server > send .refresh-code
```

The original server is running in a tail-called loop.  The `server-loop` function is looked up once at compile, time, and never again.  So when thread 2 recompiles the `foo` module and registers it with `$code`, the original loop does not see it - it's looking up the tail-call directly from its closure.  However, when the `.refresh-code` message is sent, the server loop tail-calls into a *different* function - the one returned by `$code/refresh 'foo/server-loop`, which has the new version of the module in its closure.

