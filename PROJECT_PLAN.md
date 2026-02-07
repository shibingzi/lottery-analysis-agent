# 🎱 彩票分析 Agent - 项目规划文档

**项目名称**: Lottery Analysis Agent  
**版本**: v1.0.0  
**创建日期**: 2026-02-07  
**状态**: 规划中

---

## 📋 项目概述

基于 Claude Code 架构的专业彩票数据分析系统，支持双色球、大乐透等多彩种分析，提供统计分析、固定号码预测等娱乐功能。

### 核心特性
- ✅ **多彩种支持**: 双色球、大乐透（可扩展）
- ✅ **实时数据获取**: 自动获取最新开奖结果
- ✅ **统计分析**: 热号/冷号、遗漏值、奇偶比、大小比等
- ✅ **固定号码分析**: 用户指定号码的专项分析
- ✅ **号码生成器**: 机选号码（娱乐性质）
- ✅ **专业报告**: HTML 可视化报告（shadcn/ui 设计风格）
- ✅ **⚠️ 免责声明**: 明确标注随机性和娱乐性质

---

## 🏗️ 文件结构

```
lottery-analysis-agent/
│
├── .claude/                          # Claude Code 配置核心
│   ├── settings.json                 # 主配置文件
│   ├── prompts/
│   │   ├── system_prompt_cn.md       # 中文系统提示词
│   │   └── system_prompt_en.md       # 英文系统提示词
│   ├── skills/
│   │   ├── skill_lottery_data_fetcher.md    # 数据获取专家
│   │   ├── skill_lottery_analyzer.md        # 统计分析专家
│   │   └── skill_lottery_predictor.md       # 号码预测专家（娱乐性质）
│   ├── agents/
│   │   ├── subagent_ssq_analyst.md          # 双色球专项分析代理
│   │   └── subagent_dlt_analyst.md          # 大乐透专项分析代理
│   ├── mcp.json                      # MCP 服务器配置
│   └── config/
│       └── lottery_config.json       # 彩票类型配置
│
├── scripts/                          # 工具脚本
│   ├── fetch_lottery_data.py         # 主数据获取脚本
│   ├── analyze_history.py            # 历史数据分析脚本
│   ├── generate_fixed_numbers.py     # 固定号码生成器
│   └── setup.sh                      # 环境初始化脚本
│
├── data/                             # 数据存储
│   ├── ssq/                          # 双色球数据
│   │   ├── history.json              # 历史开奖记录
│   │   ├── statistics.json           # 统计分析结果
│   │   └── predictions.json          # 预测记录
│   ├── dlt/                          # 大乐透数据
│   │   ├── history.json
│   │   ├── statistics.json
│   │   └── predictions.json
│   └── cache/                        # 缓存数据
│
├── templates/                        # 报告模板
│   ├── report_template.html          # HTML报告模板
│   └── styles.css                    # 样式文件
│
├── docs/                             # 文档
│   ├── README.md                     # 文档索引
│   ├── 01-ARCHITECTURE.md            # 架构设计
│   ├── 02-DATA_SOURCES.md            # 数据源说明
│   ├── 03-ANALYSIS_METHODS.md        # 分析方法说明
│   ├── 04-DISCLAIMER.md              # ⚠️ 免责声明
│   └── UPDATE_LOG.md                 # 更新日志
│
├── logs/                             # 运行日志
│   └── data_fetch.log
│
├── README.md                         # 项目说明
├── USER_GUIDE.md                     # 用户使用指南
├── start-lottery-agent.sh            # 启动脚本（Bash）
├── start-lottery-agent.bat           # Windows启动脚本
└── .env.example                      # 环境变量示例
```

---

## 🎯 功能模块设计

### 1️⃣ 数据获取模块

**技能文件**: `skill_lottery_data_fetcher.md`

**功能:**
- 自动获取最新开奖结果
- 支持多个数据源（官方API、第三方网站）
- 数据验证与去重
- 增量更新历史数据

**数据源:**
- 中国体彩官网: https://www.lottery.gov.cn/
- 中国福彩官网: http://www.cwl.gov.cn/
- 第三方数据平台（如聚合数据 API）

