import sys
import os
import pathlib

from logger import logger


def print_usage_and_exit(exit_code: int):
    """Prints the usage and exits with the given exit code."""
    print_usage()
    sys.exit(exit_code)


def print_usage():
    """Prints the usage and if an exit code is given, exists with it."""
    print(
        """
usage: vanish [OPTIONS] <file/directory to delete>

OPTIONS:
  --help                    Print this help message
  --snapdir <snapshot dir>  The directory where your snapper snapshots are stored.
                            If no directory is given vanish will search
                            upwards from the file/directory to delete for a
                            .snapshots directory. If none is found it will exit.
                            Most of the time you will not need to specify this.


<file/directory to delete>: Path to the file or directory you want to delete.
        Even if you already deleted it from your working subvolume, you can still
        write the old path to it here to delete it from all snapshots see Example 4.

EXAMPLE 1: vanish /home/user/big_useless_directory
EXAMPLE 2: vanish --snapdir /home/.snapshots big_useless_file
EXAMPLE 3: vanish ~/Downloads/big_useless_file

EXAMPLE 4:
  pwd # /home/user
  rm -rf a_useless_directory  # first deleted the folder... then:
  vanish --snapdir /home/.snapshots a_useless_directory # vanishes it from snapshots

DESCRIPTION:
  Vanish for Snapper and BTRFS
  A tool to make files vanish out of existence (or at least out of all snapshots)

  It's useful for reclaiming space from without deleting the snapshots themselves
  The folder or file will be deleted from all snapper snapshots in the snapshot
  directory."""
    )


def parse_args():
    snapshot_dir = None

    # check if an arg is --help
    if any(arg == "--help" for arg in sys.argv):
        print_usage_and_exit(0)

    for i in range(len(sys.argv)):
        if sys.argv[i] == "--snapdir":
            sys.argv.pop(i)
            if i >= len(sys.argv):
                logger.error("No snapshot directory given after --snapdir")
                print_usage_and_exit(1)
            else:
                # snapshot_dir = os.path.abspath(sys.argv.pop(i))
                snapshot_dir = pathlib.Path(sys.argv.pop(i)).resolve()
                break

    # check if file/directory to delete is given
    if len(sys.argv) < 2:
        logger.error("No file or directory to delete given")
        print_usage_and_exit(1)
    elif len(sys.argv) > 2:
        logger.error("Too many arguments given")
        logger.debug(f"Arguments: {sys.argv}")
        print_usage_and_exit(1)

    # file_or_folder_to_delete = os.path.abspath(sys.argv[0])
    file_or_dir_to_del = pathlib.Path(sys.argv[1]).resolve()

    # Check if the user is root
    if os.geteuid() != 0:
        logger.error("You need to run this script as root.")
        print_usage_and_exit(1)

    return snapshot_dir, file_or_dir_to_del
