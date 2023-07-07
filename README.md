Vanish - for Snapper and BTRFS
==============================

> A tool to make files and directories disappear out of existence (at least all snapshots 😉)

This is useful for reclaiming space from BTRFS snapshots without deleting the snapshots themselves.

For frequently changing files which take up a lot of space, you should consider if you want to keep them in
the snapshots at all. You could prevent this by using a separate subvolume for the frequently changing files.

- The tool tries to ensure consistency by pausing the snapper timers while it is running.
- Also it keeps track which snapshots where read only and only sets those back to read only.
- It asks you for confirmation and shows you what it is going to delete before it does it.
- In general it does what a very simple script would do, but it tries to do it in a more robust way.

As long as you use it only on files and directories you don't need anymore, it should be safe to use - but see the disclaimer below.

### DISCLAIMER:
> - I am not responsible for any data loss or other damage caused by this tool.<br>
> - Use it at your own risk.<br>
> - I use it myself and it works for me, but I can't guarantee that it will work for you.

If anything goes wrong, please open an issue so we can track down the problem.

### Usage:
```text
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
  SnapVanish for BTRFS
  A tool to make files vanish out of existence (or at least out of all snapshots)

  It's useful for reclaiming space from without deleting the snapshots themselves
  The folder or file will be deleted from all snapper snapshots in the snapshot
  directory.
```

### Requirements:
- Nothing besides a python3 installation

### Installation:
```bash
git clone https://github.com/HoroTW/vanish-for-snapper-and-btrfs.git \
&& sudo ln -s `pwd`/vanish-for-snapper-and-btrfs/vanish /usr/bin/vanish
```

### Set log level
```bash
LOG_LEVEL=DEBUG vanish file_to_delete
```

### Top level function description:
- Pause snapper timers
- Go through snapper snapshots
  - Make them read/write
  - Delete a file/directory in all of them
  - Set the snapshots to read-only again
- Resume snapper timers

### If you want to support me
You can [buy me a coffee](https://bmc.link/HoroTW) if you want to support me.
Support is not required, but it is very much appreciated - it keeps me motivated to work on this and other projects. Thank you! 😊

Useful other commands:
----------------------

Activate the snapper timers:
``` bash
sudo systemctl start snapper-timeline.timer snapper-cleanup.timer
```

Set all snapshots of a directory to read only:
```bash
sudo ls /home/.snapshots | sudo xargs -I {} btrfs property set -ts /home/.snapshots/{}/snapshot ro true
```

Inspect what is taking up space in btrfs and snapshots (space required will only be accounted for one subvolume).
But useful to find out what you need to delete (you need to have btdu installed, of course):
```bash
sudo mount <DeviceID> /mnt && btdu /mnt ; sudo umount /mnt
```

Make all snapshots in root read only again (if you want to do that):
```bash
sudo ls /.snapshots | sudo xargs -I {} btrfs property set -ts /.snapshots/{}/snapshot ro true
```
