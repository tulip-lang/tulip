" Vim syntax file
" Language:     JavaScript
" Maintainer:   Jeanine Adkisson
" URL:          TODO

let ident = "[a-zA-Z_-][\/a-zA-Z0-9_-]*"

"" dash is anywhere in an ident
setlocal iskeyword+=-

syntax sync fromstart

syntax match   tlPunctuation           /\%(:\|,\|\;\|!\|>\|=\|(\|)\|\[\|\]\||\|{\|}\|\~\)/

syn match tlLet /+\s*/ nextgroup=tlFuncName



syn match tlComment /#[^\n]*\n/
exe "syn match tlAnnot /+" . ident . "/"
exe "syn match tlName /" . ident . "/"
exe "syn match tlDotted /[.]" . ident . "/"
exe "syn match tlCheck /[\\%]" . ident . "/"
exe "syn match tlKeyword /[@]" . ident . "/"
exe "syn match tlDynamic /[\\$]" . ident . "/"
exe "syn match tlMacro /\\(\\\\" . ident . "\\)/"
exe "syn match tlFlag /-" . ident . "/"
syn match tlUppercase /[A-Z][a-zA-z0-9_-]*/

syn match tlNumber /\d\+\(\.\d\+\)/

syn match tlBareString /'[^{][^ 	\n)\];]*/
syn region tlString start="'{" end="" contains=tlStringContents
syn region tlStringContents start="{" end="}" contains=tlStringContents contained

syn region tlDQString start='"' end='"' contains=tlUnicode,tlEscape
syn match tlUnicode /\\u[0-9a-f][0-9a-f][0-9a-f][0-9a-f]/ contained
syn match tlEscape /\\[trn0e\\"]/ contained

hi! def link tlName        Name
hi! def link tlUppercase   Type
hi! def link tlDotted      Type
hi! def link tlPunctuation Punctuation
hi! def link tlCheck       Type
hi! def link tlKeyword     Keyword
hi! def link tlMacro       Punctuation
hi! def link tlFlag        Special
hi! def link tlBareString  String
hi! def link tlString      String
hi! def link tlDQString    String
hi! def link tlUnicode SpecialChar
hi! def link tlEscape SpecialChar
hi! def link tlStringContents String
hi! def link tlAnnot       Function
hi! def link tlLet         Punctuation
hi! def link tlDynamic     Identifier
hi! def link tlComment     Comment
hi! def link tlNumber      Number

"
"
"
"
" "foo"
"
"
"
