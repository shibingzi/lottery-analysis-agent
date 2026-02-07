#!/usr/bin/env python3
# 运行分析报告
import json
from collections import Counter
from pathlib import Path

print("="*70)
print("🎱 彩票分析助手 - 运行演示")
print("="*70)
print()

# 读取双色球数据
with open('data/ssq/history.json', 'r', encoding='utf-8') as f:
    ssq_data = json.load(f)

print(f"📊 双色球数据: {len(ssq_data)} 期")
print(f"   期号范围: {ssq_data[-1]['issue']} → {ssq_data[0]['issue']}")
print()

# 统计红球
red_counter = Counter()
blue_counter = Counter()

for draw in ssq_data:
    red_counter.update(draw['red_balls'])
    blue_counter.update([draw['blue_ball']])

# 热号
print("🔥 红球热号 TOP10:")
hot_red = red_counter.most_common(10)
for i, (num, count) in enumerate(hot_red, 1):
    print(f"   {i:2}. {num:02d}号 - 出现 {count} 次")

print()
print("🔵 蓝球热号 TOP5:")
hot_blue = blue_counter.most_common(5)
for i, (num, count) in enumerate(hot_blue, 1):
    print(f"   {i}. {num:02d}号 - 出现 {count} 次")

print()
print("❄️ 红球冷号 TOP10 (出现最少):")
cold_red = sorted(red_counter.items(), key=lambda x: x[1])[:10]
for i, (num, count) in enumerate(cold_red, 1):
    print(f"   {i:2}. {num:02d}号 - 出现 {count} 次")

# 计算遗漏值
print()
print("📉 红球遗漏值 TOP10:")
last_seen = {i: -1 for i in range(1, 34)}
for idx, draw in enumerate(ssq_data):
    for ball in draw['red_balls']:
        if last_seen[ball] == -1:
            last_seen[ball] = idx

missing = [(num, last_seen[num] if last_seen[num] >= 0 else len(ssq_data)) 
           for num in range(1, 34)]
missing.sort(key=lambda x: x[1], reverse=True)

for i, (num, miss) in enumerate(missing[:10], 1):
    print(f"   {i:2}. {num:02d}号 - 已遗漏 {miss} 期")

print()
print("="*70)

# 大乐透数据
with open('data/dlt/history.json', 'r', encoding='utf-8') as f:
    dlt_data = json.load(f)

print(f"📊 大乐透数据: {len(dlt_data)} 期")
print(f"   期号范围: {dlt_data[-1]['issue']} → {dlt_data[0]['issue']}")
print()

# 统计大乐透
front_counter = Counter()
back_counter = Counter()

for draw in dlt_data:
    front_counter.update(draw['front_zone'])
    back_counter.update(draw['back_zone'])

print("🔥 前区热号 TOP10:")
hot_front = front_counter.most_common(10)
for i, (num, count) in enumerate(hot_front, 1):
    print(f"   {i:2}. {num:02d}号 - 出现 {count} 次")

print()
print("🔵 后区热号 TOP5:")
hot_back = back_counter.most_common(5)
for i, (num, count) in enumerate(hot_back, 1):
    print(f"   {i}. {num:02d}号 - 出现 {count} 次")

print()
print("="*70)

# 生成随机号码
import random
print("🎲 随机机选 (娱乐性质):")
print()
print("双色球随机号码:")
for i in range(3):
    red = sorted(random.sample(range(1, 34), 6))
    blue = random.randint(1, 16)
    print(f"   {i+1}. 红球: {' '.join(f'{r:02d}' for r in red)} + 蓝球: {blue:02d}")

print()
print("大乐透随机号码:")
for i in range(3):
    front = sorted(random.sample(range(1, 36), 5))
    back = sorted(random.sample(range(1, 13), 2))
    print(f"   {i+1}. 前区: {' '.join(f'{f:02d}' for f in front)} + 后区: {' '.join(f'{b:02d}' for b in back)}")

print()
print("="*70)
print("✅ 演示完成!")
print()
print("⚠️  重要提示: 彩票开奖是完全随机的独立事件，以上分析")
print("    仅供娱乐参考，不构成投注建议。请理性购彩，量力而行。")
print("="*70)
