au BufNewFile,BufRead *.tlp setf tulip

fun! s:SelectJavascript()
  if getline(1) =~# '^#!.*/bin/env\s\+tulip\>'
    set ft=tulip
  endif
endfun

au BufNewFile,BufRead * call s:SelectTulip()
