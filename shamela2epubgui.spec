# -*- mode: python ; coding: utf-8 -*-
import platform
from os import system

block_cipher = None


a = Analysis(
    ['shamela2epub/gui/app.py'],
    pathex=[],
    binaries=[],
    datas=[('pyproject.toml', '.'), ('shamela2epub/assets', './shamela2epub/assets'), ('shamela2epub/gui/ui.ui', './shamela2epub/gui/')],
    hiddenimports=['PyQt6.sip'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='shamela2epubgui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='./shamela2epub/assets/books-duotone.ico',
)

if platform.system() != 'Windows':
    system('ls -R')

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="collect"
)
app = BUNDLE(
    coll,
    name="shamela2epubgui.app",
    icon="./shamela2epub/assets/books-duotone.icns",
    bundle_identifier="com.shamela2epub",
    version="1.4.2",
    info_plist={
        "NSPrincipalClass": "NSApplication",
        "NSHighResolutionCapable": "True",
    },
)