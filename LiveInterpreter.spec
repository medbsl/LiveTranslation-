# -*- mode: python ; coding: utf-8 -*-

# Path to Azure Speech SDK native libraries
speech_path = "/Users/hamma/Dev/Azure/azure_env/lib/python3.13/site-packages/azure/cognitiveservices/speech"

datas = [
    (f"{speech_path}/libMicrosoft.CognitiveServices.Speech.core.dylib",
     "azure/cognitiveservices/speech"),
    (f"{speech_path}/libMicrosoft.CognitiveServices.Speech.extension.kws.ort.dylib",
     "azure/cognitiveservices/speech"),
    (f"{speech_path}/libaudio_extension.a",
     "azure/cognitiveservices/speech"),
    (f"{speech_path}/libkws_factory.a",
     "azure/cognitiveservices/speech"),
]

a = Analysis(
    ['two_way_interpreter.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'azure.cognitiveservices.speech',
        'azure.cognitiveservices.speech.interop',
        'azure.cognitiveservices.speech.audio'
    ],
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
    name='LiveInterpreter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,          # MUST be off for macOS dylibs
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch="arm64",   # Your MacBook M3 uses ARM64
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    name='LiveInterpreter.app',
    icon=None,
    bundle_identifier="com.liveinterpreter.app",
    entitlements_file="entitlements.plist"
)