**数据字段（双色球）:**
```json
{
  "lottery_type": "ssq",
  "issue": "2025023",
  "draw_date": "2025-03-02",
  "red_balls": [3, 7, 12, 18, 25, 30],
  "blue_ball": 14,
  "prize_info": {
    "jackpot": "5注",
    "jackpot_amount": "1000万元/注"
  }
}
```

**数据字段（大乐透）:**
```json
{
  "lottery_type": "dlt",
  "issue": "25023",
  "draw_date": "2025-03-01",
  "front_zone": [5, 12, 23, 28, 35],
  "back_zone": [3, 9],
  "prize_info": {...}
}
```

---

### 2️⃣ 统计分析模块

**技能文件**: `skill_lottery_analyzer.md`

**核心指标:**

| 分析类型 | 说明 | 计算方式 |
|---------|------|---------|
| **热号/冷号分析** | 统计号码出现频率 | 近N期（如50期、100期）出现次数 |
| **遗漏值分析** | 号码未出现的期数 | 自上次出现以来的期数 |
| **奇偶比分析** | 奇偶号码分布 | 红球/前区奇偶比例 |
| **大小比分析** | 大小号码分布 | 双色球16为界，大乐透18为界 |
| **连号分析** | 连续号码出现情况 | 如 12,13 或 28,29,30 |
| **区间分布** | 号码在各区间的分布 | 双色球分3区，大乐透分5区 |
| **和值分析** | 红球/前区号码总和 | 所有号码相加 |
| **跨度分析** | 最大号与最小号之差 | max - min |

**统计输出示例:**
```json
{
  "red_ball_stats": {
    "hot_numbers": [12, 23, 7, 18, 30],
    "cold_numbers": [1, 33, 11, 28, 4],
    "max_missing": {"number": 1, "missing": 45},
    "odd_even_ratio": {"3:3": 35, "4:2": 28, "2:4": 22},
    "big_small_ratio": {"3:3": 38, "4:2": 25, "2:4": 20}
  },
  "blue_ball_stats": {
    "hot_numbers": [9, 14, 6],
    "cold_numbers": [1, 16, 2]
  }
}
```

---

### 3️⃣ 固定号码分析模块

**技能文件**: `skill_lottery_predictor.md`

**⚠️ 重要: 明确标注"娱乐性质"、"不构成投注建议"**

**功能:**
- 用户指定"固定号码"（如守号、生日号）
- 分析该号码的历史表现
- 生成包含固定号码的组合
- 娱乐性质的"预测分析"

**分析维度:**
1. **历史中奖情况** - 该号码是否中过奖
2. **组合合理性** - 奇偶比、大小比、区间分布是否合理
3. **遗漏分析** - 各号码的当前遗漏值
4. **生成推荐组合** - 基于固定号码生成完整组合

**输入示例:**
```
固定红球: 07, 18, 25
固定蓝球: 14
```

**输出示例:**
```json
{
  "fixed_red": [7, 18, 25],
  "fixed_blue": 14,
  "analysis": {
    "current_missing": {"7": 3, "18": 0, "25": 5, "14": 2},
    "odd_even_ratio": "2:1（需补充1奇2偶）",
    "suggested_combinations": [
      {"red": [7, 18, 25, 12, 30, 33], "blue": 14, "reason": "补充热号+均衡分布"}
    ]
  }
}
```

---

### 4️⃣ 号码生成器（娱乐性质）

**随机生成:**
- 纯随机生成
- 基于权重（热号权重高，但仍是随机）
- 机选号码

**智能生成（娱乐）:**
- 基于历史规律的"伪智能"生成
- 平衡奇偶比、大小比
- 避免全热号或全冷号

---

## 📊 报告设计

### HTML 报告结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <!-- shadcn/ui Zinc 深色主题 -->
    <style>
        :root {
            --background: #09090B;
            --card: #18181B;
            --border: #27272A;
            --chart-red: #EF4444;    /* 红球/热号 */
            --chart-blue: #3B82F6;   /* 蓝球 */
            --chart-green: #10B981;  /* 中奖/推荐 */
            --chart-orange: #F97316; /* 冷号/警示 */
        }
    </style>
