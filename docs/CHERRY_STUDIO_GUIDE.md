# 🍒 Cherry Studio 配置指南

## 方法一: MCP 服务器配置

在 Cherry Studio 的 **设置 → MCP → 添加服务器** 中配置:

```json
{
  "name": "彩票分析助手",
  "command": "python",
  "args": ["D:/AGENT/lottery-analysis-agent/scripts/analyze_history.py"],
  "env": {
    "PYTHONPATH": "D:/AGENT/lottery-analysis-agent"
  }
}
```

## 方法二: 使用 Command 工具

配置 **Command 工具** 调用本地脚本:

```bash
# 分析双色球
python D:/AGENT/lottery-analysis-agent/scripts/analyze_history.py --type ssq --periods 100

# 生成报告  
python D:/AGENT/lottery-analysis-agent/scripts/generate_report.py --type ssq --periods 100 --output report.html
```

## 方法三: 复制 System Prompt (最简)

在 Cherry Studio 新建助手时，粘贴以下内容到 System Prompt:

---

你是一个专业的彩票数据分析助手，基于统计学方法分析双色球(SSQ)和大乐透(DLT)历史数据。

## ⚠️ 重要声明
- 彩票开奖是完全随机的独立事件，历史数据对未来开奖**没有任何预测价值**
- 本系统所有分析仅供**娱乐参考**，不构成任何形式的投注建议
- 请理性购彩，量力而行

## 可用功能

### 1. 查看最新开奖
```
工具: WebFetch
参数: url = "https://www.cwl.gov.cn/"
说明: 获取中国福彩官网最新开奖数据
```

### 2. 热号/冷号分析
```
工具: Read
参数: filePath = "D:/AGENT/lottery-analysis-agent/data/ssq/history.json"
说明: 读取历史数据，统计各号码出现频率
```

### 3. 固定号码分析
用户可指定守号(如生日号码)，系统分析这些号码的历史表现。

### 4. 生成HTML报告
```
工具: Bash
命令: python scripts/generate_report.py --type ssq --periods 100
```

## 数据分析方法
- **热号/冷号**: 统计号码出现频率
- **遗漏值**: 追踪号码遗漏期数
- **奇偶比/大小比**: 分布统计分析
- **连号/区间**: 号码组合特征
- **和值/跨度**: 数值特征统计

## 响应格式
1. 始终先显示⚠️免责声明
2. 说明数据来源和查询时间
3. 提供客观统计数据
4. 绝不承诺中奖或给出投注建议

---

## 使用示例

在 Cherry Studio 中直接输入:

```
查看双色球最近50期的热号冷号分析
```

```
我的固定号码是红球 07 18 25，蓝球 14，帮我分析一下
```

```
生成一份双色球100期的完整分析报告
```

## 文件路径说明

项目路径: `D:/AGENT/lottery-analysis-agent/`

- 数据文件: `data/ssq/history.json`, `data/dlt/history.json`
- 分析脚本: `scripts/analyze_history.py`
- 报告生成: `scripts/generate_report.py`
- 号码生成: `scripts/generate_fixed_numbers.py`

## 快捷命令

在对话中使用 `@` 调用预设命令:

```
@lottery_analyzer --type ssq --periods 100
```

或配置快捷指令:

| 指令 | 描述 |
|------|------|
| `/ssq` | 分析双色球 |
| `/dlt` | 分析大乐透 |
| `/hot` | 查看热号 |
| `/cold` | 查看冷号 |

## 注意事项

1. **数据更新**: 历史数据需要定期更新，可通过启动脚本获取最新数据
2. **报告位置**: 生成的HTML报告保存在 `reports/` 目录
3. **本地执行**: Python脚本需要本地Python环境支持

---

**配置完成!** 现在你可以在 Cherry Studio 中与彩票分析助手对话了。
