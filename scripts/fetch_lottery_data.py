#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彩票数据获取脚本
支持双色球(SSQ)和大乐透(DLT)的数据获取与更新

用法:
    python fetch_lottery_data.py --type ssq --limit 100
    python fetch_lottery_data.py --type dlt --update
    python fetch_lottery_data.py --all
"""

import argparse
import json
import os
import sys
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import urllib.request
import urllib.error
import ssl

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/data_fetch.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CACHE_DIR = DATA_DIR / "cache"

# 创建目录
DATA_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)
(DATA_DIR / "ssq").mkdir(exist_ok=True)
(DATA_DIR / "dlt").mkdir(exist_ok=True)

# 彩票配置
LOTTERY_CONFIG = {
    "ssq": {
        "name": "双色球",
        "red_range": (1, 33),
        "blue_range": (1, 16),
        "red_count": 6,
        "blue_count": 1,
        "draw_days": [2, 4, 0],  # 周二、周四、周日
        "data_file": DATA_DIR / "ssq" / "history.json"
    },
    "dlt": {
        "name": "大乐透",
        "front_range": (1, 35),
        "back_range": (1, 12),
        "front_count": 5,
        "back_count": 2,
        "draw_days": [1, 3, 6],  # 周一、周三、周六
        "data_file": DATA_DIR / "dlt" / "history.json"
    }
}


class LotteryDataFetcher:
    """彩票数据获取器"""
    
    def __init__(self, lottery_type: str):
        self.lottery_type = lottery_type.lower()
        config = LOTTERY_CONFIG.get(self.lottery_type)
        if not config:
            raise ValueError(f"不支持的彩票类型: {lottery_type}")
        
        self.config: Dict = config
        self.data_file: Path = self.config["data_file"]
        self.data: List[Dict] = self._load_existing_data()
        
    def _load_existing_data(self) -> List[Dict]:
        """加载已有数据"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载已有数据失败: {e}")
        return []
    
    def _save_data(self):
        """保存数据到文件"""
        try:
            # 按期号排序
            self.data.sort(key=lambda x: x.get("issue", ""), reverse=True)
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"数据已保存: {self.data_file} ({len(self.data)} 条记录)")
        except Exception as e:
            logger.error(f"保存数据失败: {e}")
            raise
    
    def _create_ssl_context(self):
        """创建SSL上下文（忽略证书验证）"""
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context
    
    def fetch_from_api(self, limit: int = 100) -> List[Dict]:
        """
        从API获取彩票数据
        注：这里使用模拟数据作为示例，实际使用时需要替换为真实的API
        """
        logger.info(f"正在获取 {self.config['name']} 数据...")
        
        # TODO: 替换为真实的数据源API
        # 目前返回模拟数据用于测试
        mock_data = self._generate_mock_data(limit)
        
        return mock_data
    
    def _generate_mock_data(self, limit: int) -> List[Dict]:
        """生成模拟数据（用于测试）"""
        import random
        
        data = []
        base_date = datetime.now()
        
        for i in range(limit):
            issue_date = base_date - timedelta(days=i*3)
            issue_number = self._generate_issue_number(issue_date, i)
            
            if self.lottery_type == "ssq":
                record = {
                    "lottery_type": "ssq",
                    "issue": issue_number,
                    "draw_date": issue_date.strftime("%Y-%m-%d"),
                    "red_balls": sorted(random.sample(range(1, 34), 6)),
                    "blue_ball": random.randint(1, 16),
                    "prize_info": {
                        "jackpot": f"{random.randint(1, 20)}注",
                        "jackpot_amount": f"{random.randint(500, 1000)}万元/注"
                    }
                }
            else:  # dlt
                record = {
                    "lottery_type": "dlt",
                    "issue": issue_number,
                    "draw_date": issue_date.strftime("%Y-%m-%d"),
                    "front_zone": sorted(random.sample(range(1, 36), 5)),
                    "back_zone": sorted(random.sample(range(1, 13), 2)),
                    "prize_info": {
                        "jackpot": f"{random.randint(1, 15)}注",
                        "jackpot_amount": f"{random.randint(500, 1000)}万元/注"
                    }
                }
            
            data.append(record)
        
        logger.info(f"生成了 {len(data)} 条模拟数据")
        return data
    
    def _generate_issue_number(self, date: datetime, offset: int) -> str:
        """生成期号"""
        year = date.year
        # 简化处理：假设每年约150-160期
        issue_num = 160 - offset
        if issue_num <= 0:
            year -= 1
            issue_num += 160
        
        if self.lottery_type == "ssq":
            return f"{year}{issue_num:03d}"
        else:
            return f"{str(year)[2:]}{issue_num:03d}"
    
    def update_data(self, limit: int = 100) -> Tuple[int, int]:
        """
        更新数据
        
        Returns:
            (新增记录数, 总记录数)
        """
        new_data = self.fetch_from_api(limit)
        
        # 合并数据（去重）
        existing_issues = {item["issue"] for item in self.data}
        added_count = 0
        
        for record in new_data:
            if record["issue"] not in existing_issues:
                self.data.append(record)
                existing_issues.add(record["issue"])
                added_count += 1
        
        # 保存数据
        self._save_data()
        
        logger.info(f"更新完成: 新增 {added_count} 条记录，总计 {len(self.data)} 条")
        return added_count, len(self.data)
    
    def get_latest(self) -> Optional[Dict]:
        """获取最新一期数据"""
        if not self.data:
            self.update_data(10)
        
        if self.data:
            return max(self.data, key=lambda x: x.get("issue", ""))
        return None
    
    def get_by_issue(self, issue: str) -> Optional[Dict]:
        """根据期号获取数据"""
        for record in self.data:
            if record["issue"] == issue:
                return record
        return None
    
    def get_history(self, limit: int = 100) -> List[Dict]:
        """获取历史数据"""
        if not self.data:
            self.update_data(limit)
        
        # 按日期排序并限制数量
        sorted_data = sorted(self.data, key=lambda x: x.get("draw_date", ""), reverse=True)
        return sorted_data[:limit]


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="彩票数据获取工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --type ssq --limit 50          # 获取双色球最近50期
  %(prog)s --type dlt --update            # 更新大乐透数据
  %(prog)s --all --limit 100              # 获取所有彩种100期数据
        """
    )
    
    parser.add_argument(
        "--type", "-t",
        choices=["ssq", "dlt"],
        help="彩票类型: ssq=双色球, dlt=大乐透"
    )
    
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=100,
        help="获取数据条数 (默认: 100)"
    )
    
    parser.add_argument(
        "--update", "-u",
        action="store_true",
        help="更新模式：只获取新数据"
    )
    
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="获取所有支持的彩种"
    )
    
    parser.add_argument(
        "--latest",
        action="store_true",
        help="只显示最新一期"
    )
    
    args = parser.parse_args()
    
    # 参数验证
    if not args.type and not args.all:
        parser.print_help()
        sys.exit(1)
    
    # 确定要处理的彩种
    types_to_process = ["ssq", "dlt"] if args.all else [args.type]
    
    results = {}
    
    for lottery_type in types_to_process:
        try:
            fetcher = LotteryDataFetcher(lottery_type)
            
            if args.latest:
                # 只显示最新一期
                latest = fetcher.get_latest()
                if latest:
                    print(f"\n🎱 {fetcher.config['name']} 最新开奖")
                    print(f"期号: {latest['issue']}")
                    print(f"日期: {latest['draw_date']}")
                    
                    if lottery_type == "ssq":
                        print(f"红球: {' '.join(f'{n:02d}' for n in latest['red_balls'])}")
                        print(f"蓝球: {latest['blue_ball']:02d}")
                    else:
                        print(f"前区: {' '.join(f'{n:02d}' for n in latest['front_zone'])}")
                        print(f"后区: {' '.join(f'{n:02d}' for n in latest['back_zone'])}")
                else:
                    print(f"未找到 {fetcher.config['name']} 数据")
            else:
                # 更新或获取数据
                added, total = fetcher.update_data(args.limit)
                results[lottery_type] = {"added": added, "total": total}
                
        except Exception as e:
            logger.error(f"处理 {lottery_type} 时出错: {e}")
            results[lottery_type] = {"error": str(e)}
    
    # 打印汇总
    if not args.latest:
        print("\n" + "="*50)
        print("📊 数据更新汇总")
        print("="*50)
        for lottery_type, result in results.items():
            config = LOTTERY_CONFIG[lottery_type]
            if "error" in result:
                print(f"❌ {config['name']}: 失败 - {result['error']}")
            else:
                print(f"✅ {config['name']}: 新增 {result['added']} 条，总计 {result['total']} 条")
        print("="*50)


if __name__ == "__main__":
    main()
