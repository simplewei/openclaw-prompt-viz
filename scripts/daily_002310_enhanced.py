#!/usr/bin/env python3
"""
东方新能(002310)每日跟踪 - 增强版（多源冗余 + 优雅降级）
"""

import json
import os
import subprocess
import sys
import urllib.request
import urllib.error
import ssl
from datetime import datetime, timedelta
from pathlib import Path

# 设置路径
WORKSPACE = Path("/root/.openclaw/workspace")
SCRIPT_DIR = WORKSPACE / "scripts"

def run_health_check():
    """运行健康检查，返回可用数据源"""
    health_check_script = SCRIPT_DIR / "health_check_002310.py"

    if not health_check_script.exists():
        print("⚠️  未找到健康检查脚本，跳过预检查")
        return None

    try:
        result = subprocess.run(
            ["python3", str(health_check_script)],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data
        else:
            print(f"⚠️  健康检查失败：{result.stderr}")
            return None
    except Exception as e:
        print(f"⚠️  健康检查异常：{e}")
        return None

def fetch_with_tavily():
    """使用 Tavily Search 获取股票信息（无第三方依赖）"""
    try:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return {"status": "error", "message": "未配置 TAVILY_API_KEY 环境变量"}

        # 多维度搜索查询
        queries = [
            "东方新能 002310 最新消息 今日",
            "东方新能 002310 龙虎榜 资金流向",
            "东方新能 002310 公告 研报",
            "东方新能 002310 涨停 股价"
        ]

        all_results = []
        base_url = "https://api.tavily.com/search"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        context = ssl._create_unverified_context()

        for query in queries:
            try:
                payload = {
                    "query": query,
                    "max_results": 5,
                    "search_depth": "advanced",
                    "include_domains": ["eastmoney.com", "xueqiu.com", "cninfo.com.cn", "finance.sina.com.cn"]
                }
                data = json.dumps(payload).encode('utf-8')

                req = urllib.request.Request(
                    base_url,
                    data=data,
                    headers=headers,
                    method='POST'
                )

                with urllib.request.urlopen(req, context=context, timeout=15) as response:
                    if response.status == 200:
                        resp_data = json.loads(response.read().decode('utf-8'))
                        all_results.extend(resp_data.get("results", []))
                    else:
                        print(f"⚠️  Tavily 查询失败 [{query}]: HTTP {response.status}")

            except Exception as e:
                print(f"⚠️  Tavily 查询异常 [{query}]: {e}")
                continue

        if all_results:
            return {
                "status": "ok",
                "data": all_results,
                "source": "tavily"
            }
        else:
            return {"status": "error", "message": "Tavily 未返回任何结果"}

    except Exception as e:
        return {"status": "error", "message": f"Tavily 异常: {str(e)}"}

def fetch_with_browser_fallback():
    """使用 agent-browser 作为备用数据源"""
    # 这里可以调用 agent-browser 工具，但当前环境直接 exec
    # 返回一个占位，实际功能需要集成 agent-browser CLI
    return {
        "status": "partial",
        "data": [],
        "message": "agent-browser 备用方案（需手动配置 headed 模式）"
    }

def generate_report(data_primary, data_fallback, health_status):
    """生成结构化报告"""
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    # 根据主数据源状态生成中英文报告
    price_change = "数据暂缺"
    dragon_tiger = "数据暂缺"
    news_summary = []
    risk_factors = []
    recommendations = []

    if data_primary.get("status") == "ok":
        results = data_primary.get("data", [])

        # 提取价格和涨停信息
        for item in results:
            title = item.get("title", "")
            content = item.get("content", "")
            url = item.get("url", "")

            if "涨停" in title or "涨停" in content:
                price_change = "检测到涨停信息（详见来源）"

            if "龙虎榜" in title or "资金流向" in title:
                dragon_tiger = f"[龙虎榜/资金数据]({url})"

            if any(kw in title for kw in ["公告", "研报", "消息"]):
                news_summary.append(f"- [{title}]({url})")

            if any(kw in title for kw in ["风险", "减持", "解禁"]):
                risk_factors.append(f"- {title}")

        if not news_summary:
            news_summary = ["- 未检测到重要新闻（需手动查询巨潮资讯网）"]

    # 添加通用风险提示
    if not any("限售" in r for r in risk_factors):
        risk_factors.append("- 需关注限售股解禁情况（如之前提及的7亿股）")
    if not any("亏损" in r for r in risk_factors):
        risk_factors.append("- 公司持续亏损，基本面待改善")

    # 基于涨停态势给出建议
    if "涨停" in price_change:
        recommendations = [
            "🔴 短线：已连板，谨慎追高，关注开板信号",
            "🟡 中线：如回落至3.0-3.2元区间，可分批建仓",
            "🟢 长线：需观察资产收购后的业绩转化情况"
        ]
    else:
        recommendations = [
            "📊 当前无明确操作信号，建议持续观察",
            "📈 关注重大资产收购进展（海城锐海+电投瑞享）",
            "⚠️  注意业绩亏损和限售解禁风险"
        ]

    # 组装报告
    report = f"""# 东方新能(002310)每日跟踪报告

**报告日期**: {today} | **前一交易日**: {yesterday}
**数据源**: {'✅ Tavily Search' if data_primary.get('status') == 'ok' else '⚠️ 数据受限（部分来源失败）'}

---

## 📈 核心数据摘要

| 指标 | 状态 | 备注 |
|------|------|------|
| 股价表现 | {price_change} | 前一交易日收盘价待确认 |
| 龙虎榜/资金流向 | {dragon_tiger if dragon_tiger != '数据暂缺' else '❌ 数据获取失败'} | 建议查询东方财富/雪球 |
| 重大新闻 | {'✅ 已提取' if news_summary[0] != '- 未检测到重要新闻（需手动查询巨潮资讯网）' else '❌ 未检测到'} | 见下方列表 |

---

## 📰 重要新闻与公告

{chr(10).join(news_summary[:5]) if news_summary else '- 暂无新信息'}

---

## 💰 资金动向

{dragon_tiger if dragon_tiger != '数据暂缺' else '数据暂缺，请手动查询东方财富/雪球资金流向页面'}

---

## ⚠️  风险提示

{chr(10).join(risk_factors)}

---

## 💡 操作建议

{chr(10).join(recommendations)}

---

## 🔧 技术状态

- **健康检查**: {health_status.get('health_score', 'N/A') if health_status else '未执行'}
- **数据源详情**: Tavily Search {'✅ 正常' if data_primary.get('status') == 'ok' else '❌ 不可用'}
- **备用方案**: {data_fallback.get('message', '未启用') if data_fallback and data_fallback.get('status') != 'ok' else '未触发'}

---

## 📋 手动查询建议

如果自动数据不完整，请手动访问：

- **东方财富**: https://quote.eastmoney.com/sz002310.html
- **雪球**: https://xueqiu.com/S/002310
- **巨潮资讯**: http://www.cninfo.com.cn （搜索 002310）
- **新浪财经**: https://finance.sina.com.cn/realstock/company/sh002310

---

*报告生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
*自动任务，如有问题请人工复核*
"""

    return report

def publish_to_dingtalk(report_text):
    """发布报告到钉钉文档（使用 mcporter 工具）"""
    # 这里需要集成 mcporter 工具来创建钉钉文档
    # 暂时保存为本地文件，并输出提示
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"daily_report_002310_{today}.txt"
    filepath = WORKSPACE / filename

    filepath.write_text(report_text, encoding="utf-8")

    print(f"✅ 报告已保存到: {filepath}")
    print("📌 注意：需要手动发布到钉钉文档或配置 mcporter 自动化")
    return str(filepath)

def main():
    print("=" * 60)
    print("📊 东方新能(002310) 每日跟踪 - 增强版")
    print("=" * 60)

    # 步骤 1: 健康检查
    print("\n🔍 步骤 1: 数据源健康检查...")
    health_status = run_health_check()
    if health_status:
        print(f"  健康度: {health_status['health_score']}")
        if health_status['health_score'] < '80.0%':
            print("  ⚠️  警告：部分数据源异常，将尝试备用方案")
    else:
        print("  ⏩ 跳过健康检查（脚本不可用）")

    # 步骤 2: 主数据源（Tavily）
    print("\n📡 步骤 2: 主数据源采集 (Tavily Search)...")
    data_primary = fetch_with_tavily()
    if data_primary.get("status") == "ok":
        print(f"  ✅ 成功获取 {len(data_primary['data'])} 条结果")
    else:
        print(f"  ❌ 主数据源失败: {data_primary.get('message', '未知错误')}")

    # 步骤 3: 备用数据源（如果主数据源失败）
    data_fallback = None
    if data_primary.get("status") != "ok":
        print("\n🔧 步骤 3: 启用备用数据源 (agent-browser)...")
        data_fallback = fetch_with_browser_fallback()
        print(f"  ⚠️  备用方案状态: {data_fallback['status']}")
    else:
        print("\n✅ 主数据源成功，无需备用方案")

    # 步骤 4: 生成报告（优雅降级）
    print("\n📝 步骤 4: 生成报告（优雅降级机制）...")
    report = generate_report(data_primary, data_fallback, health_status)

    # 步骤 5: 发布
    print("\n🚀 步骤 5: 发布报告...")
    publish_to_dingtalk(report)

    print("\n" + "=" * 60)
    print("✅ 任务完成")
    print("=" * 60)

    return 0

if __name__ == "__main__":
    sys.exit(main())
