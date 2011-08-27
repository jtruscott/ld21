from distutils.core import setup
import py2exe

setup(console=['main.py'], options = {
    'py2exe': {
        'bundle_files': 1,
        'compressed': True,
        'ascii': True,
        'excludes': [
            '_ssl',
            'pyreadline', 'difflib', 'doctest', 'locale',
            'pdb', 'pickle', 'calendar', 'inspect'],
        }
    },
    zipfile=None
)
