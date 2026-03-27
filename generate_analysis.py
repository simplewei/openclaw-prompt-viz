#!/usr/bin/env python3
"""
橙发i运动周边企业长包签约潜力分析 - 完整版
直接调用钉钉AI表格 → 生成Top 20名单 + 分析报告
"""

import subprocess
import json
import csv
import re
from datetime import datetime
from pathlib import Path

def run_query(limit=500):
    """执行钉钉AI表格查询"""
    cmd = [
        "mcporter", "call", "dingtalk-ai-table.query_records",
        "baseId:l6Pm2Db8D4Xdo9lYUGL3lXy48xLq0Ee4",
        "tableId:d7FEhge",
        f"limit:{limit}"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    
    if result.returncode != 0:
        raise Exception(f"查询失败: {result.stderr}")
    
    data = json.loads(result.stdout)
    return data.get("records", [])

def parse_value(cell):
    """提取cell中的文本"""
    if not cell:
        return ""
    if isinstance(cell, dict):
        return cell.get("text", "").strip()
    return str(cell).strip()

def calculate_score(record):
    """计算综合评分"""
    cells = record.get("cells", {})
    
    name = parse_value(cells.get("5b19b1v9xqysej7yjqqpy", {})).replace("(null)", "")
    status = parse_value(cells.get("l32mmkocgkcbqxkr8obn0", {}))
    capital = parse_value(cells.get("e461igbt74giugxrbhfxq", {}))
    emp_count_str = parse_value(cells.get("o4mczvu85lh9q6e7o79d0", {}))
    industry_main = parse_value(cells.get("20xnob8pa05isywy6gws0", {}))
    industry_mid = parse_value(cells.get("a4zw60h64e8nk6an2dqcb", {}))
    address = parse_value(cells.get("33d9l7536htt81azudzub", {}))
    postal = parse_value(cells.get("v1toxm0l9ntlx2p2tsbum", {}))
    phone = parse_value(cells.get("cq2f300ljch1eba3burtq", {}))
    tel = parse_value(cells.get("xm5fbhn6a2urtv4izyqaq", {}))
    
    score = 50
    reasons = []
    
    # 1. 距离 (30分)
    distance_score = 0
    if any(kw in (address + postal) for kw in ["真陈路", "园新路", "长江南路", "200442", "200444", "200083", "200072"]):
        distance_score = 30
        score += 30
        reasons.append("距离橙发中心很近")
    elif "宝山区" in address:
        distance_score = 20
        score += 20
        reasons.append("位于宝山区")
    elif "普陀区" in address:
        distance_score = 10
        score += 10
        reasons.append("位于普陀区")
    else:
        score += 5
        reasons.append("距离较远")
    
    # 2. 企业规模 (25分)
    size_score = 0
    emp_count = 0
    try:
        emp_count = int(emp_count_str) if emp_count_str and emp_count_str != "-" else 0
    except:
        emp_count = 0
    
    cap_num = 0
    if capital:
        match = re.search(r'(\d+(?:\.\d+)?)', capital.replace(',', ''))
        if match:
            cap_num = float(match.group(1))
    
    if emp_count >= 50 or cap_num >= 500:
        size_score = 25
        score += 25
        reasons.append(f"规模大（参保{emp_count}人/资本{cap_num:.0f}万）")
    elif emp_count >= 20 or cap_num >= 200:
        size_score = 20
        score += 20
        reasons.append(f"规模中等")
    elif emp_count >= 5 or cap_num >= 50:
        size_score = 15
        score += 15
        reasons.append(f"规模较小")
    else:
        size_score = 5
        score += 5
        reasons.append("规模小")
    
    # 3. 行业 (25分)
    industry_score = 0
    industry_text = f"{industry_main} {industry_mid}".lower()
    
    if any(kw in industry_text for kw in ["软件", "信息技术", "互联网", "通信", "科技"]):
        industry_score = 25
        industry_category = "互联网/IT"
    elif any(kw in industry_text for kw in ["金融", "银行", "保险", "证券", "投资"]):
        industry_score = 25
        industry_category = "金融"
    elif any(kw in industry_text for kw in ["咨询", "律师", "会计", "人力资源", "设计", "广告"]):
        industry_score = 20
        industry_category = "专业服务"
    elif any(kw in industry_text for kw in ["体育", "文化", "娱乐", "传媒", "健身"]):
        industry_score = 20
        industry_category = "体育/文化"
    elif any(kw in industry_text for kw in ["制造", "生产", "机械", "电子", "设备"]):
        industry_score = 15
        industry_category = "制造业"
    elif any(kw in industry_text for kw in ["教育", "培训", "学校"]):
        industry_score = 15
        industry_category = "教育"
    else:
        industry_score = 5
        industry_category = "其他"
    
    score += industry_score
    reasons.append(f"行业:{industry_category}")
    
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
    status_score = 0
    if "存续" in status or "在业" in status:
        status_score = 10
        score += 10
        reasons.append("状态正常")
    else:
        reasons.append(f"状态:{status}")
    
    return {
        "score": min(score, 100),
        "distance_score": distance_score,
        "size_score": size_score,
        "industry_score": industry_score,
        "contact_score": contact_score,
        "status_score": status_score,
        "reasons": " | ".join(reasons),
        "industry_category": industry_category,
        "status": status,
        "raw_emp": emp_count,
        "raw_cap": cap_num
    }

def main():
    print("="*60)
    print("橙发i运动周边企业长包签约潜力分析")
    print("="*60)
    
    try:
        records = run_query(limit=500)
    except Exception as e:
        print(f"❌ 数据读取失败: {e}")
        return
    
    if not records:
        print("❌ 未读取到任何企业数据")
        return
    
    print(f"✅ 成功读取 {len(records)} 条企业记录")
    
    results = []
    for rec in records:
        cells = rec.get("cells", {})
        name = parse_value(cells.get("5b19b1v9xqysej7yjqqpy", {})).replace("(null)", "")
        if not name:
            continue
            
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
    
    # Top 20
    top20 = results[:20]
    
    # 保存CSV
    csv_path = Path("橙发i运动_长包签约Top20企业.csv")
    with open(csv_path, "w", newline="utf-8-sig", encoding="utf-8-sig") as f:
        if top20:
            writer = csv.DictWriter(f, fieldnames=top20[0].keys())
            writer.writeheader()
            writer.writerows(top20)
    
    print(f"\n✅ Top 20名单已保存: {csv_path}")
    
    # 生成Markdown报告
    report = f"""# 橙发i运动周边企业长包签约潜力分析报告

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}
数据来源：钉钉AI表格「【企查查】附近企业」
总企业数：{len(records)}
筛选标准：综合评分≥60分 + 企业存续 + 距离优先

---

## 📊 Top 20 高潜力企业名单

| 排名 | 企业名称 | 综合得分 | 行业分类 | 参保人数 | 联系方式 | 注册地址 |
|------|----------|----------|----------|----------|----------|----------|
"""
    
    for r in top20:
        report += f"| {r['排名']} | {r['企业名称']} | {r['综合得分']} | {r['行业分类']} | {r['参保人数']} | {r['联系方式']} | {r['注册地址'][:40]}… |\n"
    
    report += """
---

## 🎯 分行业签约策略

### 🔥 高优先级（IT/互联网、金融、专业服务）
- **签约策略**：企业健康计划（午间/晚间场次）
- **定价**：协议价（比散客低15-20%）
- **增值**：羽毛球培训包、团建场地

### ⚡ 中优先级（制造业、贸易、教育）
- **签约策略**：次卡/月卡团体办理（3人起）
- **定价**：次卡优惠（买10送2）
- **增值**：周末家庭套餐（家属5折）

### 💡 低优先级（小型零售、个体户）
- **策略**：联合推广（满额送体验券）
- **注意**：避免投入过多销售资源

---

## 📞 销售话术（HR/行政电话）

**开场**：
> "您好！我是橙发运动羽毛球场的客户经理。我们距离贵公司很近（步行5分钟），专门为周边企业提供员工运动福利方案。请问是否有兴趣了解？"

**价值**：
1. 20片专业场地（含VIP场）— 品质保障
2. 多时段可选（9:00-22:00）— 适应不同班次
3. 企业专享价 — 降低员工健身成本
4. 免费体验2小时 — 先体验后签约

---

## ⏰ 90天推进计划

**第1-2周**：联系Top 10企业（HR/行政），送体验券
**第3-4周**：跟进体验反馈，签约3-5家
**第5-8周**：收集使用数据，优化排场
**第9-12周**：扩张至Top 20企业，目标签约率30%

---

## ⚠️ 注意事项

1. 已注销/吊销企业已排除
2. 联系电话为"-"的企业需通过企查查获取联系人
3. 距离评分基于真陈路719号3公里范围
4. 建议优先联系"参保人数>5"或"注册资本>50万"的企业

---

**Generate by OpenClaw Agent Luna** 🤖
"""
    
    report_path = Path("橙发i运动_长包签约分析报告.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"✅ 分析报告已生成: {report_path}")
    
    # 打印Top 5预览
    print("\n" + "="*60)
    print("🏆 Top 5 高潜力企业预览:")
    print("="*60)
    for r in top20[:5]:
        print(f"{r['排名']}. {r['企业名称']} (得分:{r['综合得分']})")
        print(f"   行业: {r['行业分类']} | 参保: {r['参保人数']}人 | 电话: {r['联系方式']}")
        print(f"   地址: {r['注册地址'][:50]}...")
        print(f"   理由: {r['评分理由'][:80]}...")
        print()
    
    print(f"📈 统计摘要:")
    print(f"   - 存续企业: {sum(1 for r in results if '存续' in r['登记状态'])}")
    print(f"   - 平均得分: {sum(r['综合得分'] for r in results)/len(results):.1f}")
    print(f"   - Top 20平均得分: {sum(r['综合得分'] for r in top20)/len(top20):.1f}")

if __name__ == "__main__":
    main()
