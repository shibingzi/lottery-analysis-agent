# 彩票分析助手 - Python运行指南

## 问题描述
Windows Store 版本的 Python 存在兼容性问题，导致运行脚本时**没有输出**。

## 根本原因
```bash
# Windows Store Python 路径
/c/Users/yjw_3/AppData/Local/Microsoft/WindowsApps/python3
# 实际指向: AppInstallerPythonRedirector.exe (重定向器)
# 这会导致 Git Bash 中运行 Python 时没有输出
```

## 解决方案

### 方法 1: 使用正确的 Python 路径 ✅ (推荐)

系统上已安装的 Python 路径：

```bash
/c/Users/yjw_3/AppData/Local/uv/cache/archive-v0/-UGgKGUN9ljBRsbPMnxWj/Scripts/python.exe
```

**使用方法：**

```bash
# 1. 设置环境变量
export PYTHONIOENCODING=utf-8

# 2. 使用完整路径运行
/c/Users/yjw_3/AppData/Local/uv/cache/archive-v0/-UGgKGUN9ljBRsbPMnxWj/Scripts/python.exe run_demo.py
```

### 方法 2: 使用提供的启动脚本 ✅ (最简单)

```bash
# 在项目目录下运行
./run.sh demo      # 运行演示
./run.sh ssq 50    # 分析双色球50期
./run.sh dlt 30    # 分析大乐透30期
./run.sh report ssq # 生成HTML报告
```

### 方法 3: 创建别名

在 `~/.bashrc` 或 `~/.bash_profile` 中添加：

```bash
# Python UTF-8 编码
export PYTHONIOENCODING=utf-8

# Python 路径别名
alias py='/c/Users/yjw_3/AppData/Local/uv/cache/archive-v0/-UGgKGUN9ljBRsbPMnxWj/Scripts/python.exe'

# 然后就可以使用
py run_demo.py
py scripts/analyze_history.py --type ssq --periods 100
```

## 验证修复

运行以下命令验证：

```bash
export PYTHONIOENCODING=utf-8
PYTHON=/c/Users/yjw_3/AppData/Local/uv/cache/archive-v0/-UGgKGUN9ljBRsbPMnxWj/Scripts/python.exe
$PYTHON --version  # 应该显示 Python 3.13.2
$PYTHON run_demo.py  # 应该显示完整分析结果
```

## 常见错误

### 错误 1: UnicodeEncodeError
```
UnicodeEncodeError: 'gbk' codec can't encode character
```
**解决**: 设置 `export PYTHONIOENCODING=utf-8`

### 错误 2: 没有输出
```bash
python3 test.py  # 没有任何输出
```
**解决**: 使用上面提到的正确 Python 路径

### 错误 3: 命令未找到
```
bash: python: command not found
```
**解决**: 使用完整路径或创建别名

## 快速开始

```bash
# 1. 进入项目目录
cd /d/AGENT/lottery-analysis-agent

# 2. 运行演示 (推荐)
./run.sh demo

# 3. 或者手动运行
export PYTHONIOENCODING=utf-8
PYTHON=/c/Users/yjw_3/AppData/Local/uv/cache/archive-v0/-UGgKGUN9ljBRsbPMnxWj/Scripts/python.exe
$PYTHON run_demo.py
```

## 在 Cherry Studio 中使用

如果要在 Cherry Studio 中使用，需要配置命令工具：

```json
{
  "name": "彩票分析",
  "command": "bash",
  "args": [
    "-c",
    "export PYTHONIOENCODING=utf-8 && /c/Users/yjw_3/AppData/Local/uv/cache/archive-v0/-UGgKGUN9ljBRsbPMnxWj/Scripts/python.exe D:/AGENT/lottery-analysis-agent/run_demo.py"
  ]
}
```

---

**问题解决日期**: 2026-02-07  
**Python版本**: 3.13.2  
**状态**: ✅ 已修复
