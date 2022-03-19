"""..."""
import os
from io import BytesIO, UnsupportedOperation
from typing import Union, Any
from pathlib import Path, PosixPath
import shutil
    

def total_len(o: Any) -> int:
    """Read obj len"""

    if hasattr(o, "__len__"):
        return len(o)

    if hasattr(o, "seekable"):
        if o.seekable():
            _offset = o.tell()
            _len = o.seek(0, 2)
            o.seek(_offset, 0)
            return _len

    if hasattr(o, "len"):
        return o.len

    if hasattr(o, "fileno"):
        try:
            fileno = o.fileno()
        except UnsupportedOperation:
            pass
        else:
            return os.fstat(fileno).st_size

    if hasattr(o, "getvalue"):
        # e.g. BytesIO, cStringIO.StringIO
        return len(o.getvalue())

    raise TypeError("Unsupported Operation: no method to get len")


def clean_files(*args):
    """Bulk delete files"""
    for item in args:
        if not isinstance(item, (str, Path, PosixPath)):
            continue

        item = Path(item)
        if item == Path('./'):
            continue

        if item.is_dir():
            shutil.rmtree(item)

        elif item.is_file():
            item.unlink()


if __name__ == '__main__':
    """..."""