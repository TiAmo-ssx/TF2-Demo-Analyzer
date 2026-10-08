@echo off
setlocal
chcp 65001 >nul

echo ============================================================
echo   TF2 Demo Analyzer - 打包脚本
echo ============================================================
echo.

REM ---------- 定位 Python ----------
set "PYTHON=python"
if exist ".venv\Scripts\python.exe" (
    set "PYTHON=.venv\Scripts\python.exe"
)

echo 使用 Python: %PYTHON%
%PYTHON% --version
echo.

REM ---------- 检查 Rust 解析器 ----------
if not exist "resources\parser\parse_demo.exe" (
    echo [错误] 找不到 resources\parser\parse_demo.exe
    echo        请先从 Releases 下载解析器，或自行编译 Rust 后放置。
    echo        仓库里故意不包含这个二进制文件。
    pause
    exit /b 1
)

REM ---------- 安装依赖 ----------
echo [1/3] 安装依赖...
%PYTHON% -m pip install -r requirements.txt
echo.

REM ---------- 清理旧产物 ----------
echo [2/3] 清理旧构建...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo.

REM ---------- 打包 ----------
echo [3/3] PyInstaller 打包...
%PYTHON% -m PyInstaller --clean --noconfirm TF2-Demo-Analyzer.spec
echo.

echo ============================================================
echo   打包完成！
echo   发布目录：dist\TF2-Demo-Analyzer\
echo ============================================================
echo.

pause
