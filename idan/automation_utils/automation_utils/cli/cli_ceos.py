import time

from automation_utils.cli.cli_session import CliSession
from automation_utils.common.exceptions import (
    CommandFailed,
    SessionClosed,
    UnexpectedOutput,
    OperationNotSupported,
)

import orbital.common as common

CONFIG_SESSION_PREFIX = "auto_test"
QUIT_KEYWORD = "quit"
EXIT_KEYWORD = "exit"
CONFIGURE_SESSION_KEYWORD = "configure session %s"
DISCARD_CANDIDATE = "abort"
COMMIT_KEYWORD = "commit"
COMMIT_CONFIRM_KEYWORD = "commit timer %s"
DIFF_COMMAND = "show session-config diffs"
LOAD_OVERRIDE_COMMAND = "rollback clean-config"
DISABLE_PAGINATION_KEYWORD = "terminal length 0"
BANNER_KEYWORD = "banner login"
EOF_KEYWORD = "EOF"


logger = common.get_logger(__file__)


class CliCeos(CliSession):
    def __init__(self, hostname, username, password):
        super().__init__(hostname, username, password)

    @property
    def disable_pagination_cmd(self) -> str:
        return DISABLE_PAGINATION_KEYWORD

    @staticmethod
    def _format_minutes_to_hhmmss(minutes):
        hours, minutes = divmod(minutes, 60)
        seconds = minutes * 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

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
        session_name=None,
        stop_on_error=True,
    ) -> str:
        changes = None

        if not session_name:
            session_name = "%s_%d" % (CONFIG_SESSION_PREFIX, time.time() * 100)
        try:
            self.ssh.execute_shell_command(
                CONFIGURE_SESSION_KEYWORD % session_name, shows_output=False
            )
        except (CommandFailed, UnexpectedOutput) as ex:
            logger.error(f"Failed to open configuration session: {ex}")
            raise ex

        if replace:
            try:
                self.ssh.execute_shell_command(
                    LOAD_OVERRIDE_COMMAND, shows_output=False
                )
            except (CommandFailed, UnexpectedOutput) as ex:
                logger.error(f"Failed to override factory defaults: {ex}")
                raise ex

        is_banner_mode = False
        for command in candidate.split("\n"):
            cmd = command if is_banner_mode else command.strip()
            if not cmd and not is_banner_mode:
                continue
            logger.info(f"Executing command: {cmd}")
            try:
                is_banner_cmd = cmd == BANNER_KEYWORD
                if is_banner_cmd:
                    is_banner_mode = True
                if is_banner_mode and cmd.strip() == EOF_KEYWORD:
                    is_banner_mode = False
                    cmd = EOF_KEYWORD
                self.ssh.execute_shell_command(
                    cmd,
                    shows_output=is_banner_cmd,
                    wait_for_answer=not is_banner_mode,
                )
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

        if diff:
            try:
                changes = self.ssh.execute_shell_command(
                    DIFF_COMMAND, shows_output=True
                )
            except UnexpectedOutput as ex:
                if str(ex) == "Expected output from command, received none.":
                    logger.warning("The provided config caused no changes")
                else:
                    raise ex

        try:
            commit_cmd = COMMIT_KEYWORD
            if confirm_timeout:
                commit_cmd = (
                    COMMIT_CONFIRM_KEYWORD
                    % self._format_minutes_to_hhmmss(confirm_timeout)
                )
            logger.info(f"Executing '{commit_cmd}'...")
            self.ssh.execute_shell_command(commit_cmd, shows_output=False)
            logger.info("COMMIT succeeded")
        except (CommandFailed, UnexpectedOutput) as ex:
            logger.error(
                f"An error occurred while applying configuration: {ex}"
            )
            raise ex
        return changes

    def execute_request_command(self, command: str):
        self.ssh.execute_shell_command(
            command, match_reg="\?\s+\[(yes|confirm)\]", shows_output=False
        )
        self.ssh.execute_shell_command("y")

    def confirm_commit(self, session_name=None) -> None:
        try:
            cmd = (
                f"{CONFIGURE_SESSION_KEYWORD % session_name} {COMMIT_KEYWORD}"
            )
            logger.info(f"Executing '{cmd}'...")
            self.ssh.execute_shell_command(cmd, shows_output=False)
        except (CommandFailed, UnexpectedOutput) as ex:
            logger.exception(ex)
            raise ex

    def rollback(self, index) -> None:
        raise OperationNotSupported()
