#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彩票分析助手 - 自动化测试脚本
运行方式: python test_system.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

# 测试计数器
class TestCounter:
    def __init__(self):
        self.passed = 0
        self.failed = 0
    
    def add_pass(self):
        self.passed += 1
    
    def add_fail(self):
        self.failed += 1
    
    def total(self):
        return self.passed + self.failed
    
    def summary(self):
        print(f"\n{'='*60}")
        print(f"测试结果: {self.passed}/{self.total()} 通过")
        if self.failed == 0:
            print_success("所有测试通过！")
        else:
            print_error(f"{self.failed} 项测试失败")
        print(f"{'='*60}")

counter = TestCounter()
PROJECT_ROOT = Path(__file__).parent.absolute()

# ============ 测试1: 数据文件检查 ============
def test_data_files():
    print_info("测试1: 检查数据文件...")
    
    try:
        # 检查双色球
        ssq_file = PROJECT_ROOT / "data" / "ssq" / "history.json"
        if not ssq_file.exists():
            print_error(f"文件不存在: {ssq_file}")
            counter.add_fail()
            return False
        
        with open(ssq_file, 'r', encoding='utf-8') as f:
            ssq_data = json.load(f)
        
        if len(ssq_data) < 5:
            print_error(f"双色球数据不足: {len(ssq_data)} 期")
            counter.add_fail()
            return False
        
        # 检查必要字段
        required_fields = ['lottery_type', 'issue', 'draw_date', 'red_balls', 'blue_ball']
        if not all(field in ssq_data[0] for field in required_fields):
            print_error("双色球数据缺少必要字段")
            counter.add_fail()
            return False
        
        print_success(f"双色球数据: {len(ssq_data)} 期，字段完整")
        
        # 检查大乐透
        dlt_file = PROJECT_ROOT / "data" / "dlt" / "history.json"
        if not dlt_file.exists():
            print_error(f"文件不存在: {dlt_file}")
            counter.add_fail()
            return False
        
        with open(dlt_file, 'r', encoding='utf-8') as f:
            dlt_data = json.load(f)
        
        if len(dlt_data) < 5:
            print_error(f"大乐透数据不足: {len(dlt_data)} 期")
            counter.add_fail()
            return False
        
        required_fields = ['lottery_type', 'issue', 'draw_date', 'front_zone', 'back_zone']
        if not all(field in dlt_data[0] for field in required_fields):
            print_error("大乐透数据缺少必要字段")
            counter.add_fail()
            return False
        
        print_success(f"大乐透数据: {len(dlt_data)} 期，字段完整")
        counter.add_pass()
        return True
        
    except Exception as e:
        print_error(f"数据文件测试失败: {e}")
        counter.add_fail()
        return False

# ============ 测试2: 分析器功能 ============
def test_analyzer():
    print_info("\n测试2: 测试分析器功能...")
    
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        from analyze_history import LotteryAnalyzer
        
        # 测试双色球
        print_info("  测试双色球分析...")
        analyzer = LotteryAnalyzer("ssq")
        result = analyzer.full_analysis(10)
        
        assert result['periods_analyzed'] == 10, "分析期数不正确"
        assert 'hot_cold' in result, "缺少热号冷号分析"
        assert 'missing' in result, "缺少遗漏值分析"
        assert 'odd_even' in result, "缺少奇偶比分析"
        assert 'big_small' in result, "缺少大小比分析"
        
        print_success("双色球分析正常")
        
        # 测试大乐透
        print_info("  测试大乐透分析...")
        analyzer2 = LotteryAnalyzer("dlt")
        result2 = analyzer2.full_analysis(10)
        
        assert result2['periods_analyzed'] == 10, "分析期数不正确"
        assert 'hot_cold' in result2, "缺少热号冷号分析"
        
        print_success("大乐透分析正常")
        counter.add_pass()
        return result
        
    except Exception as e:
        print_error(f"分析器测试失败: {e}")
        import traceback
        traceback.print_exc()
        counter.add_fail()
        return None

