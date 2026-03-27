#!/usr/bin/env python3
"""
橙发i运动周边企业长包签约潜力分析 - 完整可运行版
"""

import subprocess, json, time, csv, re
from datetime import datetime
from pathlib import Path

BASE_ID = "l6Pm2Db8D4Xdo9lYUGL3lXy48xLq0Ee4"
TABLE_ID = "d7FEhge"
LIMIT = 200  # 每页条数

def fetch_all():
    all_records = []
    cursor = None
    page = 1
    
    print("="*60)
    print("开始获取企业数据（钉钉AI表格）")
    print("="*60)
    
    while True:
        cmd = ["mcporter", "call", "dingtalk-ai-table.query_records",
               f"baseId:{BASE_ID}", f"tableId:{TABLE_ID}", f"limit:{LIMIT}"]
        if cursor:
            cmd.append(f"cursor:{cursor}")
        
        print(f"\n📄 第 {page} 页...", end=" ")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            print(f"❌ 失败: {result.stderr}")
            break
        
        try:
            data = json.loads(result.stdout)
        except Exception as e:
            print(f"❌ JSON解析失败: {e}")
            print(f"输出前200字符: {result.stdout[:200]}")
            break
        
        records = data.get("records", [])
        all_records.extend(records)
        print(f"✅ 获取 {len(records)} 条，累计 {len(all_records)} 条")
        
        cursor = data.get("nextCursor")
        if not cursor:
            break
        
        page += 1
        time.sleep(0.5)
    
    return all_records

def parse(cell):
    if not cell: return ""
    if isinstance(cell, dict): return cell.get("text", "").strip()
    return str(cell).strip()

def analyze_record(cells):
    name = parse(cells.get("5b19b1v9xqysej7yjqqpy", {})).replace("(null)", "")
    if not name:
        return None
    
    addr = parse(cells.get("33d9l7536htt81azudzub", {}))
    phone = parse(cells.get("cq2f300ljch1eba3burtq", {}))
    tel = parse(cells.get("xm5fbhn6a2urtv4izyqaq", {}))
    industry = parse(cells.get("u4mupi8hd108oo56e9qc1", {})) or parse(cells.get("20xnob8pa05isywy6gws0", {}))
    capital = parse(cells.get("e461igbt74giugxrbhfxq", {}))
    emp_raw = parse(cells.get("o4mczvu85lh9q6e7o79d0", {}))
    status = parse(cells.get("l32mmkocgkcbqxkr8obn0", {}))
    qcc_link = cells.get("5b19b1v9xqysej7yjqqpy", {}).get("link", "") if isinstance(cells.get("5b19b1v9xqysej7yjqqpy", {}), dict) else ""
    
    # 计算得分
    score = 50
    reasons = []
    
    # 1. 距离 (30分)
    if "真陈路" in addr or "园新路" in addr:
        score += 30; reasons.append("极近（真陈路/园新路）")
    elif "宝山区" in addr:
        score += 20; reasons.append("宝山区")
    elif "普陀区" in addr:
        score += 10; reasons.append("普陀区")
    else: score += 5; reasons.append("距离较远")
    
    # 2. 规模 (25分)
    emp = int(emp_raw) if emp_raw and emp_raw != "-" else 0
    cap_match = re.search(r'(\d+(?:\.\d+)?)', capital.replace(',', '')) if capital else None
    cap = float(cap_match.group(1)) if cap_match else 0
    
    if emp >= 50 or cap >= 500:
        score += 25; reasons.append(f"规模大（{emp}人/{cap:.0f}万）")
    elif emp >= 20 or cap >= 200:
        score += 20; reasons.append("规模中等")
    elif emp >= 5 or cap >= 50:
        score += 15; reasons.append("规模小型")
    else:
        score += 5; reasons.append("规模微型")
    
    # 3. 行业 (25分)
    industry_text = f"{industry}".lower()
    if any(k in industry_text for k in ["软件", "信息技术", "互联网", "科技", "通信", "网络"]):
        ind_score, ind_cat = 25, "IT/互联网"
    elif any(k in industry_text for k in ["金融", "银行", "保险", "证券", "投资"]):
        ind_score, ind_cat = 25, "金融"
    elif any(k in industry_text for k in ["咨询", "人力", "律师", "会计", "设计", "广告"]):
        ind_score, ind_cat = 20, "专业服务"
    elif any(k in industry_text for k in ["体育", "文化", "娱乐", "传媒", "健身"]):
        ind_score, ind_cat = 20, "体育/文化"
    elif any(k in industry_text for k in ["制造", "机械", "电子", "设备"]):
        ind_score, ind_cat = 15, "制造业"
    elif any(k in industry_text for k in ["教育", "培训"]):
        ind_score, ind_cat = 15, "教育"
    else:
        ind_score, ind_cat = 5, "其他"
    score += ind_score
    reasons.append(f"行业:{ind_cat}")
    
    # 4. 联系方式 (10分)
    contact_score = 0
    if phone and phone != "-" and phone != "无" and len(phone) >= 7:
        contact_score += 5
        reasons.append("有手机")
    if tel and tel != "-" and tel != "无" and len(tel) >= 5:
        contact_score += 5
        reasons.append("有固话")
    score += contact_score
    
    # 5. 状态 (10分)
    if "存续" in status or "在业" in status:
        score += 10
        reasons.append("经营正常")
    
    return {
        "企业名称": name,
        "综合得分": min(score, 100),
        "企查查链接": qcc_link,
        "注册地址": addr,
        "主营业务": industry,
        "注册资本": capital,
        "参保人数": emp_raw,
        "联系方式": phone if phone not in ["-", "无"] else tel,
        "评分理由": " | ".join(reasons),
        "行业分类": ind_cat,
        "登记状态": status
    }

