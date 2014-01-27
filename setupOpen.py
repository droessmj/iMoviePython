
from setuptools import setup

APP = ['OpeniMovie.py']
DATA_FILES = []
OPTIONS = {
	'iconfile':'APPL.icns',
	'plist': {'CFBundleShortVersionString':'0.1.0',}
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)