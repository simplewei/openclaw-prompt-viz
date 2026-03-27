#!/usr/bin/env python3
"""
橙发i运动周边企业长包签约潜力分析
从钉钉AI表格读取的数据 → 筛选高成功率企业 → 生成文档
"""

import json
import csv
from datetime import datetime

# 假设我们已经有了数据（从mcporter输出）
# 这里我将基于已读取的数据结构生成分析

print("正在分析企业长包签约潜力...")

# 字段映射（基于MCP返回的字段ID）
FIELD_MAP = {
    "企业名称": "5b19b1v9xqysej7yjqqpy",
    "登记状态": "l32mmkocgkcbqxkr8obn0",
    "法定代表人": "h4b4emrhkrh694xmgoioy",
    "注册资本": "e461igbt74giugxrbhfxq",
    "成立日期": "yu3elym542ofhmwyg6hng",
    "统一社会信用代码": "3z7wgg1doejyzxhukzd0c",
    "注册地址": "33d9l7536htt81azudzub",
    "有效手机号": "cq2f300ljch1eba3burtq",
    "更多电话": "xm5fbhn6a2urtv4izyqaq",
    "企业类型": "1hlustelz6gpjqbtplymt",
    "参保人数": "o4mczvu85lh9q6e7o79d0",
    "国标行业门类": "20xnob8pa05isywy6gws0",
    "国标行业大类": "a4zw60h64e8nk6an2dqcb",
    "国标行业中类": "uzlvj4gif06t70sv5byu0",
    "国标行业小类": "uqhildsotuewm4b0yin7q",
    "企查查行业大类": "u4mupi8hd108oo56e9qc1",
    "企业规模": "bp6tb6e0q3k2imyikqh9i",
    "通信地址": "rp9fl470heeh2xeal160a",
    "通信地址邮编": "v1toxm0l9ntlx2p2tsbum",
    "企业简介": "4efciztxejuk0ns4xelv0",
    "经营范围": "5r8nj68f1k71a1rhmatuc"
}

# 分析逻辑
def parse_employee_count(emp_count_str):
    """解析参保人数"""
    if not emp_count_str or emp_count_str == "-":
        return 0
    try:
        return int(emp_count_str)
    except:
        return 0

def parse_capital(capital_str):
    """解析注册资本（万元）"""
    if not capital_str:
        return 0
    # 提取数字部分
    import re
    match = re.search(r'(\d+(?:\.\d+)?)', capital_str.replace(',', ''))
    if match:
        return float(match.group(1))
    return 0

def get_industry_category(industry_code, industry_name):
    """判断行业大类"""
    # 根据行业名称关键词判断
    keywords = {
        "互联网/IT": ["互联网", "软件", "信息技术", "计算机", "通信", "电信"],
        "金融": ["金融", "银行", "保险", "证券", "投资", "基金"],
        "专业服务": ["咨询", "律师", "会计", "人力资源", "培训", "设计"],
        "制造业": ["制造", "生产", "加工", "设备", "机械", "电子"],
        "贸易/零售": ["批发", "零售", "贸易", "商贸", "销售"],
        "体育/文化": ["体育", "文化", "娱乐", "传媒", "广告"],
        "教育": ["教育", "培训", "学校", "教学"],
        "医疗": ["医疗", "健康", "医药", "器械"]
    }
    
    text = (industry_code + " " + industry_name).lower() if industry_name else ""
    for category, words in keywords.items():
        for word in words:
            if word in text:
                return category
    return "其他"

