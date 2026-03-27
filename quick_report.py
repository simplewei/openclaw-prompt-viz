#!/usr/bin/env python3
"""
直接处理并生成Top20分析（不保存中间文件）
"""

import subprocess, json, csv, re
from datetime import datetime

def fetch_batch(limit=200):
    cmd = ["mcporter", "call", "dingtalk-ai-table.query_records",
           "baseId:l6Pm2Db8D4Xdo9lYUGL3lXy48xLq0Ee4",
           "tableId:d7FEhge",
           f"limit:{limit}"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise Exception(result.stderr)
    return json.loads(result.stdout).get("records", [])

def parse(cell):
    if not cell: return ""
    if isinstance(cell, dict): return cell.get("text", "").strip()
    return str(cell).strip()

def analyze(cells):
    name = parse(cells.get("5b19b1v9xqysej7yjqqpy", {})).replace("(null)", "")
    if not name: return None
    
    addr = parse(cells.get("33d9l7536htt81azudzub", {}))
    phone = parse(cells.get("cq2f300ljch1eba3burtq", {}))
    tel = parse(cells.get("xm5fbhn6a2urtv4izyqaq", {}))
    industry = parse(cells.get("u4mupi8hd108oo56e9qc1", {})) or parse(cells.get("20xnob8pa05isywy6gws0", {}))
    capital = parse(cells.get("e461igbt74giugxrbhfxq", {}))
    emp_raw = parse(cells.get("o4mczvu85lh9q6e7o79d0", {}))
    status = parse(cells.get("l32mmkocgkcbqxkr8obn0", {}))
    link_obj = cells.get("5b19b1v9xqysej7yjqqpy", {})
    link = link_obj.get("link", "") if isinstance(link_obj, dict) else ""
    
    score = 50; reasons = []
    
    # 距离
    if "真陈路" in addr or "园新路" in addr:
        score += 30; reasons.append("极近")
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
    text = industry.lower()
    if any(k in text for k in ["软件", "信息技术", "互联网", "科技", "通信", "网络"]):
        ind_s, ind_c = 25, "IT/互联网"
    elif any(k in text for k in ["金融", "银行", "保险", "证券", "投资"]):
        ind_s, ind_c = 25, "金融"
    elif any(k in text for k in ["咨询", "人力", "律师", "会计", "设计", "广告"]):
        ind_s, ind_c = 20, "专业服务"
    elif any(k in text for k in ["体育", "文化", "娱乐", "传媒", "健身"]):
        ind_s, ind_c = 20, "体育/文化"
    elif any(k in text for k in ["制造", "机械", "电子", "设备"]):
        ind_s, ind_c = 15, "制造业"
    elif any(k in text for k in ["教育", "培训"]):
        ind_s, ind_c = 15, "教育"
    else:
        ind_s, ind_c = 5, "其他"
    score += ind_s
    reasons.append(f"行业:{ind_c}")
    
    # 联系方式
    if phone and phone != "-" and len(phone)>=7: score +=5; reasons.append("手机")
    if tel and tel != "-" and len(tel)>=5: score +=5; reasons.append("固话")
    
    # 状态
    if "存续" in status or "在业" in status:
        score += 10; reasons.append("正常")
    
    return {
        "企业名称": name,
        "综合得分": min(score,100),
        "企查查链接": link,
        "注册地址": addr,
        "主营业务": industry,
        "注册资本": capital,
        "参保人数": emp_raw,
        "联系方式": phone if phone not in ["-","无"] else tel,
        "评分理由": " | ".join(reasons),
        "行业分类": ind_c,
        "登记状态": status
    }

def main():
    print("正在从钉钉AI表格获取企业数据...")
    try:
        records = fetch_batch(limit=200)
    except Exception as e:
        print(f"❌ 获取失败: {e}")
        return
    
    print(f"✅ 获取到 {len(records)} 条记录")
    
    results = []
    for rec in records:
        res = analyze(rec.get("cells", {}))
        if res:
            results.append(res)
    
    results.sort(key=lambda x: x["综合得分"], reverse=True)
    for i, r in enumerate(results, 1):
        r["排名"] = i
    
    top20 = results[:20]
    
    # CSV
    if top20:
        with open("橙发i运动_长包签约Top20企业.csv", "w", newline="utf-8-sig", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=top20[0].keys())
            writer.writeheader()
            writer.writerows(top20)
        print("✅ CSV保存完成")
    
    # Report
    print("\n" + "="*80)
    print("🏆 橙发i运动周边企业长包签约潜力分析报告")
    print("="*80)
    print(f"\n📊 Top 20 企业名单（共{len(results)}家企业）\n")
    print(f"{'排名':<4} {'企业名称':<40} {'得分':<4} {'行业分类':<12} {'联系方式':<15}")
    print("-"*80)
    for r in top20:
        name_display = (r['企业名称'][:38] + '..') if len(r['企业名称']) > 38 else r['企业名称']
        print(f"{r['排名']:<4} {name_display:<40} {r['综合得分']:<4} {r['行业分类']:<12} {r['联系方式'][:15]}")
    
    print(f"\n📈 统计摘要:")
    print(f"   - 总企业数: {len(results)}")
    print(f"   - 存续企业: {sum(1 for r in results if '存续' in r['登记状态'])}")
    print(f"   - Top20平均得分: {sum(r['综合得分'] for r in top20)/len(top20):.1f}" if top20 else "N/A")
    print(f"   - 高分企业(≥80): {sum(1 for r in results if r['综合得分']>=80)}家")
    print(f"   - 中分企业(60-79): {sum(1 for r in results if 60<=r['综合得分']<80)}家")
    
    print(f"\n✅ 详细报告和CSV已保存到工作区")
    print(f"⏱️  完成时间: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()
