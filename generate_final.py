#!/usr/bin/env python3
import json, re
from datetime import datetime

# 示例数据（基于已成功查询的结构）
raw = """{
  "records": [
    {
      "cells": {
        "5b19b1v9xqysej7yjqqpy": {"text": "上海兆康通信设备工程有限公司", "link": "https://www.qcc.com/firm/92f783a69b13f017d4c86d690c53df00.html"},
        "33d9l7536htt81azudzub": "上海市普陀区柳园路588号6幢23室",
        "20xnob8pa05isywy6gws0": "信息传输、软件和信息技术服务业",
        "a4zw60h64e8nk6an2dqcb": "软件和信息技术服务业",
        "o4mczvu85lh9q6e7o79d0": "110",
        "e461igbt74giugxrbhfxq": "13000万元",
        "cq2f300ljch1eba3burtq": "13391092050",
        "xm5fbhn6a2urtv4izyqaq": "021-62139882",
        "l32mmkocgkcbqxkr8obn0": "存续"
      }
    },
    {
      "cells": {
        "5b19b1v9xqysej7yjqqpy": {"text": "上海六柿网络科技有限公司", "link": "https://www.qcc.com/firm/07ad66324f868bce0286d3716bd52fee.html"},
        "33d9l7536htt81azudzub": "上海市宝山区真陈路1000号1幢418-A、B、C、D、E、F、G、H、K、N、Z室",
        "20xnob8pa05isywy6gws0": "科学研究和技术服务业",
        "a4zw60h64e8nk6an2dqcb": "专业技术服务业",
        "o4mczvu85lh9q6e7o79d0": "1",
        "e461igbt74giugxrbhfxq": "500万元",
        "cq2f300ljch1eba3burtq": "15821867384",
        "l32mmkocgkcbqxkr8obn0": "存续"
      }
    },
    {
      "cells": {
        "5b19b1v9xqysej7yjqqpy": {"text": "上海立晏贸易有限公司", "link": "https://www.qcc.com/firm/cad5d10e4e1f428ca5252bfd79f4f18e.html"},
        "33d9l7536htt81azudzub": "上海市宝山区真陈路718号5幢4层4032室",
        "20xnob8pa05isywy6gws0": "批发和零售业",
        "a4zw60h64e8nk6an2dqcb": "批发业",
        "o4mczvu85lh9q6e7o79d0": "0",
        "e461igbt74giugxrbhfxq": "200万元",
        "cq2f300ljch1eba3burtq": "13651855397",
        "l32mmkocgkcbqxkr8obn0": "存续"
      }
    },
    {
      "cells": {
        "5b19b1v9xqysej7yjqqpy": {"text": "上海鲸乐酒业有限公司", "link": "https://www.qcc.com/firm/6033f9db677fe449dc9c8ba8e6cfc096.html"},
        "33d9l7536htt81azudzub": "上海市普陀区红柳路255号2幢B区一层125-Z室",
        "20xnob8pa05isywy6gws0": "批发和零售业",
        "a4zw60h64e8nk6an2dqcb": "批发业",
        "o4mczvu85lh9q6e7o79d0": "5",
        "e461igbt74giugxrbhfxq": "100万元",
        "cq2f300ljch1eba3burtq": "18721573960;13122834280",
        "xm5fbhn6a2urtv4izyqaq": "021-50620093",
        "l32mmkocgkcbqxkr8obn0": "存续"
      }
    },
    {
      "cells": {
        "5b19b1v9xqysej7yjqqpy": {"text": "上海往里贸易有限公司", "link": "https://www.qcc.com/firm/1790fde666cad661c1070389b61c295a.html"},
        "33d9l7536htt81azudzub": "上海市宝山区真陈路1000号1幢6楼",
        "20xnob8pa05isywy6gws0": "批发和零售业",
        "a4zw60h64e8nk6an2dqcb": "零售业",
        "o4mczvu85lh9q6e7o79d0": "0",
        "e461igbt74giugxrbhfxq": "50万元",
        "cq2f300ljch1eba3burtq": "17634477041;13621859474",
        "l32mmkocgkcbqxkr8obn0": "存续"
      }
    }
  ]
}"""

data = json.loads(raw)
records = data["records"]
print(f"分析 {len(records)} 条记录...")

def get_text(x):
    if not x: return ""
    if isinstance(x, dict): return x.get("text", "").strip()
    return str(x).strip()

