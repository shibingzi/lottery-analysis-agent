# 彩票分析助手 - 文档中心

欢迎来到彩票分析助手文档中心！这里包含使用本系统所需的所有信息。

## 文档导航

### 📖 快速开始
- **[快速指南](../USER_GUIDE.md)** - 5 分钟快速上手
- **[项目总览](../PROJECT_PLAN.md)** - 项目规划和里程碑
- **[主 README](../README.md)** - 项目概述和基本信息

### 📚 详细文档

#### 01-ARCHITECTURE.md - 系统架构
系统整体架构、组件设计、执行流程和扩展性说明。

**包含内容：**
- 系统架构图
- 核心组件详解（Skill 系统、脚本系统）
- 数据格式规范
- 执行流程图
- 扩展性设计指南
- 安全设计
- 性能优化策略
- 错误处理机制

#### 02-DATA_SOURCES.md - 数据源说明
彩票数据来源、数据格式、更新策略。

**包含内容：**
- 数据源介绍
- API 接口说明
- 数据格式定义
- 数据验证规则
- 更新频率说明

#### 03-ANALYSIS_METHODS.md - 分析方法详解
8 种统计分析方法的技术说明和数学原理。

**包含内容：**
- 热号/冷号分析
- 遗漏值统计
- 奇偶比分析
- 大小比分析
- 连号分析
- 区间分布分析
- 和值分析
- 跨度分析
- 每种方法的计算公式和解读方式

#### 04-DISCLAIMER.md - 免责声明
法律声明、风险提示和使用条款。

**包含内容：**
- 法律免责声明
- 风险提示
- 使用条款
- 责任限制
- 理性购彩建议

#### 05-DESIGN_DECISIONS.md - 设计决策
项目重要设计决策的记录和说明。

**包含内容：**
- 技术选型决策
- 架构设计决策
- 分析方法选择依据
- 安全策略决策
- 未来优化方向

### 🗂️ 其他文件

#### FILE_MANIFEST.md
项目文件清单，列出所有文件及其用途。

#### plans/
实施计划文档，包含详细的开发计划和时间线。

## 文档阅读顺序建议

### 新用户
1. [主 README](../README.md) - 了解项目概况
2. [快速指南](../USER_GUIDE.md) - 学习基本使用
3. [04-DISCLAIMER.md](04-DISCLAIMER.md) - 了解风险和限制

### 开发者
1. [01-ARCHITECTURE.md](01-ARCHITECTURE.md) - 理解系统架构
2. [02-DATA_SOURCES.md](02-DATA_SOURCES.md) - 了解数据层
3. [03-ANALYSIS_METHODS.md](03-ANALYSIS_METHODS.md) - 掌握分析方法
4. [05-DESIGN_DECISIONS.md](05-DESIGN_DECISIONS.md) - 了解设计思路

### 贡献者
1. [01-ARCHITECTURE.md](01-ARCHITECTURE.md) - 系统架构
2. [05-DESIGN_DECISIONS.md](05-DESIGN_DECISIONS.md) - 设计决策
3. [PROJECT_PLAN.md](../PROJECT_PLAN.md) - 项目规划

## 文档规范

### 文档命名
- `01-`, `02-` 前缀表示阅读顺序
- 使用英文文件名
- 使用连字符分隔单词

### 文档格式
- 使用 Markdown 格式
- 包含清晰的标题层级
- 使用代码块展示示例
- 适当使用图表和流程图

### 更新记录
文档的更新历史记录在 [UPDATE_LOG.md](UPDATE_LOG.md) 中。

## 快速参考

### 常用命令

```bash
# 启动彩票助手
./start-lottery-agent.sh

# 获取数据
python scripts/fetch_lottery_data.py --type ssq --limit 50

# 分析历史
python scripts/analyze_history.py --type ssq --periods 100

# 固定号码分析
python scripts/generate_fixed_numbers.py --type ssq --fixed-red 07,18,25 --generate
```

### 彩种代码

| 彩种 | 代码 | 说明 |
|------|------|------|
| 双色球 | ssq | 中国福利彩票 |
| 大乐透 | dlt | 中国体育彩票 |

### 联系方式

如有问题或建议，请通过以下方式联系：
- GitHub Issues: https://github.com/shibingzi/lottery-analysis-agent/issues
- Email: [待添加]

---

**最后更新**: 2026-02-07  
**文档版本**: 1.0.0
