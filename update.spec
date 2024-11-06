# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['update.py'],
    pathex=[],
    binaries=[],
    datas=[('DATA', 'DATA')],  # Incluye la carpeta DATA
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='update',
    debug=True,  # Habilita el modo de depuración
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Cambiar a False si necesitas una ventana gráfica
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
