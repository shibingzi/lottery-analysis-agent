# 彩票分析助手 - 手动测试清单

## ✅ 文件结构检查

### 1. 检查所有核心文件是否存在
```bash
# 在项目根目录运行
ls -la
cat README.md | head -20
cat USER_GUIDE.md | head -20
```

### 2. 检查数据文件
```bash
cat data/ssq/history.json | python -m json.tool | head -30
cat data/dlt/history.json | python -m json.tool | head -30
```

### 3. 检查Scripts
```bash
ls -la scripts/
head -50 scripts/analyze_history.py
head -50 scripts/generate_fixed_numbers.py
head -50 scripts/generate_report.py
```

---

## ✅ 功能测试

### 测试 1: 数据文件验证
**预期结果**: 数据文件格式正确

```python
import json

# 测试双色球
with open('data/ssq/history.json') as f:
    data = json.load(f)
print(f"双色球: {len(data)} 期")
print(f"字段: {list(data[0].keys())}")
print(f"最新期号: {data[0]['issue']}")

# 测试大乐透
with open('data/dlt/history.json') as f:
    data = json.load(f)
print(f"大乐透: {len(data)} 期")
```

**预期输出**:
```
双色球: 23 期
字段: ['lottery_type', 'issue', 'draw_date', 'red_balls', 'blue_ball', 'prize_info']
最新期号: 2025023
大乐透: 23 期
```

---

### 测试 2: 分析器功能
**预期结果**: 能成功分析历史数据

```python
import sys
sys.path.insert(0, 'scripts')
from analyze_history import LotteryAnalyzer

# 测试双色球分析
analyzer = LotteryAnalyzer('ssq')
result = analyzer.full_analysis(10)

print(f"分析期数: {result['periods_analyzed']}")
print(f"期号范围: {result['date_range']['end_issue']} - {result['date_range']['start_issue']}")
print(f"热号TOP3: {result['hot_cold']['red_balls']['hot'][:3]}")
print(f"遗漏值TOP3: {list(result['missing']['red_balls'].items())[:3]}")
print(f"奇偶比分布: {dict(list(result['odd_even'].items())[:3])}")
```

**预期输出**:
```
分析期数: 10
期号范围: 2025023 - 2025014
热号TOP3: [(12, 3), (25, 3), (28, 3)]
遗漏值TOP3: [(1, 10), (2, 10), (4, 10)]
奇偶比分布: {'3:3': 4, '2:4': 3, '4:2': 3}
```

---

### 测试 3: 固定号码分析
**预期结果**: 能分析固定号码并生成组合

```python
import sys
sys.path.insert(0, 'scripts')
from analyze_history import LotteryAnalyzer
from generate_fixed_numbers import FixedNumberAnalyzer

# 先获取分析数据
analyzer = LotteryAnalyzer('ssq')
result = analyzer.full_analysis(20)

# 测试固定号码分析
fixed_analyzer = FixedNumberAnalyzer('ssq')
stats = fixed_analyzer.analyze_fixed_numbers([7, 18, 25], [14], result)

print(f"固定红球: {stats['fixed_red']}")
print(f"固定蓝球: {stats['fixed_blue']}")
print(f"需要补充: {stats['red_needed']}红 {stats['blue_needed']}蓝")

# 生成组合
combos = fixed_analyzer.generate_combinations([7, 18, 25], [14], result, 3)
for i, combo in enumerate(combos, 1):
    print(f"组合{i}: {combo['combination']}")
```

**预期输出**:
```
固定红球: [7, 18, 25]
固定蓝球: [14]
需要补充: 3红 0蓝
组合1: [7, 18, 25, 12, 28, 30] + [14]
组合2: [7, 18, 25, 5, 19, 22] + [14]
组合3: [7, 18, 25, 8, 16, 29] + [14]
```

---

### 测试 4: HTML报告生成
**预期结果**: 生成完整的HTML报告

```python
import sys
sys.path.insert(0, 'scripts')
from analyze_history import LotteryAnalyzer
from generate_report import ReportGenerator

# 获取分析数据
analyzer = LotteryAnalyzer('ssq')
result = analyzer.full_analysis(20)

# 生成报告
generator = ReportGenerator('ssq')
html = generator.generate(result, fixed_red=[7, 18, 25], fixed_blue=[14])

# 保存报告
output_path = generator.save_report(html, 'reports/test_report.html')
print(f"报告已生成: {output_path}")
print(f"文件大小: {len(html)} 字符")

# 检查HTML内容
if '<!DOCTYPE html>' in html and '</html>' in html:
    print("✅ HTML格式正确")
if '<canvas id="hotNumbersChart">' in html:
    print("✅ 包含图表")
if '热号TOP10' in html:
    print("✅ 包含热号分析")
```

