"""..."""
import pprint
from urllib.parse import unquote

def format(_obj, context, maxlevels, level):
    if isinstance(_obj, bytes):
#-#        return (repr(_obj.encode('utf8')) or "''", False, False)
        return (("'" + _obj.decode('utf8') + "'") or "''", False, False)
    if isinstance(_obj, str):
        if unquote(_obj) == _obj:
            return (repr(_obj) or "''", False, False)
        else:
#-#            return (repr(unquote(_obj).decode('unicode-escape').encode('utf8')) or "''", False, False)
#-#            return (("'" + unquote(_obj).decode('unicode-escape').encode('utf8') + "'") or "''", False, False)
            return (("'" + unquote(_obj) + "'") or "''", False, False)
    return pprint._safe_repr(_obj, context, maxlevels, level, True)
pp = pprint.PrettyPrinter(width=160)
pp.format = format
pcformat = pp.pformat