# Lottery Analysis Agent Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 构建一个基于混合架构的彩票数据分析系统，支持双色球和大乐透的数据获取、统计分析、固定号码分析和幸运数字生成，所有功能均为娱乐性质并带有明确免责声明。

**Architecture:** 采用Python脚本+Claude Agent混合架构：Python负责数据持久化和精确计算，Skills提供标准化工具接口，Sub-agents处理彩种特定业务逻辑，主Agent负责意图识别和协调。数据预置50期历史，采用实时计算策略，报告支持Markdown快速预览和HTML完整可视化双模式。

**Tech Stack:** Python 3.8+, Claude Code, Chart.js (CDN), JSON数据存储

---

## Phase 1: 项目基础架构

### Task 1: 创建项目目录结构

**Files:**
- Create: `lottery-analysis-agent/data/ssq/history.json`
- Create: `lottery-analysis-agent/data/dlt/history.json`
- Create: `lottery-analysis-agent/data/shared/config.json`
- Create: `lottery-analysis-agent/.claude/config/lottery_types.json`
- Create: `lottery-analysis-agent/scripts/__init__.py`

**Step 1: 创建目录结构**

```bash
mkdir -p lottery-analysis-agent/{data/{ssq,dlt,shared},scripts,templates,.claude/{skills,agents,prompts,config},docs/plans,logs}
```

**Step 2: 创建彩种配置文件**

`.claude/config/lottery_types.json`:
```json
{
  "lotteries": {
    "ssq": {
      "name": "双色球",
      "code": "ssq",
      "red_balls": {"count": 6, "range": [1, 33], "name": "红球"},
      "blue_balls": {"count": 1, "range": [1, 16], "name": "蓝球"},
      "draw_days": ["tuesday", "thursday", "sunday"],
      "draw_time": "21:15"
    },
    "dlt": {
      "name": "大乐透",
      "code": "dlt", 
      "front_zone": {"count": 5, "range": [1, 35], "name": "前区"},
      "back_zone": {"count": 2, "range": [1, 12], "name": "后区"},
      "draw_days": ["monday", "wednesday", "saturday"],
      "draw_time": "21:25"
    }
  }
}
```

**Step 3: 初始化验证**

```bash
ls -la lottery-analysis-agent/.claude/config/
cat lottery-analysis-agent/.claude/config/lottery_types.json
```

Expected: 文件存在且JSON格式正确

---

### Task 2: 创建预置历史数据（50期）

**Files:**
- Create: `data/ssq/history.json` (50期双色球数据)
- Create: `data/dlt/history.json` (50期大乐透数据)

**Step 1: 双色球历史数据模板**

`data/ssq/history.json`:
```json
{
  "lottery_type": "ssq",
  "last_update": "2026-02-07T00:00:00Z",
  "total_records": 50,
  "data": [
    {
      "issue": "2025010",
      "draw_date": "2025-01-26",
      "week": "星期日",
      "red_balls": [3, 7, 12, 18, 25, 30],
      "blue_ball": 14,
      "sale_amount": "450,123,456",
      "prize_pool": "2,345,678,901"
    }
  ]
}
```

**Step 2: 使用WebSearch获取真实历史数据**

搜索最近50期双色球和大乐透开奖结果填充数据。

**Step 3: 数据验证**

```bash
python3 -c "import json; d=json.load(open('data/ssq/history.json')); print(f'双色球: {d[\"total_records\"]}期'); d2=json.load(open('data/dlt/history.json')); print(f'大乐透: {d2[\"total_records\"]}期')"
```

Expected: 双色球: 50期, 大乐透: 50期

---

### Task 3: 创建核心配置和启动文件

**Files:**
- Create: `.claude/settings.json`
- Create: `scripts/utils.py` (工具函数)
- Create: `.env.example`

**Step 1: Claude配置**

`.claude/settings.json`:
```json
{
  "project": {
    "name": "Lottery Analysis Agent",
    "version": "1.0.0",
    "description": "基于娱乐性质的彩票数据分析系统"
  },
  "allowed_tools": [
    "Read", "Write", "Edit", "bash", "WebSearch", "WebFetch"
  ],
  "skills_path": ".claude/skills",
  "agents_path": ".claude/agents",
  "disclaimer": "⚠️ 彩票开奖是完全随机的独立事件，本系统仅供娱乐参考，不构成投注建议。"
}
```

**Step 2: 工具函数模块**

