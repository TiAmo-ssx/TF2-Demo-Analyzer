# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller 打包配置
#
# 用法（在项目根目录）：
#   python -m PyInstaller --clean --noconfirm TF2-Demo-Analyzer.spec
#
# 产物：
#   dist/TF2-Demo-Analyzer/
#     ├── TF2-Demo-Analyzer.exe
#     └── _internal/
#           ├── resources/parser/parse_demo.exe
#           └── web/templates/  web/static/


block_cipher = None


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Rust 解析器
        ('resources/parser/parse_demo.exe', 'resources/parser'),
        # Flask 模板与静态资源
        ('web/templates', 'web/templates'),
        ('web/static', 'web/static'),
    ],
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='TF2-Demo-Analyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    # console=False：窗口模式（不弹出黑色控制台窗口）
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)


coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TF2-Demo-Analyzer',
)
