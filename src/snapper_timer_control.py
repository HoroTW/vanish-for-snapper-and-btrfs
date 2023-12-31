import subprocess
import sys
from time import sleep

from logger import logger
from exceptions import SystemConfigurationError
from retry_annotation import retry


@retry(SystemConfigurationError, tries=3, initial_delay=1, backoff=1)
def check_snapper_systemd_timers_exist() -> bool:
    """Checks if the snapper systemd timers exist, Raises an SystemConfigurationError if something is wrong."""

    for timer in ("snapper-timeline.timer", "snapper-cleanup.timer"):
        p = subprocess.run(["systemctl", "is-active", timer], stdout=subprocess.DEVNULL)
        if p.returncode == 4:
            raise SystemConfigurationError(f"The {timer} does not exist.")
        elif p.returncode == 3:
            raise SystemConfigurationError(f"The {timer} is not running.")
        elif p.returncode != 0:
            raise SystemConfigurationError(f"Unexpected return code from systemd: {p.returncode}")
    return True


@retry(SystemConfigurationError, tries=5, initial_delay=1, backoff=2)
def stop_snapper_timers():
    """Will exit the script if the timers could not be stopped."""

    logger.info("Stopping snapper timers...")
    p1 = subprocess.run(["systemctl", "stop", "snapper-timeline.timer"])
    if p1.returncode != 0:
        raise SystemConfigurationError("Could not stop snapper-timeline.timer")

    p2 = subprocess.run(["systemctl", "stop", "snapper-cleanup.timer"])
    if p2.returncode != 0:
        raise SystemConfigurationError("Could not stop snapper-cleanup.timer")

    if are_snapper_jobs_running():
        sleep(5)  # additional time to give them a fairer chance to finish (they normally finish quickly)
        raise SystemConfigurationError("Snapper jobs are currently running, waiting for them to finish...")


def are_snapper_jobs_running() -> bool:
    """Returns true if snapper jobs are running."""
    p = subprocess.run(
        ["systemctl", "is-active", "snapper-timeline.service", "snapper-cleanup.service"],
        stdout=subprocess.PIPE,
    )
    output = p.stdout.decode("utf-8")

    if any(line.strip() == "active" for line in output.splitlines()):
        return True  # A service is active if it is running else (even if it doesn't exist) it is inactive
    return False


def resume_snapper_timers_and_exit(exit_code: int):
    """Resume snapper timers and exit with the given exit code."""
    resume_snapper_timers()
    sys.exit(exit_code)


def snap_res_fail_handler(e: Exception):
    """Informs the user about the failure and swallows the Exception to continue."""
    logger.error(f"{e}")
    logger.warning("You will need to start the timers manually.")
    logger.warning("e.g. by doing: systemctl start snapper-timeline.timer snapper-cleanup.timer")
    logger.warning("continuing...")


@retry(SystemConfigurationError, tries=5, initial_delay=1, backoff=2, failure_handler=snap_res_fail_handler)
def resume_snapper_timers():
    """Resume snapper timers and raise a SystemConfigurationError if it fails."""
    logger.info("Resuming snapper timers...")

    p1 = subprocess.run(["systemctl", "start", "snapper-timeline.timer"])
    if p1.returncode != 0:
        raise SystemConfigurationError("Could not start snapper-timeline.timer again")

    p2 = subprocess.run(["systemctl", "start", "snapper-cleanup.timer"])
    if p2.returncode != 0:
        raise SystemConfigurationError("Could not start snapper-cleanup.timer again")
