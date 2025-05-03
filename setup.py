from setuptools import setup

APP = ['tk_main_menue.py']
DATA_FILES = [
    ('', ['LICENSE.txt', 'README.md', 'screenshot.png']),
    ('assets', ['assets/icon_small.png']),
]

OPTIONS = {
    'includes': [
        'requests',
        'charset_normalizer',
        'tkinter',
        'ttkbootstrap',
        'PIL.Image',
        'PIL.ImageTk',
        'jamfscripts',
        'markdown.extensions.extra',
        'markdown.extensions.nl2br',
        'markdown.extensions.abbr',
        'markdown.extensions.attr_list',
        'markdown.extensions.def_list',
        'markdown.extensions.fenced_code',
        'markdown.extensions.footnotes',
        'markdown.extensions.tables',
        'markdown.extensions.smart_strong',
        'markdown.extensions.admonition',
        'markdown.extensions.md_in_html' ,
        'markdown.extensions.sane_lists'
    ],
    'packages': ['cryptography', 'cffi', 'charset_normalizer'],
    'plist': {
        'CFBundleName': 'Classload',
        'CFBundleDisplayName': 'Classload',
        'CFBundleIdentifier': 'com.example.classload',
        'CFBundleVersion': '1.0',
        'CFBundleShortVersionString': '1.0',
        'NSHighResolutionCapable': True,
        'CFBundleIconFile': 'icon',
        'LSUIElement': False  # <-- Sichtbarkeit & Dock-Integration
    },
    'resources': ['LICENSE.txt', 'README.md', 'screenshot.png', 'icon.icns'],
    'iconfile': 'icon.icns',
    'verbose': 1,
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

"""
from setuptools import setup

APP = ['tk_main_menue.py']
DATA_FILES = [
    ('', ['LICENSE.txt', 'README.md']),
    ('assets', ['assets/icon_small.png']),
]

OPTIONS = {
    'argv_emulation': True,  # Terminalfenster zeigt Fehler
    # 'iconfile': 'icon.icns',  # Nur aktivieren, wenn icon.icns existiert
    'includes': [
        'requests',
        'charset_normalizer',
        'tkinter',
        'ttkbootstrap',
        'PIL.Image',
        'PIL.ImageTk',
        'jamfscripts'
    ],
    'packages': ['cryptography', 'cffi', 'charset_normalizer'],
    'plist': {
        'CFBundleName': 'Classload',
        'CFBundleDisplayName': 'Classload',
        'CFBundleIdentifier': 'com.example.classload',
        'CFBundleVersion': '1.0',
        'CFBundleShortVersionString': '1.0',
        'NSHighResolutionCapable': True,
        'CFBundleIconFile': 'icon',  # nur wenn icon.icns da ist
    },
    'resources': ['LICENSE.txt', 'screenshot.png', 'hilfe.html', 'README.md'],
    'verbose': 1,
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
"""