`scripts/utils.py`:
```python
"""
彩票分析系统工具函数
"""

import json
import random
from datetime import datetime
from typing import List, Dict, Any, Optional

# 标准免责声明
DISCLAIMER = """
⚠️ 重要提示：
• 彩票开奖是完全随机的独立事件
• 历史数据对未来开奖没有任何预测价值  
• 以上分析仅供娱乐参考，不构成投注建议
• 请理性购彩，量力而行
"""

def load_lottery_config(lottery_type: str) -> Dict[str, Any]:
    """加载彩种配置"""
    with open('.claude/config/lottery_types.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config['lotteries'].get(lottery_type)

def load_history_data(lottery_type: str) -> List[Dict]:
    """加载历史数据"""
    try:
        with open(f'data/{lottery_type}/history.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('data', [])
    except FileNotFoundError:
        return []

def validate_numbers(numbers: List[int], lottery_type: str, zone: str = 'red') -> bool:
    """验证号码合法性"""
    config = load_lottery_config(lottery_type)
    if not config:
        return False
    
    # 根据彩种和区域确定范围
    if lottery_type == 'ssq':
        if zone == 'red':
            valid_range = range(1, 34)
            count = 6
        else:  # blue
            valid_range = range(1, 17)
            count = 1
    elif lottery_type == 'dlt':
        if zone == 'front':
            valid_range = range(1, 36)
            count = 5
        else:  # back
            valid_range = range(1, 13)
            count = 2
    
    # 检查数量和范围
    if len(numbers) != len(set(numbers)):
        return False  # 重复
    if len(numbers) > count:
        return False  # 数量超限
    if not all(n in valid_range for n in numbers):
        return False  # 超出范围
    
    return True

def format_disclaimer() -> str:
    """返回格式化免责声明"""
    return DISCLAIMER
```

**Step 3: 环境变量示例**

`.env.example`:
```bash
# 彩票分析系统环境变量
# 复制为 .env 并填写实际值

# 可选：第三方API密钥（如使用聚合数据等）
# JUHE_API_KEY=your_api_key_here

# 日志级别
LOG_LEVEL=INFO

# 数据更新间隔（小时）
UPDATE_INTERVAL=24
```

---

## Phase 2: Skills开发

### Task 4: Data Fetcher Skill

**Files:**
- Create: `.claude/skills/skill_lottery_data_fetcher.md`
- Create: `scripts/fetch_lottery_data.py`

**Step 1: Skill文档**

`.claude/skills/skill_lottery_data_fetcher.md`:
```markdown
# Skill: 彩票数据获取专家

## 职责
负责从多个数据源获取彩票开奖数据，验证数据准确性，并更新本地数据库。

## 使用场景
- 获取最新开奖结果
- 补充历史数据
- 验证数据一致性

## 工具
- WebFetch: 从官方网站获取数据
- WebSearch: 搜索最新开奖信息
- Read/Write: 读写本地数据文件

## 数据源优先级
1. 中国福彩/体彩官网（权威）
2. WebSearch搜索结果（备用）
3. 本地缓存（降级）

## 输入
```json
{
  "lottery_type": "ssq|dlt",
  "action": "latest|history|verify",
  "issue": "optional: specific issue number"
}
```

## 输出
```json
{
  "success": true|false,
  "data": [...],
  "source": "official|search|cache",
  "timestamp": "2026-02-07T10:30:00Z"
}
```

## 约束
- 必须验证数据完整性（号码数量、范围）
- 多源数据不一致时优先官方源
- 失败时使用本地缓存并告知用户
```

**Step 2: Python实现**

