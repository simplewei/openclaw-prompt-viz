#!/usr/bin/env python3
"""
橙发i运动周边企业长包签约潜力分析（手动模式）
将 mcporter 查询结果保存为 JSON 后分析
"""

import json
import re
from datetime import datetime
from pathlib import Path

# 提示用户保存数据
print("请先执行以下命令保存企业数据：")
print("  mcporter call dingtalk-ai-table.query_records baseId:l6Pm2Db8D4Xdo9lYUGL3lXy48xLq0Ee4 tableId:d7FEhge limit:500 > 企业数据.json")
print("然后重新运行此脚本。")
print()

# 尝试读取现有文件
data_file = Path("企业数据.json")
if not data_file.exists():
    print("❌ 未找到企业数据.json 文件")
    exit(1)

try:
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
except Exception as e:
    print(f"❌ 读取JSON失败: {e}")
    exit(1)

records = data.get("records", [])
print(f"✅ 读取到 {len(records)} 条企业记录")

# 分析逻辑（同上）
def parse_value(cell):
    if not cell: return ""
    if isinstance(cell, dict): return cell.get("text", "").strip()
    return str(cell).strip()

def calculate_score(record):
    cells = record.get("cells", {})
    name = parse_value(cells.get("5b19b1v9xqysej7yjqqpy", {})).replace("(null)", "")
    status = parse_value(cells.get("l32mmkocgkcbqxkr8obn0", {}))
    capital = parse_value(cells.get("e461igbt74giugxrbhfxq", {}))
    emp_count_str = parse_value(cells.get("o4mczvu85lh9q6e7o79d0", {}))
    industry_main = parse_value(cells.get("20xnob8pa05isywy6gws0", {}))
    industry_mid = parse_value(cells.get("a4zw60h64e8nk6an2dqcb", {}))
    address = parse_value(cells.get("33d9l7536htt81azudzub", {}))
    phone = parse_value(cells.get("cq2f300ljch1eba3burtq", {}))
    tel = parse_value(cells.get("xm5fbhn6a2urtv4izyqaq", {}))
    
    score = 50; reasons = []
    
    # 距离
    if "真陈路" in address or "园新路" in address:
        score += 30; reasons.append("距离很近")
    elif "宝山区" in address:
        score += 20; reasons.append("宝山区")
    elif "普陀区" in address:
        score += 10; reasons.append("普陀区")
    else: score += 5; reasons.append("距离远")
    
    # 规模
    emp_count = int(emp_count_str) if emp_count_str and emp_count_str != "-" else 0
    cap_match = re.search(r'(\d+(?:\.\d+)?)', capital.replace(',', '')) if capital else None
    cap_num = float(cap_match.group(1)) if cap_match else 0
    
    if emp_count >= 50 or cap_num >= 500:
        score += 25; reasons.append(f"大型({emp_count}人/{cap_num:.0f}万)")
    elif emp_count >= 20 or cap_num >= 200:
        score += 20; reasons.append("中型")
    elif emp_count >= 5 or cap_num >= 50:
        score += 15; reasons.append("小型")
    else: score += 5; reasons.append("微型")
    
    # 行业
    industry_text = f"{industry_main} {industry_mid}".lower()
    if any(kw in industry_text for kw in ["软件", "信息技术", "互联网", "科技"]):
        industry_score = 25; industry_cat = "IT/互联网"
    elif any(kw in industry_text for kw in ["金融", "银行", "证券"]):
        industry_score = 25; industry_cat = "金融"
    elif any(kw in industry_text for kw in ["咨询", "人力资源", "设计"]):
        industry_score = 20; industry_cat = "专业服务"
    elif any(kw in industry_text for kw in ["体育", "文化", "传媒"]):
        industry_score = 20; industry_cat = "体育/文化"
    else:
        industry_score = 5; industry_cat = "其他"
    score += industry_score; reasons.append(f"行业:{industry_cat}")
    
    # 联系方式
    if phone and phone != "-" and len(phone)>=7: score += 5; reasons.append("有手机")
    if tel and tel != "-" and len(tel)>=5: score += 5; reasons.append("有固话")
    
    # 状态
    if "存续" in status or "在业" in status:
        score += 10; reasons.append("存续")
    else: reasons.append(f"状态:{status}")
    
    return {
        "score": min(score,100),
        "reasons": " | ".join(reasons),
        "industry_category": industry_cat,
        "status": status,
        "raw_emp": emp_count,
        "raw_cap": cap_num
    }

# 处理所有记录
results = []
for rec in records:
    cells = rec.get("cells", {})
    name = parse_value(cells.get("5b19b1v9xqysej7yjqqpy", {})).replace("(null)", "")
    if not name: continue
    
    score_info = calculate_score(rec)
    
    address = parse_value(cells.get("33d9l7536htt81azudzub", {}))
    phone = parse_value(cells.get("cq2f300ljch1eba3burtq", {}))
    tel = parse_value(cells.get("xm5fbhn6a2urtv4izyqaq", {}))
    industry = parse_value(cells.get("u4mupi8hd108oo56e9qc1", {})) or parse_value(cells.get("20xnob8pa05isywy6gws0", {}))
    capital = parse_value(cells.get("e461igbt74giugxrbhfxq", {}))
    emp = parse_value(cells.get("o4mczvu85lh9q6e7o79d0", {}))
    qcc_link = cells.get("5b19b1v9xqysej7yjqqpy", {}).get("link", "") if isinstance(cells.get("5b19b1v9xqysej7yjqqpy", {}), dict) else ""
    
    results.append({
        "排名": 0,
        "企业名称": name,
        "综合得分": score_info["score"],
        "企查查链接": qcc_link,
        "注册地址": address,
        "主营业务": industry,
        "注册资本": capital,
        "参保人数": emp,
        "联系方式": phone if phone != "-" and phone != "无" else tel,
        "评分理由": score_info["reasons"],
        "行业分类": score_info["industry_category"],
        "登记状态": score_info["status"]
    })

# 排序
results.sort(key=lambda x: x["综合得分"], reverse=True)
for i, r in enumerate(results, 1):
    r["排名"] = i

top20 = results[:20]

# 输出统计
print(f"\n📈 统计摘要:")
print(f"   - 总企业数: {len(records)}")
print(f"   - 存续企业: {sum(1 for r in results if '存续' in r['登记状态'])}")
print(f"   - Top 20最低分: {top20[-1]['综合得分'] if top20 else 0}")

# 保存CSV (if any)
if top20:
    import csv
    csv_path = Path("橙发i运动_长包签约Top20企业.csv")
    with open(csv_path, "w", newline="utf-8-sig", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=top20[0].keys())
        writer.writeheader()
        writer.writerows(top20)
    print(f"✅ Top 20 已保存: {csv_path}")

print("\n✅ 分析完成！")
