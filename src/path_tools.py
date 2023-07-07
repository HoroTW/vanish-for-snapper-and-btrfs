import pathlib


def search_snapshot_dir_upwards(path: pathlib.Path) -> pathlib.Path:
    """Searches upwards for a .snapshots directory"""

    while path != pathlib.Path("/"):
        if (path / ".snapshots").is_dir():  # magical / operator of pathlib.Path
            return (path / ".snapshots").resolve()
        path = path.parent

    raise FileNotFoundError("Could not find a .snapshots directory")


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
