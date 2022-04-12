import os
import sys
from typing import List, Tuple, Union
import subprocess
import threading

def preexec_function():
    # Change process group in case we have to kill the subprocess and all of
    # its children later.
    # TODO: this is Unix-specific; would be good to find an OS-agnostic way
    #       to do this in case we wanna port WA to Windows.
    os.setpgrp()


# Popen is not thread safe. If two threads attempt to call it at the same time,
# one may lock up. See https://bugs.python.org/issue12739.
check_output_lock = threading.RLock()


def get_subprocess(command, **kwargs):
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden.')
    with check_output_lock:
        process = subprocess.Popen(command,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   stdin=subprocess.PIPE,
                                   preexec_fn=preexec_function,
                                   **kwargs)
    return process


def check_subprocess_output(process: subprocess.Popen, timeout=None, ignore=None, inputtext=None, decode_output=True) -> Tuple[Union[bytes, str], Union[bytes, str]]:
    output: bytes = None
    error: bytes = None
    # pylint: disable=too-many-branches
    if ignore is None:
        ignore = []
    elif isinstance(ignore, int):
        ignore = [ignore]
    elif not isinstance(ignore, list) and ignore != 'all':
        message = 'Invalid value for ignore parameter: "{}"; must be an int or a list'
        raise ValueError(message.format(ignore))

    try:
        output, error = process.communicate(inputtext, timeout=timeout)
    except subprocess.TimeoutExpired as e:
        timeout_expired = e
    else:
        timeout_expired = None

    # Currently errors=replace is needed as 0x8c throws an error
    if decode_output:
        output = output.decode(sys.stdout.encoding or 'utf-8', "replace") if output else ''
        error = error.decode(sys.stderr.encoding or 'utf-8', "replace") if error else ''

    if timeout_expired:
        raise TimeoutError(process.args, output='\n'.join([output, error]))

    retcode = process.poll()
    if retcode and ignore != 'all' and retcode not in ignore:
        raise subprocess.CalledProcessError(retcode, process.args, output, error)

    return output, error


def check_output(command: List, timeout=None, ignore=None, inputtext=None, decode_output=True, **kwargs):
    """This is a version of subprocess.check_output that adds a timeout parameter to kill
    the subprocess if it does not return within the specified time."""
    process = get_subprocess(command, **kwargs)
    return check_subprocess_output(process, timeout=timeout, ignore=ignore, inputtext=inputtext, decode_output=decode_output)


def which(name):
    """Platform-independent version of UNIX which utility."""
    if os.name == 'nt':
        paths = os.getenv('PATH').split(os.pathsep)
        exts = os.getenv('PATHEXT').split(os.pathsep)
        for path in paths:
            testpath = os.path.join(path, name)
            if os.path.isfile(testpath):
                return testpath
            for ext in exts:
                testpathext = testpath + ext
                if os.path.isfile(testpathext):
                    return testpathext
        return None
    else:  # assume UNIX-like
        try:
            return check_output(['which', name])[0].strip()  # pylint: disable=E1103
        except subprocess.CalledProcessError:
            return None
