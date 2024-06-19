""" """
from glob import glob
from os.path import splitext, basename
from setuptools import setup, find_packages

setup(
    name="heet",
    version='0.1',
    python_requires='>=3.8',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': ['heet=heet.cli.cli_ghg:start'],
    },
    zip_safe=False
    )