**预期输出**:
```
报告已生成: /path/to/lottery-analysis-agent/reports/test_report.html
文件大小: 28543 字符
✅ HTML格式正确
✅ 包含图表
✅ 包含热号分析
```

---

### 测试 5: 命令行工具
**预期结果**: 命令行参数正常工作

```bash
# 测试1: 分析历史
python scripts/analyze_history.py --type ssq --periods 10

# 测试2: 输出JSON
python scripts/analyze_history.py --type ssq --periods 10 --json

# 测试3: 保存到文件
python scripts/analyze_history.py --type ssq --periods 10 --output test_result.txt

# 测试4: 固定号码分析
python scripts/generate_fixed_numbers.py --type ssq --fixed-red 07,18,25 --generate

# 测试5: 生成报告
python scripts/generate_report.py --type ssq --periods 20 --output reports/ssq_report.html
```

---

## ✅ 手动验证清单

### 1. 检查生成的HTML报告
打开 `reports/test_report.html` 检查：
- [ ] 页面标题正确显示"双色球分析报告"
- [ ] 包含免责声明横幅
- [ ] 显示最新开奖结果（6个红球 + 1个蓝球）
- [ ] 包含热号TOP10图表
- [ ] 包含冷号TOP10图表
- [ ] 奇偶比分布表格正确
- [ ] 大小比分布表格正确
- [ ] 遗漏值柱状图正常显示
- [ ] 号码热力图有颜色区分
- [ ] 固定号码部分显示正确
- [ ] 页脚包含免责声明

### 2. 检查数据完整性
- [ ] 双色球数据包含 23 期
- [ ] 大乐透数据包含 23 期
- [ ] 每期的字段完整（issue, draw_date, red_balls/blue_ball 或 front_zone/back_zone）
- [ ] 号码格式正确（1-33 红球，1-16 蓝球）

### 3. 检查分析结果合理性
- [ ] 热号出现次数 > 冷号出现次数
- [ ] 遗漏值范围在 0 到分析期数之间
- [ ] 奇偶比总和等于6（双色球）或5（大乐透）
- [ ] 和值在合理范围内（双色球: 21-183，大乐透: 15-165）
- [ ] 跨度在合理范围内（双色球: 5-32，大乐透: 4-34）

---

## ✅ 测试通过标准

| 测试项目 | 通过标准 | 状态 |
|---------|---------|------|
| 数据文件 | JSON格式正确，数据完整 | ⬜ |
| 分析器 | 能成功分析10+期数据 | ⬜ |
| 固定号码 | 能分析并生成3+个组合 | ⬜ |
| 报告生成 | 生成有效HTML文件，>20KB | ⬜ |
| 命令行 | 所有参数正常工作 | ⬜ |
| HTML显示 | 图表、表格正常显示 | ⬜ |

**总体通过标准**: 6/6 项测试通过 ✅

---

## 🚀 快速测试命令

一键运行所有测试：
```bash
cd lottery-analysis-agent
python scripts/test_runner.py
```

或分步测试：
```bash
# 1. 验证数据
python -c "import json; d=json.load(open('data/ssq/history.json')); print(f'✅ 双色球: {len(d)}期')"

# 2. 测试分析
python scripts/analyze_history.py --type ssq --periods 10 --json > /dev/null && echo "✅ 分析器正常"

# 3. 测试固定号码
python scripts/generate_fixed_numbers.py --type ssq --fixed-red 07,18,25 --generate > /dev/null && echo "✅ 固定号码正常"

# 4. 生成报告
python scripts/generate_report.py --type ssq --periods 20 --output reports/test.html && echo "✅ 报告生成正常"

# 5. 检查报告
ls -lh reports/test.html && echo "✅ 报告文件存在"
```

---

## ⚠️ 常见问题

1. **ImportError**: 确保在项目根目录运行，或设置 `PYTHONPATH`
2. **FileNotFoundError**: 检查 `data/` 目录是否存在
3. **JSON解析错误**: 检查数据文件格式是否正确
4. **HTML显示异常**: 检查 `templates/styles.css` 是否存在

---

**测试日期**: 2026-02-07  
**测试版本**: v1.0.0
