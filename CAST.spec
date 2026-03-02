# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['CAST.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('Functions/ArtilleryFunctions.py','Functions'),
        ('Functions/MapFunctions.py','Functions'),
        ('Functions/JsonFunctions.py','Functions'),
        ('Functions/UI_Components.py','Functions'),
        ('Functions/icons/uksf.ico','Functions/icons'),
        ('Functions/icons/statuslog.ico','Functions/icons'),
        ('Functions/icons/clock.ico','Functions/icons'),
        ('Functions/icons/settings.ico','Functions/icons'),
        ('Functions/icons/scope.ico','Functions/icons'),
        ('Functions/icons/terrain.ico','Functions/icons'),
        ('Functions/icons/popout.png','Functions/icons'),
        ('Functions/icons/dropdown.png','Functions/icons'),
        ('Functions/icons/edit.png','Functions/icons'),
        ('Functions/icons/calc.png','Functions/icons'),
        ('Functions/icons/FPF.png','Functions/icons'),
        ('Functions/icons/LR.png','Functions/icons'),
        ('Functions/icons/XY.png','Functions/icons'),
        ('Functions/icons/snapshot.png','Functions/icons'),
        ('Functions/icons/reference points.png','Functions/icons'),
        ('Functions/icons/marker settings.png','Functions/icons'),
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
    icon='Functions/icons/uksf.ico'  # This sets the exe icon
)