`scripts/fetch_lottery_data.py`:
```python
#!/usr/bin/env python3
"""
彩票数据获取脚本
支持双色球(ssq)和大乐透(dlt)
"""

import json
import argparse
from datetime import datetime
from typing import List, Dict, Optional
from utils import load_lottery_config, load_history_data

def fetch_latest(lottery_type: str) -> Optional[Dict]:
    """
    获取最新开奖数据
    
    优先顺序：
    1. 本地数据（检查是否已是最新）
    2. WebFetch官方源
    3. WebSearch备用
    """
    # 检查本地最新数据
    history = load_history_data(lottery_type)
    if history:
        latest_local = history[0]
        # 这里可以添加日期检查逻辑
        return latest_local
    
    # TODO: 实现WebFetch获取逻辑
    # 由于网站可能变化，先使用本地数据
    return None

def verify_data(data: Dict, lottery_type: str) -> bool:
    """验证数据完整性和合法性"""
    config = load_lottery_config(lottery_type)
    if not config:
        return False
    
    try:
        if lottery_type == 'ssq':
            red = data.get('red_balls', [])
            blue = data.get('blue_ball')
            if len(red) != 6 or not all(1 <= r <= 33 for r in red):
                return False
            if not (1 <= blue <= 16):
                return False
        elif lottery_type == 'dlt':
            front = data.get('front_zone', [])
            back = data.get('back_zone', [])
            if len(front) != 5 or not all(1 <= f <= 35 for f in front):
                return False
            if len(back) != 2 or not all(1 <= b <= 12 for b in back):
                return False
        return True
    except:
        return False

def update_history(lottery_type: str, new_data: Dict) -> bool:
    """更新历史数据文件"""
    try:
        with open(f'data/{lottery_type}/history.json', 'r+', encoding='utf-8') as f:
            data = json.load(f)
            
            # 检查是否已存在
            exists = any(d['issue'] == new_data['issue'] for d in data['data'])
            if not exists:
                data['data'].insert(0, new_data)  # 最新在前
                data['total_records'] = len(data['data'])
                data['last_update'] = datetime.now().isoformat()
                
                f.seek(0)
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.truncate()
            return True
    except Exception as e:
        print(f"更新失败: {e}")
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='彩票数据获取工具')
    parser.add_argument('--lottery', choices=['ssq', 'dlt'], required=True)
    parser.add_argument('--action', choices=['latest', 'verify'], default='latest')
    
    args = parser.parse_args()
    
    if args.action == 'latest':
        result = fetch_latest(args.lottery)
        if result:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("获取最新数据失败，使用本地缓存")
```

**Step 3: 测试验证**

```bash
cd lottery-analysis-agent
python scripts/fetch_lottery_data.py --lottery ssq --action latest
```

Expected: 输出JSON格式的最新开奖数据

---

### Task 5: Analyzer Skill

**Files:**
- Create: `.claude/skills/skill_lottery_analyzer.md`
- Create: `scripts/analyze_history.py`

**Step 1: Skill文档**

`.claude/skills/skill_lottery_analyzer.md`:
```markdown
# Skill: 彩票统计分析专家

## 职责
对历史开奖数据进行统计分析，计算热号、冷号、遗漏值、奇偶比、大小比等指标。

## 使用场景
- 热号/冷号分析
- 遗漏值统计
- 号码分布分析
- 固定号码评估

## 核心算法

### 热号/冷号
- 统计周期内各号码出现次数
- 热号：出现次数 > 平均 + 标准差
- 冷号：出现次数 < 平均 - 标准差

### 遗漏值
- 自上次开出以来的期数
- 当前期号 - 上次开出期号

### 奇偶比/大小比
- 奇偶：1-33中奇偶分布（双色球16为界）
- 大小：小号(1-16) vs 大号(17-33)

## 输入
```json
{
  "lottery_type": "ssq|dlt",
  "analysis_type": "hot_cold|missing|distribution|full",
  "period": 50
}
```

## 输出
```json
{
  "hot_numbers": [...],
  "cold_numbers": [...],
  "missing_values": {...},
  "odd_even_ratio": {...},
  "big_small_ratio": {...}
}
```

## 注意事项
⚠️ 所有统计都是历史回顾，不代表未来趋势
```

**Step 2: Python实现**

