"""
Usage:
    python setup.py py2app
"""
from distutils.core import setup
import py2app

setup(
    name='iBugz',
    app=["iBugz.py"],
    data_files=["English.lproj"],
)
