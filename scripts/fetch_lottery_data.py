#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彩票数据获取脚本 - 分离历史数据和增量更新
支持双色球(SSQ)和大乐透(DLT)

用法:
    # 获取历史数据（大量）
    python fetch_lottery_data.py --type ssq --history --limit 1000
    
    # 增量更新（只获取新数据）
    python fetch_lottery_data.py --type ssq --update
    
    # 从CSV导入历史数据
    python fetch_lottery_data.py --type ssq --import-file history.csv
    
    # 查看最新开奖
    python fetch_lottery_data.py --type ssq --latest
"""

import argparse
import json
import os
import sys
import csv
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import random

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# 彩票配置
LOTTERY_CONFIG = {
    "ssq": {
        "name": "双色球",
        "data_file": DATA_DIR / "ssq" / "history.json",
        "red_range": (1, 33),
        "blue_range": (1, 16),
    },
    "dlt": {
        "name": "大乐透",
        "data_file": DATA_DIR / "dlt" / "history.json",
        "front_range": (1, 35),
        "back_range": (1, 12),
    }
}


class LotteryDataManager:
    """彩票数据管理器"""
    
    def __init__(self, lottery_type: str):
        self.lottery_type = lottery_type.lower()
        self.config = LOTTERY_CONFIG[self.lottery_type]
        self.data_file = self.config["data_file"]
        self.data = self._load_data()
    
    def _load_data(self) -> List[Dict]:
        """加载已有数据"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载数据失败: {e}")
        return []
    
    def _save_data(self):
        """保存数据"""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        # 按期号降序排序
        self.data.sort(key=lambda x: x.get("issue", ""), reverse=True)
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        logger.info(f"数据已保存: {self.data_file} ({len(self.data)} 条)")
    
    def fetch_history_data(self, limit: int = 1000) -> Tuple[int, int]:
        """
        获取历史数据（大量）
        用于首次填充或重新获取历史数据
        
        Returns: (新增数量, 总数量)
        """
        logger.info(f"正在获取 {self.config['name']} 历史数据，目标 {limit} 期...")
        
        # TODO: 这里应该调用真实的历史数据API
        # 目前使用模拟数据演示
        new_data = self._generate_mock_history_data(limit)
        
        # 合并数据（去重）
        existing_issues = {item["issue"] for item in self.data}
        added = 0
        for record in new_data:
            if record["issue"] not in existing_issues:
                self.data.append(record)
                existing_issues.add(record["issue"])
                added += 1
        
        self._save_data()
        logger.info(f"历史数据获取完成: 新增 {added} 条，总计 {len(self.data)} 条")
        return added, len(self.data)
    
    def fetch_latest_data(self, days: int = 7) -> Tuple[int, int]:
        """
        获取最新数据（增量更新）
        只获取最近几天的开奖数据
        
        Args:
            days: 获取最近多少天的数据
        
        Returns: (新增数量, 总数量)
        """
        logger.info(f"正在检查 {self.config['name']} 最新数据（最近{days}天）...")
        
        # TODO: 这里应该调用真实的最新数据API
        # 目前使用模拟数据演示
        new_data = self._generate_mock_latest_data(days)
        
        # 合并数据（去重）
        existing_issues = {item["issue"] for item in self.data}
        added = 0
        for record in new_data:
            if record["issue"] not in existing_issues:
                self.data.append(record)
                existing_issues.add(record["issue"])
                added += 1
        
        if added > 0:
            self._save_data()
            logger.info(f"增量更新完成: 新增 {added} 条，总计 {len(self.data)} 条")
        else:
            logger.info("数据已是最新，无需更新")
        
        return added, len(self.data)
    
    def import_from_csv(self, csv_file: str) -> Tuple[int, int]:
        """
        从CSV文件导入历史数据
        
        CSV格式示例:
        issue,draw_date,red_balls,blue_ball
        2025023,2025-03-02,03 07 12 18 25 30,14
        """
        logger.info(f"正在从CSV导入数据: {csv_file}")
        
        csv_path = Path(csv_file)
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV文件不存在: {csv_file}")
        
        imported = 0
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    if self.lottery_type == "ssq":
                        record = {
                            "lottery_type": "ssq",
                            "issue": row["issue"],
                            "draw_date": row["draw_date"],
                            "red_balls": [int(x) for x in row["red_balls"].split()],
                            "blue_ball": int(row["blue_ball"]),
                            "prize_info": {}
                        }
                    else:  # dlt
                        record = {
                            "lottery_type": "dlt",
                            "issue": row["issue"],
                            "draw_date": row["draw_date"],
                            "front_zone": [int(x) for x in row["front_zone"].split()],
                            "back_zone": [int(x) for x in row["back_zone"].split()],
                            "prize_info": {}
                        }
                    
                    # 检查是否已存在
                    if not any(d["issue"] == record["issue"] for d in self.data):
                        self.data.append(record)
                        imported += 1
                except Exception as e:
                    logger.warning(f"导入行失败: {row}, 错误: {e}")
        
        self._save_data()
        logger.info(f"CSV导入完成: 导入 {imported} 条，总计 {len(self.data)} 条")
        return imported, len(self.data)
    
    def export_to_csv(self, csv_file: str, limit: Optional[int] = None):
        """导出数据到CSV文件"""
        logger.info(f"正在导出数据到CSV: {csv_file}")
        
        data_to_export = self.data[:limit] if limit else self.data
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if self.lottery_type == "ssq":
                fieldnames = ["issue", "draw_date", "red_balls", "blue_ball"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for record in data_to_export:
                    writer.writerow({
                        "issue": record["issue"],
                        "draw_date": record["draw_date"],
                        "red_balls": " ".join(f"{x:02d}" for x in record["red_balls"]),
                        "blue_ball": record["blue_ball"]
                    })
            else:  # dlt
                fieldnames = ["issue", "draw_date", "front_zone", "back_zone"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for record in data_to_export:
                    writer.writerow({
                        "issue": record["issue"],
                        "draw_date": record["draw_date"],
                        "front_zone": " ".join(f"{x:02d}" for x in record["front_zone"]),
                        "back_zone": " ".join(f"{x:02d}" for x in record["back_zone"])
                    })
        
        logger.info(f"导出完成: {len(data_to_export)} 条记录 -> {csv_file}")
    
    def get_stats(self) -> Dict:
        """获取数据统计信息"""
        if not self.data:
            return {"count": 0, "latest_issue": None, "oldest_issue": None}
        
        sorted_data = sorted(self.data, key=lambda x: x["issue"])
        return {
            "count": len(self.data),
            "latest_issue": sorted_data[-1]["issue"],
            "latest_date": sorted_data[-1]["draw_date"],
            "oldest_issue": sorted_data[0]["issue"],
            "oldest_date": sorted_data[0]["draw_date"],
        }
    
    def _generate_mock_history_data(self, limit: int) -> List[Dict]:
        """生成模拟历史数据（用于测试）"""
        logger.info(f"生成 {limit} 条模拟历史数据...")
        data = []
        base_date = datetime.now() - timedelta(days=limit*3)
        
        for i in range(limit):
            issue_date = base_date + timedelta(days=i*3)
            
            if self.lottery_type == "ssq":
                year = issue_date.year
                issue_num = i + 1
                record = {
                    "lottery_type": "ssq",
                    "issue": f"{year}{issue_num:03d}",
                    "draw_date": issue_date.strftime("%Y-%m-%d"),
                    "red_balls": sorted(random.sample(range(1, 34), 6)),
                    "blue_ball": random.randint(1, 16),
                    "prize_info": {}
                }
            else:  # dlt
                year = issue_date.year % 100
                issue_num = i + 1
                record = {
                    "lottery_type": "dlt",
                    "issue": f"{year}{issue_num:03d}",
                    "draw_date": issue_date.strftime("%Y-%m-%d"),
                    "front_zone": sorted(random.sample(range(1, 36), 5)),
                    "back_zone": sorted(random.sample(range(1, 13), 2)),
                    "prize_info": {}
                }
            
            data.append(record)
        
        return data
    
    def _generate_mock_latest_data(self, days: int) -> List[Dict]:
        """生成模拟最新数据（用于测试）"""
        data = []
        today = datetime.now()
        
        # 生成最近几天的数据
        for i in range(days // 3):  # 假设每3天一期
            issue_date = today - timedelta(days=i*3)
            
            if self.lottery_type == "ssq":
                year = issue_date.year
                # 简化期号计算
                issue_num = (issue_date.timetuple().tm_yday // 3) + 1
                record = {
                    "lottery_type": "ssq",
                    "issue": f"{year}{issue_num:03d}",
                    "draw_date": issue_date.strftime("%Y-%m-%d"),
                    "red_balls": sorted(random.sample(range(1, 34), 6)),
                    "blue_ball": random.randint(1, 16),
                    "prize_info": {}
                }
            else:  # dlt
                year = issue_date.year % 100
                issue_num = (issue_date.timetuple().tm_yday // 3) + 1
                record = {
                    "lottery_type": "dlt",
                    "issue": f"{year}{issue_num:03d}",
                    "draw_date": issue_date.strftime("%Y-%m-%d"),
                    "front_zone": sorted(random.sample(range(1, 36), 5)),
                    "back_zone": sorted(random.sample(range(1, 13), 2)),
                    "prize_info": {}
                }
            
            data.append(record)
        
        return data


def main():
    parser = argparse.ArgumentParser(
        description="彩票数据获取工具 - 分离历史数据和增量更新",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 获取历史数据（首次使用或重新获取）
  %(prog)s --type ssq --history --limit 1000
  
  # 增量更新（日常使用）
  %(prog)s --type ssq --update
  %(prog)s --type ssq --update --days 14
  
  # 从CSV导入
  %(prog)s --type ssq --import-file history.csv
  
  # 导出到CSV
  %(prog)s --type ssq --export-file backup.csv
  
  # 查看统计信息
  %(prog)s --type ssq --stats
  
  # 查看最新开奖
  %(prog)s --type ssq --latest
  
  # 更新所有彩种
  %(prog)s --all --update
        """
    )
    
    parser.add_argument("--type", "-t", choices=["ssq", "dlt"],
                       help="彩票类型: ssq=双色球, dlt=大乐透")
    parser.add_argument("--all", "-a", action="store_true",
                       help="处理所有彩种")
    
    # 历史数据获取
    parser.add_argument("--history", action="store_true",
                       help="获取历史数据（大量）")
    parser.add_argument("--limit", "-l", type=int, default=1000,
                       help="获取历史数据的期数 (默认: 1000)")
    
    # 增量更新
    parser.add_argument("--update", "-u", action="store_true",
                       help="增量更新（只获取新数据）")
    parser.add_argument("--days", type=int, default=7,
                       help="增量更新时获取最近多少天的数据 (默认: 7)")
    
    # 导入导出
    parser.add_argument("--import-file",
                       help="从CSV文件导入数据")
    parser.add_argument("--export-file",
                       help="导出数据到CSV文件")
    parser.add_argument("--export-limit", type=int,
                       help="导出时限制记录数")
    
    # 查询
    parser.add_argument("--stats", action="store_true",
                       help="显示数据统计信息")
    parser.add_argument("--latest", action="store_true",
                       help="显示最新开奖信息")
    
    args = parser.parse_args()
    
    # 参数验证
    if not args.type and not args.all:
        parser.print_help()
        sys.exit(1)
    
    types = ["ssq", "dlt"] if args.all else [args.type]
    
    # 执行操作
    for lottery_type in types:
        try:
            manager = LotteryDataManager(lottery_type)
            
            if args.history:
                # 获取历史数据
                added, total = manager.fetch_history_data(args.limit)
                print(f"\n✅ {manager.config['name']} 历史数据获取完成")
                print(f"   新增: {added} 条")
                print(f"   总计: {total} 条")
                
            elif args.update:
                # 增量更新
                added, total = manager.fetch_latest_data(args.days)
                print(f"\n✅ {manager.config['name']} 增量更新完成")
                print(f"   新增: {added} 条")
                print(f"   总计: {total} 条")
                
            elif args.import_file:
                # 从CSV导入
                imported, total = manager.import_from_csv(args.import_file)
                print(f"\n✅ {manager.config['name']} CSV导入完成")
                print(f"   导入: {imported} 条")
                print(f"   总计: {total} 条")
                
            elif args.export_file:
                # 导出到CSV
                manager.export_to_csv(args.export_file, args.export_limit)
                
            elif args.stats:
                # 显示统计
                stats = manager.get_stats()
                print(f"\n📊 {manager.config['name']} 数据统计")
                print(f"   总记录数: {stats['count']}")
                if stats['count'] > 0:
                    print(f"   最新期号: {stats['latest_issue']} ({stats['latest_date']})")
                    print(f"   最早期号: {stats['oldest_issue']} ({stats['oldest_date']})")
                    
            elif args.latest:
                # 显示最新开奖
                if manager.data:
                    latest = max(manager.data, key=lambda x: x['issue'])
                    print(f"\n🎱 {manager.config['name']} 最新开奖")
                    print(f"   期号: {latest['issue']}")
                    print(f"   日期: {latest['draw_date']}")
                    if lottery_type == "ssq":
                        print(f"   红球: {' '.join(f'{x:02d}' for x in latest['red_balls'])}")
                        print(f"   蓝球: {latest['blue_ball']:02d}")
                    else:
                        print(f"   前区: {' '.join(f'{x:02d}' for x in latest['front_zone'])}")
                        print(f"   后区: {' '.join(f'{x:02d}' for x in latest['back_zone'])}")
                else:
                    print(f"   暂无数据")
                    
        except Exception as e:
            logger.error(f"处理 {lottery_type} 时出错: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