`scripts/analyze_history.py`:
```python
#!/usr/bin/env python3
"""
彩票历史数据分析脚本
"""

import json
import statistics
from collections import Counter
from typing import Dict, List, Tuple
from utils import load_history_data, load_lottery_config

class LotteryAnalyzer:
    def __init__(self, lottery_type: str):
        self.lottery_type = lottery_type
        self.config = load_lottery_config(lottery_type)
        self.history = load_history_data(lottery_type)
    
    def analyze_hot_cold(self, period: int = 50) -> Dict:
        """热号冷号分析"""
        recent_data = self.history[:period]
        
        # 统计各号码出现次数
        if self.lottery_type == 'ssq':
            all_numbers = []
            for draw in recent_data:
                all_numbers.extend(draw.get('red_balls', []))
            number_range = range(1, 34)
        else:  # dlt
            all_numbers = []
            for draw in recent_data:
                all_numbers.extend(draw.get('front_zone', []))
            number_range = range(1, 36)
        
        counts = Counter(all_numbers)
        
        # 计算平均和标准差
        freq_list = [counts.get(n, 0) for n in number_range]
        avg = statistics.mean(freq_list)
        std = statistics.stdev(freq_list) if len(freq_list) > 1 else 0
        
        # 分类
        hot_threshold = avg + std
        cold_threshold = avg - std
        
        hot = [n for n in number_range if counts.get(n, 0) > hot_threshold]
        cold = [n for n in number_range if counts.get(n, 0) < cold_threshold]
        
        return {
            'period': period,
            'hot_numbers': sorted(hot, key=lambda x: counts[x], reverse=True)[:10],
            'cold_numbers': sorted(cold, key=lambda x: counts[x])[:10],
            'frequency': {str(n): counts.get(n, 0) for n in number_range},
            'average': round(avg, 2)
        }
    
    def analyze_missing(self) -> Dict:
        """遗漏值分析"""
        if self.lottery_type == 'ssq':
            number_range = range(1, 34)
            key = 'red_balls'
        else:
            number_range = range(1, 36)
            key = 'front_zone'
        
        missing = {}
        for num in number_range:
            # 从最新开始查找
            for i, draw in enumerate(self.history):
                if num in draw.get(key, []):
                    missing[num] = i
                    break
            else:
                missing[num] = len(self.history)  # 从未出现
        
        # 排序
        sorted_missing = sorted(missing.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'max_missing': sorted_missing[:5],
            'hot_missing': [(n, v) for n, v in sorted_missing if v < 5][:5],
            'distribution': {
                'hot': len([v for v in missing.values() if v < 5]),
                'warm': len([v for v in missing.values() if 5 <= v <= 15]),
                'cold': len([v for v in missing.values() if v > 15])
            }
        }
    
    def analyze_fixed_numbers(self, numbers: List[int], zone: str = 'red') -> Dict:
        """固定号码分析"""
        if self.lottery_type == 'ssq':
            number_range = range(1, 34) if zone == 'red' else range(1, 17)
            key = 'red_balls' if zone == 'red' else 'blue_ball'
        else:
            number_range = range(1, 36) if zone == 'front' else range(1, 13)
            key = 'front_zone' if zone == 'front' else 'back_zone'
        
        analysis = {}
        for num in numbers:
            # 查找遗漏值
            for i, draw in enumerate(self.history):
                draw_nums = draw.get(key, [])
                if isinstance(draw_nums, int):
                    draw_nums = [draw_nums]
                if num in draw_nums:
                    analysis[num] = {
                        'current_missing': i,
                        'last_seen_issue': draw['issue'],
                        'last_seen_date': draw['draw_date']
                    }
                    break
            else:
                analysis[num] = {
                    'current_missing': len(self.history),
                    'last_seen_issue': None,
                    'last_seen_date': None
                }
        
        # 组合分析
        odd_count = len([n for n in numbers if n % 2 == 1])
        even_count = len(numbers) - odd_count
        
        return {
            'numbers': numbers,
            'missing_analysis': analysis,
            'odd_even_ratio': f'{odd_count}:{even_count}',
            'total_missing_avg': round(statistics.mean([a['current_missing'] for a in analysis.values()]), 1)
        }
    
    def generate_full_report(self, period: int = 50) -> Dict:
        """生成完整分析报告"""
        return {
            'lottery_type': self.lottery_type,
            'period': period,
            'total_records': len(self.history),
            'hot_cold': self.analyze_hot_cold(period),
            'missing': self.analyze_missing(),
            'disclaimer': '⚠️ 以上分析基于历史数据统计，不代表未来开奖趋势'
        }

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--lottery', choices=['ssq', 'dlt'], required=True)
    parser.add_argument('--type', default='full')
    parser.add_argument('--period', type=int, default=50)
    
    args = parser.parse_args()
    
    analyzer = LotteryAnalyzer(args.lottery)
    report = analyzer.generate_full_report(args.period)
    print(json.dumps(report, ensure_ascii=False, indent=2))
```

**Step 3: 测试**

```bash
python scripts/analyze_history.py --lottery ssq --type full --period 50
```

Expected: 输出包含热号冷号、遗漏值等统计的JSON

---

### Task 6: Generator Skill（含幸运数字）

**Files:**
- Create: `.claude/skills/skill_lottery_generator.md`
- Create: `scripts/generate_numbers.py`

**Step 1: Skill文档**

