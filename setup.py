from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="btrfs-simple-snapshots",
    version="0.1.3",
    description="Snapshot you btrfs subvolumes and apply a retention policy",
    long_description=long_description,
    url="https://github.com/ArnaudLevaufre/btrfs-simple-snapshots",
    author="Arnaud Levaufre",
    author_email="arnaud@levaufre.name",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "Intended Audience :: End Users/Desktop",
        "Topic :: System :: Filesystems",
        "Topic :: System :: Archiving :: Backup",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="btrfs snapshot subvolume backup",
    py_modules=['btrfs_simple_snapshots'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            "btrfs-simple-snapshots=btrfs_simple_snapshots:main"
        ],
    },
)
