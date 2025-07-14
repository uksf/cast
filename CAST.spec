# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['CAST.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('Functions/ArtilleryFunctions.py','Functions'),
        ('Functions/uksf.ico','Functions'),
        ('Functions/statuslog.ico','Functions'),
        ('Functions/edit.png','Functions'),
        ('Functions/calc.png','Functions'),
        ('Functions/ArtilleryConfigs.json','Functions'),
        ('Functions/polynomial/*','Functions/polynomial')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CAST',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='Functions/uksf.ico'  # This sets the exe icon
)