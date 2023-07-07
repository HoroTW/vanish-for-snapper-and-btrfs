import os
import pathlib
import subprocess

from logger import logger
import snapper_timer_control as stc

permission_modified_snapshots = []  # stores the snapshots that have been made writable


def find_read_only_snapshots(snapshot_dirs: list[pathlib.Path]) -> list[pathlib.Path]:
    """Finds the read-only snapshots in snapshot_dirs"""
    read_only_snapshots = []

    for snapshot in snapshot_dirs:
        if os.access(snapshot, os.W_OK):  # snapshot is read-write
            continue
        elif os.access(snapshot, os.R_OK):  # snapshot is read
            read_only_snapshots.append(snapshot)
        else:  # This snapshot is not accessible
            raise PermissionError("Could not access snapshot: " + str(snapshot))
    return read_only_snapshots


def make_snapshots_writable(snapshot_dirs: list[pathlib.Path], verbose: bool = False):
    """Makes all snapshots in snapshot_dirs writable using btrfs property set"""

    print(f"\nMaking {len(snapshot_dirs)} snapshots writable\n")

    for snapshot in snapshot_dirs:
        if verbose:
            logger.info("Making snapshot read-write using BTRFS: " + str(snapshot))
        p = subprocess.run(["btrfs", "property", "set", "-ts", snapshot, "ro", "false"])

        if p.returncode != 0:
            logger.warning("Could not make snapshot read-write: " + str(snapshot))
            logger.warning("Continuing with next snapshot")

        permission_modified_snapshots.append(snapshot)


def restore_snapshot_permissions(verbose: bool = False):
    """Makes all snapshots in snapshot_dirs read-only using btrfs property set"""

    print(f"\nMaking {len(permission_modified_snapshots)} snapshots read-only again")
    for snapshot in permission_modified_snapshots:
        if verbose:
            logger.info("Making snapshot read-only again using BTRFS: " + str(snapshot))
        p = subprocess.run(["btrfs", "property", "set", "-ts", snapshot, "ro", "true"])
        if p.returncode != 0:
            logger.error("Could not make snapshot read-only again: " + str(snapshot))
            logger.warning("You will need to make it read-only manually.")
            logger.warning(f"e.g.: sudo btrfs property set -ts {snapshot} ro true")
            logger.warning("continuing...")
