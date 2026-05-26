@echo off
echo ==========================================
echo   基于微内核的自演进 RAN 原型 — 安装脚本
echo   Alpha 1.0
echo ==========================================
echo.

echo [1/3] 创建虚拟环境...
python -m venv venv
if %errorlevel% neq 0 (
    echo 错误: 创建虚拟环境失败，请检查 Python 安装
    pause
    exit /b 1
)

echo [2/3] 激活虚拟环境...
call venv\Scripts\activate.bat

echo [3/3] 安装依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)

echo.
echo ==========================================
echo   安装完成!
echo ==========================================
echo.
echo 使用方法:
echo   1. 双击 start.bat 启动系统
echo   2. 浏览器打开 http://localhost:8501
echo.
pause