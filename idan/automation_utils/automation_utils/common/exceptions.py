# noinspection PyUnresolvedReferences
from scp import SCPException
from paramiko import SSHException as se


class UnknownCliException(Exception):
    pass


class CommitFailedException(Exception):
    pass


class OrbitalTemplateException(Exception):
    pass


class TopologyException(Exception):
    pass


FileExceptions = (FileNotFoundError, PermissionError, OSError)

# - SSHException
# |
# |-- CommandFailed
#    |-- ExecutionTimeout
#    |-- ExecutionFailed
#    |-- UnexpectedOutput
# |-- ConnectionFail
#    |-- BadCredentials
#    |-- PromptException
# |-- SessionClosed
# - SCPException


class MainException(AssertionError):
    pass


class SigKillTimeout(TimeoutError):
    """
    thrown when 'wait' decorator is killing a process with SIGKILL
    """

    def __init__(
        self, value="Timed Out"
    ):  # init required by the parent 'wait'
        self.value = value

    def __str__(self):
        return repr(self.value)


class RetryException(MainException):
    pass


class SSHException(MainException, se):
    pass


class CommandFailed(SSHException):
    pass


class ExecutionTimeout(CommandFailed):
    def __init__(self, msg, output=None):
        self.message = msg
        self.output = output


class ExecutionFailed(CommandFailed):
    pass


class UnexpectedOutput(CommandFailed):
    pass


class ConnectionFail(SSHException):
    pass


class BadCredentials(ConnectionFail):
    pass


class PromptException(ConnectionFail):
    """for prompt failures, such as endless 'CLI LOADING'"""


class SessionClosed(SSHException):
    pass


class OperationNotSupported(Exception):
    pass
