# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['tk_main_menue.py'],
    pathex=[],
    binaries=[],
    datas=[('assets/icon.icns', 'assets')],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Classload',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False  # GUI-App
)

app = BUNDLE(
    exe,
    name='Classload.app',
    icon='assets/icon.icns',
    bundle_identifier='com.example.classload',
    info_plist={
        'CFBundleName': 'Classload',
        'CFBundleDisplayName': 'Classload',
        'CFBundleExecutable': 'Classload',
        'CFBundleIdentifier': 'com.example.classload',
        'CFBundleVersion': '0.1',
        'CFBundleShortVersionString': '0.1',
        'NSHighResolutionCapable': True,
        'CFBundlePackageType': 'APPL'
    }
)