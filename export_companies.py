#!/usr/bin/env python3
import json
import csv
import sys

# 调用钉钉AI表格获取所有记录
import subprocess

result = subprocess.run([
    "mcporter", "call", "dingtalk-ai-table.query_records",
    f"baseId:l6Pm2Db8D4Xdo9lYUGL3lXy48xLq0Ee4",
    "tableId:d7FEhge",
    "limit:500"
], capture_output=True, text=True)

data = json.loads(result.stdout)

# 提取所有记录
records = data.get("records", [])

print(f"共读取 {len(records)} 条企业记录")

# 保存原始数据到文件（调试用）
with open("企业原始数据.json", "w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

print("原始数据已保存到 企业原始数据.json")
