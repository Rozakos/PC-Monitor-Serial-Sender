# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for PC Monitor Serial Sender.

Build with:   pyinstaller PC-Monitor-Sender.spec
or just run:  .\build.ps1

Produces a single windowed EXE in dist\. The app downloads
LibreHardwareMonitor at runtime, so nothing extra needs bundling.
"""

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    # icon.ico is bundled so the app can find it next to the EXE (onedir) or
    # in the unpacked temp dir (onefile). main.py reads it via BRAND_ICO.
    datas=[('icon.ico', '.')],
    # These get pulled in dynamically and can be missed by static analysis.
    hiddenimports=[
        'pystray',
        'pystray._win32',
        'PIL.Image',
        'PIL.ImageDraw',
        'serial',
        'serial.tools.list_ports',
        'clr',
    ],
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
    name='PC-Monitor-Sender',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    # console=False -> windowed app, no console window (matches pythonw design)
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)