def main():
    start = datetime.now()
    
    # 1. 获取所有数据
    records = fetch_all()
    if not records:
        print("\n❌ 未获取到任何数据，退出")
        return
    
    print(f"\n✅ 共获取 {len(records)} 条企业记录，开始分析...")
    
    # 2. 分析
    results = []
    for rec in records:
        cells = rec.get("cells", {})
        res = analyze_record(cells)
        if res:
            results.append(res)
    
    # 3. 排序
    results.sort(key=lambda x: x["综合得分"], reverse=True)
    for i, r in enumerate(results, 1):
        r["排名"] = i
    
    top20 = results[:20]
    
    # 4. 保存CSV
    if top20:
        with open("橙发i运动_长包签约Top20企业.csv", "w", newline="utf-8-sig", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=top20[0].keys())
            writer.writeheader()
            writer.writerows(top20)
        print("✅ Top 20 企业名单已保存: CSV文件")
    
    # 5. 生成Markdown报告
    report = f"""# 橙发i运动周边企业长包签约潜力分析报告

---

**生成时间**: {start.strftime('%Y-%m-%d %H:%M:%S')}
**数据来源**: 钉钉AI表格「【企查查】附近企业」
**总企业数**: {len(results)} 家 | **存续企业**: {sum(1 for r in results if '存续' in r['登记状态'])} 家

---

## 📊 Top 20 高潜力企业

| 排名 | 企业名称 | 综合得分 | 行业分类 | 参保人数 | 联系方式 | 注册地址 |
|------|----------|----------|----------|----------|----------|----------|
"""
    
    for r in top20:
        addr_display = (r['注册地址'][:25] + "...") if len(r['注册地址']) > 25 else r['注册地址']
        report += f"| {r['排名']} | {r['企业名称']} | {r['综合得分']} | {r['行业分类']} | {r['参保人数']} | {r['联系方式']} | {addr_display} |\n"
    
    report += """
---

## 🎯 分行业签约策略

### 🔥 高优先级（IT/互联网、金融、专业服务）
- **策略**: 企业健康计划（午间/晚间专属时段）
- **定价**: 协议价45-55元/小时（散客价60-70元）
- **增值**: 免费培训体验课、团建场地8折、专属订场通道

### ⚡ 中优先级（制造业、贸易、教育）
- **策略**: 次卡/月卡团体办理（3人起）
- **定价**: 次卡300元/10次（相当于30元/次）
- **增值**: 周末家庭套餐（家属5折）

### 💡 低优先级（小型零售、个体户）
- **策略**: 联合推广，避免过多销售资源投入

---

## 📞 Top 5 重点企业跟进

| 排名 | 企业名称 | 联系人 | 联系电话 | 推荐策略 | 优先级 |
|------|----------|--------|----------|----------|--------|
"""
    
    for r in top20[:5]:
        priority = "🔥极高" if r['综合得分'] >= 80 else "⚡高"
        report += f"| {r['排名']} | {r['企业名称']} | - | {r['联系方式']} | 企业健康计划+免费体验 | {priority} |\n"
    
    report += """
---

## ⏰ 90天推进计划

**第1-2周**: 联系Top 10企业（HR/行政），发送方案+体验券  
**第3-4周**: 跟进体验反馈，签约3-5家企业  
**第5-8周**: 监控使用情况，优化排场  
**第9-12周**: 扩张至Top 20，目标累计签约8-10家  

---

**Generate by OpenClaw Agent Luna** 🤖"""
    
    with open("橙发i运动_长包签约分析报告.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("✅ 分析报告已生成: Markdown文件")
    
    # 6. 汇总统计
    elapsed = datetime.now() - start
    print("\n" + "="*60)
    print("📈 分析完成")
    print("="*60)
    print(f"总企业数: {len(results)}")
    print(f"存续企业: {sum(1 for r in results if '存续' in r['登记状态'])}")
    print(f"Top 20最低分: {top20[-1]['综合得分'] if top20 else 0}")
    print(f"高分企业(≥80): {sum(1 for r in results if r['综合得分']>=80)} 家")
    print(f"中分企业(60-79): {sum(1 for r in results if 60<=r['综合得分']<80)} 家")
    print(f"低分企业(<60): {sum(1 for r in results if r['综合得分']<60)} 家")
    print(f"\n🏆 Top 5 预览:")
    for i, r in enumerate(top20[:5], 1):
        print(f"{i}. {r['企业名称']} (得分:{r['综合得分']})")
        print(f"   {r['行业分类']} | {r['参保人数']}人 | {r['联系方式']}")
        print()
    
    print(f"⏱️  总耗时: {elapsed.total_seconds():.1f}秒")

if __name__ == "__main__":
    main()
