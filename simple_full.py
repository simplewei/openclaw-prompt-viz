#!/usr/bin/env python3
import subprocess, json, re, csv
from datetime import datetime
from pathlib import Path

def get_all_records():
    """分页获取所有企业记录"""
    all_records = []
    cursor = None
    page = 1
    
    while True:
        cmd = ["mcporter", "call", "dingtalk-ai-table.query_records",
               f"baseId:{BASE_ID}", f"tableId:{TABLE_ID}", f"limit:{MAX_LIMIT}"]
        if cursor:
            cmd.append(f"cursor:{cursor}")
        
        print(f"获取第 {page} 页...", end=" ")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            print(f"失败: {result.stderr}")
            break
        
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            print(f"原始输出: {result.stdout[:200]}")
            break
        
        records = data.get("records", [])
        all_records.extend(records)
        print(f"获取 {len(records)} 条，累计 {len(all_records)} 条")
        
        cursor = data.get("nextCursor")
        if not cursor:
            break
        
        page += 1
        time.sleep(0.5)
    
    return all_records

BASE_ID = "l6Pm2Db8D4Xdo9lYUGL3lXy48xLq0Ee4"
TABLE_ID = "d7FEhge"
MAX_LIMIT = 500

import time

records = get_all_records()
print(f"\n总计获取 {len(records)} 条记录")

if not records:
    print("无数据，退出")
    exit(0)

# 解析和分析
def parse(cell):
    if not cell: return ""
    if isinstance(cell, dict): return cell.get("text", "").strip()
    return str(cell).strip()

def analyze(rec):
    c = rec.get("cells", {})
    name = parse(c.get("5b19b1v9xqysej7yjqqpy", {})).replace("(null)", "")
    if not name: return None
    
    addr = parse(c.get("33d9l7536htt81azudzub", {}))
    phone = parse(c.get("cq2f300ljch1eba3burtq", {}))
    tel = parse(c.get("xm5fbhn6a2urtv4izyqaq", {}))
    industry = parse(c.get("u4mupi8hd108oo56e9qc1", {})) or parse(c.get("20xnob8pa05isywy6gws0", {}))
    capital = parse(c.get("e461igbt74giugxrbhfxq", {}))
    emp_raw = parse(c.get("o4mczvu85lh9q6e7o79d0", {}))
    status = parse(c.get("l32mmkocgkcbqxkr8obn0", {}))
    link_obj = c.get("5b19b1v9xqysej7yjqqpy", {})
    link = link_obj.get("link", "") if isinstance(link_obj, dict) else ""
    
    # 计算得分
    score = 50
    reasons = []
    
    # 距离
    if "真陈路" in addr or "园新路" in addr:
        score += 30; reasons.append("很近")
    elif "宝山区" in addr:
        score += 20; reasons.append("宝山区")
    elif "普陀区" in addr:
        score += 10; reasons.append("普陀区")
    else: score += 5; reasons.append("远")
    
    # 规模
    emp = int(emp_raw) if emp_raw and emp_raw != "-" else 0
    cap_match = re.search(r'(\d+(?:\.\d+)?)', capital.replace(',', '')) if capital else None
    cap = float(cap_match.group(1)) if cap_match else 0
    
    if emp >= 50 or cap >= 500:
        score += 25; reasons.append(f"大({emp}人/{cap:.0f}万)")
    elif emp >= 20 or cap >= 200:
        score += 20; reasons.append("中")
    elif emp >= 5 or cap >= 50:
        score += 15; reasons.append("小")
    else:
        score += 5; reasons.append("微")
    
    # 行业
    text = f"{industry}".lower()
    if any(k in text for k in ["软件", "信息技术", "互联网", "科技", "通信", "网络"]):
        ind_score = 25; ind_cat = "IT/互联网"
    elif any(k in text for k in ["金融", "银行", "保险", "证券", "投资"]):
        ind_score = 25; ind_cat = "金融"
    elif any(k in text for k in ["咨询", "人力", "律师", "会计", "设计", "广告"]):
        ind_score = 20; ind_cat = "专业服务"
    elif any(k in text for k in ["体育", "文化", "娱乐", "传媒", "健身"]):
        ind_score = 20; ind_cat = "体育/文化"
    elif any(k in text for k in ["制造", "机械", "电子", "设备"]):
        ind_score = 15; ind_cat = "制造业"
    elif any(k in text for k in ["教育", "培训"]):
        ind_score = 15; ind_cat = "教育"
    else:
        ind_score = 5; ind_cat = "其他"
    score += ind_score
    reasons.append(f"行业:{ind_cat}")
    
    # 联系方式
    if phone and phone != "-" and len(phone)>=7: score += 5; reasons.append("手机")
    if tel and tel != "-" and len(tel)>=5: score += 5; reasons.append("固话")
    
    # 状态
    if "存续" in status or "在业" in status:
        score += 10; reasons.append("正常")
    
    return {
        "企业名称": name,
        "综合得分": score,
        "企查查链接": link,
        "注册地址": addr,
        "主营业务": industry,
        "注册资本": capital,
        "参保人数": emp_raw,
        "联系方式": phone if phone not in ["-", "无"] else tel,
        "评分理由": " | ".join(reasons),
        "行业分类": ind_cat,
        "登记状态": status
    }

results = []
for rec in records:
    res = analyze(rec)
    if res:
        results.append(res)

results.sort(key=lambda x: x["综合得分"], reverse=True)
for i, r in enumerate(results, 1):
    r["排名"] = i

top20 = results[:20]

# 保存CSV
if top20:
    with open("橙发i运动_长包签约Top20企业.csv", "w", newline="utf-8-sig", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=top20[0].keys())
        writer.writeheader()
        writer.writerows(top20)
    print("\n✅ Top 20 CSV已生成")

# 生成报告
print("\n🏆 Top 5 企业:")
for i, r in enumerate(top20[:5], 1):
    print(f"{i}. {r['企业名称']} (得分:{r['综合得分']}) - {r['行业分类']} - {r['联系方式']}")

print(f"\n总处理企业: {len(results)}")
print(f"存续企业: {sum(1 for r in results if '存续' in r['登记状态'])}")
print(f"Top20平均得分: {sum(r['综合得分'] for r in top20)/len(top20):.1f}" if top20 else "N/A")
