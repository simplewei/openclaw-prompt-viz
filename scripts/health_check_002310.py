#!/usr/bin/env python3
"""
东方新能(002310)每日跟踪 - 数据源健康检查
检查所有依赖的服务是否可用，提前发现故障
"""

import json
import os
import urllib.request
import urllib.error
import ssl
import sys
from datetime import datetime

def check_tavily_api():
    """检查 Tavily Search API 可用性"""
    try:
        url = "https://api.tavily.com/search"
        payload = {
            "query": "test",  # 简单查询，消耗小
            "max_results": 1,
            "search_depth": "basic"
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('TAVILY_API_KEY', '')}"
        }
        data = json.dumps(payload).encode('utf-8')

        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        context = ssl._create_unverified_context()

        with urllib.request.urlopen(req, context=context, timeout=10) as response:
            if response.status == 200:
                return {"status": "ok", "message": "Tavily API 正常"}
            else:
                return {"status": "error", "message": f"HTTP {response.status}"}
    except urllib.error.HTTPError as e:
        return {"status": "error", "message": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def check_website_access(url, name):
    """检查网站可访问性"""
    try:
        req = urllib.request.Request(url, method='HEAD')
        context = ssl._create_unverified_context()

        with urllib.request.urlopen(req, context=context, timeout=10) as response:
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

    # 1. 检查 Tavily Search API
    results["checks"]["tavily_search"] = check_tavily_api()

    # 2. 检查关键财经网站
    sites = {
        "eastmoney": "https://quote.eastmoney.com/sz002310.html",
        "xueqiu": "https://xueqiu.com/S/002310",
        "sina_finance": "https://finance.sina.com.cn/realstock/company/sh002310",
        "cninfo": "http://www.cninfo.com.cn"
    }

    for site_name, url in sites.items():
        results["checks"][site_name] = check_website_access(url, site_name)

    # 3. 计算总体健康度
    failed = sum(1 for c in results["checks"].values() if c["status"] != "ok")
    total = len(results["checks"])
    results["health_score"] = f"{(total - failed) / total * 100:.1f}%"

    return results

def main():
    print("🔍 开始数据源健康检查...")
    results = run_health_check()

    # 输出 JSON 结果
    print(json.dumps(results, indent=2, ensure_ascii=False))

    # 如果有故障，输出警告
    if results["health_score"] < "80.0%":
        print("\n⚠️  警告：多个数据源不可用，建议人工检查")
        sys.exit(1)
    else:
        print("\n✅ 所有数据源状态良好")
        sys.exit(0)

if __name__ == "__main__":
    main()