`.claude/skills/skill_lottery_generator.md`:
```markdown
# Skill: 彩票号码生成专家

## 职责
基于不同策略生成彩票号码组合，包括纯随机、固定号码补充、幸运数字转换。

## 生成策略

### 1. 纯随机生成
完全随机选择号码，每个号码概率相等。

### 2. 固定号码补充
用户提供部分号码，剩余号码随机填充。

### 3. 幸运数字转换 ⭐
将用户的有意义数字（生日、手机尾号等）转换为合法彩票号码：
- 提取数字片段
- 映射到有效范围（取模或截断）
- 随机补充剩余位置

## 幸运数字转换规则

**输入处理**：
- 日期格式：YYYY-MM-DD → 提取年、月、日
- 纯数字：直接提取各位
- 多组数字：合并去重

**映射规则**：
- 超出范围：取模映射（如90 → 90%33=24）
- 重复数字：只保留一次
- 不足数量：随机补充

## 输入
```json
{
  "lottery_type": "ssq|dlt",
  "strategy": "random|fixed|lucky",
  "fixed_numbers": {"red": [...], "blue": [...]},
  "lucky_numbers": {
    "birthday": "1990-05-20",
    "phone": "6688",
    "custom": [7, 18]
  },
  "count": 5
}
```

## 输出
```json
{
  "combinations": [...],
  "strategy_used": "lucky",
  "lucky_source": {"birthday": [...], "phone": [...]},
  "disclaimer": "..."
}
```

## ⚠️ 重要说明
所有生成都是随机的，幸运数字只是让号码更有意义，中奖概率与任何号码相同。
```

**Step 2: Python实现**

