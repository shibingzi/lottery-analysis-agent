#!/usr/bin/env python3
import sys
sys.path.insert(0, 'scripts')
from analyze_history import LotteryAnalyzer

analyzer = LotteryAnalyzer("ssq")
result = analyzer.full_analysis(23)

print("="*60)
print("连号分析验证")
print("="*60)

consecutive = result.get('consecutive', {})
print(f"\n从分析结果获取:")
print(f"  consecutive_rate: {consecutive.get('consecutive_rate')}")
print(f"  consecutive_periods: {consecutive.get('consecutive_periods')}")
print(f"  top_patterns: {consecutive.get('top_patterns')}")

print(f"\n手动检查数据中是否有连号:")
data = analyzer.get_periods(23)
consecutive_count = 0
for record in data:
    red_balls = sorted(record.get('red_balls', []))
    has_consecutive = False
    for i in range(len(red_balls) - 1):
        if red_balls[i+1] - red_balls[i] == 1:
            consecutive_count += 1
            print(f"  期号 {record['issue']}: {red_balls} - 连号 {red_balls[i]}-{red_balls[i+1]}")
            has_consecutive = True
            break
    if not has_consecutive:
        print(f"  期号 {record['issue']}: {red_balls} - 无连号")

print(f"\n结论: 总共 {consecutive_count}/{len(data)} 期出现连号")
