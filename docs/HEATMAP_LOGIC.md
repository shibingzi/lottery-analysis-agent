# 号码分布热力图逻辑详解

## 📊 概述

号码分布热力图是一种可视化展示，用颜色深浅表示每个号码在指定分析期数内的**出现频率**。

## 🎯 核心逻辑

### 1. 数据统计

```python
# 从原始数据重新统计所有号码的出现次数
with open(self.config["data_file"], 'r', encoding='utf-8') as f:
    all_data = json.load(f)

# 获取分析期数对应的数据（最近N期）
periods = analysis_data.get("periods_analyzed", 100)
recent_data = all_data[:periods]

# 统计所有号码出现次数
red_balls = []
for record in recent_data:
    red_balls.extend(record.get("red_balls", []))
counter = Counter(red_balls)
```

**示例**（100期双色球分析）：
- 02号出现26次
- 09号出现27次
- 29号出现9次
- 17号出现19次

### 2. 热度等级计算

采用**相对频率**而非绝对次数，确保热力图更有意义：

```python
# 找出出现次数最多的号码
max_count = max(all_counts.values())  # 例如：27次（09号）

# 计算每个号码的相对频率
ratio = count / max_count
```

**热度等级划分**：

| 等级 | CSS类名 | 条件 | 颜色 | 含义 |
|:---:|:---:|:---:|:---:|:---:|
| 🔥🔥🔥 | `hot-3` | ratio ≥ 0.8 | 深红色 | 最热 |
| 🔥🔥 | `hot-2` | ratio ≥ 0.6 | 橙色 | 很热 |
| 🔥 | `hot-1` | ratio ≥ 0.4 | 浅橙色 | 较热 |
| 🌡️ | `heat-1` | count > 0 | 青色 | 温热 |
| ❄️ | `cold` | count = 0 | 灰色 | 冷号 |

**示例计算**：
```
09号: 27次 / 27次(最大) = 1.0 → hot-3 (深红)
02号: 26次 / 27次 = 0.96 → hot-3 (深红)
13号: 23次 / 27次 = 0.85 → hot-3 (深红)
03号: 22次 / 27次 = 0.81 → hot-3 (深红)
24号: 22次 / 27次 = 0.81 → hot-3 (深红)
08号: 22次 / 27次 = 0.81 → hot-3 (深红)
29号: 9次 / 27次 = 0.33 → heat-1 (青色)
```

### 3. 颜色渐变原理

```css
/* 冷号 - 从未出现 */
.heatmap-cell.cold {
    background: var(--border);      /* 深灰色 */
    color: var(--text-muted);        /* 浅灰色文字 */
}

/* heat-1 - 出现但较少 */
.heatmap-cell.heat-1 {
    background: rgba(6, 182, 212, 0.3);  /* 青色，30%透明度 */
    color: var(--cold);                   /* 青色文字 */
}

/* hot-1 - 较热 */
.heatmap-cell.hot-1 {
    background: rgba(249, 115, 22, 0.3);  /* 橙色，30%透明度 */
    color: #FB923C;                        /* 橙色文字 */
}

/* hot-2 - 很热 */
.heatmap-cell.hot-2 {
    background: rgba(249, 115, 22, 0.5);  /* 橙色，50%透明度 */
    color: #F97316;                        /* 深橙色文字 */
}

/* hot-3 - 最热 */
.heatmap-cell.hot-3 {
    background: rgba(239, 68, 68, 0.5);   /* 红色，50%透明度 */
    color: #EF4444;                        /* 红色文字 */
}
```

### 4. 为什么使用相对频率？

**问题**：如果使用绝对次数，不同分析期数的热力图无法比较。

**示例**：
- 分析50期：最热门的号码出现15次
- 分析100期：最热门的号码出现27次

如果使用绝对值，100期的热力图整体会更"红"，不利于跨期数比较。

**解决方案**：使用相对频率（相对于最大出现次数的比例）
- 无论分析多少期，最热号码始终是 `hot-3`（深红色）
- 便于直观比较不同分析期数的结果

## 📈 实际效果示例

### 双色球100期热力图

```
01[16]  02[26]🔥 03[22]🔥  04[21]🔥  05[20]🔥  06[20]🔥
07[15]  08[22]🔥 09[27]🔥🔥 10[20]🔥  11[14]    12[17]
13[23]🔥 14[18]   15[19]   16[17]   17[19]   18[18]
...
29[9]   30[18]   31[17]   32[18]   33[19]

图例：
🔥🔥 = hot-3 (出现≥80%最大次数)
🔥   = hot-2 (出现≥60%最大次数)
🌡️  = hot-1 (出现≥40%最大次数)
     = heat-1 (出现但<40%)
     = cold (未出现)
```

### 从热力图可以观察到什么？

1. **热号聚集区**：某些号码段是否集中出现
2. **冷号区域**：哪些号码长期未出
3. **分布均匀性**：号码是否均匀分布
4. **异常值**：是否有号码明显偏离平均水平

## 🛠️ 技术实现

### 数据流

```
原始JSON数据 → 统计出现次数 → 计算相对频率 → 分配热度等级 → 生成HTML
```

### 关键代码

```python
def _generate_heatmap_section(self, analysis_data: Dict) -> Dict:
    # 1. 统计
    counter = Counter(all_numbers)
    all_counts = {num: counter.get(num, 0) for num in range(1, 34)}
    
    # 2. 找最大值
    max_count = max(all_counts.values())
    
    # 3. 分级
    for num, count in all_counts.items():
        ratio = count / max_count if max_count > 0 else 0
        if ratio >= 0.8:
            heat_class = "hot-3"
        elif ratio >= 0.6:
            heat_class = "hot-2"
        elif ratio >= 0.4:
            heat_class = "hot-1"
        elif count > 0:
            heat_class = "heat-1"
        else:
            heat_class = "cold"
        
        heatmap_data.append({
            "NUMBER": f"{num:02d}",
            "COUNT": count,
            "HEAT_CLASS": heat_class
        })
    
    return {"NUMBER_HEATMAP": heatmap_data}
```

## 💡 使用建议

1. **短周期分析**（10-30期）：适合观察近期趋势
2. **中周期分析**（50-100期）：适合观察中期规律
3. **长周期分析**（200+期）：适合观察长期分布

不同周期可能显示不同的热力分布，建议多周期对比观察。

## 📊 与其他指标的关系

| 指标 | 热力图 | 关系 |
|:---:|:---:|:---|
| **热号TOP10** | 最红的格子 | 对应hot-2和hot-3的号码 |
| **冷号TOP10** | 灰色/青色格子 | 对应cold和heat-1的号码 |
| **遗漏值** | 不直接显示 | 但长期未出的号码会显示为cold |

热力图提供了**全局视角**，而热号/冷号排行只显示极端值。两者结合使用效果更佳！
