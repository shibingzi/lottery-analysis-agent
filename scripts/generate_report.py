#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML 报告生成器
基于分析结果生成美观的 HTML 报告

用法:
    python generate_report.py --type ssq --periods 100 --output report.html
    python generate_report.py --type ssq --input analysis.json --output report.html
    python generate_report.py --type ssq --fixed-red 07,18,25 --fixed-blue 14 --output report.html
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
TEMPLATE_DIR = PROJECT_ROOT / "templates"

# 彩票配置
LOTTERY_CONFIG = {
    "ssq": {
        "name": "双色球",
        "name_en": "SSQ",
        "red_range": (1, 33),
        "blue_range": (1, 16),
        "data_file": DATA_DIR / "ssq" / "history.json",
    },
    "dlt": {
        "name": "大乐透",
        "name_en": "DLT",
        "front_range": (1, 35),
        "back_range": (1, 12),
        "data_file": DATA_DIR / "dlt" / "history.json",
    }
}


class ReportGenerator:
    """HTML 报告生成器"""
    
    def __init__(self, lottery_type: str):
        self.lottery_type = lottery_type.lower()
        config = LOTTERY_CONFIG.get(self.lottery_type)
        if not config:
            raise ValueError(f"不支持的彩票类型: {lottery_type}")
        self.config = config
        
        # 加载模板
        template_path = TEMPLATE_DIR / "report_template.html"
        if not template_path.exists():
            raise FileNotFoundError(f"模板文件不存在: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            self.template = f.read()
        
        # 加载样式
        css_path = TEMPLATE_DIR / "styles.css"
        if css_path.exists():
            with open(css_path, 'r', encoding='utf-8') as f:
                self.css_content = f.read()
        else:
            self.css_content = ""
    
    def load_analysis_data(self, periods: int = 100) -> Dict:
        """从分析脚本加载数据"""
        # 导入分析器
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        from analyze_history import LotteryAnalyzer
        
        analyzer = LotteryAnalyzer(self.lottery_type)
        return analyzer.full_analysis(periods)
    
    def load_json_data(self, json_path: str) -> Dict:
        """从 JSON 文件加载分析数据"""
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _format_number(self, num) -> str:
        """格式化号码，确保两位数"""
        if isinstance(num, int):
            return f"{num:02d}"
        return str(num).zfill(2)
    
    def _generate_hot_cold_section(self, analysis_data: Dict) -> Dict:
        """生成热号冷号部分的数据"""
        hot_cold = analysis_data.get("hot_cold", {})
        
        if self.lottery_type == "ssq":
            red_hot = hot_cold.get("red_balls", {}).get("hot", [])
            red_cold = hot_cold.get("red_balls", {}).get("cold", [])
            
            hot_numbers = []
            for i, (num, count) in enumerate(red_hot[:10], 1):
                freq = count / analysis_data['periods_analyzed'] * 100
                hot_numbers.append({
                    "RANK": i,
                    "NUMBER": self._format_number(num),
                    "COUNT": count,
                    "FREQUENCY": f"{freq:.1f}"
                })
            
            cold_numbers = []
            for i, (num, count) in enumerate(red_cold[:10], 1):
                # 获取遗漏值
                missing_data = analysis_data.get("missing", {}).get("red_balls", {})
                missing = missing_data.get(num, 0)
                cold_numbers.append({
                    "RANK": i,
                    "NUMBER": self._format_number(num),
                    "COUNT": count,
                    "MISSING": missing
                })
            
            # Chart.js 数据
            hot_labels = [self._format_number(num) for num, _ in red_hot[:10]]
            hot_data = [count for _, count in red_hot[:10]]
            cold_labels = [self._format_number(num) for num, _ in red_cold[:10]]
            cold_data = [count for _, count in red_cold[:10]]
            
        else:  # dlt
            front_hot = hot_cold.get("front_zone", {}).get("hot", [])
            front_cold = hot_cold.get("front_zone", {}).get("cold", [])
            
            hot_numbers = []
            for i, (num, count) in enumerate(front_hot[:10], 1):
                freq = count / analysis_data['periods_analyzed'] * 100
                hot_numbers.append({
                    "RANK": i,
                    "NUMBER": self._format_number(num),
                    "COUNT": count,
                    "FREQUENCY": f"{freq:.1f}"
                })
            
            cold_numbers = []
            for i, (num, count) in enumerate(front_cold[:10], 1):
                missing_data = analysis_data.get("missing", {}).get("front_zone", {})
                missing = missing_data.get(num, 0)
                cold_numbers.append({
                    "RANK": i,
                    "NUMBER": self._format_number(num),
                    "COUNT": count,
                    "MISSING": missing
                })
            
            hot_labels = [self._format_number(num) for num, _ in front_hot[:10]]
            hot_data = [count for _, count in front_hot[:10]]
            cold_labels = [self._format_number(num) for num, _ in front_cold[:10]]
            cold_data = [count for _, count in front_cold[:10]]
        
        return {
            "HOT_NUMBERS": hot_numbers,
            "COLD_NUMBERS": cold_numbers,
            "HOT_LABELS": json.dumps(hot_labels, ensure_ascii=False),
            "HOT_DATA": json.dumps(hot_data),
            "COLD_LABELS": json.dumps(cold_labels, ensure_ascii=False),
            "COLD_DATA": json.dumps(cold_data)
        }
    
    def _generate_odd_even_section(self, analysis_data: Dict) -> Dict:
        """生成奇偶比部分的数据"""
        odd_even = analysis_data.get("odd_even", {})
        
        odd_even_data = []
        labels = []
        values = []
        
        for ratio, count in sorted(odd_even.items(), key=lambda x: -x[1]):
            pct = count / analysis_data['periods_analyzed'] * 100
            odd_even_data.append({
                "RATIO": ratio,
                "COUNT": count,
                "PERCENTAGE": f"{pct:.1f}"
            })
            labels.append(ratio)
            values.append(count)
        
        return {
            "ODD_EVEN_DATA": odd_even_data,
            "ODD_EVEN_LABELS": json.dumps(labels, ensure_ascii=False),
            "ODD_EVEN_VALUES": json.dumps(values)
        }
    
    def _generate_big_small_section(self, analysis_data: Dict) -> Dict:
        """生成大小比部分的数据"""
        big_small = analysis_data.get("big_small", {})
        
        big_small_data = []
        labels = []
        values = []
        
        for ratio, count in sorted(big_small.items(), key=lambda x: -x[1]):
            pct = count / analysis_data['periods_analyzed'] * 100
            big_small_data.append({
                "RATIO": ratio,
                "COUNT": count,
                "PERCENTAGE": f"{pct:.1f}"
            })
            labels.append(ratio)
            values.append(count)
        
        return {
            "BIG_SMALL_DATA": big_small_data,
            "BIG_SMALL_LABELS": json.dumps(labels, ensure_ascii=False),
            "BIG_SMALL_VALUES": json.dumps(values)
        }
    
    def _generate_missing_section(self, analysis_data: Dict) -> Dict:
        """生成遗漏值部分的数据"""
        missing = analysis_data.get("missing", {})
        
        missing_data = []
        labels = []
        values = []
        
        if self.lottery_type == "ssq":
            red_missing = missing.get("red_balls", {})
            items = sorted(red_missing.items(), key=lambda x: -x[1])[:15]
        else:
            front_missing = missing.get("front_zone", {})
            items = sorted(front_missing.items(), key=lambda x: -x[1])[:15]
        
        for num, miss in items:
            # 根据遗漏值确定状态
            if miss > 20:
                status = "超冷"
                status_class = "danger"
                tag_class = "cold"
            elif miss > 10:
                status = "较冷"
                status_class = "warning"
                tag_class = "cool"
            else:
                status = "正常"
                status_class = "normal"
                tag_class = "normal"
            
            missing_data.append({
                "NUMBER": self._format_number(num),
                "CURRENT_MISSING": miss,
                "MAX_MISSING": miss + 5,  # 简化处理
                "STATUS": status,
                "STATUS_CLASS": status_class,
                "TAG_CLASS": tag_class
            })
            labels.append(self._format_number(num))
            values.append(miss)
        
        return {
            "MISSING_DATA": missing_data,
            "MISSING_LABELS": json.dumps(labels, ensure_ascii=False),
            "MISSING_VALUES": json.dumps(values)
        }
    
    def _generate_consecutive_section(self, analysis_data: Dict) -> Dict:
        """生成连号部分的数据"""
        consecutive = analysis_data.get("consecutive", {})
        
        top_patterns = consecutive.get("top_patterns", [])
        most_common = top_patterns[0][0] if top_patterns else "无"
        
        return {
            "CONSECUTIVE_RATE": consecutive.get("consecutive_rate", 0),
            "CONSECUTIVE_COUNT": consecutive.get("consecutive_periods", 0),
            "MOST_COMMON_CONSECUTIVE": most_common
        }
    
    def _generate_heatmap_section(self, analysis_data: Dict) -> Dict:
        """生成号码分布热力图"""
        from collections import Counter
        
        # 从原始数据重新统计所有号码的出现次数
        with open(self.config["data_file"], 'r', encoding='utf-8') as f:
            all_data = json.load(f)
        
        # 获取分析期数对应的数据
        periods = analysis_data.get("periods_analyzed", 100)
        recent_data = all_data[:periods]
        
        if self.lottery_type == "ssq":
            # 统计所有红球出现次数
            red_balls = []
            for record in recent_data:
                red_balls.extend(record.get("red_balls", []))
            counter = Counter(red_balls)
            numbers_range = range(1, 34)
        else:  # dlt
            # 统计所有前区号码出现次数
            front_zone = []
            for record in recent_data:
                front_zone.extend(record.get("front_zone", []))
            counter = Counter(front_zone)
            numbers_range = range(1, 36)
        
        # 生成所有号码的统计数据
        all_counts = {num: counter.get(num, 0) for num in numbers_range}
        
        # 计算百分位数阈值（确保均匀分布）
        sorted_counts = sorted(all_counts.values())
        n = len(sorted_counts)
        
        # 计算四分位数
        p25 = sorted_counts[int(n * 0.25)] if n > 0 else 0
        p50 = sorted_counts[int(n * 0.50)] if n > 0 else 0
        p75 = sorted_counts[int(n * 0.75)] if n > 0 else 0
        p90 = sorted_counts[int(n * 0.90)] if n > 0 else 0
        
        heatmap_data = []
        for num in numbers_range:
            count = all_counts[num]
            # 根据百分位数确定热度等级
            # 这样确保每个等级分布更均匀
            if count >= p90:
                heat_class = "hot-3"  # 最热（前10%）
            elif count >= p75:
                heat_class = "hot-2"  # 很热（前25%）
            elif count >= p50:
                heat_class = "hot-1"  # 较热（前50%）
            elif count >= p25:
                heat_class = "heat-1"  # 温热（前75%）
            elif count > 0:
                heat_class = "heat-0"  # 微温（后25%但>0）
            else:
                heat_class = "cold"  # 冷号（0次）
            
            heatmap_data.append({
                "NUMBER": self._format_number(num),
                "COUNT": count,
                "HEAT_CLASS": heat_class
            })
        
        return {"NUMBER_HEATMAP": heatmap_data}
    
    def _generate_latest_draw_section(self, analysis_data: Dict) -> Dict:
        """生成最新开奖结果"""
        # 确保配置已加载
        config = self.config
        assert config is not None, "配置未初始化"
        
        date_range = analysis_data.get("date_range", {})
        
        # 从数据文件加载最新一期
        with open(config["data_file"], 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if data:
            latest = max(data, key=lambda x: x.get("issue", ""))
            
            result = {
                "LATEST_ISSUE": latest.get("issue", ""),
                "LATEST_DATE": latest.get("draw_date", ""),
                "IS_SSQ": self.lottery_type == "ssq",
                "IS_DLT": self.lottery_type == "dlt"
            }
            
            if self.lottery_type == "ssq":
                result["LATEST_RED_BALLS"] = [self._format_number(n) for n in latest.get("red_balls", [])]
                result["LATEST_BLUE_BALL"] = self._format_number(latest.get("blue_ball", 0))
            else:
                result["LATEST_FRONT_ZONE"] = [self._format_number(n) for n in latest.get("front_zone", [])]
                result["LATEST_BACK_ZONE"] = [self._format_number(n) for n in latest.get("back_zone", [])]
            
            return result
        
        return {}
    
    def _generate_fixed_numbers_section(self, fixed_red: List[int], fixed_blue: List[int], 
                                       analysis_data: Dict) -> Optional[Dict]:
        """生成固定号码分析部分"""
        if not fixed_red and not fixed_blue:
            return None
        
        hot_cold = analysis_data.get("hot_cold", {})
        missing = analysis_data.get("missing", {})
        
        if self.lottery_type == "ssq":
            red_stats = dict(hot_cold.get("red_balls", {}).get("hot", []))
            red_missing = missing.get("red_balls", {})
            blue_stats = dict(hot_cold.get("blue_ball", {}).get("hot", []))
            blue_missing = missing.get("blue_ball", {})
        else:
            red_stats = dict(hot_cold.get("front_zone", {}).get("hot", []))
            red_missing = missing.get("front_zone", {})
            blue_stats = dict(hot_cold.get("back_zone", {}).get("hot", []))
            blue_missing = missing.get("back_zone", {})
        
        fixed_stats = []
        
        for num in fixed_red:
            count = red_stats.get(num, 0)
            miss = red_missing.get(num, 0)
            status = "热号" if count > analysis_data['periods_analyzed'] * 0.1 else "冷号"
            fixed_stats.append({
                "NUMBER": self._format_number(num),
                "COUNT": count,
                "MISSING": miss,
                "STATUS": status,
                "TYPE_CLASS": "red",
                "STATUS_CLASS": "hot" if status == "热号" else "cold"
            })
        
        for num in fixed_blue:
            count = blue_stats.get(num, 0)
            miss = blue_missing.get(num, 0)
            status = "热号" if count > analysis_data['periods_analyzed'] * 0.05 else "冷号"
            fixed_stats.append({
                "NUMBER": self._format_number(num),
                "COUNT": count,
                "MISSING": miss,
                "STATUS": status,
                "TYPE_CLASS": "blue",
                "STATUS_CLASS": "hot" if status == "热号" else "cold"
            })
        
        # 生成推荐组合
        recommendations = self._generate_recommendations(fixed_red, fixed_blue, analysis_data)
        
        return {
            "HAS_FIXED_NUMBERS": True,
            "FIXED_RED": [self._format_number(n) for n in fixed_red],
            "FIXED_BLUE": [self._format_number(n) for n in fixed_blue],
            "FIXED_STATS": fixed_stats,
            "RECOMMENDED_COMBINATIONS": recommendations
        }
    
    def _generate_recommendations(self, fixed_red: List[int], fixed_blue: List[int], 
                                  analysis_data: Dict) -> List[Dict]:
        """生成推荐组合"""
        recommendations = []
        hot_cold = analysis_data.get("hot_cold", {})
        
        if self.lottery_type == "ssq":
            red_hot = [num for num, _ in hot_cold.get("red_balls", {}).get("hot", [])[:15]]
            blue_hot = [num for num, _ in hot_cold.get("blue_ball", {}).get("hot", [])[:8]]
            
            # 排除已固定的号码
            available_red = [n for n in red_hot if n not in fixed_red]
            available_blue = [n for n in blue_hot if n not in fixed_blue]
            
            for i in range(min(3, len(available_red) // (6 - len(fixed_red)))):
                red_needed = 6 - len(fixed_red)
                blue_needed = 1 - len(fixed_blue)
                
                combo_red = fixed_red + available_red[i*red_needed:(i+1)*red_needed]
                combo_blue = fixed_blue + available_blue[i*blue_needed:(i+1)*blue_needed]
                
                if len(combo_red) == 6 and len(combo_blue) == 1:
                    recommendations.append({
                        "ID": i + 1,
                        "RED_BALLS": sorted([self._format_number(n) for n in combo_red]),
                        "BLUE_BALL": self._format_number(combo_blue[0]),
                        "STRATEGY": "热号补充策略"
                    })
        
        return recommendations
    
    def _replace_template_vars(self, template: str, data: Dict) -> str:
        """替换模板变量"""
        result = template
        
        # 简单变量替换
        for key, value in data.items():
            if isinstance(value, str):
                result = result.replace(f"{{{{{key}}}}}", value)
            elif isinstance(value, (int, float)):
                # 处理数字类型，转换为字符串
                result = result.replace(f"{{{{{key}}}}}", str(value))
            elif isinstance(value, bool):
                # 处理条件块 {{#KEY}}...{{/KEY}}
                if value:
                    # 保留内容，移除标记
                    pattern = f"{{{{#{key}}}}}(.+?){{{{/{key}}}}}"
                    result = re.sub(pattern, r"\1", result, flags=re.DOTALL)
                else:
                    # 移除整个块
                    pattern = f"{{{{#{key}}}}}(.+?){{{{/{key}}}}}"
                    result = re.sub(pattern, "", result, flags=re.DOTALL)
        
        # 处理列表循环 {{#KEY}}...{{/KEY}}
        for key, value in data.items():
            if isinstance(value, list):
                pattern = f"{{{{#{key}}}}}(.+?){{{{/{key}}}}}"
                match = re.search(pattern, result, re.DOTALL)
                if match:
                    template_block = match.group(1)
                    rendered = ""
                    if value and isinstance(value[0], dict):
                        # 字典列表
                        for item in value:
                            item_rendered = template_block
                            for item_key, item_value in item.items():
                                item_rendered = item_rendered.replace(f"{{{{{item_key}}}}}", str(item_value))
                            rendered += item_rendered
                    else:
                        # 简单值列表，处理 {{.}}
                        for item in value:
                            item_rendered = template_block.replace("{{.}}", str(item))
                            rendered += item_rendered
                    result = re.sub(pattern, rendered, result, flags=re.DOTALL)
        
        # 清理未替换的变量
        result = re.sub(r"\{\{[#/]?[A-Z_]+\}\}", "", result)
        result = re.sub(r"\{\{\.\}\}", "", result)
        
        return result
    
    def generate(self, analysis_data: Dict, fixed_red: Optional[List[int]] = None, 
                fixed_blue: Optional[List[int]] = None) -> str:
        """生成完整 HTML 报告"""
        
        # 确保配置已加载
        config = self.config
        assert config is not None, "配置未初始化"
        
        # 基础数据
        template_data = {
            "LOTTERY_NAME": config["name"],
            "LOTTERY_TYPE": config["name_en"],
            "ANALYSIS_TIME": analysis_data.get("analysis_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "PERIODS_ANALYZED": str(analysis_data.get("periods_analyzed", 0)),
            "START_ISSUE": analysis_data.get("date_range", {}).get("start_issue", ""),
            "END_ISSUE": analysis_data.get("date_range", {}).get("end_issue", "")
        }
        
        # 最新开奖
        template_data.update(self._generate_latest_draw_section(analysis_data))
        
        # 热号冷号
        template_data.update(self._generate_hot_cold_section(analysis_data))
        
        # 奇偶比
        template_data.update(self._generate_odd_even_section(analysis_data))
        
        # 大小比
        template_data.update(self._generate_big_small_section(analysis_data))
        
        # 遗漏值
        template_data.update(self._generate_missing_section(analysis_data))
        
        # 连号
        template_data.update(self._generate_consecutive_section(analysis_data))
        
        # 热力图
        template_data.update(self._generate_heatmap_section(analysis_data))
        
        # 固定号码
        if fixed_red or fixed_blue:
            fixed_section = self._generate_fixed_numbers_section(
                fixed_red or [], fixed_blue or [], analysis_data
            )
            if fixed_section:
                template_data.update(fixed_section)
        else:
            template_data["HAS_FIXED_NUMBERS"] = False
        
        # 生成 HTML
        html = self._replace_template_vars(self.template, template_data)
        
        # 内嵌 CSS
        if self.css_content:
            html = html.replace(
                '<link rel="stylesheet" href="styles.css">',
                f'<style>\n{self.css_content}\n</style>'
            )
        
        return html
    
    def save_report(self, html: str, output_path: str):
        """保存报告到文件"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return output_file.absolute()


def main():
    parser = argparse.ArgumentParser(description="生成彩票分析 HTML 报告")
    parser.add_argument("--type", "-t", choices=["ssq", "dlt"], required=True, help="彩票类型")
    parser.add_argument("--periods", "-p", type=int, default=100, help="分析期数")
    parser.add_argument("--input", "-i", help="输入 JSON 文件（分析结果）")
    parser.add_argument("--output", "-o", required=True, help="输出 HTML 文件路径")
    parser.add_argument("--fixed-red", help="固定红球号码，逗号分隔，如: 07,18,25")
    parser.add_argument("--fixed-blue", help="固定蓝球号码，逗号分隔，如: 14")
    
    args = parser.parse_args()
    
    try:
        # 初始化生成器
        generator = ReportGenerator(args.type)
        
        # 加载分析数据
        if args.input:
            print(f"📂 从文件加载分析数据: {args.input}")
            analysis_data = generator.load_json_data(args.input)
        else:
            print(f"📊 执行分析，期数: {args.periods}")
            analysis_data = generator.load_analysis_data(args.periods)
        
        # 解析固定号码
        fixed_red = None
        fixed_blue = None
        if args.fixed_red:
            fixed_red = [int(n.strip()) for n in args.fixed_red.split(",")]
            print(f"🔢 固定红球: {fixed_red}")
        if args.fixed_blue:
            fixed_blue = [int(n.strip()) for n in args.fixed_blue.split(",")]
            print(f"🔵 固定蓝球: {fixed_blue}")
        
        # 生成报告
        print("🎨 生成 HTML 报告...")
        html = generator.generate(analysis_data, fixed_red, fixed_blue)
        
        # 保存报告
        output_path = generator.save_report(html, args.output)
        print(f"✅ 报告已生成: {output_path}")
        
    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
