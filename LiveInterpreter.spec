# -*- mode: python ; coding: utf-8 -*-

import os

# -----------------------------
# PATHS
# -----------------------------

VENV = "/Users/hamma/Dev/Azure/azure_env/lib/python3.13/site-packages"

speech_path = f"{VENV}/azure/cognitiveservices/speech"
deepl_path  = f"{VENV}/deepl"


# -----------------------------
# DATA FILES (bundled inside the .app)
# -----------------------------
datas = [

    # ----- Azure Speech dylibs -----
    (f"{speech_path}/libMicrosoft.CognitiveServices.Speech.core.dylib",
     "azure/cognitiveservices/speech"),
    (f"{speech_path}/libMicrosoft.CognitiveServices.Speech.extension.kws.ort.dylib",
     "azure/cognitiveservices/speech"),
    (f"{speech_path}/libaudio_extension.a",
     "azure/cognitiveservices/speech"),
    (f"{speech_path}/libkws_factory.a",
     "azure/cognitiveservices/speech"),

    # ----- Your Settings.ini -----
    ("Settings.ini", "."),

    # ----- DeepL package -----
    (deepl_path, "deepl"),
]


# -----------------------------
# ANALYSIS (main modules included)
# -----------------------------
a = Analysis(
    ['main.py', 'subtitle_window.py'],       # ENTRY POINTS
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'azure.cognitiveservices.speech',
        'azure.cognitiveservices.speech.interop',
        'azure.cognitiveservices.speech.audio',
        'deepl',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)


# -----------------------------
# BUILD PYZ
# -----------------------------
pyz = PYZ(a.pure)


# -----------------------------
# BUILD EXECUTABLE
# -----------------------------
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='LiveInterpreter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,                # MUST be OFF on macOS
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch="arm64",      # Apple Silicon (M1/M2/M3)
    codesign_identity=None,
    entitlements_file="entitlements.plist",
)


# -----------------------------
# BUNDLE INTO macOS .app
# -----------------------------
app = BUNDLE(
    exe,
    name='LiveInterpreter.app',
    icon=None,                                # you can add .icns later
    bundle_identifier="com.liveinterpreter.app",
    entitlements_file="entitlements.plist"
)
