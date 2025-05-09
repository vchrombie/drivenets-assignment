from automation_utils.cli.cli_session import CliSession
from automation_utils.common.exceptions import (
    CommandFailed,
    SessionClosed,
    UnexpectedOutput,
    UnknownCliException,
    CommitFailedException,
)

import orbital.common as common

QUIT_KEYWORD = "quit"
EXIT_KEYWORD = "exit"
TOP_KEYWORD = "top"
CONFIGURE_KEYWORD = "configure"
DISCARD_CANDIDATE = "rollback 0"
COMMIT_KEYWORD = "commit"
COMMIT_CONFIRM_KEYWORD = "commit confirm"
COMMIT_AND_EXIT_KEYWORD = "commit and-exit"
DIFF_COMMAND = "show config compare rollback 0 rollback 1"
COMMIT_SUCCEEDED = "Commit succeeded"
COMMIT_CONFIRMED = "Commit confirmed"
ROLLBACK_COMPLETE = "rollback complete"
LOAD_OVERRIDE_COMMAND = "load override factory-default"
ROLLBACK_KEYWORD = "rollback"


logger = common.get_logger(__file__)


class CliDnos(CliSession):
    def __init__(self, hostname, username, password):
        super().__init__(hostname, username, password)

    @property
    def disable_pagination_suffix(self) -> str:
        return "|no-more"

    def close_session(self):
        try:
            if self.is_connected:
                self.ssh.execute_shell_command(
                    QUIT_KEYWORD, wait_for_answer=False, reconnect=False
                )
        except (CommandFailed, OSError, SessionClosed):
            pass
        finally:
            self.ssh.close()

    def edit_config(
        self,
        candidate,
        replace=False,
        diff=False,
        confirm_timeout=None,
        stop_on_error=True,
    ) -> str:
        changes = None

        try:
            self.ssh.execute_shell_command(
                CONFIGURE_KEYWORD, shows_output=False
            )
        except (CommandFailed, UnexpectedOutput) as ex:
            logger.error(f"Failed to enter configure mode: {ex}")
            raise ex

        if replace:
            try:
                self.ssh.execute_shell_command(
                    LOAD_OVERRIDE_COMMAND, shows_output=False
                )
            except (CommandFailed, UnexpectedOutput) as ex:
                logger.error(f"Failed to override factory defaults: {ex}")
                raise ex

        for command in candidate.split("\n"):
            cmd = command.strip()
            if not cmd:
                continue
            logger.debug(f"Executing command: {cmd}")
            try:
                self.ssh.execute_shell_command(cmd, shows_output=False)
            except (CommandFailed, UnexpectedOutput) as ex:
                logger.exception(ex)
                if not stop_on_error:
                    continue
                logger.warning(
                    "An error occurred while applying the configuration. The candidate will be disregarded"
                )
                self.ssh.execute_shell_command(
                    DISCARD_CANDIDATE, shows_output=False
                )
                raise ex

        try:
            commit_cmd = COMMIT_AND_EXIT_KEYWORD
            if confirm_timeout:
                commit_cmd = f"{COMMIT_CONFIRM_KEYWORD} {confirm_timeout}"
            logger.debug(f"Executing '{commit_cmd}'...")
            res = self.ssh.execute_shell_command(commit_cmd, shows_output=True)
            if COMMIT_SUCCEEDED not in res:
                logger.error(f"Commit failed: {res}")
                logger.debug("Trying to discard changes...")
                self.ssh.execute_shell_command(
                    DISCARD_CANDIDATE, shows_output=False
                )
                raise CommitFailedException(res)
            logger.debug("COMMIT succeeded")
            if diff:
                changes = self.ssh.execute_shell_command(
                    DIFF_COMMAND, shows_output=True
                )
        except (CommandFailed, UnexpectedOutput) as ex:
            logger.error(
                f"An error occurred while applying configuration: {ex}"
            )
            raise ex
        return changes

    def execute_request_command(self, command: str):
        self.ssh.execute_shell_command(
            command, match="(yes/no) [no]?", shows_output=False
        )
        self.ssh.execute_shell_command("yes")

    def confirm_commit(self, session_name=None) -> None:
        try:
            logger.debug("Entering configure mode...")
            self.ssh.execute_shell_command(
                CONFIGURE_KEYWORD, shows_output=False
            )
            logger.debug(f"Executing '{COMMIT_AND_EXIT_KEYWORD}'...")
            res = self.ssh.execute_shell_command(
                COMMIT_AND_EXIT_KEYWORD, shows_output=True
            )
            if COMMIT_SUCCEEDED not in res and COMMIT_CONFIRMED not in res:
                logger.error(f"Commit failed: {res}")
                raise CommitFailedException(res)
        except (CommandFailed, UnexpectedOutput) as ex:
            logger.exception(ex)
            raise ex

    def _commit(self) -> None:
        try:
            logger.debug(f"Executing '{COMMIT_AND_EXIT_KEYWORD}'...")
            res = self.ssh.execute_shell_command(
                COMMIT_AND_EXIT_KEYWORD, shows_output=True
            )
            if COMMIT_SUCCEEDED not in res:
                logger.error(f"Commit failed: {res}")
                raise CommitFailedException(res)
        except (CommandFailed, UnexpectedOutput) as ex:
            logger.exception(ex)
            raise ex

    def rollback(self, index) -> None:
        try:
            self.ssh.execute_shell_command(
                CONFIGURE_KEYWORD, shows_output=False
            )
            cmd = f"{ROLLBACK_KEYWORD} {index}"
            logger.debug(f"Executing '{cmd}'...")
            res = self.ssh.execute_shell_command(cmd, shows_output=True)
            if ROLLBACK_COMPLETE not in res:
                logger.error(f"Rollback failed: {res}")
                raise UnknownCliException(res)
        except (CommandFailed, UnexpectedOutput) as ex:
            logger.exception(ex)
            raise ex
        self._commit()
