"""Command executor for running external commands."""

import subprocess
from typing import Optional

from ytdlp_subs.domain.exceptions import CommandExecutionError
from ytdlp_subs.infrastructure.logging import get_logger

logger = get_logger(__name__)


class CommandResult:
    """Result of a command execution."""

    def __init__(
        self,
        stdout: str,
        stderr: str,
        return_code: int,
        command: list[str],
    ) -> None:
        """
        Initialize command result.

        Args:
            stdout: Standard output
            stderr: Standard error
            return_code: Process return code
            command: Command that was executed
        """
        self.stdout = stdout
        self.stderr = stderr
        self.return_code = return_code
        self.command = command

    @property
    def success(self) -> bool:
        """Check if command executed successfully."""
        return self.return_code == 0

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"CommandResult(command={' '.join(self.command)}, "
            f"return_code={self.return_code}, "
            f"success={self.success})"
        )


class CommandExecutor:
    """Executor for running external commands with proper error handling."""

    def __init__(self, timeout: Optional[int] = None) -> None:
        """
        Initialize command executor.

        Args:
            timeout: Optional timeout in seconds for command execution
        """
        self.timeout = timeout

    def execute(
        self,
        command: list[str],
        check: bool = True,
        capture_output: bool = True,
    ) -> CommandResult:
        """
        Execute a command.

        Args:
            command: Command and arguments to execute
            check: Whether to raise exception on non-zero exit code
            capture_output: Whether to capture stdout/stderr

        Returns:
            CommandResult object

        Raises:
            CommandExecutionError: If command fails and check=True
        """
        logger.debug("Executing command", command=" ".join(command))

        try:
            result = subprocess.run(
                command,
                capture_output=capture_output,
                text=True,
                encoding="utf-8",
                timeout=self.timeout,
                check=False,  # We handle checking ourselves
            )

            cmd_result = CommandResult(
                stdout=result.stdout,
                stderr=result.stderr,
                return_code=result.returncode,
                command=command,
            )

            if check and not cmd_result.success:
                logger.error(
                    "Command failed",
                    command=" ".join(command),
                    return_code=result.returncode,
                    stderr=result.stderr,
                )
                raise CommandExecutionError(
                    f"Command failed with return code {result.returncode}",
                    command=command,
                    return_code=result.returncode,
                    stderr=result.stderr,
                )

            logger.debug(
                "Command completed",
                command=" ".join(command),
                return_code=result.returncode,
            )

            return cmd_result

        except subprocess.TimeoutExpired as e:
            logger.error("Command timed out", command=" ".join(command), timeout=self.timeout)
            raise CommandExecutionError(
                f"Command timed out after {self.timeout} seconds",
                command=command,
                timeout=self.timeout,
            ) from e

        except FileNotFoundError as e:
            logger.error("Command not found", command=command[0])
            raise CommandExecutionError(
                f"Command not found: {command[0]}",
                command=command,
            ) from e

        except Exception as e:
            logger.error("Unexpected error executing command", command=" ".join(command), error=str(e))
            raise CommandExecutionError(
                f"Unexpected error executing command: {e}",
                command=command,
            ) from e
