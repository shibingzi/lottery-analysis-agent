# 彩票分析 Agent - 数据源说明

**文档版本**: v1.0.0  
**最后更新**: 2026-02-07

---

## 📡 官方数据源

### 1. 中国福利彩票发行管理中心

**官网**: http://www.cwl.gov.cn/

**提供数据**:
- 双色球历史开奖数据
- 3D 历史开奖数据
- 七乐彩历史开奖数据
- 快乐8历史开奖数据

**数据更新频率**:
- 开奖后30分钟内更新
- 历史数据可查询近10年

**数据字段**:
```json
{
  "lottery_code": "ssq",
  "issue": "2025023",
  "draw_date": "2025-03-02",
  "week": "星期日",
  "red_balls": ["03", "07", "12", "18", "25", "30"],
  "blue_ball": "14",
  "sale_amount": "450,123,456",
  "prize_pool": "2,345,678,901",
  "first_prize_count": 5,
  "first_prize_amount": "10,000,000",
  "second_prize_count": 89,
  "second_prize_amount": "285,000"
}
```

---

### 2. 中国体育彩票管理中心

**官网**: https://www.lottery.gov.cn/

**提供数据**:
- 大乐透历史开奖数据
- 排列3/排列5历史数据
- 七星彩历史开奖数据
- 足彩/竞彩数据

**数据更新频率**:
- 开奖后30分钟内更新
- 历史数据可查询近10年

**数据字段**:
```json
{
  "lottery_code": "dlt",
  "issue": "25023",
  "draw_date": "2025-03-01",
  "week": "星期六",
  "front_zone": ["05", "12", "23", "28", "35"],
  "back_zone": ["03", "09"],
  "sale_amount": "380,456,789",
  "prize_pool": "1,876,543,210",
  "first_prize_count": 3,
  "first_prize_amount": "10,000,000",
  "second_prize_count": 67,
  "second_prize_amount": "156,000"
}
```

---

## 🔧 数据获取方式

### 方式 1: WebFetch 直接抓取

```python
# 示例: 使用 WebFetch 获取开奖数据
WebFetch("http://www.cwl.gov.cn/fcpz/yxjs/ssq/")
WebFetch("https://www.lottery.gov.cn/dlt/")
```

**优点**:
- 无需 API Key
- 数据权威可靠

**缺点**:
- 需要解析 HTML
- 网站结构可能变化

---

### 方式 2: WebSearch 搜索最新数据

```bash
# 搜索最新开奖结果
WebSearch("双色球 2025023 开奖结果")
WebSearch("大乐透 25023 开奖号码")
```

**优点**:
- 快速获取最新信息
- 可获取新闻和分析

**缺点**:
- 数据格式不统一
- 需要验证数据准确性

---

### 方式 3: 第三方数据 API

#### 聚合数据
**官网**: https://www.juhe.cn/

**提供 API**:
- 双色球开奖结果查询
- 大乐透开奖结果查询
- 历史数据查询

**数据格式**: JSON

**认证方式**: API Key

#### 彩票网 API
**官网**: https://www.lotteryapi.com/

**提供 API**:
- 多彩种开奖数据
- 实时开奖推送

**数据格式**: JSON

**认证方式**: API Key

---

## 📝 数据存储结构

### 双色球数据 (`data/ssq/`)

```
data/ssq/
├── history.json          # 历史开奖数据
├── statistics.json       # 统计分析结果
└── predictions.json      # 预测记录
```

**history.json 结构**:
```json
{
  "lottery_type": "ssq",
  "last_update": "2026-02-07T15:30:00Z",
  "total_records": 3000,
  "data": [
    {
      "issue": "2025023",
      "draw_date": "2025-03-02",
      "red_balls": [3, 7, 12, 18, 25, 30],
      "blue_ball": 14,
      "prize_info": {...}
    }
  ]
}
```

### 大乐透数据 (`data/dlt/`)

```
data/dlt/
├── history.json
├── statistics.json
└── predictions.json
```

**history.json 结构**:
```json
{
  "lottery_type": "dlt",
  "last_update": "2026-02-07T15:30:00Z",
  "total_records": 2500,
  "data": [
    {
      "issue": "25023",
      "draw_date": "2025-03-01",
      "front_zone": [5, 12, 23, 28, 35],
      "back_zone": [3, 9],
      "prize_info": {...}
    }
  ]
}
```

---

## 🔄 数据更新策略

### 自动更新

**触发条件**:
1. 系统启动时检查数据时效
2. 用户查询时检查最新开奖
3. 定时任务（每晚开奖后）

**更新流程**:
```
检查数据时效
    ↓
如过期，调用 WebFetch 获取最新数据
    ↓
验证数据完整性和准确性
    ↓
更新本地数据文件
    ↓
记录更新日志
```

### 手动更新

```bash
# 强制更新所有数据
python scripts/fetch_lottery_data.py --update-all

# 更新特定彩种
python scripts/fetch_lottery_data.py --lottery ssq
python scripts/fetch_lottery_data.py --lottery dlt
```

---

## ⚠️ 数据准确性声明

1. **数据时效**: 数据更新可能存在延迟，请以官方开奖结果为准
2. **数据错误**: 如发现数据错误，请联系官方渠道核实
3. **使用风险**: 因数据错误导致的任何问题，开发者不承担责任

---

## 📞 联系方式

**中国福利彩票**: http://www.cwl.gov.cn/  
**中国体育彩票**: https://www.lottery.gov.cn/

---

<div align="center">

**数据仅供参考 · 请以官方为准**

</div>
