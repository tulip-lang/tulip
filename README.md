# tulip

```
 )`(   )`(   )`(   )`(   )`(   )`(   )`(   )`(   )`(   )`(   )`(   )`(   )`(   )`(   )`(
(   ) (   ) (   ) (   ) (   ) (   ) (   ) (   ) (   ) (   ) (   ) (   ) (   ) (   ) (   )
  |/    |/    |/    |/    |/    |/    |/    |/    |/    |/    |/    |/    |/    |/    |/
```

[coc]: http://tinyurl.com/tulip-conduct "Code of Conduct"
[post]: http://www.jneen.net/posts/2015-07-29-tulip-language-updated "Tulip"

[Tulip is a language!][post]

## Why Tulip?

* Repl-oriented to encourage linear thinking and composition
* Lightweight tagging, pattern-matching, and open methods for easy, clear communication between parts of the runtime
* First-class parameterized modules for simple, easy encapsulation
* Flexible actor-based concurrency model with no shared state (lifted from Erlang, really)
* A diverse core team, and a founder who is not cis, straight, or a man. Also a [real, enforced code of conduct][coc], and a pretty-flower aesthetic.

For more details, please read the blog post linked above.

## Contributing

A language is a very large project, and I need your help!  Especially if you are queer/trans, disabled, a woman, and/or a person of color, and in that case especially if you think you don't know anything about compilers.  I feel a little conflicted asking for this kind of help because I can't pay anyone (nor am I getting paid), so please don't feel guilty at all if you simply don't have the time or energy for it.  But I think it's a super cool project, and it is much more likely to be successful with your help.

Tulip is still very much in design mode, so the architecture is still being decided on.  I hang out with a few others in `#tuliplang` on freenode if you want to see where you can best contribute.  Here are some specific things I'll need help with:

* Design / implementation of the macro definition and parsing system, in lua
* Implementation of modules / imports (pure design plus maybe some C)
* Designing and implementing the vm interpreter / runtime in C (including concurrency)
* Implementation of basic tulip data structures in C - tags, encoded strings, etc
* Writing the compile step, from skeleton trees to bytecode, in lua
* Doc writing - mostly tutorials and intro material for now
  - intro to tagged values, pattern matching
  - how skeleton trees / macros work
  - the process model
* Design of the packaging system
* Implementation of the standard library (in tulip!)
