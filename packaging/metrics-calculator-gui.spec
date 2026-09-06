# PyInstaller spec for the desktop app. Build from the repo root with:
#     pyinstaller packaging/metrics-calculator-gui.spec
#
# Produces a single self-contained executable (MetricsCalculator[.exe]) in
# dist/. PySide6's PyInstaller hook pulls in the Qt plugins we need
# (platforms, styles, imageformats); pandas/openpyxl are collected when
# present so the packaged app can also write .xlsx.

import os

from PyInstaller.utils.hooks import collect_submodules

_here = SPECPATH  # noqa: F821 - injected by PyInstaller
_src = os.path.normpath(os.path.join(_here, os.pardir, "src"))

_optional_xlsx = []
for _module in ("pandas", "openpyxl"):
    try:
        __import__(_module)
    except ImportError:
        continue
    _optional_xlsx += collect_submodules(_module)

block_cipher = None

a = Analysis(
    [os.path.join(_here, "gui_entry.py")],
    pathex=[_src],
    binaries=[],
    datas=[],
    hiddenimports=_optional_xlsx,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "PySide6.QtWebEngineCore", "PySide6.Qt3DCore"],
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
    name="MetricsCalculator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