</head>
<body>
    <!-- 1. ⚠️ 免责声明（醒目位置） -->
    <div class="disclaimer-banner">
        <h2>⚠️ 重要声明</h2>
        <p>彩票开奖是完全随机的独立事件...</p>
    </div>
    
    <!-- 2. 最新开奖结果 -->
    <section class="latest-draw">
        <h2>最新开奖结果</h2>
        <div class="balls-display">
            <!-- 红球/前区 -->
            <!-- 蓝球/后区 -->
        </div>
    </section>
    
    <!-- 3. 统计分析 -->
    <section class="statistics">
        <h2>数据统计分析（最近100期）</h2>
        <div class="charts">
            <!-- Chart.js 热号冷号图 -->
            <!-- 遗漏值柱状图 -->
            <!-- 奇偶比饼图 -->
        </div>
    </section>
    
    <!-- 4. 固定号码分析 -->
    <section class="fixed-numbers">
        <h2>固定号码分析</h2>
        <!-- 用户输入的固定号码 -->
        <!-- 历史表现 -->
        <!-- 建议组合 -->
    </section>
    
    <!-- 5. 号码生成器 -->
    <section class="generator">
        <h2>号码生成器（娱乐）</h2>
        <!-- 机选按钮 -->
        <!-- 生成结果 -->
    </section>
    
    <!-- 6. 数据来源 -->
    <footer>
        <h3>数据来源</h3>
        <p>中国体彩/福彩官网 | 查询时间: 2026-02-07</p>
    </footer>
</body>
</html>
```

---

## 🚀 使用流程

### 用户输入示例

**场景1: 查看最新开奖**
```
查看双色球最新开奖结果
```

**场景2: 统计分析**
```
分析双色球最近100期的热号冷号
```

**场景3: 固定号码分析**
```
我的固定号码是红球: 07 18 25，蓝球: 14，分析一下
```

**场景4: 生成号码**
```
帮我机选5注双色球号码
```

### Agent 执行流程

```
用户请求 → 识别彩种和意图
    ↓
1. 检查本地数据是否最新
    ↓
2. 如需要，调用 WebSearch/WebFetch 获取最新数据
    ↓
3. 调用 skill_lottery_analyzer 进行统计分析
    ↓
4. 如需要，调用 skill_lottery_predictor 进行固定号码分析
    ↓
5. 生成 HTML 报告
    ↓
6. 输出结果（含⚠️免责声明）
```

---

## ⚠️ 免责声明（必须包含）

### 随机性声明
- 彩票开奖是完全随机的独立事件
- 历史数据对未来开奖没有任何预测价值
- 每个号码在每期中奖概率相等

### 娱乐性质声明
- 本系统所有分析仅供娱乐参考
- 不构成任何形式的投注建议
- 不保证任何中奖承诺

### 理性购彩提醒
- 彩票是概率游戏，中奖率极低
- 请量力而行，理性购彩
- 未成年人不得购买彩票

### 法律责任声明
- 用户因使用本系统产生的任何损失，开发者不承担责任
- 请遵守当地彩票管理法规

---

## 📅 开发计划

### 第一阶段: 基础架构 (Week 1)
- [ ] 创建项目结构和配置文件
- [ ] 开发数据获取脚本
- [ ] 实现基础数据模型

### 第二阶段: 核心功能 (Week 2)
- [ ] 开发统计分析模块
- [ ] 实现固定号码分析
- [ ] 开发号码生成器

### 第三阶段: 报告系统 (Week 3)
- [ ] 设计 HTML 报告模板
- [ ] 实现数据可视化
- [ ] 集成 Chart.js 图表

### 第四阶段: 测试优化 (Week 4)
- [ ] 功能测试
- [ ] 性能优化
- [ ] 文档完善

---

## 📞 联系方式

如有问题或建议，请提交 Issue。

---

**最后更新**: 2026-02-07  
**文档版本**: v1.0.0
