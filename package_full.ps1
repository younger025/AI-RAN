# package_full.ps1 — 基于微内核的自演进 RAN 原型 完整分发包创建脚本
$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
if (-not $ProjectRoot) { $ProjectRoot = Get-Location }
$Timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$OutputDir = "$ProjectRoot\dist\AI_RAN_Demo_$Timestamp"

Write-Host "=== 基于微内核的自演进 RAN 原型 — 完整打包脚本 ==="

# 1. 清理
Write-Host "[1/6] 清理缓存..."
Get-ChildItem -Path $ProjectRoot -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
Get-ChildItem -Path $ProjectRoot -Recurse -Directory -Filter ".pytest_cache" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
Remove-Item "$ProjectRoot\outputs" -Recurse -Force -ErrorAction SilentlyContinue

# 2. 创建输出目录
Write-Host "[2/6] 创建输出目录..."
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

# 3. 复制核心文件
Write-Host "[3/6] 复制核心代码..."
Copy-Item -Path "$ProjectRoot\uran" -Destination $OutputDir -Recurse
Copy-Item -Path "$ProjectRoot\configs" -Destination $OutputDir -Recurse
Copy-Item -Path "$ProjectRoot\tests" -Destination $OutputDir -Recurse
Copy-Item -Path "$ProjectRoot\docs" -Destination $OutputDir -Recurse
Copy-Item -Path "$ProjectRoot\requirements.txt" -Destination $OutputDir

# 4. 生成 setup 脚本
Write-Host "[4/6] 生成安装脚本..."

@"
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
"@ | Out-File -FilePath "$OutputDir\install.bat" -Encoding Default

@"
@echo off
call venv\Scripts\activate.bat
echo ==========================================
echo   基于微内核的自演进 RAN 原型
echo   Alpha 1.0
echo ==========================================
echo.
echo 正在启动系统...
echo 请稍候，浏览器将自动打开...
echo 如未自动打开，请手动访问: http://localhost:8501
echo.
echo 按 Ctrl+C 可停止服务
echo.
streamlit run uran/dashboard/research_app.py --server.port 8501
pause
"@ | Out-File -FilePath "$OutputDir\start.bat" -Encoding Default

# 5. 生成 README
Write-Host "[5/6] 生成部署说明..."
@"
# 基于微内核的自演进 RAN 原型 (Microkernel-based Self-Evolving RAN Prototype)

> Alpha 1.0

## 快速开始

### 前提条件
- 已安装 Python 3.10 ~ 3.13
- Python 已添加到系统 PATH

### 安装
双击运行 `install.bat`

### 启动
双击运行 `start.bat`

### 访问
浏览器打开 http://localhost:8501

### 详细文档
请参阅 `docs/AI_RAN_Demo_部署与打包文档.md`
"@ | Out-File -FilePath "$OutputDir\README.md" -Encoding UTF8

# 6. 压缩
Write-Host "[6/6] 压缩打包..."
Compress-Archive -Path "$OutputDir\*" -DestinationPath "$OutputDir.zip" -Force

Remove-Item -Recurse -Force $OutputDir

Write-Host "打包完成: $OutputDir.zip"
Write-Host "将该 ZIP 文件传输到目标电脑后解压，双击 install.bat 即可一键部署"
