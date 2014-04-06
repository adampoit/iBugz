"""
Usage:
    python setup.py py2app
"""
from distutils.core import setup
import py2app

setup(
    name='FogBugz Tracker',
    app=["FogBugzTracker.py"],
    data_files=["English.lproj"],
)
