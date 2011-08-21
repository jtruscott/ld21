from distutils.core import setup
import py2exe

setup(console=['main.py'],
options = {'py2exe': {'bundle_files': 1}},
zipfile=None
)
