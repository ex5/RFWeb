import os
import string

class error(Exception):
    """Base class for exceptions in scheduler."""
    def __init__(self, message=None):
        self.message = message
    def __str__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.message)
    def complete_message(self):
        if self.message:
            return "%s: %s" % (self.ExceptionShortDescription, self.message)
        else:
            return "%s" % self.ExceptionShortDescription
    ExceptionShortDescription = "scheduler generic exception"

class ExecutableNotFound(error):
    """Exception raised when executable can't be found."""
    ExceptionShortDescription = "Executable not found"

class SchedulerSystemError(error):
    """Exception raised when scheduler cannot perform a "system \
operation" (e.g., a system call) that should work in "normal" situations.

    This is a convenience exception: schedulerIOError, schedulerOSError
    and schedulerErrorBeforeExecInChildProcess all derive from this
    exception. As a consequence, watching for schedulerSystemError instead
    of the aformentioned exceptions is enough if you don't need precise
    details about these kinds of errors.

    Don't confuse this exception with Python's builtin SystemError
    exception.

    """
    ExceptionShortDescription = "System error"

class SchedulerOSError(SchedulerSystemError):
    """Exception raised when pythondialog catches an OSError exception that \
should be passed to the calling program."""
    ExceptionShortDescription = "OS error"

def _find_in_path(prog_name):
    """Search an executable in the PATH.

    If PATH is not defined, the default path ":/bin:/usr/bin" is
    used.

    Return a path to the file or None if no readable and executable
    file is found.

    Notable exception: PythonDialogOSError

    """
    try:
        # Note that the leading empty component in the default value for PATH
        # could lead to the returned path not being absolute.
        PATH = os.getenv("PATH", ":/bin:/usr/bin") # see the execvp(3) man page
        for dir in string.split(PATH, ":"):
            file_path = os.path.join(dir, prog_name)
            if os.path.isfile(file_path) \
               and os.access(file_path, os.R_OK | os.X_OK):
                return file_path
        return None
    except os.error, v:
        raise PythonDialogOSError(v.strerror)

def _path_to_executable(f):
    """Find a path to an executable.

    Find a path to an executable, using the same rules as the POSIX
    exec*p functions (see execvp(3) for instance).

    If `f' contains a '/', it is assumed to be a path and is simply
    checked for read and write permissions; otherwise, it is looked
    for according to the contents of the PATH environment variable,
    which defaults to ":/bin:/usr/bin" if unset.

    The returned path is not necessarily absolute.

    Notable exceptions:

        ExecutableNotFound
        SchedulerOSError
        
    """
    try:
        if '/' in f:
            if os.path.isfile(f) and \
                   os.access(f, os.R_OK | os.X_OK):
                res = f
            else:
                raise ExecutableNotFound("%s cannot be read and executed" % f)
        else:
            res = _find_in_path(f)
            if res is None:
                raise ExecutableNotFound(
                    "can't find the executable for the dialog-like "
                    "program")
    except os.error, v:
        raise SchedulerOSError(v.strerror)

    return res

