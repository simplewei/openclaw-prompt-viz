#!/usr/bin/env python3
"""
最终版：220条企业数据 → 分析Top20 → 写入钉钉多维表格
"""

import json, re, time, subprocess, sys
from datetime import datetime

INPUT_FILE = '企业数据_完整.json'
TARGET_BASE_ID = '7QG4Yx2JpLZb15rBFB5gNrGdJ9dEq3XD'  # OpenClaw测试表格

def main():
    start = datetime.now()
    
    print("="*70)
    print("橙发i运动_长包签约潜力分析 — 最终版")
    print("="*70)
    
    # 1️⃣ 加载数据
    print("\n📂 正在加载企业数据...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    records = data.get('records', [])
    print(f'✅ 共加载 {len(records)} 条企业记录')
    
    # 2️⃣ 分析函数
    def parse(cell):
        if not cell: return ""
        if isinstance(cell, dict): return cell.get("text", "").strip()
        return str(cell).strip()
    
    def analyze_company(cells):
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
        link_obj = cells.get("5b19b1v9xqysej7yjqqpy", {})
        qcc_link = link_obj.get("link", "") if isinstance(link_obj, dict) else ""
        
        # 综合评分
        score = 50
        reasons = []
        
        # 距离 30分
        if "真陈路" in addr or "园新路" in addr:
            score += 30; reasons.append("极近")
        elif "宝山区" in addr:
            score += 20; reasons.append("宝山区")
        elif "普陀区" in addr:
            score += 10; reasons.append("普陀区")
        else: score += 5; reasons.append("远")
        
        # 规模 25分
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
        
        # 行业 25分
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
        else:
            ind_s, ind_cat = 5, "其他"
        score += ind_s
        reasons.append(f"行业:{ind_cat}")
        
        # 联系方式 10分
        if phone and phone != "-" and len(phone)>=7: score += 5; reasons.append("手机")
        if tel and tel != "-" and len(tel)>=5: score += 5; reasons.append("固话")
        
        # 状态 10分
        if "存续" in status or "在业" in status:
            score += 10; reasons.append("正常")
        
        return {
            "企业名称": name,
            "综合得分": min(score, 100),
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
    
    # 3️⃣ 执行分析
    print("\n📊 正在分析企业签约潜力...")
    results = []
    for rec in records:
        res = analyze_company(rec.get("cells", {}))
        if res:
            results.append(res)
    
    print(f'✅ 有效分析企业: {len(results)} 家')
    
    results.sort(key=lambda x: x["综合得分"], reverse=True)
    for i, r in enumerate(results, 1):
        r["排名"] = i
    
    top20 = results[:20]
    
    print(f'\n🏆 Top 5 企业预览:')
    for i, r in enumerate(top20[:5], 1):
        print(f'{i}. {r["企业名称"]} (得分:{r["综合得分"]}) - {r["行业分类"]} - {r["联系方式"]}')
    
    # 4️⃣ 创建钉钉表格
    print("\n" + "="*70)
    print("🔨 在钉钉创建结果表格并写入数据")
    print("="*70)
    
    table_name = f"橙发i运动_长包签约Top20_{datetime.now().strftime('%Y%m%d_%H%M')}"
    
    try:
        # 创建表格
        print(f"\n📊 创建表格: {table_name}")
        create_cmd = ['mcporter', 'call', 'dingtalk-ai-table.create_table',
                      f'baseId:{TARGET_BASE_ID}', f'name:{table_name}', 'viewType:Grid']
        res = subprocess.run(create_cmd, capture_output=True, text=True, timeout=60)
        
        if res.returncode != 0:
            print(f'❌ 创建表格失败: {res.stderr}')
            raise Exception("创建表格失败")
        
        table_data = json.loads(res.stdout)
        table_id = table_data.get('tableId')
        print(f'✅ 表格创建成功')
        print(f'   Table ID: {table_id}')
        
        # 定义字段
        fields = [
            {"fieldName": "排名", "type": "Number", "property": {"precision": 0}},
            {"fieldName": "企业名称", "type": "SingleText"},
            {"fieldName": "综合得分", "type": "Number", "precision": 0},
            {"fieldName": "行业分类", "type": "SingleText"},
            {"fieldName": "参保人数", "type": "SingleText"},
            {"fieldName": "注册资本", "type": "SingleText"},
            {"fieldName": "联系方式", "type": "SingleText"},
            {"fieldName": "注册地址", "type": "SingleText"},
            {"fieldName": "企查查链接", "type": "Url"},
            {"fieldName": "评分理由", "type": "SingleText"},
            {"fieldName": "登记状态", "type": "SingleText"},
            {"fieldName": "主营业务", "type": "SingleText"}
        ]
        
        print('\n📋 添加字段...')
        for f in fields:
            cmd = ['mcporter', 'call', 'dingtalk-ai-table.add_field',
                   f'baseId:{TARGET_BASE_ID}', f'tableId:{table_id}',
                   f'fieldName:{f["fieldName"]}', f'type:{f["type"]}']
            if 'property' in f:
                cmd.append(f'property:{json.dumps(f["property"])}')
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if r.returncode == 0:
                print(f'  ✅ {f["fieldName"]}')
            else:
                print(f'  ⚠️  {f["fieldName"]}')
        
        time.sleep(1)
        
        # 插入Top20数据
        print(f'\n📥 正在插入 Top 20 数据...')
        success_count = 0
        for idx, r in enumerate(top20, 1):
            record = {
                "排名": r["排名"],
                "企业名称": r["企业名称"],
                "综合得分": r["综合得分"],
                "行业分类": r["行业分类"],
                "参保人数": r["参保人数"],
                "注册资本": r["注册资本"],
                "联系方式": r["联系方式"],
                "注册地址": r["注册地址"],
                "企查查链接": r["企查查链接"],
                "评分理由": r["评分理由"],
                "登记状态": r["登记状态"],
                "主营业务": r["主营业务"]
            }
            cmd = ['mcporter', 'call', 'dingtalk-ai-table.add_record',
                   f'baseId:{TARGET_BASE_ID}', f'tableId:{table_id}',
                   f'recordData:{json.dumps(record, ensure_ascii=False)}']
            rres = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if rres.returncode != 0:
                print(f'  ❌ 第{idx}条失败: {rres.stderr[:50]}')
            else:
                success_count += 1
                if idx % 5 == 0:
                    print(f'  ✅ 已插入 {idx}/{len(top20)} 条')
        
        print(f'\n✅ 数据插入完成！成功 {success_count}/{len(top20)} 条')
        
        # 5️⃣ 生成本地Markdown备份
        print("\n📄 生成本地Markdown报告...")
        report = f"""# 橙发i运动周边企业长包签约潜力分析报告

---

**生成时间**：{start.strftime('%Y-%m-%d %H:%M:%S')}
**数据来源**：钉钉AI表格「【企查查】附近企业」
**总企业数**：{len(results)} 家（存续：{sum(1 for r in results if '存续' in r['登记状态'])} 家）

---

## 📊 Top 20 高潜力企业名单

| 排名 | 企业名称 | 综合得分 | 行业分类 | 参保人数 | 联系方式 | 注册地址 |
|------|----------|----------|----------|----------|----------|----------|
"""
        for r in top20:
            addr_display = (r['注册地址'][:20] + '..') if len(r['注册地址']) > 20 else r['注册地址']
            report += f"| {r['排名']} | {r['企业名称']} | {r['综合得分']} | {r['行业分类']} | {r['参保人数']} | {r['联系方式']} | {addr_display} |\n"
        
        report += """
---

## 🎯 分行业签约策略

### 🔥 高优先级（IT/互联网、金融、专业服务）
- **策略**：企业健康计划（午间/晚间专属时段）
- **定价**：协议价45-55元/小时（散客价60-70元）
- **增值**：免费培训体验课、团建场地8折、专属订场通道

### ⚡ 中优先级（制造业、贸易、教育）
- **策略**：次卡/月卡团体办理（3人起）
- **定价**：次卡300元/10次（相当于30元/次）
- **增值**：周末家庭套餐（家属5折）

---

## 📞 Top 5 重点企业跟进

| 排名 | 企业名称 | 联系电话 | 推荐策略 | 优先级 |
|------|----------|----------|----------|--------|
"""
        for r in top20[:5]:
            priority = "🔥极高" if r['综合得分'] >= 80 else "⚡高"
            report += f"| {r['排名']} | {r['企业名称']} | {r['联系方式']} | 企业健康计划+免费体验 | {priority} |\n"
        
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
        
        with open("橙发i运动_长包签约潜力分析_完整版.md", "w", encoding="utf-8") as f:
            f.write(report)
        print("✅ Markdown报告已生成")
        
        # 6️⃣ 输出结果
        print("\n" + "="*70)
        print("🎉 任务完成！")
        print("="*70)
        print(f"\n📊 统计摘要:")
        print(f"   - 总企业数: {len(results)}")
        print(f"   - 存续企业: {sum(1 for r in results if '存续' in r['登记状态'])}")
        print(f"   - Top20最低分: {top20[-1]['综合得分']}")
        print(f"   - 高分企业(≥80): {sum(1 for r in results if r['综合得分']>=80)}家")
        print(f"   - 中分企业(60-79): {sum(1 for r in results if 60<=r['综合得分']<80)}家")
        
        print(f"\n🔗 钉钉多维表格链接:")
        print(f"https://alidocs.dingtalk.com/i/nodes/{TARGET_BASE_ID}")
        print(f"\n📋 表格名称: {table_name}")
        print(f"   Table ID: {table_id}")
        
        print(f"\n⏱️  总耗时: {(datetime.now()-start).total_seconds():.1f}秒")
        
    except Exception as e:
        print(f'\n❌ 过程出错: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
