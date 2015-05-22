" Vim syntax file
" Language:     JavaScript
" Maintainer:   Jeanine Adkisson
" URL:          TODO

let ident = "[a-zA-Z_-][a-zA-Z0-9_-]*"

"" dash is anywhere in an ident
setlocal iskeyword+=-

syntax sync fromstart

syntax match   tlPunctuation           /\%(:\|,\|\;\|!\|>\|=\|(\|)\|\[\|\]\||\)/

syn match tlLet /+\s*/ nextgroup=tlFuncName



syn match tlComment /#[^\n]*\n/
exe "syn match tlFuncName /" . ident . "/ contained"
exe "syn match tlName /" . ident . "/"
exe "syn match tlDotted /[.]" . ident . "/"
exe "syn match tlCheck /[\\%]" . ident . "/"
exe "syn match tlKeyword /[@]" . ident . "/"
exe "syn match tlMacro /\\(\\/" . ident . "\\)/"
exe "syn match tlFlag /-" . ident . "/"

syn match tlBareString /'[^{]\S*/
syn region tlString start="'{" end="" contains=tlStringContents
syn region tlStringContents start="{" end="}" contains=tlStringContents contained

hi! def link tlName        Name
hi! def link tlDotted      Type
hi! def link tlPunctuation Punctuation
hi! def link tlCheck       Type
hi! def link tlKeyword     Keyword
hi! def link tlMacro       Punctuation
hi! def link tlFlag        Special
hi! def link tlBareString  String
hi! def link tlString      String
hi! def link tlStringContents String
hi! def link tlFuncName    Function
hi! def link tlLet         Punctuation
hi! def link tlComment     Comment
