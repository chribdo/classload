from setuptools import setup

APP = ['tk_main_menue_v060425.py']
DATA_FILES = [('assets', ['assets/icon.icns'])]  # Icon-Datei (optional)
OPTIONS = {
    'argv_emulation': False,  # Debug-Modus: Terminal öffnet sich bei Doppelklick
    'iconfile': 'icon.icns',
    'packages': ['tkinter', 'requests'],
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