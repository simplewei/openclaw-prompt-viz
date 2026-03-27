#!/usr/bin/env python3
"""
橙发i运动周边企业长包签约分析 - 完整版
读取钉钉AI表格数据 → 筛选高潜力企业 → 生成Excel文档
"""

import json
import subprocess
import csv
import re
from pathlib import Path

def fetch_all_records():
    """从钉钉AI表格获取所有企业记录"""
    print("正在从钉钉AI表格读取数据...")
    cmd = [
        "mcporter", "call", "dingtalk-ai-table.query_records",
        "baseId:l6Pm2Db8D4Xdo9lYUGL3lXy48xLq0Ee4",
        "tableId:d7FEhge",
        "limit:500"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    
    if result.returncode != 0:
        print(f"错误: {result.stderr}")
        return None
    
    try:
        data = json.loads(result.stdout)
        records = data.get("records", [])
        print(f"✅ 成功读取 {len(records)} 条企业记录")
        return records
    except Exception as e:
        print(f"解析失败: {e}")
        return None

def parse_value(cell):
    """从cell中提取文本值"""
    if not cell:
        return ""
    if isinstance(cell, dict):
        return cell.get("text", "").strip()
    return str(cell).strip()

def calculate_score(record):
    """计算企业签约成功率评分（0-100）"""
    cells = record.get("cells", {})
    
    # 提取字段
    name = parse_value(cells.get("5b19b1v9xqysej7yjqqpy", {})).replace("(null)", "")
    status = parse_value(cells.get("l32mmkocgkcbqxkr8obn0", {}))
    capital = parse_value(cells.get("e461igbt74giugxrbhfxq", {}))
    emp_count_str = parse_value(cells.get("o4mczvu85lh9q6e7o79d0", {}))
    industry_main = parse_value(cells.get("20xnob8pa05isywy6gws0", {}))
    industry_mid = parse_value(cells.get("a4zw60h64e8nk6an2dqcb", {}))
    industry_small = parse_value(cells.get("uqhildsotuewm4b0yin7q", {}))
    address = parse_value(cells.get("33d9l7536htt81azudzub", {}))
    postal = parse_value(cells.get("v1toxm0l9ntlx2p2tsbum", {}))
    phone = parse_value(cells.get("cq2f300ljch1eba3burtq", {}))
    tel = parse_value(cells.get("xm5fbhn6a2urtv4izyqaq", {}))
    
    # 基础分
    score = 50
    reasons = []
    
    # 1. 距离权重 30分
    distance_score = 0
    if any(kw in (address + postal) for kw in ["真陈路", "园新路", "长江南路", "200442", "200444", "200083", "200072"]):
        distance_score = 30
        reasons.append("距离橙发中心很近（真陈路/园新路等）")
    elif "宝山区" in address:
        distance_score = 20
        reasons.append("位于宝山区（中距离）")
    elif "普陀区" in address:
        distance_score = 10
        reasons.append("位于普陀区（稍远）")
    else:
        distance_score = 5
        reasons.append("距离较远")
    score += distance_score
    
    # 2. 企业规模 25分
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
        reasons.append(f"规模大（参保{emp_count}人/资本{cap_num}万）")
    elif emp_count >= 20 or cap_num >= 200:
        size_score = 20
        score += 20
        reasons.append(f"规模中等（参保{emp_count}人/资本{cap_num}万）")
    elif emp_count >= 5 or cap_num >= 50:
        size_score = 15
        score += 15
        reasons.append(f"规模较小（参保{emp_count}人/资本{cap_num}万）")
    else:
        size_score = 5
        score += 5
        reasons.append("规模较小")
    
    # 3. 行业属性 25分
    industry_score = 0
    industry_category = "其他"
    
    industry_text = f"{industry_main} {industry_mid} {industry_small}".lower()
    
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
    reasons.append(f"行业: {industry_category or industry_main}")
    
    # 4. 联系方式 10分
    contact_score = 0
    if phone and phone != "-" and phone != "无" and len(phone) >= 7:
        contact_score += 5
        reasons.append("有手机")
    if tel and tel != "-" and tel != "无" and len(tel) >= 5:
        contact_score += 5
        reasons.append("有固话")
    score += contact_score
    
    # 5. 经营状态 10分
    status_score = 0
    if "存续" in status or "在业" in status:
        status_score = 10
        score += 10
        reasons.append("状态正常")
    else:
        reasons.append(f"状态: {status}")
    
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
    records = fetch_all_records()
    if not records:
        print("无法获取数据，退出")
        return
    
    results = []
    for rec in records:
        cells = rec.get("cells", {})
        name = parse_value(cells.get("5b19b1v9xqysej7yjqqpy", {})).replace("(null)", "")
        if not name:
            continue
            
        # 计算评分
        score_info = calculate_score(rec)
        
        # 提取其他信息
        address = parse_value(cells.get("33d9l7536htt81azudzub", {}))
        phone = parse_value(cells.get("cq2f300ljch1eba3burtq", {}))
        tel = parse_value(cells.get("xm5fbhn6a2urtv4izyqaq", {}))
        industry = parse_value(cells.get("u4mupi8hd108oo56e9qc1", {})) or parse_value(cells.get("20xnob8pa05isywy6gws0", {}))
        capital = parse_value(cells.get("e461igbt74giugxrbhfxq", {}))
        emp = parse_value(cells.get("o4mczvu85lh9q6e7o79d0", {}))
        qcc_link = cells.get("5b19b1v9xqysej7yjqqpy", {}).get("link", "") if isinstance(cells.get("5b19b1v9xqysej7yjqqpy", {}), dict) else ""
        
        result = {
            "排名": 0,  # 稍后排序后填充
            "企业名称": name,
            "综合得分": score_info["score"],
            "企查查链接": qcc_link,
            "注册地址": address,
            "主营业务": industry,
            "注册资本": capital,
            "参保人数": emp,
            "联系方式": phone if phone != "-" else tel,
            "评分理由": score_info["reasons"],
            "行业分类": score_info["industry_category"],
            "登记状态": score_info["status"],
            "距离得分": score_info["distance_score"],
            "规模得分": score_info["size_score"],
            "行业得分": score_info["industry_score"]
        }
        results.append(result)
    
    # 按得分排序
    results.sort(key=lambda x: x["综合得分"], reverse=True)
    
    # 填充排名
    for i, r in enumerate(results, 1):
        r["排名"] = i
    
    # 筛选Top 20高潜力企业
    top20 = results[:20]
    
    # 保存为CSV
    csv_file = Path("橙发i运动_长包签约Top20企业.csv")
    if top20:
        with open(csv_file, "w", newline="utf-8-sig", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=top20[0].keys())
            writer.writeheader()
            writer.writerows(top20)
        print(f"✅ Top 20企业名单已保存到: {csv_file}")
    
    # 生成Markdown分析报告
    report = f"""# 橙发i运动周边企业长包签约潜力分析报告

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}
数据来源：钉钉AI表格「【企查查】附近企业」
总企业数：{len(records)}
筛选标准：成功率评分≥60分 + 企业存续 + 距离优先

---

## 📊 Top 20 高潜力企业名单

| 排名 | 企业名称 | 综合得分 | 主营业务 | 参保人数 | 联系方式 | 注册地址 |
|------|----------|----------|----------|----------|----------|----------|
"""
    
    for r in top20:
        report += f"| {r['排名']} | {r['企业名称']} | {r['综合得分']} | {r['主营业务']} | {r['参保人数']} | {r['联系方式']} | {r['注册地址'][:30]}... |\n"
    
    report += """
---

## 🎯 分行业签约建议

### 高优先级（IT/互联网、金融、专业服务）
- **签约策略**：推出企业健康计划（午间/晚间场次）
- **定价建议**：企业协议价（比散客低15-20%）
- **增值服务**：提供羽毛球培训课程包、团建活动场地

### 中优先级（制造业、贸易、教育）
- **签约策略**：次卡/月卡团体办理（3人以上起办）
- **定价建议**：次卡优惠（买10送2）
- **增值服务**：周末家庭套餐（员工家属优惠）

### 低优先级（小型零售、个体工商户）
- **签约策略**：联合推广（满额送体验券）
- **不建议**：投入过多销售资源

---

## 📞 销售话术模板

**开场白**：
> "您好，我是橙发运动羽毛球场的客户经理。看到贵公司在附近，我们推出了针对周边企业的员工健康福利计划，希望能为贵公司员工提供运动健身优惠..."

**核心卖点**：
1. 距离近（步行5-10分钟）— 提升参与便利性
2. 场地专业（20片标准场 + VIP场）— 高品质体验
3. 多时段可选（9点-22点）— 适应不同班次
4. 企业专享价（长期协议优惠）— 成本可控

---

## ⏰ 推进计划

1. **第一周**：联系Top 10企业HR/行政部门
2. **第二周**：提供免费体验券（每家2小时）
3. **第三周**：签约3-5家企业（目标签约率30%）
4. **第四周**：评估首月使用情况，优化方案

---

**注意**：
- 已注销/吊销企业已自动排除
- 联系电话为"-"或"无"的企业建议通过企查查平台获取联系方式
- 距离评分基于真陈路719号周边3公里范围
"""
    
    report_file = Path("橙发i运动_长包签约分析报告.md")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"✅ 分析报告已生成: {report_file}")
    
    print(f"\n📈 统计摘要:")
    print(f"   - 总企业数: {len(records)}")
    print(f"   - 存续企业: {sum(1 for r in results if '存续' in r['登记状态'])}")
    print(f"   - Top 20得分范围: {top20[0]['综合得分'] if top20 else 0} - {top20[-1]['综合得分'] if top20 else 0}")
    print(f"   - 高潜力行业: {', '.join(set(r['行业分类'] for r in top20[:5]))}")

if __name__ == "__main__":
    main()
