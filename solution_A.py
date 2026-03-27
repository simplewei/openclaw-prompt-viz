#!/usr/bin/env python3
"""
方案A：获取企业数据 → 分析 → 写入钉钉多维表格
"""

import subprocess, json, time, sys, re
from datetime import datetime

BASE_ID = "l6Pm2Db8D4Xdo9lYUGL3lXy48xLq0Ee4"
TABLE_ID = "d7FEhge"
TARGET_BASE_ID = "7QG4Yx2JpLZb15rBFB5gNrGdJ9dEq3XD"  # OpenClaw测试表格
LIMIT = 20  # 每页条数（保守）

def query_records(cursor=None):
    """调用mcporter查询"""
    cmd = [
        "mcporter", "call", "dingtalk-ai-table.query_records",
        f"baseId:{BASE_ID}",
        f"tableId:{TABLE_ID}",
        f"limit:{LIMIT}"
    ]
    if cursor:
        cmd.append(f"cursor:{cursor}")
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise Exception(f"mcporter错误: {result.stderr}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise Exception(f"JSON解析失败: {e}, 输出长度={len(result.stdout)}")

def fetch_all():
    """分页获取所有企业"""
    all_records = []
    cursor = None
    page = 1
    
    print("开始获取企业数据（分页，每页20条）...")
    
    while page <= 50:  # 最多50页（1000条）
        try:
            print(f"  第{page}页...", end=" ")
            data = query_records(cursor)
            records = data.get("records", [])
            all_records.extend(records)
            print(f"获取{len(records)}条，累计{len(all_records)}条")
            
            cursor = data.get("nextCursor")
            if not cursor or len(records) < LIMIT:
                break
            
            page += 1
            time.sleep(0.3)
        except Exception as e:
            print(f"失败: {e}")
            break
    
    return all_records

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
    try:
        emp = int(emp_raw) if emp_raw and emp_raw != "-" else 0
    except:
        emp = 0
    cap = 0
    if capital:
        m = re.search(r'(\d+(?:\.\d+)?)', capital.replace(',', ''))
        if m: cap = float(m.group(1))
    
    if emp >= 50 or cap >= 500:
        score += 25; reasons.append(f"大型({emp}人/{cap:.0f}万)")
    elif emp >= 20 or cap >= 200:
        score += 20; reasons.append("中型")
    elif emp >= 5 or cap >= 50:
        score += 15; reasons.append("小型")
    else:
        score += 5; reasons.append("微型")
    
    # 行业
    ind_low = industry.lower()
    if any(k in ind_low for k in ["软件","信息技术","互联网","科技","通信","网络"]):
        ind_s, ind_cat = 25, "IT/互联网"
    elif any(k in ind_low for k in ["金融","银行","保险","证券","投资"]):
        ind_s, ind_cat = 25, "金融"
    elif any(k in ind_low for k in ["咨询","人力","律师","会计","设计","广告"]):
        ind_s, ind_cat = 20, "专业服务"
    elif any(k in ind_low for k in ["体育","文化","娱乐","传媒","健身"]):
        ind_s, ind_cat = 20, "体育/文化"
    elif any(k in ind_low for k in ["制造","机械","电子","设备"]):
        ind_s, ind_cat = 15, "制造业"
    elif any(k in ind_low for k in ["教育","培训"]):
        ind_s, ind_cat = 15, "教育"
    else:
        ind_s, ind_cat = 5, "其他"
    score += ind_s
    reasons.append(f"行业:{ind_cat}")
    
    # 联系方式
    if phone and phone != "-" and len(phone)>=7: score += 5; reasons.append("手机")
    if tel and tel != "-" and len(tel)>=5: score += 5; reasons.append("固话")
    
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
        "行业分类": ind_cat,
        "登记状态": status,
        "评分理由": " | ".join(reasons)
    }