`scripts/generate_numbers.py`:
```python
#!/usr/bin/env python3
"""
彩票号码生成脚本
支持：随机生成、固定号码补充、幸运数字转换
"""

import random
import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from utils import load_lottery_config, validate_numbers, format_disclaimer

class NumberGenerator:
    def __init__(self, lottery_type: str):
        self.lottery_type = lottery_type
        self.config = load_lottery_config(lottery_type)
    
    def generate_random(self, count: int = 1) -> List[Dict]:
        """纯随机生成"""
        combinations = []
        
        for _ in range(count):
            if self.lottery_type == 'ssq':
                red = sorted(random.sample(range(1, 34), 6))
                blue = random.randint(1, 16)
                combinations.append({
                    'red_balls': red,
                    'blue_ball': blue,
                    'type': 'random'
                })
            else:  # dlt
                front = sorted(random.sample(range(1, 36), 5))
                back = sorted(random.sample(range(1, 13), 2))
                combinations.append({
                    'front_zone': front,
                    'back_zone': back,
                    'type': 'random'
                })
        
        return combinations
    
    def generate_with_fixed(self, fixed_red: List[int], fixed_blue: Optional[int] = None, 
                           fixed_front: List[int] = None, fixed_back: List[int] = None,
                           count: int = 3) -> List[Dict]:
        """固定号码补充生成"""
        combinations = []
        
        for _ in range(count):
            if self.lottery_type == 'ssq':
                # 补充红球
                remaining_red = 6 - len(fixed_red)
                available_red = [n for n in range(1, 34) if n not in fixed_red]
                supplement_red = sorted(random.sample(available_red, remaining_red))
                red = sorted(fixed_red + supplement_red)
                
                # 蓝球
                blue = fixed_blue if fixed_blue else random.randint(1, 16)
                
                combinations.append({
                    'red_balls': red,
                    'blue_ball': blue,
                    'fixed_red': fixed_red,
                    'fixed_blue': fixed_blue,
                    'type': 'fixed'
                })
            else:  # dlt
                # 补充前区
                remaining_front = 5 - len(fixed_front) if fixed_front else 5
                if fixed_front:
                    available_front = [n for n in range(1, 36) if n not in fixed_front]
                    supplement_front = sorted(random.sample(available_front, remaining_front))
                    front = sorted(fixed_front + supplement_front)
                else:
                    front = sorted(random.sample(range(1, 36), 5))
                
                # 补充后区
                remaining_back = 2 - len(fixed_back) if fixed_back else 2
                if fixed_back:
                    available_back = [n for n in range(1, 13) if n not in fixed_back]
                    supplement_back = sorted(random.sample(available_back, remaining_back))
                    back = sorted(fixed_back + supplement_back)
                else:
                    back = sorted(random.sample(range(1, 13), 2))
                
                combinations.append({
                    'front_zone': front,
                    'back_zone': back,
                    'fixed_front': fixed_front,
                    'fixed_back': fixed_back,
                    'type': 'fixed'
                })
        
        return combinations
    
    def parse_lucky_numbers(self, birthday: Optional[str] = None, 
                           phone: Optional[str] = None,
                           custom: Optional[List[int]] = None) -> Dict[str, List[int]]:
        """解析幸运数字"""
        lucky_sources = {}
        
        # 解析生日
        if birthday:
            try:
                # 支持格式：1990-05-20 或 19900520
                digits = re.findall(r'\d+', birthday)
                numbers = []
                for d in digits:
                    if len(d) == 4:  # 年份
                        numbers.extend([int(d[:2]), int(d[2:])])
                    elif len(d) == 2:  # 月日
                        numbers.append(int(d))
                    else:
                        numbers.append(int(d))
                lucky_sources['birthday'] = list(set(numbers))
            except:
                pass
        
        # 解析手机号
        if phone:
            try:
                # 提取所有数字
                digits = re.findall(r'\d', phone)
                # 两两分组
                numbers = []
                for i in range(0, len(digits)-1, 2):
                    num = int(digits[i] + digits[i+1])
                    numbers.append(num)
                lucky_sources['phone'] = list(set(numbers))
            except:
                pass
        
        # 自定义数字
        if custom:
            lucky_sources['custom'] = custom
        
        return lucky_sources
    
    def map_to_valid_range(self, numbers: List[int], max_num: int) -> List[int]:
        """将数字映射到有效范围"""
        valid = []
        for n in numbers:
            if 1 <= n <= max_num and n not in valid:
                valid.append(n)
            elif n > max_num:
                # 取模映射
                mapped = (n - 1) % max_num + 1
                if mapped not in valid:
                    valid.append(mapped)
        return sorted(valid)
    
    def generate_with_lucky(self, birthday: Optional[str] = None,
                           phone: Optional[str] = None,
                           custom: Optional[List[int]] = None,
                           count: int = 3) -> Dict:
        """基于幸运数字生成"""
        lucky_sources = self.parse_lucky_numbers(birthday, phone, custom)
        
        # 合并所有幸运数字
        all_lucky = []
        for source, nums in lucky_sources.items():
            all_lucky.extend(nums)
        all_lucky = list(set(all_lucky))
        
        # 生成组合
        combinations = []
        
        for i in range(count):
            if self.lottery_type == 'ssq':
                # 映射到红球范围
                lucky_red = self.map_to_valid_range(all_lucky, 33)
                # 随机选择部分幸运数字（避免全固定）
                if len(lucky_red) >= 3:
                    selected_lucky = random.sample(lucky_red, min(3, len(lucky_red)))
                else:
                    selected_lucky = lucky_red
                
                # 补充红球
                remaining = 6 - len(selected_lucky)
                available = [n for n in range(1, 34) if n not in selected_lucky]
                supplement = random.sample(available, remaining)
                red = sorted(selected_lucky + supplement)
                
                # 蓝球（从幸运数字映射或随机）
                lucky_blue_candidates = [n for n in all_lucky if 1 <= n <= 16]
                blue = random.choice(lucky_blue_candidates) if lucky_blue_candidates else random.randint(1, 16)
                
                combinations.append({
                    'red_balls': red,
                    'blue_ball': blue,
                    'lucky_source': selected_lucky,
                    'type': 'lucky'
                })
            else:  # dlt
                # 映射到前区
                lucky_front = self.map_to_valid_range(all_lucky, 35)
                if len(lucky_front) >= 2:
                    selected_lucky = random.sample(lucky_front, min(2, len(lucky_front)))
                else:
                    selected_lucky = lucky_front
                
                # 补充前区
                remaining = 5 - len(selected_lucky)
                available = [n for n in range(1, 36) if n not in selected_lucky]
                supplement = random.sample(available, remaining)
                front = sorted(selected_lucky + supplement)
                
                # 后区
                lucky_back_candidates = [n for n in all_lucky if 1 <= n <= 12]
                if len(lucky_back_candidates) >= 2:
                    back = sorted(random.sample(lucky_back_candidates, 2))
                else:
                    remaining_back = 2 - len(lucky_back_candidates)
                    available_back = [n for n in range(1, 13) if n not in lucky_back_candidates]
                    back = sorted(lucky_back_candidates + random.sample(available_back, remaining_back))
                
                combinations.append({
                    'front_zone': front,
                    'back_zone': back,
                    'lucky_source': selected_lucky,
                    'type': 'lucky'
                })
        
        return {
            'combinations': combinations,
            'lucky_sources': lucky_sources,
            'all_lucky_numbers': all_lucky,
            'disclaimer': format_disclaimer()
        }

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='彩票号码生成工具')
    parser.add_argument('--lottery', choices=['ssq', 'dlt'], required=True)
    parser.add_argument('--strategy', choices=['random', 'fixed', 'lucky'], default='random')
    parser.add_argument('--count', type=int, default=5)
    parser.add_argument('--birthday', help='生日，格式：1990-05-20')
    parser.add_argument('--phone', help='手机尾号')
    
    args = parser.parse_args()
    
    generator = NumberGenerator(args.lottery)
    
    if args.strategy == 'random':
        result = generator.generate_random(args.count)
    elif args.strategy == 'lucky':
        result = generator.generate_with_lucky(
            birthday=args.birthday,
            phone=args.phone,
            count=args.count
        )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
```

