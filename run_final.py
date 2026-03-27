#!/usr/bin/env python3
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

print("开始分析...")
results = []
for rec in records:
    res = analyze(rec.get("cells", {}))
    if res:
        results.append(res)

results.sort(key=lambda x: x["综合得分"], reverse=True)
for i, r in enumerate(results, 1):
    r["排名"] = i
top20 = results[:20]

print(f'\n✅ 分析完成，共 {len(results)} 家有效企业')
print(f'🏆 Top 5:')
for i, r in enumerate(top20[:5], 1):
    print(f'{i}. {r["企业名称"]} (得分:{r["综合得分"]}) - {r["行业分类"]}')

# 创建钉钉表格
TARGET_BASE_ID = '7QG4Yx2JpLZb15rBFB5gNrGdJ9dEq3XD'
table_name = f"橙发i运动_长包签约Top20_{datetime.now().strftime('%Y%m%d_%H%M')}"

print(f'\n📊 创建钉钉表格: {table_name}')
create_cmd = ['mcporter', 'call', 'dingtalk-ai-table.create_table',
              f'baseId:{TARGET_BASE_ID}', f'name:{table_name}', 'viewType:Grid']
res = subprocess.run(create_cmd, capture_output=True, text=True)
if res.returncode != 0:
    print(f'❌ 创建表格失败: {res.stderr}')
    exit(1)
table_id = json.loads(res.stdout)['tableId']
print(f'✅ 表格创建成功，Table ID: {table_id}')

# 添加字段
fields = [
    ("排名", "Number", {"precision": 0}),
    ("企业名称", "SingleText", None),
    ("综合得分", "Number", {"precision": 0}),
    ("行业分类", "SingleText", None),
    ("参保人数", "SingleText", None),
    ("注册资本", "SingleText", None),
    ("联系方式", "SingleText", None),
    ("注册地址", "SingleText", None),
    ("企查查链接", "Url", None),
    ("评分理由", "SingleText", None),
    ("登记状态", "SingleText", None),
    ("主营业务", "SingleText", None)
]
for name, typ, prop in fields:
    cmd = ['mcporter', 'call', 'dingtalk-ai-table.add_field',
           f'baseId:{TARGET_BASE_ID}', f'tableId:{table_id}',
           f'fieldName:{name}', f'type:{typ}']
    if prop:
        cmd.append(f'property:{json.dumps(prop)}')
    subprocess.run(cmd, capture_output=True, text=True)
print('✅ 字段添加完成')

time.sleep(1)

# 插入数据
print(f'📥 插入 {len(top20)} 条数据...')
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
    subprocess.run(cmd, capture_output=True, text=True)
    if idx % 5 == 0:
        print(f'  已插入 {idx}/{len(top20)} 条')

print('\n✅ 全部完成！')
print(f'\n🔗 钉钉表格链接:')
print(f'https://alidocs.dingtalk.com/i/nodes/{TARGET_BASE_ID}')
print(f'\n📊 统计:')
print(f'   总企业: {len(results)} | 存续: {sum(1 for r in results if "存续" in r["登记状态"])}')
print(f'   Top20最低分: {top20[-1]["综合得分"]}')
print(f'   ≥80分: {sum(1 for r in results if r["综合得分"]>=80)}家')