# ============ 测试3: 固定号码分析 ============
def test_fixed_numbers(analysis_result):
    print_info("\n测试3: 测试固定号码分析...")
    
    if not analysis_result:
        print_warning("跳过测试（无分析数据）")
        return False
    
    try:
        from generate_fixed_numbers import LotteryPredictor
        
        predictor = LotteryPredictor("ssq")
        
        # 测试号码验证
        is_valid, msg = predictor.validate_numbers([7, 18, 25], "red")
        assert is_valid, f"红球验证失败: {msg}"
        print_success("红球验证通过")
        
        is_valid, msg = predictor.validate_numbers([14], "blue")
        assert is_valid, f"蓝球验证失败: {msg}"
        print_success("蓝球验证通过")
        
        # 测试号码生成
        numbers = predictor.generate_numbers(count=5)
        assert len(numbers) == 5, "生成的号码数量不正确"
        assert all('red_balls' in n and 'blue_ball' in n for n in numbers), "号码格式不正确"
        
        print_success(f"生成 {len(numbers)} 组号码")
        counter.add_pass()
        return True
        
    except Exception as e:
        print_error(f"固定号码测试失败: {e}")
        import traceback
        traceback.print_exc()
        counter.add_fail()
        return False

# ============ 测试4: HTML报告生成 ============
def test_report_generator(analysis_result):
    print_info("\n测试4: 测试HTML报告生成...")
    
    if not analysis_result:
        print_warning("跳过测试（无分析数据）")
        return False
    
    try:
        from generate_report import ReportGenerator
        
        generator = ReportGenerator("ssq")
        html = generator.generate(analysis_result, fixed_red=[7, 18, 25], fixed_blue=[14])
        
        # 检查HTML内容
        checks = [
            ('<!DOCTYPE html>', 'HTML声明'),
            ('<html', 'HTML标签'),
            ('</html>', '结束标签'),
            ('双色球分析报告', '标题'),
            ('hotNumbersChart', '热号图表'),
            ('热号TOP10', '热号表格'),
            ('遗漏值', '遗漏值分析'),
            ('免责声明', '免责声明'),
        ]
        
        passed = 0
        for keyword, desc in checks:
            if keyword in html:
                passed += 1
            else:
                print_warning(f"  缺少: {desc}")
        
        if passed >= 6:
            print_success(f"HTML报告内容完整 ({passed}/{len(checks)})")
        else:
            print_warning(f"HTML报告内容不完整 ({passed}/{len(checks)})")
        
        # 保存报告
        output_path = PROJECT_ROOT / "reports" / "test_report.html"
        output_path.parent.mkdir(exist_ok=True)
        saved = generator.save_report(html, str(output_path))
        
        file_size = len(html)
        print_success(f"报告已保存: {saved} ({file_size} 字符)")
        
        counter.add_pass()
        return True
        
    except Exception as e:
        print_error(f"报告生成测试失败: {e}")
        import traceback
        traceback.print_exc()
        counter.add_fail()
        return False

# ============ 测试5: Skills文档 ============
def test_skills():
    print_info("\n测试5: 检查Skills文档...")
    
    skills = [
        ".claude/skills/skill_lottery_data_fetcher.md",
        ".claude/skills/skill_lottery_analyzer.md",
        ".claude/skills/skill_lottery_predictor.md"
    ]
    
    all_exist = True
    for skill in skills:
        path = PROJECT_ROOT / skill
        if path.exists():
            size = path.stat().st_size
            print_success(f"{skill} ({size} bytes)")
        else:
            print_error(f"{skill} 不存在")
            all_exist = False
    
    if all_exist:
        counter.add_pass()
        return True
    else:
        counter.add_fail()
        return False

# ============ 测试6: 配置文件 ============
def test_config():
    print_info("\n测试6: 检查配置文件...")
    
    try:
        config_file = PROJECT_ROOT / ".claude" / "config" / "lottery_config.json"
        if not config_file.exists():
            print_error(f"配置文件不存在: {config_file}")
            counter.add_fail()
            return False
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        assert 'lottery_types' in config, "缺少lottery_types"
        assert 'ssq' in config['lottery_types'], "缺少ssq配置"
        assert 'dlt' in config['lottery_types'], "缺少dlt配置"
        
        print_success("配置文件完整")
        counter.add_pass()
        return True
        
    except Exception as e:
        print_error(f"配置文件测试失败: {e}")
        counter.add_fail()
        return False

# ============ 主函数 ============
def main():
    print(f"{'='*60}")
    print("🧪 彩票分析助手 - 系统测试")
    print(f"{'='*60}")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"项目路径: {PROJECT_ROOT}")
    print()
    
    # 运行所有测试
    test_data_files()
    analysis_result = test_analyzer()
    
    if analysis_result:
        test_fixed_numbers(analysis_result)
        test_report_generator(analysis_result)
    else:
        print_warning("\n跳过依赖分析数据的测试")
    
    test_skills()
    test_config()
    
    # 打印总结
    counter.summary()
    
    # 返回退出码
    return 0 if counter.failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