**Step 3: 测试**

```bash
# 测试随机生成
python scripts/generate_numbers.py --lottery ssq --strategy random --count 3

# 测试幸运数字
python scripts/generate_numbers.py --lottery ssq --strategy lucky --birthday 1990-05-20 --phone 6688 --count 3
```

Expected: 输出生成的号码组合，幸运数字模式显示来源

---

## Phase 3: 报告系统

### Task 7: Markdown报告模板

**Files:**
- Create: `templates/report_markdown.md`

**内容**:
```markdown
# {{lottery_name}} 分析报告

> ⚠️ **免责声明**：彩票开奖是完全随机的独立事件，本报告仅供娱乐参考，不构成投注建议。请理性购彩，量力而行。

---

## 📊 统计概览

- **分析彩种**: {{lottery_name}}
- **统计周期**: 最近{{period}}期
- **数据更新时间**: {{update_time}}

---

## 🔥 热号冷号分析

### 热号 TOP10
{{#hot_numbers}}
- {{number}}号 - 出现{{count}}次
{{/hot_numbers}}

### 冷号 TOP10
{{#cold_numbers}}
- {{number}}号 - 出现{{count}}次
{{/cold_numbers}}

---

## 📉 遗漏值分析

### 最大遗漏（长期未开出）
{{#max_missing}}
- {{number}}号 - 遗漏{{count}}期
{{/max_missing}}

### 遗漏分布
- 热遗漏（<5期）: {{hot_missing_count}}个号码
- 温遗漏（5-15期）: {{warm_missing_count}}个号码
- 冷遗漏（>15期）: {{cold_missing_count}}个号码

---

## ⚖️ 分布统计

### 奇偶比分布
{{#odd_even_stats}}
- {{ratio}}: {{count}}次（{{percentage}}%）
{{/odd_even_stats}}

### 大小比分布
{{#big_small_stats}}
- {{ratio}}: {{count}}次（{{percentage}}%）
{{/big_small_stats}}

---

## 🎲 号码生成（娱乐）

{{#generated_numbers}}
### 组合 {{index}}
{{#ssq}}
红球: {{red_balls}}
蓝球: {{blue_ball}}
{{/ssq}}
{{#dlt}}
前区: {{front_zone}}
后区: {{back_zone}}
{{/dlt}}
{{/generated_numbers}}

---

*报告生成时间: {{report_time}}*
*数据来源: 中国福彩/体彩官网*
```

---

### Task 8: HTML报告模板

**Files:**
- Create: `templates/report_template.html`

