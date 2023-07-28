import os
import pathlib
import shutil
import subprocess
from multiprocessing import Pool

from logger import logger
from retry_annotation import retry

permission_modified_snapshots: list[pathlib.Path] = []  # stores the snapshots that have been made writable


@retry(PermissionError, tries=3, initial_delay=1, backoff=2)
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


@retry(PermissionError, tries=6, initial_delay=1, backoff=1)
def set_snapshots_writable(snapshot_dirs: list[pathlib.Path], verbose: bool = False):
    """Sets all snapshots in snapshot_dirs to writable using btrfs property set"""

    # Filter out the snapshots that have already been made writable (in case of a retry)
    to_modify = [snap for snap in snapshot_dirs if snap not in permission_modified_snapshots]

    print(f"\nMaking {len(to_modify)} snapshots writable\n", flush=True)

    for snapshot in to_modify:
        if verbose:
            logger.info("Making snapshot read-write using BTRFS: " + str(snapshot))
        p = subprocess.run(["btrfs", "property", "set", "-ts", snapshot, "ro", "false"])

        if p.returncode != 0:
            raise PermissionError("Could not make all snapshots read-write, failed on: " + str(snapshot))

        permission_modified_snapshots.append(snapshot)


def restore_snap_fail_handler(e: PermissionError):
    """Informs the user about the failure and swallows the Exception to continue."""
    logger.error(f"{e}")
    logger.warning("You will need to make the snapshots read-only manually.")
    logger.warning("e.g.: sudo btrfs property set -ts <snapshot> ro true")
    logger.warning("continuing...")


@retry(PermissionError, tries=10, initial_delay=1, backoff=1.2, failure_handler=restore_snap_fail_handler)
def restore_snapshot_permissions(verbose: bool = False):
    """Makes all snapshots in snapshot_dirs read-only using btrfs property set"""

    print(f"\nMaking {len(permission_modified_snapshots)} snapshots read-only again", flush=True)
    to_change_back = permission_modified_snapshots.copy()
    for snapshot in to_change_back:
        if verbose:
            logger.info("Making snapshot read-only again using BTRFS: " + str(snapshot))
        p = subprocess.run(["btrfs", "property", "set", "-ts", snapshot, "ro", "true"])
        if p.returncode != 0:
            raise PermissionError("Could not make snapshot read-only again: " + str(snapshot))
        permission_modified_snapshots.remove(snapshot)  # on retry, it is not modified anymore


def delete_single_path(path_to_delete: pathlib.Path):
    """Deletes a single file/directory"""
    logger.info("Deleting: " + str(path_to_delete))

    try:
        if os.path.isdir(path_to_delete):
            shutil.rmtree(path_to_delete)
        else:
            os.remove(path_to_delete)
    except Exception as e:
        logger.error(f"Could not delete: {path_to_delete}")
        logger.warning(f"Most likely the snapshot couldn't be made writable. Exception is: {e}")
        logger.warning("Continuing...")
        return False
    return True


def delete_paths(paths_to_delete: list[pathlib.Path]):
    for path in paths_to_delete:
        _ignored_result = delete_single_path(path)


def delete_paths_in_parallel(paths_to_delete: list[pathlib.Path], parallel_processes: int = -1):
    """Deletes all files/directories in paths_to_delete in parallel"""
    if parallel_processes == -1:
        parallel_processes = max(len(paths_to_delete), os.cpu_count() * 2)

    logger.info(f"Deleting files/directories in parallel using {parallel_processes} processes")

    # initialize the pool with the number of cpu cores:
    pool = Pool(processes=parallel_processes)

    # delete the paths in parallel:
    results = pool.map_async(delete_single_path, paths_to_delete)

    # wait for the results to finish:
    result_values = results.get(None)

    if any(result_values) is False:
        logger.error(
            f"Could not delete all files/directories (see above)... continuing\n"
            f"since you can rerun the command to retry and nothing serious happened."
        )

    # close the pool:
    pool.close()
