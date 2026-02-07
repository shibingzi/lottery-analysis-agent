#!/bin/bash
# =============================================================================
# Lottery Analysis Agent 启动脚本
# =============================================================================
# 用法:
#   ./start-lottery-agent.sh              # 交互式模式
#   ./start-lottery-agent.sh --fetch      # 获取最新数据
#   ./start-lottery-agent.sh --analyze    # 运行分析
#   ./start-lottery-agent.sh --help       # 显示帮助
# =============================================================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 项目目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="Lottery Analysis Agent"
VERSION="1.0.0"

# 显示Banner
echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║         🎱 彩票数据分析 Agent v${VERSION}                  ║"
echo "║                                                          ║"
echo "║     支持双色球(SSQ)、大乐透(DLT)数据分析                  ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# 显示免责声明
echo -e "${YELLOW}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚠️  重要声明："
echo ""
echo "   彩票开奖是完全随机的独立事件"
echo "   历史数据对未来开奖没有任何预测价值"
echo "   本系统所有分析仅供娱乐参考"
echo "   不构成任何形式的投注建议"
echo "   请理性购彩，量力而行"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${NC}"
echo ""

# 检查依赖
check_dependencies() {
    echo -e "${BLUE}🔍 检查依赖...${NC}"
    
    # 检查Python
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        echo -e "${RED}❌ 错误: 未找到 Python，请先安装 Python 3.8+${NC}"
        exit 1
    fi
    
    PYTHON_CMD=$(command -v python3 || command -v python)
    echo -e "${GREEN}✅ Python: $PYTHON_CMD${NC}"
    
    # 检查数据目录
    if [ ! -d "${SCRIPT_DIR}/data" ]; then
        echo -e "${BLUE}📁 创建数据目录...${NC}"
        mkdir -p "${SCRIPT_DIR}/data/ssq"
        mkdir -p "${SCRIPT_DIR}/data/dlt"
        mkdir -p "${SCRIPT_DIR}/data/cache"
    fi
    
    # 检查日志目录
    if [ ! -d "${SCRIPT_DIR}/logs" ]; then
        mkdir -p "${SCRIPT_DIR}/logs"
    fi
    
    echo -e "${GREEN}✅ 依赖检查完成${NC}"
    echo ""
}

# 获取数据
fetch_data() {
    echo -e "${BLUE}📥 获取最新开奖数据...${NC}"
    
    cd "${SCRIPT_DIR}"
    
    echo -e "${CYAN}获取双色球数据...${NC}"
    $PYTHON_CMD scripts/fetch_lottery_data.py --type ssq --limit 100
    
    echo ""
    echo -e "${CYAN}获取大乐透数据...${NC}"
    $PYTHON_CMD scripts/fetch_lottery_data.py --type dlt --limit 100
    
    echo ""
    echo -e "${GREEN}✅ 数据获取完成${NC}"
}

# 显示最新开奖
show_latest() {
    echo -e "${BLUE}🎱 查看最新开奖结果${NC}"
    echo ""
    
    cd "${SCRIPT_DIR}"
    
    echo -e "${CYAN}双色球最新开奖:${NC}"
    $PYTHON_CMD scripts/fetch_lottery_data.py --type ssq --latest
    
    echo ""
    echo -e "${CYAN}大乐透最新开奖:${NC}"
    $PYTHON_CMD scripts/fetch_lottery_data.py --type dlt --latest
}

# 交互式菜单
interactive_menu() {
    while true; do
        echo ""
        echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${CYAN}  请选择操作:${NC}"
        echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo "  1. 🔄 获取最新开奖数据"
        echo "  2. 🎱 查看最新开奖结果"
        echo "  3. 📊 运行数据分析"
        echo "  4. 🔢 固定号码分析"
        echo "  5. 🎲 机选号码生成"
        echo "  6. 📄 生成分析报告"
        echo "  7. ❓ 查看使用帮助"
        echo "  0. 🚪 退出"
        echo ""
        echo -n "请输入选项 [0-7]: "
        
        read -r choice
        
        case $choice in
            1)
                fetch_data
                ;;
            2)
                show_latest
                ;;
            3)
                echo -e "${YELLOW}📊 数据分析功能开发中...${NC}"
                ;;
            4)
                echo -e "${YELLOW}🔢 固定号码分析功能开发中...${NC}"
                ;;
            5)
                echo -e "${YELLOW}🎲 号码生成功能开发中...${NC}"
                ;;
            6)
                echo -e "${YELLOW}📄 报告生成功能开发中...${NC}"
                ;;
            7)
                show_help
                ;;
            0)
                echo ""
                echo -e "${GREEN}感谢使用 ${PROJECT_NAME}，再见！👋${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}❌ 无效选项，请重新选择${NC}"
                ;;
        esac
    done
}

# 显示帮助
show_help() {
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}  使用帮助${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "可用命令:"
    echo "  ./start-lottery-agent.sh              启动交互式菜单"
    echo "  ./start-lottery-agent.sh --fetch      获取最新数据"
    echo "  ./start-lottery-agent.sh --latest     查看最新开奖"
    echo "  ./start-lottery-agent.sh --help       显示此帮助"
    echo ""
    echo "支持的彩种:"
    echo "  • 双色球 (SSQ) - 每周二、四、日开奖"
    echo "  • 大乐透 (DLT) - 每周一、三、六开奖"
    echo ""
    echo "功能说明:"
    echo "  1. 数据获取 - 自动获取最新开奖结果"
    echo "  2. 统计分析 - 热号/冷号、遗漏值等分析"
    echo "  3. 固定号码 - 分析您指定的号码组合"
    echo "  4. 号码生成 - 随机生成号码（娱乐）"
    echo ""
    echo -e "${YELLOW}⚠️  免责声明:${NC}"
    echo "   本系统仅供娱乐，不构成投注建议。"
    echo "   彩票开奖完全随机，请理性购彩。"
    echo ""
}

# 主函数
main() {
    # 检查依赖
    check_dependencies
    
    # 处理命令行参数
    case "${1:-}" in
        --fetch|-f)
            fetch_data
            ;;
        --latest|-l)
            show_latest
            ;;
        --help|-h)
            show_help
            ;;
        "")
            interactive_menu
            ;;
        *)
            echo -e "${RED}❌ 未知选项: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