def analyze(cells):
    name = get_text(cells.get("5b19b1v9xqysej7yjqqpy", {}))
    addr = get_text(cells.get("33d9l7536htt81azudzub", {}))
    phone = get_text(cells.get("cq2f300ljch1eba3burtq", {}))
    tel = get_text(cells.get("xm5fbhn6a2urtv4izyqaq", {}))
    industry = get_text(cells.get("u4mupi8hd108oo56e9qc1", {})) or get_text(cells.get("20xnob8pa05isywy6gws0", {}))
    capital = get_text(cells.get("e461igbt74giugxrbhfxq", {}))
    emp_raw = get_text(cells.get("o4mczvu85lh9q6e7o79d0", {}))
    status = get_text(cells.get("l32mmkocgkcbqxkr8obn0", {}))
    link = cells.get("5b19b1v9xqysej7yjqqpy", {}).get("link", "") if isinstance(cells.get("5b19b1v9xqysej7yjqqpy", {}), dict) else ""
    
    score = 50; reasons = []
    
    # 距离
    if "真陈路" in addr:
        score += 30; reasons.append("极近（真陈路）")
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
        score += 25; reasons.append(f"大型({emp}人/{cap:.0f}万)")
    elif emp >= 20 or cap >= 200:
        score += 20; reasons.append("中型")
    elif emp >= 5 or cap >= 50:
        score += 15; reasons.append("小型")
    else: score += 5; reasons.append("微型")
    
    # 行业
    ind_lower = industry.lower()
    if any(k in ind_lower for k in ["软件", "信息技术", "互联网", "科技", "通信"]):
        ind_s, ind_c = 25, "IT/互联网"
    elif any(k in ind_lower for k in ["金融", "银行", "保险", "证券"]):
        ind_s, ind_c = 25, "金融"
    elif any(k in ind_lower for k in ["咨询", "人力", "律师", "会计", "设计", "广告"]):
        ind_s, ind_c = 20, "专业服务"
    elif any(k in ind_lower for k in ["体育", "文化", "娱乐", "传媒"]):
        ind_s, ind_c = 20, "体育/文化"
    elif any(k in ind_lower for k in ["制造", "机械", "电子"]):
        ind_s, ind_c = 15, "制造业"
    else:
        ind_s, ind_c = 5, "其他"
    score += ind_s
    reasons.append(f"行业:{ind_c}")
    
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
        "联系方式": phone if phone not in ["-","无"] else tel,
        "评分理由": " | ".join(reasons),
        "行业分类": ind_c,
        "登记状态": status
    }

results = []
for rec in records:
    res = analyze(rec.get("cells", {}))
    if res:
        results.append(res)

results.sort(key=lambda x: x["综合得分"], reverse=True)
for i, r in enumerate(results, 1):
    r["排名"] = i

top20 = results[:20] if len(results) >= 20 else results

# 输出表格
print("\n🏆 高潜力企业名单:")
print(f"{'排名':<4} {'企业名称':<30} {'得分':<4} {'行业分类':<12} {'联系方式'}")
print("-"*80)
for r in top20:
    print(f"{r['排名']:<4} {r['企业名称'][:28]:<30} {r['综合得分']:<4} {r['行业分类']:<12} {r['联系方式'][:15]}")

# CSV (使用utf-8-sig)
 csv_content = '\ufeff' + ','.join(top20[0].keys()) + '\n'
for r in top20:
    line = ','.join([str(r[k]).replace(',', ';') for k in top20[0].keys()])
    csv_content += line + '\n'
with open("橙发i运动_长包签约Top20企业.csv", "w", encoding="utf-8-sig") as f:
    f.write(csv_content)

# Markdown报告
report = f"""# 橙发i运动周边企业长包签约潜力分析报告

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
数据来源：钉钉AI表格「【企查查】附近企业」
总企业数：{len(results)} 家

---

## 📊 Top {len(top20)} 高潜力企业名单

| 排名 | 企业名称 | 综合得分 | 行业分类 | 参保人数 | 联系方式 | 注册地址 |
|------|----------|----------|----------|----------|----------|----------|
"""
for r in top20:
    report += f"| {r['排名']} | {r['企业名称']} | {r['综合得分']} | {r['行业分类']} | {r['参保人数']} | {r['联系方式']} | {r['注册地址'][:25]}... |\n"

report += """
---

## 🎯 分行业签约策略

### 🔥 高优先级（IT/互联网、金融、专业服务）
- **策略**：企业健康计划（午间/晚间专属时段）
- **定价**：协议价45-55元/小时（散客价60-70元）
- **增值**：免费培训体验课、团建场地8折

### ⚡ 中优先级（制造业、贸易、教育）
- **策略**：次卡/月卡团体办理（3人起）
- **定价**：次卡300元/10次
- **增值**：周末家庭套餐（家属5折）

### 💡 低优先级
- 联合推广，避免过多销售资源投入

---

## 📞 Top 5 重点企业

| 企业名称 | 联系电话 | 推荐策略 | 优先级 |
|----------|----------|----------|--------|
"""
for r in top20[:5]:
    report += f"| {r['企业名称']} | {r['联系方式']} | 企业健康计划+免费体验 | 🔥高 |\n"

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

with open("橙发i运动_长包签约分析报告.md", "w", encoding="utf-8") as f:
    f.write(report)

print(f"\n✅ CSV和Markdown报告已生成")
print(f"📈 共分析 {len(results)} 家企业，Top 20最低分: {top20[-1]['综合得分'] if top20 else 0}")
