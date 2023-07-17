import pathlib


def search_snapshot_dir_upwards(path: pathlib.Path) -> pathlib.Path:
    """Searches upwards for a .snapshots directory"""
    path = path.parent  # we don't check for the file itself but for the directory it is in

    # this is a do while in python... (python has no real do while loop ^^')
    while True:
        print(f"checking {path / '.snapshots'}")
        if (path / ".snapshots").is_dir():  # / operator of pathlib.Path joins paths
            return (path / ".snapshots").resolve()
        path = path.parent

        if path == pathlib.Path("/"):  # Condition for the do while loop
            break

    raise FileNotFoundError("Could not find a .snapshots directory - You need to specify one manually")


def get_path_relative_to_snapshot(path: pathlib.Path, snapshot_dir: pathlib.Path) -> pathlib.Path:
    """Removes the beginning of path that is the same as in the snapshot_dirs snapshots
    e.g. if path is /home/user/dir_to_del and snapshot_dir is /home/.snapshots
    we would like path to be /user/dir_to_del (so without the /home part)
    """
    parts_of_path = list(path.parts)

    for part in snapshot_dir.parts:
        if parts_of_path[0] == part:
            parts_of_path.pop(0)
        else:
            break

    return pathlib.Path(*parts_of_path)
