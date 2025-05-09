from abc import ABC, abstractmethod

from automation_utils.ssh_client.ssh_client import SSHClient
from automation_utils.helpers.deciphers.decipher_base import Decipher

SHOW_COMMAND_PREFIX = "show "


class CliSession(ABC):
    def __init__(self, hostname, username, password, session_conf=None):
        self.ssh = SSHClient(
            hostname=hostname,
            username=username,
            password=password,
            session_conf=session_conf if session_conf else {},
        )
        self._pagination_disabled = False
        import logging


        module_logger = logging.getLogger('paramiko')
        module_logger.handlers = []
        module_logger.propagate = False

    def open_session(self):
        self.ssh.connect_wait_for_prompt(prompt_retries=3)

    @abstractmethod
    def close_session(self):
        """This method will gracefully close the CLI session,
        providing a clear exit message. The method is vendor specific and should be overriden
        """
        pass

    def disconnect(self):
        self.ssh.close()

    @property
    def is_connected(self):
        return self.ssh.is_connected

    @property
    def disable_pagination_cmd(self) -> str:
        return ""

    @property
    def disable_pagination_suffix(self) -> str:
        return ""

    @abstractmethod
    def execute_request_command(self, command: str):
        """This method performs interactive commands that need to be confirmed by the user
        The method is vendor specific and should be overriden
        """
        pass

    @abstractmethod
    def edit_config(
        self,
        candidate,
        replace=False,
        diff=False,
        confirm_timeout=None,
        session_name=None,
        stop_on_error=True,
    ) -> str:
        """
        Loads the candidate configuration into the network device.

        Args:
            candidate: The configuration to load.
            replace: How to handle existing configuration (optional):
            - False: Merge with current configuration.
            - True: Completely replace current configuration.
            diff: Whether to generate a diff of the changes (default: False)
            confirm_timeout: Time (in minutes) before the commit will be automatically rolled back
            session_name: The name for the configuration session (if supported by the device)
            stop_on_error: Whether to proceed or stop and raise exception ot error
        Returns:
            A string with the diff of the changes, in case the diff is True

        Raises:
            UnknownCliException, CommandFailed, SessionClosed, UnexpectedOutput, CommitFailedException
        """
        pass

    def send_command(
        self, command: str, sendonly: bool = False, decipher: Decipher = None
    ):
        """Executes a command over the device connection
        This method will execute a command over the device connection and
        return the results to the caller.
        :param command: The command to send over the connection to the device
        :param sendonly: Bool value that will send the command but not wait for a result.
        :param decipher: Callback method for processing the response

        :returns: The output from the device after executing the command.
                  If decipher is provided, it will return the correspondent data object
        """
        if not command:
            return None

        if (
            not self._pagination_disabled
            and self.disable_pagination_cmd
            and command.startswith(SHOW_COMMAND_PREFIX)
        ):
            self.ssh.execute_shell_command(
                self.disable_pagination_cmd,
                wait_for_answer=True,
                shows_output=True,
            )
            self._pagination_disabled = True

        if self.disable_pagination_suffix and command.startswith(
            SHOW_COMMAND_PREFIX
        ):
            command = f"{command}{self.disable_pagination_suffix}"

        cli_output = self.ssh.execute_shell_command(
            command, wait_for_answer=not sendonly, shows_output=not sendonly
        )
        if decipher:
            return decipher.decipher(cli_output)
        return cli_output

    @abstractmethod
    def confirm_commit(self, session_name=None) -> None:
        """
        Confirm commiting configuration changes (if supported by the device).
        """
        pass

    @abstractmethod
    def rollback(self, index) -> None:
        """
        Rollback configuration to specific index (if supported by the device).
        """
        pass
