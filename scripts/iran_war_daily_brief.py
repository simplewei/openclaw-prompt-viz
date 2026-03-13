#!/usr/bin/env python3
"""
每日美伊战争新闻简报生成器
每天9点自动运行，抓取最新新闻并发送到钉钉群
"""

import json
import subprocess
import os
import sys
from datetime import datetime

# News search queries
QUERIES = [
    "US Iran war latest news",
    "Iran conflict news today",
    "Middle East tensions Iran US",
    "Iran US military news",
    "美伊战争 最新消息",
    "伊朗 美国 冲突 新闻"
]

def log(msg):
    """Simple logging to stderr"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}", file=sys.stderr)

def search_via_tavily():
    """使用 tavily-search 技能搜索新闻"""
    news_items = []

    tavily_key = os.environ.get("TAVILY_API_KEY") or subprocess.getoutput("grep -i TAVILY_API_KEY ~/.openclaw/.env 2>/dev/null | cut -d= -f2").strip()

    if not tavily_key:
        log("⚠️ 未检测到 TAVILY_API_KEY，跳过 Tavily 搜索")
        return []

    log(f"✓ 检测到 Tavily API key，开始搜索...")

    for query in QUERIES[:2]:
        try:
            result = subprocess.run(
                [
                    "python3",
                    "/root/.openclaw/workspace/skills/openclaw-tavily-search/scripts/tavily_search.py",
                    "--query", query,
                    "--max-results", "5",
                    "--format", "brave"
                ],
                capture_output=True, text=True, timeout=60
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                for item in data.get("results", []):
                    news_items.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "snippet": item.get("snippet", "")[:200],
                        "source": "Tavily",
                        "query": query
                    })
            else:
                log(f"Tavily 搜索失败 ({query}): {result.stderr}")

        except Exception as e:
            log(f"Tavily 搜索异常 ({query}): {e}")

    return news_items

def search_via_browser():
    """使用 agent-browser 访问新闻网站（备用方案）"""
    news_items = []

    log("尝试通过浏览器访问新闻网站...")

    try:
        # 访问 Google News
        search_url = "https://news.google.com/search?q=iran%20us%20war&hl=en-US&gl=US"
        subprocess.run(
            ["agent-browser", "open", search_url],
            capture_output=True, timeout=30
        )
        subprocess.run(["sleep", "3"], timeout=5)

        result = subprocess.run(
            ["agent-browser", "eval", "document.body.innerText"],
            capture_output=True, text=True, timeout=30
        )

        if result.returncode == 0:
            text = result.stdout
            lines = text.split('\n')

            for line in lines:
                line = line.strip()
                if len(line) > 30 and len(line) < 150:
                    if any(keyword in line.lower() for keyword in ['iran', 'us', 'war', 'military', 'attack', 'iran', '美国', '伊朗', '战争']):
                        news_items.append({
                            "title": line[:100],
                            "url": search_url,
                            "snippet": "",
                            "source": "Google News (text)"
                        })
                        if len(news_items) >= 10:
                            break

    except Exception as e:
        log(f"浏览器访问失败: {e}")

    # 访问路透社
    try:
        log("访问 Reuters 中东新闻...")
        subprocess.run(["agent-browser", "open", "https://www.reuters.com/world/middle-east/"], timeout=30)
        subprocess.run(["sleep", "3"], timeout=5)

        result = subprocess.run(
            ["agent-browser", "eval", "document.body.innerText"],
            capture_output=True, text=True, timeout=30
        )

        if result.returncode == 0:
            text = result.stdout
            lines = text.split('\n')

            for line in lines:
                line = line.strip()
                if len(line) > 30 and len(line) < 150:
                    if any(keyword in line.lower() for keyword in ['iran', 'us', 'war', 'military', 'israel', 'houthi']):
                        news_items.append({
                            "title": line[:100],
                            "url": "https://www.reuters.com/world/middle-east/",
                            "snippet": "",
                            "source": "Reuters"
                        })
                        if len(news_items) >= 15:
                            break

    except Exception as e:
        log(f"Reuters 访问失败: {e}")

    return news_items

def summarize_news(news_items):
    """生成中英文摘要"""

    if not news_items:
        date_str = datetime.now().strftime('%Y年%m月%d日')
        date_en = datetime.now().strftime('%Y-%m-%d')
        return {
            "zh": f"📅 {date_str}\n📰 美伊战争每日简报\n\n今日无重大进展。",
            "en": f"📅 {date_en}\n📰 US-Iran War Daily Brief\n\nNo significant developments reported today."
        }

    # 去重
    seen = set()
    unique_news = []
    for item in news_items:
        title_key = item['title'][:60].lower()
        if title_key not in seen:
            seen.add(title_key)
            unique_news.append(item)

    date_str = datetime.now().strftime('%Y年%m月%d日')
    date_en = datetime.now().strftime('%Y-%m-%d')

    # 中文摘要
    zh_lines = [
        f"📅 {date_str}",
        "📰 美伊战争每日简报",
        f"📊 新闻来源: {len(unique_news)} 条最新报道",
        ""
    ]

    for i, item in enumerate(unique_news[:10], 1):
        title = item['title'][:120]
        snippet = item.get('snippet', '')[:200]
        source = item.get('source', 'Unknown')

        zh_lines.append(f"{i}. **{title}**")
        if snippet and len(snippet) > 10:
            zh_lines.append(f"   {snippet}")
        zh_lines.append(f"   🔗 [{source}]({item.get('url', '#')})")
        zh_lines.append("")

    zh_summary = "\n".join(zh_lines)

    # 英文摘要
    en_lines = [
        f"📅 {date_en}",
        "📰 US-Iran War Daily Brief",
        f"📊 Sources: {len(unique_news)} latest reports",
        ""
    ]

    for i, item in enumerate(unique_news[:10], 1):
        title = item['title'][:120]
        snippet = item.get('snippet', '')[:200]
        source = item.get('source', 'Unknown')

        en_lines.append(f"{i}. **{title}**")
        if snippet and len(snippet) > 10:
            en_lines.append(f"   {snippet}")
        en_lines.append(f"   🔗 [{source}]({item.get('url', '#')})")
        en_lines.append("")

    en_summary = "\n".join(en_lines)

    return {"zh": zh_summary, "en": en_summary}

def send_to_dingtalk_via_agent(zh_text, en_text):
    """使用 openclaw agent 命令发送消息到钉钉群"""

    separator = "\n\n" + "="*60 + "\n\n"
    full_message = f"{zh_text}{separator}{en_text}"

    try:
        # 使用当前群聊的 session-key 确保发送到正确的地方
        result = subprocess.run(
            [
                "openclaw", "agent",
                "--session-key", "agent:main:dingtalk:group:cidj1wleiezwdpcgkekpmaywq==",
                "--message", full_message,
                "--deliver"
            ],
            capture_output=True, text=True, timeout=30
        )

        if result.returncode == 0:
            log("✓ 已通过 openclaw agent 发送到钉钉群")
            return True
        else:
            log(f"✗ openclaw agent 发送失败: {result.stderr}")
            # 失败回退：直接 print 到 stderr
            print(full_message, file=sys.stderr)
            return False

    except Exception as e:
        log(f"发送异常: {e}")
        print(full_message, file=sys.stderr)
        return False

def main():
    log("开始执行美伊战争新闻抓取任务...")

    # 1. 优先尝试 Tavily 搜索
    news = search_via_tavily()

    # 2. 如果 Tavily 没结果或没配置，尝试浏览器方式
    if not news:
        log("Tavily 无结果或未配置，切换到浏览器模式...")
        news = search_via_browser()

    log(f"共收集到 {len(news)} 条新闻")

    # 3. 生成摘要
    summaries = summarize_news(news)
    log(f"摘要生成完成（中文{len(summaries['zh'])}字符，英文{len(summaries['en'])}字符）")

    # 4. 发送
    success = send_to_dingtalk_via_agent(summaries["zh"], summaries["en"])

    if success:
        log("✅ 任务完成")
        return 0
    else:
        log("❌ 任务完成但发送失败，内容已输出到 stderr")
        return 1

if __name__ == "__main__":
    sys.exit(main())
