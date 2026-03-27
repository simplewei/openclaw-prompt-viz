#!/usr/bin/env python3
"""
生成分析报告并发布到钉钉文档
"""

import json, re, subprocess, time
from datetime import datetime

# 读取数据
with open('企业数据_全量.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
records = data['records']
print(f'加载 {len(records)} 条企业数据')

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
    qcc_link = link_obj.get("link", "") if isinstance(link_obj, dict) else ""
    
    score = 50; reasons = []
    if "真陈路" in addr or "园新路" in addr: score += 30; reasons.append("极近")
    elif "宝山区" in addr: score += 20; reasons.append("宝山区")
    elif "普陀区" in addr: score += 10; reasons.append("普陀区")
    else: score += 5; reasons.append("远")
    
    emp = int(emp_raw) if emp_raw and emp_raw != "-" else 0
    cap_match = re.search(r'(\d+(?:\.\d+)?)', capital.replace(',', '')) if capital else None
    cap = float(cap_match.group(1)) if cap_match else 0
    if emp >= 50 or cap >= 500: score += 25; reasons.append(f"大({emp}人/{cap:.0f}万)")
    elif emp >= 20 or cap >= 200: score += 20; reasons.append("中")
    elif emp >= 5 or cap >= 50: score += 15; reasons.append("小")
    else: score += 5; reasons.append("微")
    
    ind_lower = industry.lower()
    if any(k in ind_lower for k in ["软件", "信息技术", "互联网", "科技", "通信", "网络"]):
        ind_s, ind_cat = 25, "IT/互联网"
    elif any(k in ind_lower for k in ["金融", "银行", "保险", "证券", "投资"]):
        ind_s, ind_cat = 25, "金融"
    elif any(k in ind_lower for k in ["咨询", "人力", "律师", "会计", "设计", "广告"]):
        ind_s, ind_cat = 20, "专业服务"
    elif any(k in ind_lower for k in ["体育", "文化", "娱乐", "传媒", "健身"]):
        ind_s, ind_cat = 20, "体育/文化"
    elif any(k in ind_lower for k in ["制造", "机械", "电子", "设备"]):
        ind_s, ind_cat = 15, "制造业"
    elif any(k in ind_lower for k in ["教育", "培训"]):
        ind_s, ind_cat = 15, "教育"
    else: ind_s, ind_cat = 5, "其他"
    score += ind_s; reasons.append(f"行业:{ind_cat}")
    
    if phone and phone != "-" and len(phone)>=7: score += 5; reasons.append("手机")
    if tel and tel != "-" and len(tel)>=5: score += 5; reasons.append("固话")
    if "存续" in status or "在业" in status: score += 10; reasons.append("正常")
    
    return {
        "企业名称": name,
        "综合得分": min(score,100),
        "企查查链接": qcc_link,
        "注册地址": addr,
        "主营业务": industry,
        "注册资本": capital,
        "参保人数": emp_raw,
        "联系方式": phone if phone not in ["-","无"] else tel,
        "行业分类": ind_cat,
        "登记状态": status,
        "评分理由": " | ".join(reasons)
    }

# 分析
results = []
for rec in records:
    res = analyze(rec.get("cells", {}))
    if res:
        results.append(res)

results.sort(key=lambda x: x["综合得分"], reverse=True)
for i, r in enumerate(results, 1):
    r["排名"] = i
top20 = results[:20]

print(f'✅ 分析完成，共 {len(results)} 家有效企业，Top20已生成')

# 生成Markdown报告
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
report = f"""# 橙发i运动周边企业长包签约潜力分析报告

生成时间：{timestamp}
数据来源：钉钉AI表格「【企查查】附近企业」
总企业数：{len(results)} 家（已筛选存续企业）

---

## 📊 Top 20 高潜力企业名单

| 排名 | 企业名称 | 综合得分 | 行业分类 | 参保人数 | 联系方式 | 注册地址 |
|------|----------|----------|----------|----------|----------|----------|
"""
for r in top20:
    addr_disp = (r['注册地址'][:25] + '...') if len(r['注册地址']) > 25 else r['注册地址']
    report += f"| {r['排名']} | {r['企业名称']} | {r['综合得分']} | {r['行业分类']} | {r['参保人数']} | {r['联系方式']} | {addr_disp} |\n"

report += """
---

## 🎯 分行业签约策略

### 🔥 高优先级（IT/互联网、金融、专业服务）
- **策略**：企业健康计划（午间/晚间专属时段）
- **定价**：协议价45-55元/小时（散客价60-70元）
- **增值**：免费培训体验课、团建场地8折、专属订场通道

### ⚡ 中优先级（制造业、贸易、教育）
- **策略**：次卡/月卡团体办理（3人起）
- **定价**：次卡300元/10次
- **增值**：周末家庭套餐（家属5折）

### 💡 低优先级
- 联合推广，避免过多销售资源投入

---

## 📞 Top 5 重点企业跟进

| 排名 | 企业名称 | 联系电话 | 推荐策略 |
|------|----------|----------|----------|
"""
for r in top20[:5]:
    report += f"| {r['排名']} | {r['企业名称']} | {r['联系方式']} | 企业健康计划+免费体验 |\n"

report += """
---

## ⏰ 90天推进计划
- **第1-2周**：联系Top 10企业（HR/行政），发送方案+体验券
- **第3-4周**：跟进体验反馈，签约3-5家企业
- **第5-8周**：监控使用情况，优化排场
- **第9-12周**：扩张至Top 20，目标累计签约8-10家

---

**Generate by OpenClaw Agent Luna** 🤖
"""

# 保存本地
with open('橙发i运动_长包签约潜力分析报告.md', 'w', encoding='utf-8') as f:
    f.write(report)
print('✅ Markdown报告已保存')

# 发布到钉钉文档（使用配置的openclaw文件夹）
print('\n📤 正在发布到钉钉文档...')
try:
    # 读取默认父节点ID
    import json
    try:
        with open('/root/.openclaw/workspace/config/dingtalk_folders.json', 'r') as cf:
            cfg = json.load(cf)
            parent_id = cfg.get('defaultParentDentryUuid', 'ndMj49yWjXNaR09OIDDmZwy3J3pmz5aA')
    except:
        parent_id = 'ndMj49yWjXNaR09OIDDmZwy3J3pmz5aA'  # 默认openclaw文件夹
    
    doc_title = f"橙发i运动_长包签约潜力分析_{datetime.now().strftime('%Y%m%d_%H%M')}"
    create_cmd = [
        "mcporter", "call", "dingtalk-docs.create_doc_under_node",
        f"parentDentryUuid:{parent_id}",
        f"title:{doc_title}",
        f"content:{report}"
    ]
    res = subprocess.run(create_cmd, capture_output=True, text=True, timeout=120)
    
    if res.returncode == 0:
        doc_data = json.loads(res.stdout)
        doc_id = doc_data.get('documentId') or doc_data.get('dentryUuid')
        doc_url = f"https://alidocs.dingtalk.com/i/nodes/{doc_id}"
        print(f'✅ 钉钉文档发布成功！')
        print(f'\n🔗 文档链接: {doc_url}')
        print(f'📄 文档ID: {doc_id}')
    else:
        print(f'⚠️  钉钉文档发布失败: {res.stderr[:100]}')
        print('报告已保存在本地文件')
except Exception as e:
    print(f'⚠️  发布过程出错: {e}')
    print('请查看本地文件: 橙发i运动_长包签约潜力分析报告.md')

print(f'\n📊 完成统计:')
print(f'   总企业数: {len(results)}')
print(f'   存续企业: {sum(1 for r in results if "存续" in r["登记状态"])}')
print(f'   Top20最低分: {top20[-1]["综合得分"]}')
print(f'   高分企业(≥80): {sum(1 for r in results if r["综合得分"]>=80)}家')
print(f'   中分企业(60-79): {sum(1 for r in results if 60<=r["综合得分"]<80)}家')

print(f'\n🏆 Top 5 企业:')
for i, r in enumerate(top20[:5], 1):
    print(f'{i}. {r["企业名称"]} (得分:{r["综合得分"]}) - {r["行业分类"]}')
    print(f'   电话: {r["联系方式"]}')
