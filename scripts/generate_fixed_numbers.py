#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
固定号码分析和号码生成脚本
支持双色球(SSQ)和大乐透(DLT)

用法:
    # 分析固定号码
    python generate_fixed_numbers.py --type ssq --fixed-red 07,18,25 --fixed-blue 14
    
    # 生成随机号码
    python generate_fixed_numbers.py --type ssq --generate --count 5
    
    # 基于固定号码生成组合
    python generate_fixed_numbers.py --type dlt --fixed-red 05,12 --generate --count 3
"""

import argparse
import json
import random
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

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
        "big_boundary": 17,
        "data_file": DATA_DIR / "ssq" / "history.json"
    },
    "dlt": {
        "name": "大乐透",
        "front_range": (1, 35),
        "back_range": (1, 12),
        "front_count": 5,
        "back_count": 2,
        "big_boundary": 18,
        "data_file": DATA_DIR / "dlt" / "history.json"
    }
}


class LotteryPredictor:
    """彩票号码预测器（娱乐性质）"""
    
    def __init__(self, lottery_type: str):
        self.lottery_type = lottery_type.lower()
        config = LOTTERY_CONFIG.get(self.lottery_type)
        if not config:
            raise ValueError(f"不支持的彩票类型: {lottery_type}")
        
        self.config: Dict = config
        self.history_data = self._load_history()
        self.hot_numbers = self._calculate_hot_numbers()
    
    def _load_history(self) -> List[Dict]:
        """加载历史数据"""
        if not self.config["data_file"].exists():
            return []
        
        with open(self.config["data_file"], 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _calculate_hot_numbers(self) -> List[int]:
        """计算热号"""
        if not self.history_data:
            return []
        
        if self.lottery_type == "ssq":
            all_numbers = []
            for record in self.history_data[:100]:  # 最近100期
                all_numbers.extend(record.get("red_balls", []))
            counter = Counter(all_numbers)
            return [num for num, _ in counter.most_common(10)]
        else:
            all_numbers = []
            for record in self.history_data[:100]:
                all_numbers.extend(record.get("front_zone", []))
            counter = Counter(all_numbers)
            return [num for num, _ in counter.most_common(10)]
    
    def validate_numbers(self, numbers: List[int], num_type: str) -> Tuple[bool, str]:
        """验证号码有效性"""
        if self.lottery_type == "ssq":
            if num_type == "red":
                if len(numbers) != len(set(numbers)):
                    return False, "红球号码不能重复"
                if not all(1 <= n <= 33 for n in numbers):
                    return False, "红球号码必须在1-33之间"
                if len(numbers) > 6:
                    return False, "红球最多选择6个号码"
            else:  # blue
                if len(numbers) != 1:
                    return False, "蓝球必须选择1个号码"
                if not (1 <= numbers[0] <= 16):
                    return False, "蓝球号码必须在1-16之间"
        else:  # dlt
            if num_type == "front":
                if len(numbers) != len(set(numbers)):
                    return False, "前区号码不能重复"
                if not all(1 <= n <= 35 for n in numbers):
                    return False, "前区号码必须在1-35之间"
                if len(numbers) > 5:
                    return False, "前区最多选择5个号码"
            else:  # back
                if len(numbers) != len(set(numbers)):
                    return False, "后区号码不能重复"
                if not all(1 <= n <= 12 for n in numbers):
                    return False, "后区号码必须在1-12之间"
                if len(numbers) > 2:
                    return False, "后区最多选择2个号码"
        
        return True, "验证通过"
    
    def analyze_fixed_numbers(self, fixed_red: List[int], fixed_blue: List[int]) -> Dict:
        """分析固定号码"""
        # 验证号码
        if self.lottery_type == "ssq":
            valid, msg = self.validate_numbers(fixed_red, "red")
            if not valid:
                raise ValueError(f"红球{msg}")
            valid, msg = self.validate_numbers(fixed_blue, "blue")
            if not valid:
                raise ValueError(f"蓝球{msg}")
        else:
            valid, msg = self.validate_numbers(fixed_red, "front")
            if not valid:
                raise ValueError(f"前区{msg}")
            valid, msg = self.validate_numbers(fixed_blue, "back")
            if not valid:
                raise ValueError(f"后区{msg}")
        
        # 计算各号码的历史表现
        number_stats = {}
        
        if self.lottery_type == "ssq":
            # 红球统计
            for num in fixed_red:
                count = sum(1 for r in self.history_data if num in r.get("red_balls", []))
                missing = next((i for i, r in enumerate(self.history_data) 
                              if num in r.get("red_balls", [])), len(self.history_data))
                number_stats[f"red_{num}"] = {
                    "number": num,
                    "type": "红球",
                    "count": count,
                    "frequency": round(count / len(self.history_data) * 100, 2) if self.history_data else 0,
                    "current_missing": missing,
                    "status": "热号" if count > len(self.history_data) * 0.15 else "正常" if count > len(self.history_data) * 0.08 else "冷号"
                }
            
            # 蓝球统计
            for num in fixed_blue:
                count = sum(1 for r in self.history_data if r.get("blue_ball") == num)
                missing = next((i for i, r in enumerate(self.history_data) 
                              if r.get("blue_ball") == num), len(self.history_data))
                number_stats[f"blue_{num}"] = {
                    "number": num,
                    "type": "蓝球",
                    "count": count,
                    "frequency": round(count / len(self.history_data) * 100, 2) if self.history_data else 0,
                    "current_missing": missing,
                    "status": "热号" if count > len(self.history_data) * 0.10 else "正常"
                }
            
            # 组合评估
            odd_count = sum(1 for n in fixed_red if n % 2 == 1)
            even_count = len(fixed_red) - odd_count
            big_count = sum(1 for n in fixed_red if n >= self.config["big_boundary"])
            small_count = len(fixed_red) - big_count
            
            evaluation = {
                "odd_even_ratio": f"{odd_count}:{even_count}",
                "odd_even_score": 2 if abs(odd_count - even_count) <= 1 else 1,
                "big_small_ratio": f"{big_count}:{small_count}",
                "big_small_score": 2 if abs(big_count - small_count) <= 1 else 1,
                "fixed_red_count": len(fixed_red),
                "fixed_blue_count": len(fixed_blue),
                "need_red": 6 - len(fixed_red),
                "need_blue": 1 - len(fixed_blue)
            }
        
        else:  # dlt
            # 前区统计
            for num in fixed_red:
                count = sum(1 for r in self.history_data if num in r.get("front_zone", []))
                missing = next((i for i, r in enumerate(self.history_data) 
                              if num in r.get("front_zone", [])), len(self.history_data))
                number_stats[f"front_{num}"] = {
                    "number": num,
                    "type": "前区",
                    "count": count,
                    "frequency": round(count / len(self.history_data) * 100, 2) if self.history_data else 0,
                    "current_missing": missing,
                    "status": "热号" if count > len(self.history_data) * 0.15 else "正常"
                }
            
            # 后区统计
            for num in fixed_blue:
                count = sum(1 for r in self.history_data if num in r.get("back_zone", []))
                missing = next((i for i, r in enumerate(self.history_data) 
                              if num in r.get("back_zone", [])), len(self.history_data))
                number_stats[f"back_{num}"] = {
                    "number": num,
                    "type": "后区",
                    "count": count,
                    "frequency": round(count / len(self.history_data) * 100, 2) if self.history_data else 0,
                    "current_missing": missing,
                    "status": "热号" if count > len(self.history_data) * 0.10 else "正常"
                }
            
            # 组合评估
            odd_count = sum(1 for n in fixed_red if n % 2 == 1)
            even_count = len(fixed_red) - odd_count
            big_count = sum(1 for n in fixed_red if n >= self.config["big_boundary"])
            small_count = len(fixed_red) - big_count
            
            evaluation = {
                "odd_even_ratio": f"{odd_count}:{even_count}",
                "odd_even_score": 2 if abs(odd_count - even_count) <= 1 else 1,
                "big_small_ratio": f"{big_count}:{small_count}",
                "big_small_score": 2 if abs(big_count - small_count) <= 1 else 1,
                "fixed_front_count": len(fixed_red),
                "fixed_back_count": len(fixed_blue),
                "need_front": 5 - len(fixed_red),
                "need_back": 2 - len(fixed_blue)
            }
        
        total_score = evaluation.get("odd_even_score", 0) + evaluation.get("big_small_score", 0)
        evaluation["total_score"] = total_score
        evaluation["max_score"] = 4
        evaluation["rating"] = "⭐" * (total_score + 1)
        
        return {
            "lottery_type": self.lottery_type,
            "lottery_name": self.config["name"],
            "fixed_red": fixed_red,
            "fixed_blue": fixed_blue,
            "number_stats": number_stats,
            "evaluation": evaluation,
            "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def generate_combinations(self, fixed_red: Optional[List[int]] = None, fixed_blue: Optional[List[int]] = None, 
                             count: int = 3, mode: str = "random") -> List[Dict]:
        """生成号码组合"""
        combinations = []
        
        for i in range(count):
            if self.lottery_type == "ssq":
                # 红球
                if fixed_red:
                    remaining = 6 - len(fixed_red)
                    available = [n for n in range(1, 34) if n not in fixed_red]
                    
                    if mode == "weighted":
                        # 热号权重稍高
                        weights = [1.5 if n in self.hot_numbers else 1.0 for n in available]
                        additional = random.choices(available, weights=weights, k=remaining)
                        # 去重并重新选择
                        additional = list(set(additional))
                        while len(additional) < remaining:
                            new_num = random.choice(available)
                            if new_num not in additional and new_num not in fixed_red:
                                additional.append(new_num)
                    else:
                        additional = random.sample(available, remaining)
                    
                    red_balls = sorted(fixed_red + additional)
                else:
                    red_balls = sorted(random.sample(range(1, 34), 6))
                
                # 蓝球
                if fixed_blue:
                    blue_ball = fixed_blue[0]
                else:
                    blue_ball = random.randint(1, 16)
                
                combinations.append({
                    "id": i + 1,
                    "red_balls": red_balls,
                    "blue_ball": blue_ball,
                    "fixed_red": fixed_red if fixed_red else [],
                    "fixed_blue": fixed_blue if fixed_blue else []
                })
            
            else:  # dlt
                # 前区
                if fixed_red:
                    remaining = 5 - len(fixed_red)
                    available = [n for n in range(1, 36) if n not in fixed_red]
                    additional = random.sample(available, remaining)
                    front_zone = sorted(fixed_red + additional)
                else:
                    front_zone = sorted(random.sample(range(1, 36), 5))
                
                # 后区
                if fixed_blue:
                    back_zone = sorted(fixed_blue)
                else:
                    back_zone = sorted(random.sample(range(1, 13), 2))
                
                combinations.append({
                    "id": i + 1,
                    "front_zone": front_zone,
                    "back_zone": back_zone,
                    "fixed_front": fixed_red if fixed_red else [],
                    "fixed_back": fixed_blue if fixed_blue else []
                })
        
        return combinations
    
    def generate_report(self, analysis_result: Dict, combinations: Optional[List[Dict]] = None) -> str:
        """生成文本报告"""
        lines = []
        
        # 标题
        lines.append(f"## 🔢 {analysis_result['lottery_name']}固定号码分析报告")
        lines.append("")
        
        # 用户输入
        lines.append("### 用户输入")
        if self.lottery_type == "ssq":
            lines.append(f"- 彩票类型: 双色球")
            lines.append(f"- 固定红球: {', '.join(f'{n:02d}' for n in analysis_result['fixed_red'])}")
            if analysis_result['fixed_blue']:
                lines.append(f"- 固定蓝球: {analysis_result['fixed_blue'][0]:02d}")
        else:
            lines.append(f"- 彩票类型: 大乐透")
            lines.append(f"- 固定前区: {', '.join(f'{n:02d}' for n in analysis_result['fixed_red'])}")
            if analysis_result['fixed_blue']:
                lines.append(f"- 固定后区: {', '.join(f'{n:02d}' for n in analysis_result['fixed_blue'])}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # 历史表现
        lines.append("### 📊 固定号码历史表现")
        lines.append("")
        lines.append("| 号码 | 类型 | 出现次数 | 频率 | 当前遗漏 | 状态 |")
        lines.append("|------|------|----------|------|----------|------|")
        for key, stat in analysis_result["number_stats"].items():
            lines.append(f"| {stat['number']:02d} | {stat['type']} | {stat['count']}次 | {stat['frequency']}% | {stat['current_missing']}期 | {stat['status']} |")
        lines.append("")
        
        # 组合评估
        eval_info = analysis_result["evaluation"]
        lines.append("### ⚖️ 组合合理性评估")
        lines.append("")
        lines.append("**当前组合特征:**")
        lines.append(f"- 奇偶比: {eval_info['odd_even_ratio']}")
        lines.append(f"- 大小比: {eval_info['big_small_ratio']}")
        if self.lottery_type == "ssq":
            lines.append(f"- 已选红球: {eval_info['fixed_red_count']}个（需补充{eval_info['need_red']}个）")
        else:
            lines.append(f"- 已选前区: {eval_info['fixed_front_count']}个（需补充{eval_info['need_front']}个）")
        lines.append("")
        lines.append(f"**评估结果:** {eval_info['rating']} ({eval_info['total_score']}/{eval_info['max_score']}分)")
        lines.append("")
        
        # 推荐组合
        if combinations:
            lines.append("### 🎲 推荐组合（娱乐性质）")
            lines.append("")
            lines.append("基于您的固定号码，以下是生成的娱乐性组合：")
            lines.append("")
            
            for combo in combinations:
                lines.append(f"#### 组合 {combo['id']}")
                if self.lottery_type == "ssq":
                    red_str = ' '.join(f'{n:02d}' for n in combo['red_balls'])
                    lines.append(f"🔴 红球: {red_str}")
                    lines.append(f"🔵 蓝球: {combo['blue_ball']:02d}")
                else:
                    front_str = ' '.join(f'{n:02d}' for n in combo['front_zone'])
                    back_str = ' '.join(f'{n:02d}' for n in combo['back_zone'])
                    lines.append(f"🔴 前区: {front_str}")
                    lines.append(f"🔵 后区: {back_str}")
                lines.append("")
        
        # 免责声明
        lines.append("---")
        lines.append("")
        lines.append("⚠️ **重要声明**:")
        lines.append("以上分析仅供娱乐参考，不构成投注建议。彩票开奖是完全随机的独立事件，历史数据对未来开奖没有任何预测价值。每个号码在每期中奖概率相等。请理性购彩，量力而行。")
        lines.append("")
        lines.append(f"生成时间: {analysis_result['analysis_time']}")
        
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="固定号码分析和号码生成工具")
    parser.add_argument("--type", "-t", choices=["ssq", "dlt"], required=True, help="彩票类型")
    parser.add_argument("--fixed-red", help="固定红球/前区号码，逗号分隔，如: 07,18,25")
    parser.add_argument("--fixed-blue", help="固定蓝球/后区号码，逗号分隔，如: 14 或 03,09")
    parser.add_argument("--generate", "-g", action="store_true", help="生成号码组合")
    parser.add_argument("--count", "-c", type=int, default=3, help="生成组合数量")
    parser.add_argument("--mode", "-m", choices=["random", "weighted"], default="random", help="生成模式")
    parser.add_argument("--output", "-o", help="输出文件路径")
    
    args = parser.parse_args()
    
    try:
        predictor = LotteryPredictor(args.type)
        
        # 解析固定号码
        fixed_red = []
        fixed_blue = []
        
        if args.fixed_red:
            fixed_red = [int(n.strip()) for n in args.fixed_red.split(",")]
        
        if args.fixed_blue:
            fixed_blue = [int(n.strip()) for n in args.fixed_blue.split(",")]
        
        # 分析或生成
        if fixed_red or fixed_blue:
            # 分析固定号码
            analysis = predictor.analyze_fixed_numbers(fixed_red, fixed_blue)
            
            # 生成组合
            combinations = None
            if args.generate:
                combinations = predictor.generate_combinations(
                    fixed_red if fixed_red else None,
                    fixed_blue if fixed_blue else None,
                    args.count,
                    args.mode
                )
            
            report = predictor.generate_report(analysis, combinations)
        else:
            # 仅生成随机号码
            combinations = predictor.generate_combinations(
                count=args.count,
                mode=args.mode
            )
            
            lines = ["## 🎲 机选号码生成结果", ""]
            lines.append(f"**生成模式**: {'完全随机' if args.mode == 'random' else '热号加权'}")
            lines.append(f"**生成注数**: {args.count}注")
            lines.append("")
            lines.append("---")
            lines.append("")
            
            for combo in combinations:
                lines.append(f"### 第{combo['id']}注")
                if args.type == "ssq":
                    red_str = ' '.join(f'{n:02d}' for n in combo['red_balls'])
                    lines.append(f"🔴 红球: {red_str}")
                    lines.append(f"🔵 蓝球: {combo['blue_ball']:02d}")
                else:
                    front_str = ' '.join(f'{n:02d}' for n in combo['front_zone'])
                    back_str = ' '.join(f'{n:02d}' for n in combo['back_zone'])
                    lines.append(f"🔴 前区: {front_str}")
                    lines.append(f"🔵 后区: {back_str}")
                lines.append("")
            
            lines.append("---")
            lines.append("")
            lines.append("⚠️ **免责声明**: 以上号码完全随机生成，仅供娱乐。不保证任何中奖结果。")
            report = "\n".join(lines)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"✅ 报告已保存到: {args.output}")
        else:
            print(report)
            
    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
