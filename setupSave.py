
from setuptools import setup

APP = ['SaveOnExit.py']
DATA_FILES = []
OPTIONS = {
	'iconfile':'iMovie.icns'
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)