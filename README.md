# tulip

```
 )`(
(   )
  |/
```

Tulip is a language! [Here is a slightly out-of-date description of it](http://www.jneen.net/posts/2015-03-01-tulip-language).

## Contributing

A language is a very large project, and I need your help!  Especially if you are queer/trans, a woman, and/or a person of color, and in that case especially if you think you don't know anything about compilers.  I feel a little conflicted asking for this kind of help because I can't pay anyone (nor am I getting paid), so please don't feel guilty at all if you simply don't have the time or energy for it.  But I think it's a super cool project, and it is much more likely to be successful with your help.

Tulip is still very much in design mode, so the architecture is still being decided on.  I hang out with a few others in `#tuliplang` on freenode if you want to see where you can best contribute.  Here are some specific things I'll need help with:

* Design of the macro definition and parsing system
* Implementation of modules / imports
* Fleshing out the parser (parser.py)
* Designing and implementing the vm interpreter / runtime (including concurrency)
* Writing the compile step (syntax -> bytecode)
* Doc writing (there's a blog post to be written about the changes to the language since the last post)
* Design of the packaging system
* Implementation of the standard library (in tulip!)

Here's a general sketch of the architecture:

* Parsing is three steps:
  - A hand-written lexer in `lexer.py` (an object with setup/next/teardown methods)
  - Pre-baked simple parse which leaves macros unparsed (`parser.py` and `parser_gen.py`)
  - Macro parsing, which might use the pre-baked parser to consume expressions, etc

* From parsing, a `Syntax` object is created.  These will have `.compile(ctx)` methods, which accept a CompileContext object to which instructions and constants are pushed.
* A compile context can render its bytecode to a Bytecode object, which can be used to create Function objects, etc.
* The VM interpreter will be able to interpret Bytecode objects given appropriate links to arguments and a closure.

* A lot of functionality will be implemented by NativeFunction objects, which will be implemented in rpython and can use the FFI.
