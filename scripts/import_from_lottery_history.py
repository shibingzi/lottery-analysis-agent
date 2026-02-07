#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 lottery_history 项目自动下载和导入数据
GitHub: https://github.com/gudaoxuri/lottery_history

用法:
    python scripts/import_from_lottery_history.py --type ssq
    python scripts/import_from_lottery_history.py --type dlt
    python scripts/import_from_lottery_history.py --all
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict
import urllib.request
import urllib.error

# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# 数据源配置
DATA_SOURCES = {
    "ssq": {
        "name": "双色球",
        "url": "https://raw.githubusercontent.com/gudaoxuri/lottery_history/main/data/ssq.json",
        "data_file": DATA_DIR / "ssq" / "history.json"
    },
    "dlt": {
        "name": "大乐透",
        "url": "https://raw.githubusercontent.com/gudaoxuri/lottery_history/main/data/dlt.json",
        "data_file": DATA_DIR / "dlt" / "history.json"
    }
}


def download_data(url: str) -> List[Dict]:
    """从URL下载JSON数据"""
    print(f"📥 正在下载数据...")
    print(f"   URL: {url}")
    
    try:
        # 设置请求头，模拟浏览器
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read().decode('utf-8')
            return json.loads(data)
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP错误: {e.code} - {e.reason}")
        raise
    except urllib.error.URLError as e:
        print(f"❌ URL错误: {e.reason}")
        raise
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        raise


def convert_ssq_data(source_data: List[Dict]) -> List[Dict]:
    """转换双色球数据格式"""
    converted = []
    for record in source_data:
        converted.append({
            "lottery_type": "ssq",
            "issue": record["issueNumber"],
            "draw_date": record["drawDate"],
            "red_balls": record["redBalls"],
            "blue_ball": record["blueBall"],
            "prize_info": {}
        })
    return converted


def convert_dlt_data(source_data: List[Dict]) -> List[Dict]:
    """转换大乐透数据格式"""
    converted = []
    for record in source_data:
        converted.append({
            "lottery_type": "dlt",
            "issue": record["issueNumber"],
            "draw_date": record["drawDate"],
            "front_zone": record["frontBalls"],
            "back_zone": record["backBalls"],
            "prize_info": {}
        })
    return converted


def import_lottery_data(lottery_type: str) -> tuple:
    """
    导入指定彩种的数据
    
    Returns: (新增数量, 总数量)
    """
    config = DATA_SOURCES[lottery_type]
    print(f"\n{'='*60}")
    print(f"🎱 正在导入 {config['name']} 数据")
    print(f"{'='*60}")
    
    # 1. 下载数据
    source_data = download_data(config["url"])
    print(f"✅ 下载完成: {len(source_data)} 条记录")
    
    # 2. 转换格式
    if lottery_type == "ssq":
        converted_data = convert_ssq_data(source_data)
    else:
        converted_data = convert_dlt_data(source_data)
    print(f"✅ 格式转换完成")
    
    # 3. 加载现有数据
    existing_data = []
    if config["data_file"].exists():
        with open(config["data_file"], 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        print(f"📊 现有数据: {len(existing_data)} 条")
    
    # 4. 合并数据（去重）
    existing_issues = {item["issue"] for item in existing_data}
    added_count = 0
    
    for record in converted_data:
        if record["issue"] not in existing_issues:
            existing_data.append(record)
            existing_issues.add(record["issue"])
            added_count += 1
    
    # 5. 保存数据
    config["data_file"].parent.mkdir(parents=True, exist_ok=True)
    
    # 按期号降序排序
    existing_data.sort(key=lambda x: x["issue"], reverse=True)
    
    with open(config["data_file"], 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 数据保存完成: {config['data_file']}")
    print(f"📈 导入统计:")
    print(f"   新增: {added_count} 条")
    print(f"   总计: {len(existing_data)} 条")
    
    return added_count, len(existing_data)


def main():
    parser = argparse.ArgumentParser(
        description="从 lottery_history 项目导入彩票历史数据",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 导入双色球数据
  %(prog)s --type ssq
  
  # 导入大乐透数据
  %(prog)s --type dlt
  
  # 导入所有彩种
  %(prog)s --all
  
数据源:
  双色球: https://github.com/gudaoxuri/lottery_history
  大乐透: https://github.com/gudaoxuri/lottery_history
  
数据每天自动更新，包含从2003年至今的所有历史开奖数据。
        """
    )
    
    parser.add_argument(
        "--type", "-t",
        choices=["ssq", "dlt"],
        help="彩票类型: ssq=双色球, dlt=大乐透"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="导入所有彩种"
    )
    
    args = parser.parse_args()
    
    # 参数验证
    if not args.type and not args.all:
        parser.print_help()
        sys.exit(1)
    
    # 确定要导入的彩种
    types_to_import = ["ssq", "dlt"] if args.all else [args.type]
    
    print("="*60)
    print("🎱 彩票数据导入工具")
    print("📦 数据源: lottery_history (GitHub)")
    print("🔄 数据每天自动更新")
    print("="*60)
    
    total_added = 0
    total_records = 0
    
    for lottery_type in types_to_import:
        try:
            added, total = import_lottery_data(lottery_type)
            total_added += added
            total_records += total
        except Exception as e:
            print(f"\n❌ 导入 {lottery_type} 失败: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("✅ 导入完成!")
    print(f"{'='*60}")
    print(f"📊 总新增: {total_added} 条")
    print(f"📊 总记录: {total_records} 条")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
