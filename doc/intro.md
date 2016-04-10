#Tulip, an Untyped Functional Language Which is Going to Be Pretty Cool

[variants-talk]: https://www.youtube.com/watch?v=ZQkIWWTygio "Variants Are Not Unions"

```
 )`(
(   ) .tulip
  |/
```

This language is gonna rock, I'm really excited about it.  An older version of this document originally appeared on `jneen.net`, and has been moved here and edited so we can keep it up to date more easily.

So here's tulip!

## Design goals

Tulip is designed to sit in the intersection of repl tools (bash, zsh, ex, etc) and scripting languages.  It's intended to scale both *down* to small things typed at a repl, and *up* to large-ish programs, to the extent you'd want to build with ruby, python, clojure, etc.

It's an interpreted, impure, dynamic functional language, but for the most part it enables the user to behave as if they were in a pure language with a Hindley-Milner type-checker. Open variants (called "tagwords"), paired with patterns and open methods, are the central strategy to manage polymorphism.

Importantly, tulip aims to be obvious and easy to explain.  You should not need to study PLT to understand the core concepts of tulip.  To that end, we try to avoid jargon and unclear language.

Finally, tulip is a language full of flowers and rainbows and unicorns, with a deliberately diverse team and a strictly enforced [code of conduct](http://tinyurl.com/tulip-conduct). If that's a problem you can maybe find another language.

## Basic syntax

Variables are `kebab-case` identifiers, comments are from `#` to the end of the line, and values are assigned to variables with `my-variable = my-value`.  Indentation is not semantic (as that's not a repl-friendly feature), and newlines and semicolons (`;`) are syntactically equivalent.  All user and library functions are identifiers, and all symbols are reserved for the language.  There are no identifier keywords - all special directives will be prefixed with `@` (see `@method` and `@impl` below, for example).

## Chaining and Auto-Curry

For ergonomic purposes on a repl, it is critical to support typing small but powerful programs *linearly* - from left to right.  Prefix function calls usually require seeking left every time you want to use the result of an expression.  This gets very tedious very quickly.  Tulip has two features that combine to make this easy.

The first is auto-currying.  Users of Haskell or ML will find this familiar.  If a function is called with fewer than its expected number of arguments, it returns a function expecting the rest of the arguments.  For example,

``` tulip
(add 5) 3
```

calls the function `(add 5)` on the value 3, and returns 8.  Luckily the precedence works out such that you can just type `add 5 3` in this case and get on with your day.

The second is one of two infix operators in the language: `>`, pronounced "into", "reverse-apply", or simply "then".  This operator expects a value on the left and a function on the right, and simply applies the function to the value.  So the example above could be rewritten as:

``` tulip
3 > add 5
```

Proper standard library design here is critical.  Functions to be used on the repl must be written to take their chained argument last, or else typing becomes much more difficult.  In the case that you are using a function in a way the author didn't expect, there's a sibling symbol to `>`, which is the special variable `-`.  If a segment in a `>`-chain contains `-`, the chained argument is placed there instead.  For example,

``` tulip
foo > bar - baz
```

is equivalent to `bar foo baz`.  Alternately, you can bind a variable to a name for later within a chain:

``` tulip
foo > x => bar > baz > add x
```

## Tagwords, Tuples

Tagwords are the basic building block of all tulip's user-space data structures.  Syntactically, a tagword is simply an identifier sigiled with a `.`, as in `.foo`.  When a tagword is called as a function, it creates a **tagged value**.  When a tagged value is called as a function, it appends the data to its internal list.  Let's look at an example:

``` tulip
.foo # => .foo
.foo 1 # => .foo 1
.foo 1 2 # => .foo 1 2
```

In simple terms, they construct values.  Some examples of tagwords that will be commonly used in the standard library are:

``` tulip
# booleans
.t
.f

# lists
.cons 1 (.cons 2 (.cons 3 .nil))

# result
.ok value
.err message

# option
.some value
.none
```

For a more detailed explanation of this pattern, see [my talk at clojure conj 2014][variants-talk]

A **tuple** is multiple expressions joined with `,`, as in `foo bar > baz, zot`.  The comma has lower precedence than `>`, so often tuples are surrounded by parentheses: `foo (bar, baz > zot)`.  Tuples are represented with the `.tuple` tag, and are right-nesting, so that:

```
(.x, .y, .z) # => .tuple x (.tuple .y .z)
((.x, .y), .z) # => .tuple (.tuple .x .y) .z
```

This allows for open methods (see below) to be defined for arbitrary lengths of tuples.

## Lambdas and patterns

It's expected that lambdas will be a common thing to type on the repl, so the syntax has been kept very lightweight.  A basic lambda looks like this:

``` tulip
[ foo => some-expr-in foo ]
```

where the variable `foo` is bound inside the block.  Nested blocks have the usual properties of closures.

Things get a little more interesting with destructuring.  Rather than being a simple variable binder (`foo` above), the binder can also match and destructure tagged values over multiple clauses:

``` tulip
map f = [ .nil => .nil; .cons x xs => .cons (f x) (map f xs) ]
```

The `:` symbol matches and binds multiple patterns over the same value.  Patterns can also include named pattern or type checks (sigiled with `%`).

``` tulip
add = [ (x : %uint) (y : %uint) => add-uint x y ]
map (f:%callable) = ...
foo (bar : .bar _ _) = ...
```

All the native types will have `%`-sigiled type names, and there will be a way to implement your own named checks, which is still in design.

Patterns also have predicates on any part of the match that can use bound names from sub-matches:

``` tulip
[ .foo (x ? gt 4 -) => ...; .foo x ? is-even x => ... ]
```

Blocks can be used with `>` to destructure arguments.  For example, here is tulip's equivalent of an `if` expression:

``` tulip
condition > [ .t => true-value; .f => false-value ]
```

The special pattern `_` acts as usual - it matches any value and binds no results.  A simple guard pattern can be implemented as

``` tulip
[ _? cond-1 => val-1; _? cond-2 => val-2 ]
```

Naming all the variables and typing `=>` every time can be a pain on the repl, so for simple blocks tulip provides a feature called **autoblocks** and the **autovar**.  Autoblocks are also delimited by square brackets, but contain no pattern and only a single clause.  The autovar, denoted `$`, is the argument to the closest-nested autoblock:

``` tulip
list > map [ some-fn $ arg ]
```

Future plans may also include support for `$1`, `$2`, etc.

## Literals and Macros

I strongly dislike macros that can hide in code.  I get really frustrated when I open a source file and see `(foo ...)` and can't tell whether it's a function or a macro until I read documentation.  For these reasons, extensible literals and macros in tulip are all sigiled with `/`.  Here is a basic macro: the list constructor:

``` tulip
/list[1; 2; 3]
```

The implementation syntax for these is still in design phase, but they will take after rust in that they will pattern-match against syntax, and result in new syntax.  I expect `list` to be so common that for that special case it is permitted to leave off the macro name: `/[1; 2; 3]` is equivalent.

Strings are delimited with `'{...}`, which balances curly braces and respects `\{` and `\}`.  But since many string literals are much simpler, you can also use `'` as a one-sided delimiter that scans to whitespace or one of the delimiters `]`, `)`, or `>`.  Here are some examples:

``` tulip
'{foo} # => the string {foo}
'foo # => the string {foo}
```

For interpolation, use `"{...}` with `$(...)`:

``` tulip
"{a string with $(some-expression) interpolated}
```

## Let, recursion, laziness

Tulip is not a lazy language (mostly).  If you want a lazy expression, simply prefix it with `~`.  Evaluation of lazy expressions is deferred until a pattern-match needs the value.  A non-pattern-matching function called with a lazy value results in a further lazy value.

To bind variables in an ad-hoc way, open a **block scope** with `{}`:

``` tulip
foo = {
  bar = 1

  # defines a local function
  baz zot = 2

  quux
}
```

Variables defined in this way are called **let-bound**, as opposed to **argument-bound**.  Let-bound function arguments can pattern match in the same way as lambda arguments.  Multiple definitions of the same function in a sequence of bindings behaves the same as multiple clauses in a lambda.

Tulip supports **let-recursion**: a variable bound in a let-expression (`name = value`) can use itself in its definition.  A sequence of let-expressions can also refer to each other recursively.  This generally works fine when the values defined are all functions, but it can break down when the values use recursive references strictly:

``` tulip
# the lazy y-combinator (.o_o).
fix f = { x = f x; x }
```

In this case, tulip will detect the recursion, and the `f x` will be automatically wrapped with a lazy operator (`~`). Any reference loop in a sequence of lets will be closed by converting the last link to a lazy reference.  This makes it simple to create graph-like structures.

Tail call optimization is supported and tail recursion encouraged.

Definitions that begin with `>` are desugared as follows:

``` tulip
foo = > bar > baz

# equivalent to
foo x = x > bar > baz
```

## Flags, Optional Arguments, Maps

Flags are identifiers that begin with `-`.  A flag-pair is a flag followed immediately (no space) by an `:` and an expression.  When a flag-pair is called with another flag-pair argument, it merges that pair into its internal record.  For example,

``` tulip
-foo: 1 # => (-foo:1)
-foo: 1 -bar: 2 # => (-foo:1 -bar:2)
```

Flags are used for keyword arguments.  Given a function defined as:

``` tulip
foo -bar: x -baz: y = ...
```

it can be called as:

``` tulip
foo -baz: 3 -bar: 2
```

Splats for keyword arguments are still in design phase, as are optional arguments and boolean flags. The latter will automatically be converted to `.some`/`.none` or `.t`/`.f`.

I should be note here that flags - in particular optional arguments - are **complex**, especially when paired with auto-currying.  But they are a critical tool for implementing repl interfaces.  So they are supported, but are generally discouraged unless you are exporting a function to be used on a repl.

## Methods, Protocols, Implementations

A common problem in general-purpose languages is to define an interface that can be implemented by users later.  This is the purpose of, for example, `defprotocol` and multimethods in clojure, most good uses of interfaces in java, and typeclasses in Haskell.  A method declaration in tulip looks like this:

``` tulip
@method map _ %
```

This is read as: `map` is a method that takes two arguments, and dispatches on the second argument.  Some implementations of this method might look like:

``` tulip
@impl map f (.cons x xs) = .cons (f x) (map f xs)
@impl map f .nil = .nil
@impl map f (.some x) = .some (f x)
@impl map _ .none = .none
@impl map f (.ok x) = .ok (f x)
@impl map f (.err e) = .err e
```

In implementation definitions, only the dispatched argument can be pattern-matched, and only simple tag destructures, native type checks, and default (`_`) are allowed.  Open recursion, hower is both allowed and encouraged.  Multiple dispatch is also planned, but not yet designed.

## Side Effects, Zero Arguments, Multiple Expressions

Tulip is an *impure* language - functions are allowed to have *side effects* - i.e. change the state of the world in some way other than the arguments passed to it.

If you want to execute a function just for its side effects and return a different value, you may use a block:

``` tulip
{ do-thing arg1; actual-value }
```

You can chain together as many calls here as you like.  If you want to define a function that takes no arguments, you can use the special parameter `!`:

``` tulip
# a zero-argument definition
do-all-things! = {
  do-thing-1 arg-1
  do-thing-2 arg-2
  .ok
}

# a zero-argument call
do-all-things!

# a zero-argument lambda clause
[ ! => ... ]
```

Often, for lambdas whose primary purpose is side effects, you will want to simply evaluate multiple expressions without an extra layer of nesting.  For this, tulip supports **block-lambda sugar**:

``` tulip
# a block-lambda
{ x => foo x; bar x }

# equivalent to...
[ x => { foo x; bar x }]

# a zero-argument block-lambda
{ ! => do-a-thing! ; do-another-thing! }
```

## Concurrency

Tulip's data structures are *immutable*.  Under the hood, there are only 4 side-effecting operations: `spawn`, `send`, `receive`, and ffi calls.

The `spawn` function takes a zero-argument function and spawns an erlang-style actor with a message queue and a backup queue, and returns a handle to the process.  The `receive` function takes a single-argument function and blocks until the queue contains a matching message.  An optional `-timeout: (seconds, action)` flag can be passed, which will run the zero-argument function `action` if `timeout` seconds pass without a matching message.  The `send` function takes a process handle and a message, and sends the message to the process.

## Modules, Objects, Importing

A module is a collection of definitions, usually living in a file.  A file can either be a script or export multiple modules.

A module is declared as follows:

``` tulip
@module my-module-name [
  foo = 1
  bar = 2
]

my-module-name/foo # => 1
```

Any name ending with `-` is considered private and will not be re-exported.  Tagwords whose names start with two dots (as in `..foo`) are namespaced to the module - pattern matches in other modules against those tagwords will need to use `.my-module-name/foo` to pattern-match.

For the root module of a file, the square brackets can be omitted.  A module is imported into another module with the `@import` directive:

``` tulip
@module my-module

@import another-module
@import yet-another-module
```

A module with parameters is called an **object**:

``` tulip
@object Point x y [
  magnitude = /[x; y] > map square > sum > sqrt
  move dx dy = Point (add x dx) (add y dy)
]

center = Point 0 0 # => *<Point 0 0>
center/x # => 0
center/move 2 3 # => *<Point 2 3>
```

The arguments act as if every member was a function with those arguments curried in.  Here, `Point` is an **object constructor** and `center` is an **object instance**.

## Coming Soon

Features coming soon include:

* dynamic variables sigiled with `$`
* custom binding behavior with infix `|`
* infixing user functions with <code>\`foo</code>
* an ffi system to RPython and C
* macro definition syntax
* custom `@annotations`, special defs

## Putting it all together

Tulip is not a small language.  My goal was to include enough features to be useful, add extensibility in the right places, but also guarantee a consistent look with predictable behaviors.  Tulip is still in active development, and I could use a whole lot of help, both filling in the design gaps here and actually churning out the implementation.  Please ping me on twitter (`@jneen_`) with any feedback or if you want to get involved!

Still interested?  Follow `@tuliplang` on Twitter for more updates, and come join us in `#tulip` on the [snek slack](http://snek.translunar.space/).

If you're queer/trans, a person of color, and/or a woman, we'd love for you to join the very small team working on this.  We currently need help with:

  * VM implementation (in RPython)
  * spec writing
  * example writing
  * the frontend implementation (parsing, etc)
  * test infrastructure
  * standard library design.

<3 <3 <3

--Jeanine
