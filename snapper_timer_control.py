import subprocess
import sys
from time import sleep
from logger import logger
from exceptions import SystemConfigurationError


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


def stop_snapper_timers():
    """Will exit the script if the timers could not be stopped."""

    logger.info("Stopping snapper timers...")
    p1 = subprocess.run(["systemctl", "stop", "snapper-timeline.timer"])
    if p1.returncode != 0:
        logger.error("Could not stop snapper-timeline.timer")
        logger.error("Aborting. changed nothing.")
        sys.exit(1)

    p2 = subprocess.run(["systemctl", "stop", "snapper-cleanup.timer"])
    if p2.returncode != 0:
        logger.error("Could not stop snapper-cleanup.timer")
        logger.error("Aborting. changed nothing.")
        sys.exit(1)

    # Wait for potential current snapper operations to finish
    sleep(2)


def resume_snapper_timers_and_exit(exit_code: int):
    """Resume snapper timers and exit with the given exit code."""
    resume_snapper_timers()
    sys.exit(exit_code)


def resume_snapper_timers():
    """Will inform the user if the timers could not be resumed."""

    logger.info("Resuming snapper timers...")
    p1 = subprocess.run(["systemctl", "start", "snapper-timeline.timer"])
    if p1.returncode != 0:
        logger.error("Could not start snapper-timeline.timer")
        logger.warning("WARNING: You will need to start it manually.")
        logger.warning("e.g.: systemctl start snapper-timeline.timer")
        logger.warning("continuing...")

    p2 = subprocess.run(["systemctl", "start", "snapper-cleanup.timer"])
    if p2.returncode != 0:
        logger.error("Could not start snapper-cleanup.timer")
        logger.warning("WARNING: You will need to start it manually.")
        logger.warning("e.g.: systemctl start snapper-cleanup.timer")
        logger.warning("continuing...")
