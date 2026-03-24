#!/usr/bin/env python3
"""
国内AI媒体动态监控 - 健康检查
检查国内主流科技媒体的可访问性
"""

import json
import os
import urllib.request
import urllib.error
import ssl
import sys
from datetime import datetime

# 国内主流科技媒体列表（AI相关）
CHINESE_TECH_MEDIA = {
    "36氪": "https://36kr.com",
    "虎嗅": "https://huxiu.com",
    "量子位": "https://www.qbitai.com",
    "机器之心": "https://www.jiqizhixin.com",
    "雷锋网": "https://www.leiphone.com",
    "钛媒体": "https://www.tmtpost.com",
    "界面新闻": "https://www.jiemian.com",
    "品玩": "https://www.pintu360.com",
    "爱范儿": "https://www.ifanr.com",
    "极客公园": "https://www.geekpark.net",
    "InfoQ": "https://www.infoq.cn",
    "CSDN": "https://www.csdn.net",
    "开源中国": "https://www.oschina.net",
    "AI科技评论": "https://www.leiphone.com/category/ailuntan",  # 雷锋网子站
}

def check_website_access(url, name, timeout=10):
    """检查网站可访问性（HEAD请求）"""
    try:
        req = urllib.request.Request(url, method='HEAD')
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(req, context=context, timeout=timeout) as response:
            if response.status < 400:
                return {"status": "ok", "latency": ""}
            else:
                return {"status": "error", "message": f"HTTP {response.status}"}
    except urllib.error.HTTPError as e:
        return {"status": "error", "message": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def run_health_check():
    """执行完整健康检查"""
    results = {
        "timestamp": datetime.now().isoformat(),
        "checks": {}
    }

    # 检查所有国内科技媒体
    for name, url in CHINESE_TECH_MEDIA.items():
        results["checks"][name] = check_website_access(url, name)

    # 计算健康度
    ok_count = sum(1 for c in results["checks"].values() if c["status"] == "ok")
    total = len(results["checks"])
    results["health_score"] = f"{(ok_count / total * 100):.1f}%"
    results["ok_count"] = ok_count
    results["total"] = total

    return results

def main():
    print("🔍 国内AI媒体健康检查...")
    results = run_health_check()

    print(json.dumps(results, indent=2, ensure_ascii=False))

    print(f"\n📊 健康度: {results['health_score']} ({results['ok_count']}/{results['total']} 媒体可用)")

    # 列出不可用的媒体
    failed = [(name, info) for name, info in results["checks"].items() if info["status"] != "ok"]
    if failed:
        print("\n❌ 不可用媒体:")
        for name, info in failed[:5]:  # 只显示前5个
            print(f"  - {name}: {info['message']}")
        if len(failed) > 5:
            print(f"  ... 还有 {len(failed)-5} 个")

    # 阈值警告
    if results["health_score"] < "70.0%":
        print("\n⚠️  警告：大部分媒体不可达，可能影响AI动态抓取")
        sys.exit(1)
    else:
        print("\n✅ 媒体访问状态良好")
        sys.exit(0)

if __name__ == "__main__":
    main()
