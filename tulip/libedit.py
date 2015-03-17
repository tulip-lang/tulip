import py

from rpython.rlib.runicode import str_decode_utf_8, unicode_encode_utf_8

from rpython.rtyper.lltypesystem import lltype, rffi
from rpython.translator import cdir
from rpython.translator.tool.cbuild import ExternalCompilationInfo

# ____________________________________________________________

srcdir = py.path.local(cdir) / 'src'
compilation_info = ExternalCompilationInfo(
        includes=['editline/readline.h'],
        libraries=["edit"])

def llexternal(*args, **kwargs):
    return rffi.llexternal(*args, compilation_info=compilation_info, **kwargs)

__readline = llexternal('readline', [rffi.CCHARP], rffi.CCHARP)

def readline(prompt):
    result = __readline(rffi.str2charp(prompt))
    if result == lltype.nullptr(rffi.CCHARP.TO):
        raise EOFError
    else:
        return unicode_from_utf8(rffi.charp2str(result))

def unicode_to_utf8(s):
    """Converts a `unicode` value to a UTF8 encoded `str` value."""
    return unicode_encode_utf_8(s, len(s), 'strict')

def unicode_from_utf8(s):
    """Converts a `str` value to a `unicode` value assuming it's encoded in UTF8."""
    res, _ = str_decode_utf_8(s, len(s), 'strict')
    return res
