#!/usr/bin/env python3
"""
国内AI媒体动态监控 - Optimized v3
主数据源: Tavily Search（多site查询）
输出: 领域分布 + 核心要闻 + 关键洞察
"""

import json, os, subprocess, sys, urllib.request, ssl
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

WORKSPACE = Path("/root/.openclaw/workspace")

def quick_health_check():
    """快速健康检查（可选）"""
    try:
        # 快速测试 Tavily API 连通性
        test_url = "https://api.tavily.com/search"
        payload = {"query": "test", "max_results": 1}
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('TAVILY_API_KEY', '')}"
        }
        req = urllib.request.Request(
            test_url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(req, context=ctx, timeout=8) as r:
            return r.status == 200
    except:
        return False

def fetch_news():
    """单次 Tavily 查询获取国内AI媒体新闻"""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        print("❌ 未配置 TAVILY_API_KEY 环境变量")
        return {"status": "error", "data": []}

    # 覆盖主流科技AI媒体
    query = """国内AI最新进展 2025
      36氪 虎嗅 量子位 机器之心 雷锋网 钛媒体 界面 品玩 极客公园
      site:36kr.com OR site:huxiu.com OR site:qbitai.com OR site:jiqizhixin.com
      OR site:leiphone.com OR site:tmtpost.com OR site:jiemian.com"""

    try:
        payload = {
            "query": query,
            "max_results": 20,           # 增加结果数
            "search_depth": "basic",
            "time_range": "week",
            "include_domains": [
                "36kr.com", "huxiu.com", "qbitai.com", "jiqizhixin.com",
                "leiphone.com", "tmtpost.com", "jiemian.com", "geekpark.net", "ifanr.com"
            ]
        }
        req = urllib.request.Request(
            "https://api.tavily.com/search",
            data=json.dumps(payload).encode('utf-8'),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            method='POST'
        )
        ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(req, context=ctx, timeout=22) as r:
            if r.status == 200:
                resp = json.loads(r.read().decode('utf-8'))
                results = resp.get("results", [])
                print(f"✅ 获取到 {len(results)} 条新闻")
                return {"status": "ok", "data": results}
            else:
                print(f"⚠️  Tavily HTTP: {r.status}")
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    return {"status": "error", "data": []}

def extract_source(url):
    """从URL提取媒体名称"""
    try:
        domain = urlparse(url).netloc.lower()
        # 简化域名
        mapping = {
            "36kr.com": "36氪",
            "huxiu.com": "虎嗅",
            "qbitai.com": "量子位",
            "jiqizhixin.com": "机器之心",
            "leiphone.com": "雷锋网",
            "tmtpost.com": "钛媒体",
            "jiemian.com": "界面新闻",
            "geekpark.net": "极客公园",
            "ifanr.com": "爱范儿",
            "pintu360.com": "品玩",
            "infoq.cn": "InfoQ",
            "csdn.net": "CSDN",
            "oschina.net": "开源中国"
        }
        for d, name in mapping.items():
            if d in domain:
                return name
        return domain
    except:
        return "未知"

def categorize(results):
    """新闻分类"""
    cats = {
        "大模型进展": [], "商业竞争": [], "融资动态": [],
        "应用落地": [], "技术趋势": [], "政策法规": [], "其他": []
    }
    kw = {
        "大模型进展": ["大模型", "LLM", "GPT", "Claude", "千问", "文心", "通义", "Kimi", "DeepSeek", "GLM", "Baichuan", "Yi"],
        "商业竞争": ["竞争", "之战", "市场份额", "用户", "百团", "龙头", "领先", "追赶"],
        "融资动态": ["融资", "投资", "收购", "IPO", "估值", "亿元", "美元", "轮"],
        "应用落地": ["落地", "应用", "场景", "解决方案", "产品", "toB", "toC", "Agent", "智能体"],
        "技术趋势": ["技术", "架构", "算法", "推理", "训练", "MoE", "多模态", "Agent", "强化学习"],
        "政策法规": ["政策", "法规", "监管", "备案", "安全", "合规", "审查"]
    }
    for it in results:
        text = (it.get("title", "") + " " + it.get("content", "")).lower()
        hit = False
        for cat, keys in kw.items():
            if any(k.lower() in text for k in keys):
                cats[cat].append(it)
                hit = True
                break
        if not hit:
            cats["其他"].append(it)
    return cats

def generate_report(health_ok, data, cats):
    today = datetime.now().strftime("%Y-%m-%d")
    total = len(data)
    counts = {k: len(v) for k, v in cats.items() if v}

    # Top 10 新闻
    top_items = []
    for cat, items in cats.items():
        for it in items[:2]:
            top_items.append({
                "title": it.get("title", "")[:80],
                "url": it.get("url", ""),
                "source": extract_source(it.get("url", "")),
                "cat": cat
            })

    # 关键洞察
    insights = []
    if counts.get("大模型进展", 0) >= 3:
        insights.append("• 大模型领域本周活跃，多家厂商发布新版本或开源成果")
    if counts.get("融资动态", 0) >= 2:
        insights.append("• AI赛道持续获得资本关注，关注头部融资事件")
    if counts.get("应用落地", 0) >= 3:
        insights.append("• AI应用落地案例增多，垂直行业解决方案成焦点")
    if counts.get("商业竞争", 0) >= 2:
        insights.append("• 市场竞争加剧，头部效应进一步显现")
    if not insights:
        insights.append("• 本周AI领域新闻分布相对均衡，无明显热点")

    # 生成报告
    report = f"""# 国内AI媒体动态简报

**日期**: {today} | **新闻总数**: {total} | **数据源**: Tavily Search
**监测媒体**: 36氪、虎嗅、量子位、机器之心、雷锋网、钛媒体等14家

## 📊 领域分布
{chr(10).join([f"- {k}: {v} 条" for k, v in counts.items()])}

## 🔥 核心要闻（Top {len(top_items[:10])}）
{chr(10).join([f"{i+1}. [{t['title']}]({t['url']})  \\n   **来源**: {t['source']} | **领域**: {t['cat']}" for i, t in enumerate(top_items[:10])])}

## 💡 关键洞察
{chr(10).join(insights)}

## 📈 媒体覆盖
{health_note(health_ok)}

## 📚 数据源说明
本报告自动采集自国内主流科技媒体（36氪、虎嗅、量子位、机器之心等），
通过 Tavily Search 聚合过滤，重点关注：
- AI大模型技术与产品进展
- 商业化落地与市场竞争
- 融资与政策动态

*生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
*自动任务，仅供参考，请以官方原文为准*
"""
    return report

def health_note(ok):
    if ok:
        return "✅ Tavily API 状态正常"
    else:
        return "⚠️  API 连通性异常，数据可能不完整"

def main():
    print("="*60)
    print("🤖 国内AI媒体动态监控")
    print("="*60)

    print("🔍 检查 API 连通性...")
    health_ok = quick_health_check()
    print(f"  {'✅' if health_ok else '⚠️ '} Tavily API {'正常' if health_ok else '异常'}")

    print("\n📡 采集新闻...")
    news = fetch_news()

    if news["status"] != "ok":
        print(f"❌ 任务终止: {news.get('message', '未知错误')}")
        sys.exit(1)

    print("📊 分类统计...")
    cats = categorize(news["data"])
    for k, v in cats.items():
        if v:
            print(f"  {k}: {len(v)} 条")

    print("📝 生成简报...")
    report = generate_report(health_ok, news["data"], cats)

    # 保存文件
    fname = f"ai_media_report_{today}.txt".replace("today", datetime.now().strftime("%Y-%m-%d"))
    fpath = WORKSPACE / fname
    fpath.write_text(report, encoding="utf-8")

    print(f"\n✅ 已保存: {fpath}")
    print("="*60 + "\n")
    print(report)
    print("\n" + "="*60)

if __name__ == "__main__":
    today = datetime.now().strftime("%Y-%m-%d")
    main()
