# 基于微内核的自演进 RAN 原型 — 系统迁移指南（Trae 版）

> **目标**：将本系统从源电脑完整迁移到另一台已安装 Trae 的电脑上，并通过 Trae 完成环境配置、依赖安装、验证启动  
> **适用版本**：Alpha 1.0  
> **更新日期**：2026-05-22

---

## 前提条件（在执行前请确认）

- 目标电脑已安装 **Trae IDE**
- 项目文件已拷贝到目标电脑（U 盘 / 局域网共享 / 云盘 等方式）
- 目标电脑的操作系统为 Windows 10+（macOS/Linux 操作类似，仅命令略有不同）

---

## 第一步：在 Trae 中打开项目

1. 将拷贝过来的 `AI RAN Demo` 文件夹放到目标电脑的任意位置，**路径不要含中文和空格**（推荐放在盘符根目录，如 `E:\AI RAN Demo`）
2. 启动 Trae，点击「打开文件夹」，选择 `AI RAN Demo` 目录
3. 确认 Trae 的终端（Terminal）工作目录为项目根目录

---

## 第二步：检查 Python 环境

在 Trae 终端中执行以下命令，检查 Python 是否已安装：

```powershell
python --version
```

**预期输出**：`Python 3.10.x` / `3.11.x` / `3.12.x` / `3.13.x`

### 如果没有 Python 或版本 < 3.10

1. 访问 https://www.python.org/downloads/ 下载 Python 3.12 或 3.13
2. 安装时**务必勾选 "Add Python to PATH"**
3. 安装完成后**关闭并重新打开 Trae**，再次运行 `python --version` 验证

> **注意**：如果安装 Python 时 Trae 处于打开状态，需要重启 Trae 才能识别到新的 PATH。

---

## 第三步：创建虚拟环境

在 Trae 终端中依次执行：

```powershell
python -m venv .venv
```

创建完成后激活虚拟环境：

```powershell
.venv\Scripts\activate
```

激活成功后终端提示符前会显示 `(.venv)`，例如：

```
(.venv) PS E:\AI RAN Demo>
```

> **macOS / Linux 用户**：激活命令为 `source .venv/bin/activate`

---

## 第四步：安装项目依赖

```powershell
pip install -r requirements.txt
```

以下 8 个包将被安装（含其间接依赖）：

| 包名 | 版本 | 用途 |
|------|------|------|
| streamlit | ≥1.30.0 | Web 仪表盘 |
| plotly | ≥5.18.0 | KPI 交互图表 |
| pandas | ≥2.0.0 | 数据处理 |
| numpy | ≥1.24.0 | 数值计算 |
| pydantic | ≥2.0.0 | 数据校验 |
| PyYAML | ≥6.0.0 | 场景配置 |
| pytest | ≥7.0.0 | 测试框架 |
| kaleido | ≥0.2.1 | 图表导出 |

安装过程约 1-3 分钟。

---

## 第五步：验证环境

### 5.1 快速导入检查

```powershell
python -c "import streamlit; import plotly; import pandas; import numpy; import pydantic; import yaml; print('依赖全部就绪')"
```

预期输出：`依赖全部就绪`

### 5.2 运行全部测试

```powershell
python -m pytest tests/ -v --tb=short
```

预期结果：

```
11 passed in 1.xxs
```

> 共 11 个测试文件、119 个测试用例，全部通过。

---

## 第六步：启动系统

```powershell
streamlit run uran/dashboard/research_app.py --server.headless true
```

启动成功后终端显示：

```
Local URL: http://localhost:8501
Network URL: http://<你的IP>:8501
```

在浏览器打开 `http://localhost:8501`，应看到**系统首页**：

- 左侧边栏：LOGO + "基于微内核的自演进 RAN 原型" + 8 个页面导航 + 频段配置选择器
- 右侧主区域：系统定位与核心能力介绍

### 快速验证清单

按以下顺序验证各模块功能正常：

| 操作 | 预期结果 |
|------|----------|
| 左侧导航切到「模块1」→ 选场景 → 顶部点「初始化」→「全部」 | KPI 曲线和拓扑图正常渲染 |
| 左侧边栏底部切换频段（如 n79）→ 重新「初始化」→「全部」 | KPI 数值随频段变化 |
| 切换到「模块2」→ 输入需求 → 点「生成方案」 | 显示候选方案列表 |
| 切换到「端到端」→ 输入需求 → 点「运行全流程」 | 六阶段完整展示 |

### 停止系统

在终端按 `Ctrl+C`。

---

## 第七步（可选）：创建快捷启动脚本

在项目根目录创建 `start.bat`（内容如下），之后双击即可启动：

```bat
@echo off
call .venv\Scripts\activate.bat
echo ==========================================
echo   基于微内核的自演进 RAN 原型
echo   Alpha 1.0
echo ==========================================
echo.
echo 正在启动系统...
echo 浏览器打开 http://localhost:8501
echo 按 Ctrl+C 停止服务
echo.
streamlit run uran/dashboard/research_app.py --server.headless true
pause
```

---

## 常见问题

### Q1: `pip install` 报超时或网络错误

```powershell
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q2: `streamlit: command not found`

使用以下方式替代：

```powershell
python -m streamlit run uran/dashboard/research_app.py
```

### Q3: 端口 8501 被占用

```powershell
streamlit run uran/dashboard/research_app.py --server.port 8502
```

### Q4: `kaleido` 安装失败

不影响核心功能，仅影响静态图表导出。可跳过：

```powershell
pip install -r requirements.txt --ignore-installed kaleido
```

或直接编辑 `requirements.txt` 删除 `kaleido` 行后重新安装。

### Q5: 导入模块报 `ModuleNotFoundError`

确认当前工作目录是项目根目录（包含 `uran/` 和 `tests/` 文件夹的那个目录）：

```powershell
pwd
# 应输出: E:\AI RAN Demo (或你的实际路径)

ls uran
# 应能看到 __init__.py 等文件
```

---

> **迁移完成后**：系统已在目标电脑上完整运行，包含 8 个 Web 页面、4 个科研场景配置、119 个自动化测试用例。
