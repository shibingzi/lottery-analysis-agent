#!/bin/bash
# 彩票分析助手启动脚本 (Git Bash)

# 设置正确的Python路径
PYTHON_PATH="/c/Users/yjw_3/AppData/Local/uv/cache/archive-v0/-UGgKGUN9ljBRsbPMnxWj/Scripts/python.exe"

# 设置UTF-8编码
export PYTHONIOENCODING=utf-8

# 进入项目目录
cd /d/AGENT/lottery-analysis-agent

echo "================================================"
echo "🎱 彩票分析助手"
echo "================================================"
echo ""

# 检查参数
if [ $# -eq 0 ]; then
    echo "可用命令:"
    echo "  demo          - 运行演示分析"
    echo "  ssq [期数]    - 分析双色球 (默认23期)"
    echo "  dlt [期数]    - 分析大乐透 (默认23期)"
    echo "  report [类型] - 生成HTML报告"
    echo "  test          - 运行测试"
    echo ""
    read -p "请输入命令: " CMD
else
    CMD=$1
fi

case $CMD in
    demo)
        echo "运行演示分析..."
        $PYTHON_PATH run_demo.py
        ;;
    ssq)
        PERIODS=${2:-23}
        echo "分析双色球最近 $PERIODS 期..."
        $PYTHON_PATH scripts/analyze_history.py --type ssq --periods $PERIODS
        ;;
    dlt)
        PERIODS=${2:-23}
        echo "分析大乐透最近 $PERIODS 期..."
        $PYTHON_PATH scripts/analyze_history.py --type dlt --periods $PERIODS
        ;;
    report)
        TYPE=${2:-ssq}
        mkdir -p reports
        echo "生成 $TYPE HTML报告..."
        $PYTHON_PATH scripts/generate_report.py --type $TYPE --periods 23 --output reports/${TYPE}_report.html
        echo "报告已保存到: reports/${TYPE}_report.html"
        ;;
    test)
        echo "运行系统测试..."
        $PYTHON_PATH test_system.py
        ;;
    *)
        echo "未知命令: $CMD"
        echo "使用: demo, ssq, dlt, report, test"
        ;;
esac
