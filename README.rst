Btrfs simple snapshots
======================

Take snapshots of your btrfs subvolumes and apply a retention policy in order
to keep your snapshot directory somewhat clean and small.

The retention policy, defined bellow, is hardcoded for now but it should be enought for the
average use case. I may adjust it, or provide a way to change it at runtime if needed.

* Hourly snapshots are kept for 24 hours
* Daily snapshots are kept for 4 weeks
* Weekly snapshots are kept for 12 weeks
* Monthly snapshots are kept for a year
* yearly snapshots are kept for 10 years

Every subvolume that should be snapshoted must be given as argument to the
script. For example if you want to snapshot every home directory created as
subvolumes and your `/etc` and `/srv` directory you would do

.. doctest:: bash
btrfs-simple-snapshots /home/* /etc /srv
..

Once done, you will find a new subvolume named `.snapshots` inside the
snapshoted subvolume with a name formated as `%Y-%m-%d-%H%M%S`

Installation
------------

Install from pip using `pip install btrfs-simple-snapshots`. Then you can run
it as root or with a user able to manage btrfs subvolumes. It is probably a
good thing to run it automatically with a cron job. Depending on you need you
may run it once per day (at 2 a.m.) to snapshot every home folder (created as
subvolumes) with this kind of job definition.

.. doctest:: cron
0 2 * * * python -m btrfs_simple_snapshots /home/*
..
