#!/usr/bin/env python3
"""
完整流程：获取全部企业数据 → 分析 → 写入钉钉表格
"""

import subprocess, json, time, re, sys
from datetime import datetime

BASE_ID = 'l6Pm2Db8D4Xdo9lYUGL3lXy48xLq0Ee4'
TABLE_ID = 'd7FEhge'
LIMIT = 20  # 保守值，避免截断
TARGET_BASE_ID = '7QG4Yx2JpLZb15rBFB5gNrGdJ9dEq3XD'  # OpenClaw测试表格

def fetch_all():
    print("="*60)
    print("第1步：全量获取企业数据（钉钉AI表格）")
    print("="*60)
    
    cursor = None
    page = 1
    total = 0
    all_data = []
    
    while page <= 100:
        cmd = ['mcporter', 'call', 'dingtalk-ai-table.query_records',
               f'baseId:{BASE_ID}', f'tableId:{TABLE_ID}', f'limit:{LIMIT}']
        if cursor:
            cmd.append(f'cursor:{cursor}')
        
        print(f'  第{page}页...', end=' ')
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if res.returncode != 0:
            print(f'失败: {res.stderr[:80]}')
            break
        
        try:
            data = json.loads(res.stdout)
        except Exception as e:
            print(f'JSON解析失败')
            break
        
        records = data.get('records', [])
        all_data.extend(records)
        total += len(records)
        print(f'获取{len(records)}条，累计{total}条')
        
        cursor = data.get('nextCursor')
        if not cursor or len(records) < LIMIT:
            break
        
        page += 1
        time.sleep(0.5)
    
    print(f'\n✅ 数据获取完成，共 {len(all_data)} 条记录')
    return all_data

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
    
    # 评分
    score = 50
    reasons = []
    
    # 距离 (30)
    if "真陈路" in addr:
        score += 30; reasons.append("极近")
    elif "宝山区" in addr:
        score += 20; reasons.append("宝山区")
    elif "普陀区" in addr:
        score += 10; reasons.append("普陀区")
    else: score += 5; reasons.append("远")
    
    # 规模 (25)
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
    
    # 行业 (25)
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
    
    # 联系 (10)
    if phone and phone != "-" and len(phone)>=7: score += 5; reasons.append("手机")
    if tel and tel != "-" and len(tel)>=5: score += 5; reasons.append("固话")
    
    # 状态 (10)
    if "存续" in status or "在业" in status:
        score += 10; reasons.append("正常")
    
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

def create_table(results):
    print("\n" + "="*60)
    print("第2步：在钉钉创建结果表格")
    print("="*60)
    
    table_name = f"橙发i运动_长包签约Top20_{datetime.now().strftime('%Y%m%d_%H%M')}"
    
    try:
        # 创建表格
        create_cmd = ['mcporter', 'call', 'dingtalk-ai-table.create_table',
                      f'baseId:{TARGET_BASE_ID}', f'name:{table_name}', 'viewType:Grid']
        res = subprocess.run(create_cmd, capture_output=True, text=True, timeout=60)
        
        if res.returncode != 0:
            print(f'❌ 创建表格失败: {res.stderr}')
            return None
        
        table_data = json.loads(res.stdout)
        table_id = table_data.get('tableId')
        print(f'✅ 表格创建成功: {table_name}')
        print(f'   Table ID: {table_id}')
        
        # 添加字段
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
        
        # 插入数据
        print(f'\n📥 插入 {len(results)} 条数据...')
        for idx, r in enumerate(results, 1):
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
                print(f'  ❌ 第{idx}条失败')
            elif idx % 10 == 0:
                print(f'  ✅ 已插入 {idx}/{len(results)} 条')
        
        print('\n✅ 数据插入完成！')
        print(f'\n🔗 钉钉表格链接:')
        print(f'https://alidocs.dingtalk.com/i/nodes/{TARGET_BASE_ID}')
        return table_id
        
    except Exception as e:
        print(f'❌ 出错: {e}')
        import traceback
        traceback.print_exc()
        return None

def main():
    start = datetime.now()
    
    # 第1步：获取全部数据
    records = fetch_all()
    if not records:
        print("\n❌ 未获取到数据，退出")
        return
    
    # 第2步：分析
    print("\n" + "="*60)
    print("第3步：分析企业签约潜力")
    print("="*60)
    
    results = []
    for rec in records:
        res = analyze(rec.get("cells", {}))
        if res:
            results.append(res)
    
    print(f'✅ 有效分析企业: {len(results)} 家')
    
    # 排序
    results.sort(key=lambda x: x["综合得分"], reverse=True)
    for i, r in enumerate(results, 1):
        r["排名"] = i
    
    top20 = results[:20]
    
    # 预览Top5
    print(f'\n🏆 Top 5 企业:')
    for i, r in enumerate(top20[:5], 1):
        print(f'{i}. {r["企业名称"]} (得分:{r["综合得分"]}) - {r["行业分类"]} - {r["联系方式"]}')
    
    # 第4步：创建钉钉表格
    table_id = create_table(top20)
    
    elapsed = datetime.now() - start
    print(f"\n⏱️  总耗时: {elapsed.total_seconds():.1f}秒")
    print(f"\n🎉 全部完成！")
    
    if table_id:
        print(f"\n📊 结果表格: https://alidocs.dingtalk.com/i/nodes/{TARGET_BASE_ID}")
        print(f"   表格名: 橙发i运动_长包签约Top20_*")
        print(f"   Table ID: {table_id}")

if __name__ == "__main__":
    main()
