# 彩票数据获取工具使用指南

## 📋 功能概述

本工具将**历史数据获取**和**新数据获取**分离，支持：
- 批量获取历史数据（首次填充）
- 增量更新最新数据（日常使用）
- CSV格式导入/导出
- 数据统计查询

## 🚀 快速开始

### 1️⃣ 首次使用 - 获取历史数据

```bash
# 获取双色球历史数据（1000期）
python scripts/fetch_lottery_data.py --type ssq --history --limit 1000

# 获取大乐透历史数据（500期）
python scripts/fetch_lottery_data.py --type dlt --history --limit 500

# 获取所有彩种历史数据
python scripts/fetch_lottery_data.py --all --history --limit 1000
```

### 2️⃣ 日常使用 - 增量更新

```bash
# 更新双色球（最近7天）
python scripts/fetch_lottery_data.py --type ssq --update

# 更新双色球（最近14天）
python scripts/fetch_lottery_data.py --type ssq --update --days 14

# 更新所有彩种
python scripts/fetch_lottery_data.py --all --update
```

### 3️⃣ 查看数据状态

```bash
# 查看双色球数据统计
python scripts/fetch_lottery_data.py --type ssq --stats

# 查看最新开奖
python scripts/fetch_lottery_data.py --type ssq --latest
```

## 📊 数据导入/导出

### 从CSV导入历史数据

CSV格式要求（双色球）：
```csv
issue,draw_date,red_balls,blue_ball
2026161,2026-02-09,05 12 18 24 29 33,09
2026162,2026-02-11,03 08 15 22 28 31,07
```

导入命令：
```bash
python scripts/fetch_lottery_data.py --type ssq --import-file history.csv
```

CSV格式要求（大乐透）：
```csv
issue,draw_date,front_zone,back_zone
25061,2026-02-09,05 12 18 24 29,03 09
25062,2026-02-11,03 08 15 22 28,02 07
```

### 导出数据到CSV

```bash
# 导出全部数据
python scripts/fetch_lottery_data.py --type ssq --export-file backup.csv

# 导出最近100期
python scripts/fetch_lottery_data.py --type ssq --export-file recent.csv --export-limit 100
```

## 🔧 获取真实数据

### 方案1: 使用RollToolsApi (推荐)

修改脚本中的 `_generate_mock_history_data` 和 `_generate_mock_latest_data` 方法，替换为真实API调用：

```python
def fetch_history_from_api(self, limit: int) -> List[Dict]:
    """从RollToolsApi获取历史数据"""
    import requests
    
    url = "https://www.mxnzp.com/api/lottery/common/history"
    params = {
        "code": self.lottery_type,
        "app_id": "YOUR_APP_ID",
        "app_secret": "YOUR_APP_SECRET",
        "page": 1,
        "size": limit
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    # 转换为统一格式
    records = []
    for item in data["data"]["list"]:
        if self.lottery_type == "ssq":
            balls = item["openCode"].split("+")
            red_balls = [int(x) for x in balls[0].split(",")]
            blue_ball = int(balls[1])
            records.append({
                "lottery_type": "ssq",
                "issue": item["expect"],
                "draw_date": item["time"][:10],
                "red_balls": red_balls,
                "blue_ball": blue_ball,
                "prize_info": {}
            })
    
    return records
```

申请地址：https://www.mxnzp.com

### 方案2: 从GitHub下载

```bash
# 下载lottery_history项目的数据
git clone https://github.com/gudaoxuri/lottery_history.git
cd lottery_history

# 转换并导入
cp data/ssq.json /path/to/lottery-analysis-agent/data/ssq/
```

### 方案3: 从CSDN下载Excel

1. 访问 https://blog.csdn.net/tianchounh/article/details/136435112
2. 下载Excel格式的历史数据
3. 另存为CSV格式
4. 使用本工具导入：
   ```bash
   python scripts/fetch_lottery_data.py --type ssq --import-file history.csv
   ```

## 📅 推荐工作流

### 首次部署

```bash
# 1. 获取历史数据（只需执行一次）
python scripts/fetch_lottery_data.py --type ssq --history --limit 2000

# 2. 验证数据
python scripts/fetch_lottery_data.py --type ssq --stats
```

### 每日更新（可设置定时任务）

```bash
#!/bin/bash
# update_lottery_data.sh

cd /path/to/lottery-analysis-agent

# 更新所有彩种
python scripts/fetch_lottery_data.py --all --update

# 生成最新报告
python scripts/generate_report.py --type ssq --periods 100 --output reports/latest_ssq.html
python scripts/generate_report.py --type dlt --periods 100 --output reports/latest_dlt.html
```

添加到crontab（每天22:30执行）：
```bash
30 22 * * * /path/to/update_lottery_data.sh >> /var/log/lottery_update.log 2>&1
```

### 定期备份

```bash
# 每周备份一次
python scripts/fetch_lottery_data.py --type ssq --export-file backups/ssq_$(date +%Y%m%d).csv
python scripts/fetch_lottery_data.py --type dlt --export-file backups/dlt_$(date +%Y%m%d).csv
```

## 📊 数据格式

### JSON格式

```json
{
  "lottery_type": "ssq",
  "issue": "2026165",
  "draw_date": "2026-02-18",
  "red_balls": [2, 11, 20, 24, 28, 33],
  "blue_ball": 15,
  "prize_info": {}
}
```

### CSV格式

```csv
issue,draw_date,red_balls,blue_ball
2026165,2026-02-18,02 11 20 24 28 33,15
```

## ⚠️ 注意事项

1. **当前版本**使用的是模拟数据，仅供演示
2. **生产环境**需要接入真实API或手动导入官方数据
3. **数据去重**：导入时会自动跳过已存在的期号
4. **备份建议**：定期导出CSV备份数据

## 🆘 故障排查

### 问题1: 导入CSV时编码错误

**解决**: 确保CSV文件使用UTF-8编码
```bash
# Linux/Mac转换编码
iconv -f GBK -t UTF-8 input.csv > output.csv
```

### 问题2: 数据格式不匹配

**解决**: 检查CSV列名是否正确
- 双色球: `issue`, `draw_date`, `red_balls`, `blue_ball`
- 大乐透: `issue`, `draw_date`, `front_zone`, `back_zone`

### 问题3: 增量更新没有新数据

**可能原因**:
1. 数据源暂时没有更新
2. API调用频率限制
3. 日期范围设置太小

**解决**: 增大 `--days` 参数值

## 📞 相关资源

- **API申请**: https://www.mxnzp.com
- **历史数据**: https://github.com/gudaoxuri/lottery_history
- **Excel数据**: https://blog.csdn.net/tianchounh
- **官方数据源**: 
  - 福彩: http://www.cwl.gov.cn/
  - 体彩: https://www.lottery.gov.cn/

---

**最后更新**: 2026-02-07
