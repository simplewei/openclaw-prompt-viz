#!/usr/bin/env python3
"""
获取企业数据并写入钉钉多维表格
"""

import subprocess, json, time, re
from datetime import datetime

BASE_ID = "l6Pm2Db8D4Xdo9lYUGL3lXy48xLq0Ee4"
TABLE_ID = "d7FEhge"
LIMIT = 50  # 使用小批量避免解析问题

def fetch_all_records():
    """分页获取所有企业记录"""
    all_records = []
    cursor = None
    page = 1
    
    print("="*60)
    print("开始从钉钉AI表格获取企业数据")
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
            print(f"❌ JSON解析失败")
            print(f"  输出前200字符: {result.stdout[:200]}")
            break
        
        records = data.get("records", [])
        all_records.extend(records)
        print(f"✅ 获取 {len(records)} 条，累计 {len(all_records)} 条")
        
        cursor = data.get("nextCursor")
        if not cursor or len(records) == 0:
            break
        
        page += 1
        time.sleep(0.5)
    
    return all_records

def parse(cell):
    if not cell: return ""
    if isinstance(cell, dict): return cell.get("text", "").strip()
    return str(cell).strip()

def analyze_company(cells):
    """分析单个企业，返回评分和分类"""
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
    
    # 1. 距离 (30分)
    if "真陈路" in addr or "园新路" in addr:
        score += 30; reasons.append("极近")
    elif "宝山区" in addr:
        score += 20; reasons.append("宝山区")
    elif "普陀区" in addr:
        score += 10; reasons.append("普陀区")
    else: score += 5; reasons.append("远")
    
    # 2. 规模 (25分)
    emp = int(emp_raw) if emp_raw and emp_raw != "-" else 0
    cap_match = re.search(r'(\d+(?:\.\d+)?)', capital.replace(',', '')) if capital else None
    cap = float(cap_match.group(1)) if cap_match else 0
    
    if emp >= 50 or cap >= 500:
        score += 25; reasons.append(f"大型({emp}人/{cap:.0f}万)")
    elif emp >= 20 or cap >= 200:
        score += 20; reasons.append("中型")
    elif emp >= 5 or cap >= 50:
        score += 15; reasons.append("小型")
    else:
        score += 5; reasons.append("微型")
    
    # 3. 行业 (25分)
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
    
    # 4. 联系方式 (10分)
    contact_score = 0
    if phone and phone != "-" and len(phone) >= 7:
        contact_score += 5
        reasons.append("有手机")
    if tel and tel != "-" and len(tel) >= 5:
        contact_score += 5
        reasons.append("有固话")
    score += contact_score
    
    # 5. 状态 (10分)
    if "存续" in status or "在业" in status:
        score += 10
        reasons.append("正常")
    
    return {
        "企业名称": name,
        "综合得分": min(score, 100),
        "企查查链接": qcc_link,
        "注册地址": addr,
        "主营业务": industry,
        "注册资本": capital,
        "参保人数": emp_raw,
        "联系方式": phone if phone not in ["-", "无"] else tel,
        "行业分类": ind_cat,
        "登记状态": status,
        "评分理由": " | ".join(reasons)
    }