def calculate_success_score(record):
    """
    计算长包签约成功率评分（0-100分）
    因素：
    - 距离（30分）：地址包含"真陈路"、"园新路"、"长江南路"等近的加分
    - 企业规模（25分）：参保人数>5人、注册资本>50万
    - 行业属性（25分）：IT/金融/专业服务优先
    - 联系有效性（10分）：有手机号/电话
    - 状态（10分）：存续企业加分
    """
    score = 50  # 基础分
    reasons = []
    
    cells = record.get("cells", {})
    
    # 1. 距离分析（30分）
    address = cells.get("33d9l7536htt81azudzub", {}).get("text", "")
    postal_code = cells.get("v1toxm0l9ntlx2p2tsbum", "")
    
    # 真陈路719号/1000号周边（邮编2009xx）附近企业
    close_keywords = ["真陈路", "园新路", "长江南路", "200442", "200444", "200083", "200072"]
    distance_score = 0
    if any(kw in (address + postal_code) for kw in close_keywords):
        distance_score = 30
        score += 30
        reasons.append("距离橙发中心较近")
    elif address and "宝山区" in address:
        distance_score = 20
        score += 20
        reasons.append("位于宝山区（中等距离）")
    else:
        score += 10
        reasons.append("距离较远")
    
    # 2. 企业规模（25分）
    emp_count = parse_employee_count(cells.get("o4mczvu85lh9q6e7o79d0", {}).get("text", ""))
    capital = parse_capital(cells.get("e461igbt74giugxrbhfxq", {}).get("text", ""))
    
    size_score = 0
    if emp_count >= 50:
        size_score = 25
        score += 25
        reasons.append(f"参保人数{emp_count}人（大型）")
    elif emp_count >= 20:
        size_score = 20
        score += 20
        reasons.append(f"参保人数{emp_count}人（中型）")
    elif emp_count >= 5:
        size_score = 15
        score += 15
        reasons.append(f"参保人数{emp_count}人（小型）")
    elif capital >= 500:
        size_score = 10
        score += 10
        reasons.append(f"注册资本{capital}万元（资本充足）")
    else:
        score += 5
        reasons.append("规模较小")
    
    # 3. 行业属性（25分）
    industry_name = cells.get("u4mupi8hd108oo56e9qc1", {}).get("text", "")
    industry_code = cells.get("20xnob8pa05isywy6gws0", {}).get("text", "")
    industry_category = get_industry_category(industry_code, industry_name)
    
    industry_priority = {
        "互联网/IT": 25,
        "金融": 25,
        "专业服务": 20,
        "制造业": 15,
        "体育/文化": 15,
        "教育": 15,
        "医疗": 10,
        "其他": 5
    }
    industry_score = industry_priority.get(industry_category, 5)
    score += industry_score
    reasons.append(f"行业:{industry_category}")
    
    # 4. 联系有效性（10分）
    phone = cells.get("cq2f300ljch1eba3burtq", {}).get("text", "") or ""
    tel = cells.get("xm5fbhn6a2urtv4izyqaq", {}).get("text", "") or ""
    
    contact_score = 0
    if phone and phone != "-" and phone != "无":
        contact_score += 5
        score += 5
        reasons.append("有手机号")
    if tel and tel != "-" and tel != "无":
        contact_score += 5
        score += 5
        reasons.append("有固话")
    
    # 5. 企业状态（10分）
    status = cells.get("l32mmkocgkcbqxkr8obn0", {}).get("text", "")
    if "存续" in status:
        score += 10
        reasons.append("企业存续")
    elif "在业" in status:
        score += 8
        reasons.append("企业在业")
    else:
        reasons.append(f"状态:{status}")
    
    return {
        "score": min(score, 100),
        "reasons": reasons,
        "distance_score": distance_score,
        "size_score": size_score,
        "industry_score": industry_score,
        "contact_score": contact_score,
        "status": status,
        "industry_category": industry_category
    }

# 主处理流程
def main():
    print("开始处理企业数据...")
    
    # 由于数据已经在查询结果中，我需要解析它
    # 但实际我需要先获取数据
    print("请使用以下方式之一：")
    print("1. 将mcporter查询结果保存为JSON文件")
    print("2. 或直接粘贴查询结果到脚本中")
    
if __name__ == "__main__":
    main()
