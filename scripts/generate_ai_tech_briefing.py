#!/usr/bin/env python3
"""
AI科技每日简报生成脚本
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/root/.openclaw/workspace")

def run_mcporter(method, params):
    """调用 mcporter"""
    cmd = ["mcporter", "call", method]
    for k, v in params.items():
        cmd.append(f"{k}={v}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stdout.strip(), result.stderr.strip()

def get_root_uuid():
    """获取钉钉文档根目录ID"""
    success, output, error = run_mcporter("dingtalk-docs.get_my_docs_root_dentry_uuid", {})
    if not success:
        print(f"❌ 获取根目录失败: {error}")
        return None
    try:
        data = json.loads(output)
        return data.get("rootDentryUuid")
    except Exception as e:
        print(f"❌ 解析根目录ID失败: {e}")
        return None

def create_doc(title, parent_uuid):
    """创建钉钉文档"""
    success, output, error = run_mcporter("dingtalk-docs.create_doc_under_node", {
        "name": title,
        "parentDentryUuid": parent_uuid
    })
    if not success:
        print(f"❌ 创建文档失败: {error or output}")
        return None
    try:
        data = json.loads(output)
        return data.get("result", {}).get("dentryUuid")
    except Exception as e:
        print(f"❌ 解析创建返回失败: {e}")
        return None

def write_content(doc_uuid, content):
    """写入文档内容"""
    success, output, error = run_mcporter("dingtalk-docs.write_content_to_document", {
        "content": content,
        "updateType": 0,
        "targetDentryUuid": doc_uuid
    })
    if not success:
        print(f"❌ 写入内容失败: {error}")
        return False
    return True

def read_file(path):
    """读取文件内容"""
    try:
        return Path(path).read_text(encoding="utf-8")
    except Exception as e:
        print(f"❌ 读取文件失败 {path}: {e}")
        return None

def main():
    today = datetime.now().strftime("%Y-%m-%d")
    briefing_file = WORKSPACE / f"AI_Tech_Briefing_{today}.md"
    
    # 检查是否已有今日简报文件（用于测试）
    if briefing_file.exists():
        print(f"📄 找到现有简报文件: {briefing_file}")
        content = read_file(briefing_file)
        if content:
            print(f"   内容长度: {len(content)} 字符")
    else:
        print(f"❌ 未找到今日简报文件: {briefing_file}")
        print("   请先生成简报内容后再运行此脚本")
        sys.exit(1)

    print(f"🚀 开始发布AI科技简报到钉钉文档...")
    
    # 1. 获取根目录
    root_uuid = get_root_uuid()
    if not root_uuid:
        sys.exit(1)
    print(f"✅ 根目录ID: {root_uuid}")

    # 2. 创建文档
    title = f"AI科技每日简报 {today}"
    print(f"📝 创建文档: {title}")
    doc_uuid = create_doc(title, root_uuid)
    if not doc_uuid:
        sys.exit(1)
    print(f"✅ 文档创建成功，ID: {doc_uuid}")

    # 3. 写入内容
    print("📄 写入内容...")
    if write_content(doc_uuid, content):
        print(f"✅ 内容写入完成")
        print(f"📋 文档链接: https://alidocs.dingtalk.com/i/nodes/{doc_uuid}")
    else:
        sys.exit(1)

    print("✅ 发布完成！")

if __name__ == "__main__":
    main()
