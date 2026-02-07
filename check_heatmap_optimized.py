#!/usr/bin/env python3
"""检查优化后的热力图分布"""
import sys
sys.path.insert(0, 'scripts')
from analyze_history import LotteryAnalyzer
from collections import Counter


analyzer = LotteryAnalyzer("ssq")
data = analyzer.get_periods(100)

# 统计红球出现次数
red_balls = []
for record in data:
    red_balls.extend(record.get("red_balls", []))
counter = Counter(red_balls)

# 获取所有号码的出现次数
all_counts = {num: counter.get(num, 0) for num in range(1, 34)}
sorted_counts = sorted(all_counts.values())
n = len(sorted_counts)

# 计算百分位数
p25 = sorted_counts[int(n * 0.25)]
p50 = sorted_counts[int(n * 0.50)]
p75 = sorted_counts[int(n * 0.75)]
p90 = sorted_counts[int(n * 0.90)]

print(f"分析期数: 100期")
print(f"百分位数阈值:")
print(f"  P90 (前10%): ≥{p90}次")
print(f"  P75 (前25%): ≥{p75}次")
print(f"  P50 (前50%): ≥{p50}次")
print(f"  P25 (前75%): ≥{p25}次")
print()

# 统计每个等级
cold = heat0 = heat1 = hot1 = hot2 = hot3 = 0
level_counts = {}

for num, count in all_counts.items():
    if count >= p90:
        level = "🔥🔥🔥 hot-3"
        hot3 += 1
    elif count >= p75:
        level = "🔥🔥 hot-2"
        hot2 += 1
    elif count >= p50:
        level = "🔥 hot-1"
        hot1 += 1
    elif count >= p25:
        level = "🌡️ heat-1"
        heat1 += 1
    elif count > 0:
        level = "🌡️ heat-0"
        heat0 += 1
    else:
        level = "❄️ cold"
        cold += 1
    
    level_name = level.split()[1]
    if level_name not in level_counts:
        level_counts[level_name] = []
    level_counts[level_name].append((num, count))

print("优化后的分布:")
print("="*60)

for level_name in ["hot-3", "hot-2", "hot-1", "heat-1", "heat-0", "cold"]:
    if level_name in level_counts:
        numbers = level_counts[level_name]
        emoji = {"hot-3": "🔥🔥🔥", "hot-2": "🔥🔥", "hot-1": "🔥", "heat-1": "🌡️", "heat-0": "🌡️", "cold": "❄️"}[level_name]
        print(f"\n{emoji} {level_name}: {len(numbers)}个号码")
        for num, count in sorted(numbers, key=lambda x: x[1], reverse=True):
            print(f"    {num:02d}号: {count}次")

print()
print("="*60)
print(f"总计: {hot3 + hot2 + hot1 + heat1 + heat0 + cold}个号码")
print(f"分布: hot-3={hot3}, hot-2={hot2}, hot-1={hot1}, heat-1={heat1}, heat-0={heat0}, cold={cold}")
