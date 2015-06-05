# parsing notation

`  |  ` denotes a choice between terms

`[...]` denotes a grouping, where all items must be satisfied in the order specified
- normally bnf implies grouping but i prefer not to

`(...)` denotes an optional term, which does not need to be satisfied

many is satisfied by multiple occurrences of a term
- `(many ...)` denotes 0 or more occurrences
- `[many ...]` denotes 1 or more occurrences

# direct translation
atom          := name | number | paren | lam | tag | autovar

apply         := [many atom]

chain         := [apply (many [`>` apply])]

expr          := [(many definition) chain]

definition    := [name (many pattern) `=` expr]

pattern       := var_pattern | tag_pattern | named_pattern | paren_pattern

paren_pattern := [`(` pattern `)`]

var_pattern   := name

tag_pattern   := [tag (many pattern)]

named_pattern := [`%` name]

name           := utf-8 except whitespace

number        := floating point literal (no spec for exponents)

paren         := [`(` expr `)`]

autovar       := [`$` name]

tag           := [`.` name]

lam_start     := `[`

lam_clause    := [pattern `=>` expr]

lam_end       := [(many lam_clause) `]`]

autolam_end   := [expr `]`]

lam           := [lam_start [lam_end | autolam_end]]
