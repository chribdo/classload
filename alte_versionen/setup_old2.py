from setuptools import setup

APP = ['tk_main_menue.py']
DATA_FILES = []  # Icon muss im Projektverzeichnis liegen
OPTIONS = {
    'argv_emulation': False,  # Debug: Terminalfenster beim Doppelklick sichtbar
    'iconfile': 'icon.icns',
    'includes': [
        'requests',
        'charset_normalizer',
        '_cffi_backend',
        'certifi',
        'dotenv',
        'ttkbootstrap',
    ],
    'packages': ['cryptography', 'cffi'],
    'plist': {
        'CFBundleName': 'Classload',
        'CFBundleDisplayName': 'Classload',
        'CFBundleIdentifier': 'com.example.classload',
        'CFBundleVersion': '1.0',
        'CFBundleShortVersionString': '1.0',
        'NSHighResolutionCapable': True,
        'CFBundleIconFile': 'icon',  # Wichtig: ohne .icns-Endung
    },
    'verbose': 1,
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)