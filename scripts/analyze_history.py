#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彩票历史数据分析脚本
支持双色球(SSQ)和大乐透(DLT)的统计分析

用法:
    python analyze_history.py --type ssq --periods 100
    python analyze_history.py --type dlt --metric hot-cold
    python analyze_history.py --type ssq --all
"""

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# 彩票配置
LOTTERY_CONFIG = {
    "ssq": {
        "name": "双色球",
        "red_range": (1, 33),
        "blue_range": (1, 16),
        "red_count": 6,
        "blue_count": 1,
        "data_file": DATA_DIR / "ssq" / "history.json",
        "big_boundary": 17,  # 大小分界
        "zones": [(1, 11), (12, 22), (23, 33)]  # 三区
    },
    "dlt": {
        "name": "大乐透",
        "front_range": (1, 35),
        "back_range": (1, 12),
        "front_count": 5,
        "back_count": 2,
        "data_file": DATA_DIR / "dlt" / "history.json",
        "big_boundary": 18,  # 大小分界
        "zones": [(1, 7), (8, 14), (15, 21), (22, 28), (29, 35)]  # 五区
    }
}


class LotteryAnalyzer:
    """彩票数据分析器"""
    
    def __init__(self, lottery_type: str):
        self.lottery_type = lottery_type.lower()
        config = LOTTERY_CONFIG.get(self.lottery_type)
        if not config:
            raise ValueError(f"不支持的彩票类型: {lottery_type}")
        
        self.config: Dict = config
        self.data: List[Dict] = self._load_data()
    
    def _load_data(self) -> List[Dict]:
        """加载历史数据"""
        if not self.config["data_file"].exists():
            raise FileNotFoundError(f"数据文件不存在: {self.config['data_file']}")
        
        with open(self.config["data_file"], 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 按期号降序排序
        data.sort(key=lambda x: x.get("issue", ""), reverse=True)
        return data
    
    def get_periods(self, n: int) -> List[Dict]:
        """获取最近N期数据"""
        return self.data[:n]
    
    def analyze_hot_cold(self, periods: int = 100) -> Dict:
        """热号冷号分析"""
        data = self.get_periods(periods)
        
        if self.lottery_type == "ssq":
            # 统计红球
            red_balls = []
            blue_balls = []
            for record in data:
                red_balls.extend(record.get("red_balls", []))
                blue_balls.append(record.get("blue_ball"))
            
            red_counter = Counter(red_balls)
            blue_counter = Counter(blue_balls)
            
            return {
                "red_balls": {
                    "hot": red_counter.most_common(10),
                    "cold": red_counter.most_common()[:-11:-1]
                },
                "blue_ball": {
                    "hot": blue_counter.most_common(5),
                    "cold": blue_counter.most_common()[:-6:-1]
                }
            }
        else:  # dlt
            front_zone = []
            back_zone = []
            for record in data:
                front_zone.extend(record.get("front_zone", []))
                back_zone.extend(record.get("back_zone", []))
            
            front_counter = Counter(front_zone)
            back_counter = Counter(back_zone)
            
            return {
                "front_zone": {
                    "hot": front_counter.most_common(10),
                    "cold": front_counter.most_common()[:-11:-1]
                },
                "back_zone": {
                    "hot": back_counter.most_common(5),
                    "cold": back_counter.most_common()[:-6:-1]
                }
            }
    
    def analyze_missing(self, periods: int = 100) -> Dict:
        """遗漏值分析"""
        data = self.get_periods(periods)
        
        if self.lottery_type == "ssq":
            red_range = range(1, 34)
            blue_range = range(1, 17)
            
            red_missing = {n: periods for n in red_range}
            blue_missing = {n: periods for n in blue_range}
            
            for i, record in enumerate(data):
                for ball in record.get("red_balls", []):
                    if red_missing[ball] == periods:
                        red_missing[ball] = i
                
                blue = record.get("blue_ball")
                if blue is not None and blue_missing[blue] == periods:
                    blue_missing[blue] = i
            
            return {
                "red_balls": dict(sorted(red_missing.items(), key=lambda x: -x[1])[:10]),
                "blue_ball": dict(sorted(blue_missing.items(), key=lambda x: -x[1])[:5])
            }
        else:  # dlt
            front_range = range(1, 36)
            back_range = range(1, 13)
            
            front_missing = {n: periods for n in front_range}
            back_missing = {n: periods for n in back_range}
            
            for i, record in enumerate(data):
                for ball in record.get("front_zone", []):
                    if front_missing[ball] == periods:
                        front_missing[ball] = i
                
                for ball in record.get("back_zone", []):
                    if back_missing[ball] == periods:
                        back_missing[ball] = i
            
            return {
                "front_zone": dict(sorted(front_missing.items(), key=lambda x: -x[1])[:10]),
                "back_zone": dict(sorted(back_missing.items(), key=lambda x: -x[1])[:5])
            }
    
    def analyze_odd_even(self, periods: int = 100) -> Dict:
        """奇偶比分析"""
        data = self.get_periods(periods)
        ratios = Counter()
        
        for record in data:
            if self.lottery_type == "ssq":
                numbers = record.get("red_balls", [])
            else:
                numbers = record.get("front_zone", [])
            
            odd = sum(1 for n in numbers if n % 2 == 1)
            even = len(numbers) - odd
            ratio = f"{odd}:{even}"
            ratios[ratio] += 1
        
        return dict(ratios.most_common())
    
    def analyze_big_small(self, periods: int = 100) -> Dict:
        """大小比分析"""
        data = self.get_periods(periods)
        boundary = self.config["big_boundary"]
        ratios = Counter()
        
        for record in data:
            if self.lottery_type == "ssq":
                numbers = record.get("red_balls", [])
            else:
                numbers = record.get("front_zone", [])
            
            big = sum(1 for n in numbers if n >= boundary)
            small = len(numbers) - big
            ratio = f"{big}:{small}"
            ratios[ratio] += 1
        
        return dict(ratios.most_common())
    
    def analyze_consecutive(self, periods: int = 100) -> Dict:
        """连号分析"""
        data = self.get_periods(periods)
        consecutive_count = 0
        consecutive_patterns = Counter()
        
        for record in data:
            if self.lottery_type == "ssq":
                numbers = sorted(record.get("red_balls", []))
            else:
                numbers = sorted(record.get("front_zone", []))
            
            # 查找连号
            i = 0
            current_consecutive = []
            while i < len(numbers):
                if not current_consecutive or numbers[i] == current_consecutive[-1] + 1:
                    current_consecutive.append(numbers[i])
                else:
                    if len(current_consecutive) >= 2:
                        consecutive_count += 1
                        pattern = f"{current_consecutive[0]}-{current_consecutive[-1]}"
                        consecutive_patterns[pattern] += 1
                    current_consecutive = [numbers[i]]
                i += 1
            
            if len(current_consecutive) >= 2:
                consecutive_count += 1
                pattern = f"{current_consecutive[0]}-{current_consecutive[-1]}"
                consecutive_patterns[pattern] += 1
        
        return {
            "consecutive_periods": consecutive_count,
            "consecutive_rate": round(consecutive_count / periods * 100, 2),
            "top_patterns": consecutive_patterns.most_common(5)
        }
    
    def analyze_zones(self, periods: int = 100) -> Dict:
        """区间分布分析"""
        data = self.get_periods(periods)
        zones = self.config["zones"]
        zone_distribution = defaultdict(list)
        
        for record in data:
            if self.lottery_type == "ssq":
                numbers = record.get("red_balls", [])
            else:
                numbers = record.get("front_zone", [])
            
            zone_counts = []
            for i, (start, end) in enumerate(zones, 1):
                count = sum(1 for n in numbers if start <= n <= end)
                zone_counts.append(count)
            
            zone_distribution[tuple(zone_counts)].append(record["issue"])
        
        return {
            f"zone_{i+1}": sum(zone[i] for zone in zone_distribution.keys()) / len(zone_distribution)
            for i in range(len(zones))
        }
    
    def analyze_sum(self, periods: int = 100) -> Dict:
        """和值分析"""
        data = self.get_periods(periods)
        sums = []
        
        for record in data:
            if self.lottery_type == "ssq":
                numbers = record.get("red_balls", [])
            else:
                numbers = record.get("front_zone", [])
            
            sums.append(sum(numbers))
        
        if sums:
            return {
                "min": min(sums),
                "max": max(sums),
                "average": round(sum(sums) / len(sums), 2),
                "median": sorted(sums)[len(sums) // 2]
            }
        return {}
    
    def analyze_span(self, periods: int = 100) -> Dict:
        """跨度分析"""
        data = self.get_periods(periods)
        spans = []
        
        for record in data:
            if self.lottery_type == "ssq":
                numbers = record.get("red_balls", [])
            else:
                numbers = record.get("front_zone", [])
            
            if numbers:
                spans.append(max(numbers) - min(numbers))
        
        if spans:
            return {
                "min": min(spans),
                "max": max(spans),
                "average": round(sum(spans) / len(spans), 2)
            }
        return {}
    
    def full_analysis(self, periods: int = 100) -> Dict:
        """全面分析"""
        data = self.get_periods(periods)
        
        if not data:
            raise ValueError("没有可用的历史数据")
        
        return {
            "lottery_type": self.lottery_type,
            "lottery_name": self.config["name"],
            "periods_analyzed": len(data),
            "date_range": {
                "start_issue": data[-1]["issue"],
                "end_issue": data[0]["issue"],
                "start_date": data[-1]["draw_date"],
                "end_date": data[0]["draw_date"]
            },
            "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "hot_cold": self.analyze_hot_cold(periods),
            "missing": self.analyze_missing(periods),
            "odd_even": self.analyze_odd_even(periods),
            "big_small": self.analyze_big_small(periods),
            "consecutive": self.analyze_consecutive(periods),
            "zones": self.analyze_zones(periods),
            "sum": self.analyze_sum(periods),
            "span": self.analyze_span(periods)
        }
    
    def generate_report(self, analysis_result: Dict) -> str:
        """生成文本报告"""
        lines = []
        
        # 标题
        lines.append(f"## 📊 {analysis_result['lottery_name']}统计分析报告")
        lines.append("")
        lines.append(f"**分析期数**: 最近{analysis_result['periods_analyzed']}期")
        lines.append(f"**期号范围**: {analysis_result['date_range']['end_issue']}期 - {analysis_result['date_range']['start_issue']}期")
        lines.append(f"**分析时间**: {analysis_result['analysis_time']}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # 热号冷号
        hot_cold = analysis_result["hot_cold"]
        if self.lottery_type == "ssq":
            lines.append("### 🔥 热号TOP10（红球出现频率最高）")
            lines.append("")
            lines.append("| 排名 | 号码 | 出现次数 | 频率 |")
            lines.append("|------|------|----------|------|")
            for i, (num, count) in enumerate(hot_cold["red_balls"]["hot"][:10], 1):
                freq = count / analysis_result['periods_analyzed'] * 100
                lines.append(f"| {i} | {num:02d} | {count}次 | {freq:.1f}% |")
            lines.append("")
            
            lines.append("### ❄️ 冷号TOP10（红球出现频率最低）")
            lines.append("")
            lines.append("| 排名 | 号码 | 出现次数 | 频率 |")
            lines.append("|------|------|----------|------|")
            for i, (num, count) in enumerate(hot_cold["red_balls"]["cold"][:10], 1):
                freq = count / analysis_result['periods_analyzed'] * 100
                lines.append(f"| {i} | {num:02d} | {count}次 | {freq:.1f}% |")
            lines.append("")
            
            lines.append("### 🔵 蓝球热号TOP5")
            lines.append("")
            lines.append("| 排名 | 号码 | 出现次数 |")
            lines.append("|------|------|----------|")
            for i, (num, count) in enumerate(hot_cold["blue_ball"]["hot"][:5], 1):
                lines.append(f"| {i} | {num:02d} | {count}次 |")
            lines.append("")
        
        # 遗漏值
        missing = analysis_result["missing"]
        if self.lottery_type == "ssq":
            lines.append("### 📉 遗漏值TOP10（红球）")
            lines.append("")
            lines.append("| 号码 | 当前遗漏期数 |")
            lines.append("|------|-------------|")
            for num, miss in list(missing["red_balls"].items())[:10]:
                lines.append(f"| {num:02d} | {miss}期 |")
            lines.append("")
        
        # 奇偶比
        odd_even = analysis_result["odd_even"]
        lines.append("### ⚖️ 奇偶比分布")
        lines.append("")
        lines.append("| 比例 | 出现次数 | 占比 |")
        lines.append("|------|----------|------|")
        for ratio, count in odd_even.items():
            pct = count / analysis_result['periods_analyzed'] * 100
            lines.append(f"| {ratio} | {count}次 | {pct:.1f}% |")
        lines.append("")
        
        # 大小比
        big_small = analysis_result["big_small"]
        lines.append("### 📏 大小比分布")
        lines.append("")
        lines.append("| 比例 | 出现次数 | 占比 |")
        lines.append("|------|----------|------|")
        for ratio, count in big_small.items():
            pct = count / analysis_result['periods_analyzed'] * 100
            lines.append(f"| {ratio} | {count}次 | {pct:.1f}% |")
        lines.append("")
        
        # 连号
        consecutive = analysis_result["consecutive"]
        lines.append("### 🔗 连号分析")
        lines.append("")
        lines.append(f"- 出现连号期数: {consecutive['consecutive_periods']}期 ({consecutive['consecutive_rate']}%)")
        lines.append(f"- 最常见的连号: {consecutive['top_patterns'][0][0] if consecutive['top_patterns'] else '无'}")
        lines.append("")
        
        # 和值
        sum_stats = analysis_result["sum"]
        lines.append("### 🎯 和值分析")
        lines.append("")
        lines.append(f"- 最小和值: {sum_stats['min']}")
        lines.append(f"- 最大和值: {sum_stats['max']}")
        lines.append(f"- 平均和值: {sum_stats['average']}")
        lines.append(f"- 中位数: {sum_stats['median']}")
        lines.append("")
        
        # 免责声明
        lines.append("---")
        lines.append("")
        lines.append("⚠️ **免责声明**: 以上分析仅供娱乐参考，不构成投注建议。彩票开奖是完全随机的独立事件，历史数据对未来开奖没有任何预测价值。请理性购彩，量力而行。")
        lines.append("")
        lines.append(f"数据来源: 中国福彩/体彩官网 | 查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="彩票历史数据分析工具")
    parser.add_argument("--type", "-t", choices=["ssq", "dlt"], required=True, help="彩票类型")
    parser.add_argument("--periods", "-p", type=int, default=100, help="分析期数")
    parser.add_argument("--metric", "-m", choices=["hot-cold", "missing", "odd-even", "big-small", "consecutive", "zone", "sum", "span", "all"], default="all", help="分析指标")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--json", "-j", action="store_true", help="输出JSON格式")
    
    args = parser.parse_args()
    
    try:
        analyzer = LotteryAnalyzer(args.type)
        
        if args.metric == "all":
            result = analyzer.full_analysis(args.periods)
            if args.json:
                output = json.dumps(result, ensure_ascii=False, indent=2)
            else:
                output = analyzer.generate_report(result)
        else:
            # 单项分析
            metric_map = {
                "hot-cold": analyzer.analyze_hot_cold,
                "missing": analyzer.analyze_missing,
                "odd-even": analyzer.analyze_odd_even,
                "big-small": analyzer.analyze_big_small,
                "consecutive": analyzer.analyze_consecutive,
                "zone": analyzer.analyze_zones,
                "sum": analyzer.analyze_sum,
                "span": analyzer.analyze_span
            }
            
            result = metric_map[args.metric](args.periods)
            output = json.dumps(result, ensure_ascii=False, indent=2) if args.json else str(result)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"✅ 分析结果已保存到: {args.output}")
        else:
            print(output)
            
    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