def create_table_and_insert(results):
    """在目标Base中创建表格并插入数据"""
    print("\n" + "="*60)
    print(f"在目标Base创建表格: {TARGET_BASE_ID}")
    print("="*60)
    
    table_name = f"橙发i运动_长包签约潜力分析_{datetime.now().strftime('%Y%m%d_%H%M')}"
    
    # 创建表格
    create_cmd = [
        "mcporter", "call", "dingtalk-ai-table.create_table",
        f"baseId:{TARGET_BASE_ID}",
        f"name:{table_name}",
        "viewType:Grid"
    ]
    res = subprocess.run(create_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"❌ 创建表格失败: {res.stderr}")
        return None
    
    table_id = json.loads(res.stdout).get("tableId")
    print(f"✅ 表格创建成功: {table_name} (ID: {table_id})")
    
    # 添加字段
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
    
    print("\n添加字段:")
    for f in fields:
        cmd = [
            "mcporter", "call", "dingtalk-ai-table.add_field",
            f"baseId:{TARGET_BASE_ID}",
            f"tableId:{table_id}",
            f"fieldName:{f['fieldName']}",
            f"type:{f['type']}"
        ]
        if 'property' in f:
            cmd.append(f"property:{json.dumps(f['property'])}")
        
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0:
            print(f"  ✅ {f['fieldName']}")
        else:
            print(f"  ⚠️  {f['fieldName']} - 可能已存在")
    
    time.sleep(1)
    
    # 插入数据（每5条显示一次进度）
    print(f"\n插入数据（共{len(results)}条）...")
    for i, r in enumerate(results, 1):
        rec = json.dumps(r, ensure_ascii=False)
        cmd = [
            "mcporter", "call", "dingtalk-ai-table.add_record",
            f"baseId:{TARGET_BASE_ID}",
            f"tableId:{table_id}",
            f"recordData:{rec}"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"  ❌ 第{i}条失败: {res.stderr[:80]}")
        elif i % 5 == 0:
            print(f"  ✅ 已插入 {i}/{len(results)} 条")
    
    print(f"\n✅ 数据插入完成！")
    print(f"\n🔗 钉钉多维表格链接:")
    print(f"https://alidocs.dingtalk.com/i/nodes/{TARGET_BASE_ID}")
    
    return {"base_id": TARGET_BASE_ID, "table_id": table_id, "table_name": table_name}

def main():
    start = datetime.now()
    
    print(f"方案A: 读取钉钉多维表格 → 分析 → 写入钉钉多维表格")
    print(f"源表格: {BASE_ID}/{TABLE_ID}")
    print(f"目标Base: {TARGET_BASE_ID}\n")
    
    # 1. 获取数据
    records = fetch_all()
    print(f"\n✅ 获取到 {len(records)} 条源记录")
    
    if not records:
        print("❌ 无数据，退出")
        return
    
    # 2. 分析
    results = []
    for rec in records:
        res = analyze(rec.get("cells", {}))
        if res:
            results.append(res)
    
    print(f"✅ 分析完成，有效企业: {len(results)} 家")
    
    # 3. 排序取Top20
    results.sort(key=lambda x: x["综合得分"], reverse=True)
    for i, r in enumerate(results, 1):
        r["排名"] = i
    
    top20 = results[:20]
    
    print(f"\n🏆 Top 5 预览:")
    for i, r in enumerate(top20[:5], 1):
        print(f"{i}. {r['企业名称']} (得分:{r['综合得分']}) - {r['行业分类']} - {r['联系方式']}")
    
    # 4. 创建钉钉表格
    info = create_table_and_insert(top20)
    
    elapsed = datetime.now() - start
    print(f"\n⏱️  总耗时: {elapsed.total_seconds():.1f}秒")
    print(f"\n🎉 方案A执行完毕！")
    
    if info:
        print(f"\n📊 结果表格: {info['table_name']}")
        url = info.get('url', f"https://alidocs.dingtalk.com/i/nodes/{info['base_id']}")
        print(f"🔗 访问链接: {url}")

if __name__ == "__main__":
    main()
