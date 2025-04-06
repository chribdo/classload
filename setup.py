from setuptools import setup
import pathlib

# Automatisch alle Module aus requirements.txt lesen
requirements = []
req_file = pathlib.Path("requirements.txt")
if req_file.exists():
    with req_file.open() as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                pkg = line.split("==")[0].strip()
                requirements.append(pkg)

APP = ['tk_main_menue.py']
DATA_FILES = [('assets', ['assets/icon.icns'])]  # optional
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'assets/icon.icns',
    'packages': ['tkinter'] + requirements,
    'plist': {
        'CFBundleName': 'Classload',
        'CFBundleDisplayName': 'Classload',
        'CFBundleIdentifier': 'com.example.classload',
        'CFBundleVersion': '1.0',
        'CFBundleShortVersionString': '1.0',
        'NSHighResolutionCapable': True,
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)