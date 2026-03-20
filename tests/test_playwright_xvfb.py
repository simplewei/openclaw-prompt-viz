#!/usr/bin/env python3
"""
测试 Playwright 在 Xvfb 环境中的可用性
"""
import os
import sys
from playwright.sync_api import sync_playwright

def test_playwright():
    with sync_playwright() as p:
        # 尝试启动 chromium
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://36kr.com")
        title = page.title()
        print(f"Page title: {title}")
        content = page.text_content("body")
        print(f"Content length: {len(content)}")
        print(f"First 500 chars:\n{content[:500]}")
        browser.close()
        return True

if __name__ == "__main__":
    # 确保 DISPLAY 已设置
    if "DISPLAY" not in os.environ:
        print("ERROR: DISPLAY not set. Xvfb may not be running.")
        sys.exit(1)
    try:
        test_playwright()
        print("✅ Playwright test passed")
    except Exception as e:
        print(f"❌ Playwright test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)