**核心结构**:
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>彩票分析报告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg-primary: #09090B;
            --bg-secondary: #18181B;
            --border: #27272A;
            --text-primary: #FAFAFA;
            --text-secondary: #A1A1AA;
            --red: #EF4444;
            --blue: #3B82F6;
            --orange: #F97316;
            --green: #10B981;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
        }
        
        .disclaimer-banner {
            background: linear-gradient(135deg, #F97316 0%, #EF4444 100%);
            padding: 20px;
            text-align: center;
            font-weight: bold;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .card {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
        }
        
        .chart-container {
            position: relative;
            height: 300px;
            margin: 20px 0;
        }
        
        .ball {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            font-weight: bold;
            margin: 4px;
        }
        
        .ball-red {
            background: var(--red);
            color: white;
        }
        
        .ball-blue {
            background: var(--blue);
            color: white;
        }
    </style>
</head>
<body>
    <!-- 免责声明 -->
    <div class="disclaimer-banner">
        ⚠️ 彩票开奖是完全随机的独立事件，本报告仅供娱乐参考，不构成投注建议
    </div>
    
    <div class="container">
        <!-- 报告内容 -->
        <h1>{{lottery_name}} 分析报告</h1>
        
        <!-- 统计图表 -->
        <div class="card">
            <h2>热号冷号分布</h2>
            <div class="chart-container">
                <canvas id="hotColdChart"></canvas>
            </div>
        </div>
        
        <!-- 更多内容... -->
    </div>
    
    <script>
        // Chart.js 配置
    </script>
</body>
</html>
```

---

## Phase 4: 集成与部署

### Task 9: Sub-agents开发

**Files:**
- Create: `.claude/agents/subagent_ssq_analyst.md`
- Create: `.claude/agents/subagent_dlt_analyst.md`

**双色球Agent示例**:
```markdown
# Sub-agent: 双色球分析专家

## 职责
专门处理双色球的业务逻辑和数据分析。

## 能力
- 理解双色球规则（6红+1蓝）
- 调用Data Fetcher获取数据
- 调用Analyzer进行统计分析
- 调用Generator生成号码
- 生成双色球专属报告

## 工作流
1. 接收用户请求
2. 识别意图（查看最新/统计分析/固定号码/幸运数字）
3. 调用相应Skills
4. 整合结果并添加双色球特定说明
5. 输出带免责声明的结果

## 输出格式
始终包含：
- 双色球特定术语（红球、蓝球）
- 开奖时间说明（周二、四、日 21:15）
- 标准免责声明
```

---

### Task 10: 启动脚本

**Files:**
- Create: `start-lottery-agent.sh`
- Create: `start-lottery-agent.bat`

**Bash版本**:
```bash
#!/bin/bash

# 彩票分析 Agent 启动脚本
# Lottery Analysis Agent Launcher

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}"
echo "╔════════════════════════════════════╗"
echo "║     🎱 彩票分析 Agent v1.0.0       ║"
echo "║   Lottery Analysis Agent          ║"
echo "╚════════════════════════════════════╝"
echo -e "${NC}"

# 检查目录
if [ ! -d ".claude" ]; then
    echo -e "${RED}错误：请在项目根目录运行此脚本${NC}"
    exit 1
fi

# 显示免责声明
echo -e "${YELLOW}"
echo "⚠️  重要提示："
echo "    彩票开奖是完全随机的独立事件"
echo "    本系统仅供娱乐参考，不构成投注建议"
echo "    请理性购彩，量力而行"
echo -e "${NC}"
echo ""

# 检查参数
if [ $# -eq 0 ]; then
    # 交互模式
    echo "启动交互模式..."
    echo "请输入您的请求（例如：'查看双色球最新开奖'）："
    echo ""
    
    # 启动 Claude
    claude
else
    # 命令行模式
    echo "执行命令: $*"
    claude -p "$*"
fi
```

---

## 完整任务清单

| Phase | 任务 | 文件 | 优先级 |
|-------|------|------|--------|
| 1 | 创建目录结构 | - | P0 |
| 1 | 彩种配置 | `.claude/config/lottery_types.json` | P0 |
| 1 | 预置历史数据 | `data/ssq/history.json`, `data/dlt/history.json` | P0 |
| 1 | 工具函数 | `scripts/utils.py` | P0 |
| 1 | Claude配置 | `.claude/settings.json` | P0 |
| 2 | Data Fetcher Skill | `.claude/skills/skill_lottery_data_fetcher.md` | P0 |
| 2 | Data Fetcher脚本 | `scripts/fetch_lottery_data.py` | P0 |
| 2 | Analyzer Skill | `.claude/skills/skill_lottery_analyzer.md` | P0 |
| 2 | Analyzer脚本 | `scripts/analyze_history.py` | P0 |
| 2 | Generator Skill | `.claude/skills/skill_lottery_generator.md` | P0 |
| 2 | Generator脚本 | `scripts/generate_numbers.py` | P0 |
| 3 | Markdown模板 | `templates/report_markdown.md` | P1 |
| 3 | HTML模板 | `templates/report_template.html` | P1 |
| 4 | SSQ Agent | `.claude/agents/subagent_ssq_analyst.md` | P1 |
| 4 | DLT Agent | `.claude/agents/subagent_dlt_analyst.md` | P1 |
| 4 | 启动脚本 | `start-lottery-agent.sh`, `.bat` | P1 |

---

## 实施策略建议

### 选项1: Subagent-Driven（推荐）
- 在当前会话中执行
- 每个Task分配一个子Agent
- 我负责审核每个Task的结果
- 适合：需要频繁沟通和调整

### 选项2: Parallel Session
- 创建新会话执行
- 使用 `superpowers:executing-plans` skill
- 批量执行，定期汇报进度
- 适合：明确需求，可以放手执行

---

**计划保存完成！**

下一步：
1. ✅ 初始化Git仓库
2. 🚀 开始实施（选择上述策略）

**请告诉我您想如何继续？**