def create_dingtalk_table(results):
    """在钉钉创建新表格并插入数据"""
    print("\n" + "="*60)
    print("正在创建钉钉多维表格...")
    print("="*60)
    
    # 先创建表格结构（字段定义）
    fields = [
        {"fieldName": "排名", "type": "Number", "property": {"precision": 0}},
        {"fieldName": "企业名称", "type": "SingleText"},
        {"fieldName": "综合得分", "type": "Number", "property": {"precision": 0}},
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
    
    try:
        # 创建多维表格
        base_name = f"橙发i运动_长包签约潜力分析_{datetime.now().strftime('%Y%m%d')}"
        print(f"📊 创建Base: {base_name}")
        
        # 使用 dingtalk-ai-table.create_base
        create_base_cmd = [
            "mcporter", "call", "dingtalk-ai-table.create_base",
            f"name:{base_name}",
            "description:橙发羽毛球馆周边企业长包签约潜力分析结果"
        ]
        base_result = subprocess.run(create_base_cmd, capture_output=True, text=True, timeout=60)
        
        if base_result.returncode != 0:
            print(f"❌ 创建Base失败: {base_result.stderr}")
            # 如果失败，尝试在已有Base中创建表格
            print("尝试在已有Base中创建表格...")
            return None
        
        base_data = json.loads(base_result.stdout)
        new_base_id = base_data.get("baseId")
        print(f"✅ Base创建成功: {new_base_id}")
        
        # 创建表格
        table_name = "高潜力企业Top20"
        create_table_cmd = [
            "mcporter", "call", "dingtalk-ai-table.create_table",
            f"baseId:{new_base_id}",
            f"name:{table_name}",
            "viewType:Grid"
        ]
        table_result = subprocess.run(create_table_cmd, capture_output=True, text=True, timeout=60)
        
        if table_result.returncode != 0:
            print(f"❌ 创建表格失败: {table_result.stderr}")
            return None
        
        table_data = json.loads(table_result.stdout)
        new_table_id = table_data.get("tableId")
        print(f"✅ 表格创建成功: {new_table_id}")
        
        # 添加字段
        for field in fields:
            add_field_cmd = [
                "mcporter", "call", "dingtalk-ai-table.add_field",
                f"baseId:{new_base_id}",
                f"tableId:{new_table_id}",
                f"fieldName:{field['fieldName']}",
                f"type:{field['type']}"
            ]
            if 'property' in field:
                add_field_cmd.append(f"property:{json.dumps(field['property'])}")
            
            field_result = subprocess.run(add_field_cmd, capture_output=True, text=True, timeout=30)
            if field_result.returncode == 0:
                print(f"  ✅ 添加字段: {field['fieldName']}")
            else:
                print(f"  ⚠️  字段添加失败: {field['fieldName']}")
        
        time.sleep(1)
        
        # 插入数据
        print(f"\n📥 开始插入 {len(results)} 条数据...")
        for idx, r in enumerate(results, 1):
            record_data = {
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
            
            add_record_cmd = [
                "mcporter", "call", "dingtalk-ai-table.add_record",
                f"baseId:{new_base_id}",
                f"tableId:{new_table_id}",
                f"recordData:{json.dumps(record_data, ensure_ascii=False)}"
            ]
            
            rec_result = subprocess.run(add_record_cmd, capture_output=True, text=True, timeout=30)
            if rec_result.returncode != 0:
                print(f"  ❌ 第{idx}条失败: {rec_result.stderr}")
            elif idx % 10 == 0:
                print(f"  ✅ 已插入 {idx}/{len(results)} 条")
        
        print(f"\n✅ 数据插入完成！")
        print(f"\n🔗 钉钉多维表格链接: https://alidocs.dingtalk.com/i/nodes/{new_base_id}")
        return new_base_id
        
    except Exception as e:
        print(f"❌ 创建表格过程出错: {e}")
        return None

def main():
    start_time = datetime.now()
    
    # 1. 获取所有数据
    records = fetch_all_records()
    if not records:
        print("\n❌ 未获取到企业数据，无法继续")
        return
    
    print(f"\n✅ 共获取 {len(records)} 条企业记录")
    
    # 2. 分析所有企业
    print("\n📊 正在分析企业签约潜力...")
    results = []
    for rec in records:
        res = analyze_company(rec.get("cells", {}))
        if res:
            results.append(res)
    
    print(f"✅ 有效分析企业: {len(results)} 家")
    
    # 3. 排序，取Top20
    results.sort(key=lambda x: x["综合得分"], reverse=True)
    for i, r in enumerate(results, 1):
        r["排名"] = i
    
    top20 = results[:20]
    
    print(f"\n🏆 Top 5 高潜力企业:")
    for i, r in enumerate(top20[:5], 1):
        print(f"{i}. {r['企业名称']} (得分:{r['综合得分']}) - {r['行业分类']} - {r['联系方式']}")
    
    # 4. 创建钉钉表格并写入
    new_base_id = create_dingtalk_table(top20)
    
    elapsed = datetime.now() - start_time
    print(f"\n⏱️  总耗时: {elapsed.total_seconds():.1f} 秒")
    print(f"\n🎉 任务完成！")
    
    if new_base_id:
        print(f"\n📋 结果查看: https://alidocs.dingtalk.com/i/nodes/{new_base_id}")
    else:
        print("\n⚠️  表格创建可能失败，已保存结果到本地CSV和Markdown")
        # 保存本地备份
        with open("橙发i运动_长包签约Top20企业_本地备份.csv", "w", encoding="utf-8-sig") as f:
            f.write("排名,企业名称,综合得分,行业分类,参保人数,注册资本,联系方式,注册地址,企查查链接,评分理由,登记状态,主营业务\n")
            for r in top20:
                f.write(f"{r['排名']},{r['企业名称']},{r['综合得分']},{r['行业分类']},{r['参保人数']},{r['注册资本']},{r['联系方式']},{r['注册地址']},{r['企查查链接']},{r['评分理由']},{r['登记状态']},{r['主营业务']}\n")
        print("本地备份: 橙发i运动_长包签约Top20企业_本地备份.csv")

if __name__ == "__main__":
    main()
