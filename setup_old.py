from setuptools import setup

APP = ['tk_main_menue_v060425.py']
DATA_FILES = [('assets', ['assets/icon1.icns'])]  # optional: Bilder etc.
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'assets/icon1.icns',
    'packages': ['tkinter'],
    'plist': {
        'CFBundleName': 'Classload',
        'CFBundleDisplayName': 'Classload',
        'CFBundleIdentifier': 'com.example.classload',
        'CFBundleVersion': '0.1',
        'CFBundleShortVersionString': '0.1',
        'NSHighResolutionCapable': True,
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
