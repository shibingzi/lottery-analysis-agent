@echo off
chcp 65001 >nul
:: =============================================================================
:: Lottery Analysis Agent 启动脚本 (Windows)
:: =============================================================================
:: 用法:
::   start-lottery-agent.bat              交互式模式
::   start-lottery-agent.bat --fetch      获取最新数据
::   start-lottery-agent.bat --analyze    运行分析
::   start-lottery-agent.bat --help       显示帮助
:: =============================================================================

setlocal EnableDelayedExpansion

set "PROJECT_NAME=Lottery Analysis Agent"
set "VERSION=1.0.0"
set "SCRIPT_DIR=%~dp0"

:: 检测Python命令
set "PYTHON_CMD="
for %%A in (python3 python py) do (
    where %%A >nul 2>&1
    if !errorlevel! == 0 (
        set "PYTHON_CMD=%%A"
        goto :found_python
    )
)
:found_python

:: 显示Banner
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                                                          ║
echo ║              Lottery Analysis Agent v%VERSION%                   ║
echo ║                                                          ║
echo ║        支持双色球(SSQ)、大乐透(DLT)数据分析                 ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

:: 显示免责声明
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ⚠️  重要声明：
echo.
echo    彩票开奖是完全随机的独立事件
echo    历史数据对未来开奖没有任何预测价值
echo    本系统所有分析仅供娱乐参考
echo    不构成任何形式的投注建议
echo    请理性购彩，量力而行
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

:: 检查Python
if "!PYTHON_CMD!"=="" (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)
echo [✓] Python: !PYTHON_CMD!

:: 检查并创建目录
if not exist "%SCRIPT_DIR%data" (
    echo [信息] 创建数据目录...
    mkdir "%SCRIPT_DIR%data\ssq" 2>nul
    mkdir "%SCRIPT_DIR%data\dlt" 2>nul
    mkdir "%SCRIPT_DIR%data\cache" 2>nul
)

if not exist "%SCRIPT_DIR%logs" (
    mkdir "%SCRIPT_DIR%logs" 2>nul
)

echo [✓] 依赖检查完成
echo.

:: 处理命令行参数
if "%~1"=="--fetch" goto :fetch_data
if "%~1"=="-f" goto :fetch_data
if "%~1"=="--latest" goto :show_latest
if "%~1"=="-l" goto :show_latest
if "%~1"=="--help" goto :show_help
if "%~1"=="-h" goto :show_help
if "%~1"=="" goto :interactive_menu
echo [错误] 未知选项: %~1
goto :show_help

:: 获取数据
:fetch_data
echo [信息] 获取最新开奖数据...
echo.
echo 获取双色球数据...
!PYTHON_CMD! "%SCRIPT_DIR%scripts\fetch_lottery_data.py" --type ssq --limit 100
echo.
echo 获取大乐透数据...
!PYTHON_CMD! "%SCRIPT_DIR%scripts\fetch_lottery_data.py" --type dlt --limit 100
echo.
echo [✓] 数据获取完成
pause
goto :end

:: 显示最新开奖
:show_latest
echo [信息] 查看最新开奖结果...
echo.
echo 双色球最新开奖:
!PYTHON_CMD! "%SCRIPT_DIR%scripts\fetch_lottery_data.py" --type ssq --latest
echo.
echo 大乐透最新开奖:
!PYTHON_CMD! "%SCRIPT_DIR%scripts\fetch_lottery_data.py" --type dlt --latest
pause
goto :end

:: 交互式菜单
:interactive_menu
:menu_loop
cls
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo   请选择操作:
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo   1. 刷新最新开奖数据
echo   2. 查看最新开奖结果
echo   3. 运行数据分析
echo   4. 固定号码分析
echo   5. 机选号码生成
echo   6. 生成分析报告
echo   7. 查看使用帮助
echo   0. 退出
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
set /p choice="请输入选项 [0-7]: "

if "%choice%"=="1" goto :menu_fetch
if "%choice%"=="2" goto :menu_latest
if "%choice%"=="3" goto :menu_analyze
if "%choice%"=="4" goto :menu_fixed
if "%choice%"=="5" goto :menu_generate
if "%choice%"=="6" goto :menu_report
if "%choice%"=="7" goto :menu_help
if "%choice%"=="0" goto :end

echo [错误] 无效选项，请重新选择
pause
goto :menu_loop

:menu_fetch
echo.
echo [信息] 获取双色球数据...
!PYTHON_CMD! "%SCRIPT_DIR%scripts\fetch_lottery_data.py" --type ssq --limit 100
echo.
echo [信息] 获取大乐透数据...
!PYTHON_CMD! "%SCRIPT_DIR%scripts\fetch_lottery_data.py" --type dlt --limit 100
echo.
pause
goto :menu_loop

:menu_latest
echo.
echo 双色球最新开奖:
!PYTHON_CMD! "%SCRIPT_DIR%scripts\fetch_lottery_data.py" --type ssq --latest
echo.
echo 大乐透最新开奖:
!PYTHON_CMD! "%SCRIPT_DIR%scripts\fetch_lottery_data.py" --type dlt --latest
echo.
pause
goto :menu_loop

:menu_analyze
echo.
echo [信息] 数据分析功能开发中...
pause
goto :menu_loop

:menu_fixed
echo.
echo [信息] 固定号码分析功能开发中...
pause
goto :menu_loop

:menu_generate
echo.
echo [信息] 号码生成功能开发中...
pause
goto :menu_loop

:menu_report
echo.
echo [信息] 报告生成功能开发中...
pause
goto :menu_loop

:menu_help
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo   使用帮助
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 可用命令:
echo   start-lottery-agent.bat              启动交互式菜单
echo   start-lottery-agent.bat --fetch      获取最新数据
echo   start-lottery-agent.bat --latest     查看最新开奖
echo   start-lottery-agent.bat --help       显示此帮助
echo.
echo 支持的彩种:
echo   • 双色球 (SSQ) - 每周二、四、日开奖
echo   • 大乐透 (DLT) - 每周一、三、六开奖
echo.
echo 功能说明:
echo   1. 数据获取 - 自动获取最新开奖结果
echo   2. 统计分析 - 热号/冷号、遗漏值等分析
echo   3. 固定号码 - 分析您指定的号码组合
echo   4. 号码生成 - 随机生成号码（娱乐）
echo.
echo ⚠️ 免责声明:
echo    本系统仅供娱乐，不构成投注建议。
echo    彩票开奖完全随机，请理性购彩。
echo.
pause
goto :menu_loop

:: 显示帮助
:show_help
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo   使用帮助
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 可用命令:
echo   start-lottery-agent.bat              启动交互式菜单
echo   start-lottery-agent.bat --fetch      获取最新数据
echo   start-lottery-agent.bat --latest     查看最新开奖
echo   start-lottery-agent.bat --help       显示此帮助
echo.
echo 支持的彩种:
echo   • 双色球 (SSQ) - 每周二、四、日开奖
echo   • 大乐透 (DLT) - 每周一、三、六开奖
echo.
echo ⚠️ 免责声明:
echo    本系统仅供娱乐，不构成投注建议。
echo    彩票开奖完全随机，请理性购彩。
echo.
pause
goto :end

:end
echo.
echo 感谢使用 %PROJECT_NAME%，再见！
echo.
endlocal
