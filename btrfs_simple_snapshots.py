"""

Copyright (c) 2018 Arnaud Levaufre <arnaud@levaufre.name>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

import argparse
import datetime
import logging
import os
import subprocess


logger = logging.getLogger(__name__)


SNAP_FORMAT = "%Y-%m-%d-%H%M%S"


def get_snap_dir(subvolume):
    return os.path.join(subvolume, ".snapshots")


def btrfs_create_subvolume(subvolume):
    cmd = ["btrfs", "subvolume", "create", subvolume]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        return False
    return True


def btrfs_delete_subvolume(subvolume):
    cmd = ["btrfs", "subvolume", "delete", subvolume]
    subprocess.run(cmd)


def btrfs_snapshot(subvolume, snapshot_path):
    cmd = ["btrfs", "subvolume", "snapshot", "-r", subvolume, snapshot_path]
    subprocess.run(cmd)


def snapshot(subvolume):
    snap_dir = get_snap_dir(subvolume)

    if not os.path.exists(snap_dir):
        btrfs_create_subvolume(snap_dir)
        stat = os.stat(subvolume)
        os.chown(subvolume, stat.st_uid, stat.st_gid)

    snap_name = datetime.datetime.now().strftime(SNAP_FORMAT)
    snap_path = os.path.join(snap_dir, snap_name)
    if not os.path.exists(snap_path):
        btrfs_snapshot(subvolume, snap_path)


def apply_retention_policy(subvolume, policies=None):
    if not policies:
        policies = [
            (86400, '%Y%m%d%H'),  # Keep an hourly snapshot for 24 hours
            (2419200, '%Y%m%d'),  # Keep a daily snapshot for 4 weeks
            (7257600, '%Y%W'),  # Keep a weekly snapshot for 12 weeks
            (31536000, '%Y%m'),  # Keep a monthly snaphost for 12 months
            (315360000, '%Y'),  # Keep a yearly snapshot 10 years
        ]
    snap_dir = get_snap_dir(subvolume)
    snaps = os.listdir(snap_dir)

    # use a cmmon refenrece to now for every steps of the terention policy
    # application.
    now = datetime.datetime.now()

    # Populate policy workspace used to find which snapshot must be kept or
    # deleted according to the various retentio policies
    policy_workspaces = {}
    for snap in snaps:
        snap_datetime = datetime.datetime.strptime(snap, SNAP_FORMAT)

        # Populate weekly snapshots
        for duration, policy in policies:
            if policy not in policy_workspaces:
                policy_workspaces[policy] = {}

            key = snap_datetime.strftime(policy)
            if key not in policy_workspaces[policy]:
                policy_workspaces[policy][key] = []

            if now - snap_datetime < datetime.timedelta(seconds=duration):
                policy_workspaces[policy][key].append(snap)

    # Find which snapshots must be kept
    exclude_snap = []
    for policy_workspace in policy_workspaces.values():
        for workspace_snaps in policy_workspace.values():
            if len(workspace_snaps):
                exclude_snap.append(sorted(workspace_snaps)[0])

    snaps_to_delete = filter(lambda x: x not in exclude_snap, snaps)
    for snap in snaps_to_delete:
        btrfs_delete_subvolume(os.path.join(snap_dir, snap))


def main():
    logging.basicConfig(level="DEBUG")

    parser = argparse.ArgumentParser(
        description="""
        Btrfs simple snapshot utility that create snapshots inside a .snapshots
        subvolume inside the snapshot you want to backup.
        """
    )
    parser.add_argument("subvolume", nargs="+")
    args = parser.parse_args()
    for subvolume in args.subvolume:
        snapshot(subvolume)
        apply_retention_policy(subvolume)


if __name__ == "__main__":
    main()
