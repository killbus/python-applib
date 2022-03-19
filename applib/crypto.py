"""..."""
import subprocess
from typing import List, Union, Tuple, IO
import re
from zlib import crc32
from hashlib import md5, sha1

from .platform import IS_LINUX, IS_MACOS


def _md5_cmd(localpath: str) -> List[str]:
    if IS_MACOS:
        cmd = ["md5", localpath]
    elif IS_LINUX:
        cmd = ["md5sum", localpath]
    else:  # windows
        cmd = ["CertUtil", "-hashfile", localpath, "MD5"]
    return cmd


def calu_file_md5(localpath: str) -> str:
    cp = subprocess.run(
        _md5_cmd(localpath), universal_newlines=True, stdout=subprocess.PIPE
    )

    output = cp.stdout.strip()
    if IS_MACOS:
        return re.split(r"\s+", output)[-1]
    elif IS_LINUX:
        return re.split(r"\s+", output)[0]
    else:  # windows
        cn = output.split("CertUtil")[0].strip()
        cn = cn.split(":")[-1].strip().replace(" ", "")
        return cn


def calu_md5(buf: Union[str, bytes], encoding="utf-8") -> str:
    assert isinstance(buf, (str, bytes))

    if isinstance(buf, str):
        buf = buf.encode(encoding)
    return md5(buf).hexdigest()


def calu_crc32_and_md5(stream: IO, chunk_size: int) -> Tuple[int, str]:
    md5_v = md5()
    crc32_v = 0
    while True:
        buf = stream.read(chunk_size)
        if buf:
            md5_v.update(buf)
            crc32_v = crc32(buf, crc32_v).conjugate()
        else:
            break
    return crc32_v.conjugate() & 0xFFFFFFFF, md5_v.hexdigest()


def _sha1_cmd(localpath: str) -> List[str]:
    if IS_MACOS:
        cmd = ["shasum", localpath]
    elif IS_LINUX:
        cmd = ["sha1sum", localpath]
    else:  # windows
        cmd = ["CertUtil", "-hashfile", localpath, "SHA1"]
    return cmd


def calu_file_sha1(localpath: str) -> str:
    cp = subprocess.run(
        _sha1_cmd(localpath), universal_newlines=True, stdout=subprocess.PIPE
    )

    output = cp.stdout.strip()
    if IS_MACOS:
        return re.split(r"\s+", output)[-1]
    elif IS_LINUX:
        return re.split(r"\s+", output)[0]
    else:  # windows
        cn = output.split("CertUtil")[0].strip()
        cn = cn.split(":")[-1].strip().replace(" ", "")
        return cn

def calu_sha1(buf: Union[str, bytes], encoding="utf-8") -> str:
    assert isinstance(buf, (str, bytes))

    if isinstance(buf, str):
        buf = buf.encode(encoding)
    return sha1(buf).hexdigest()
