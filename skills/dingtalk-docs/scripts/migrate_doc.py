#!/usr/bin/env python3
"""
将文档迁移到指定目录

用法:
    python migrate_doc.py <doc_uuid> <target_parent_uuid>

示例:
    python migrate_doc.py gpG2NdyVX3qL4v6NhAqbbDRZWMwvDqPk 1R7q3QmWee9XZaQbfXGzMRQmWxkXOEP2
"""

import sys
from typing import Optional
from mcporter_utils import run_mcporter, parse_response

def get_document_content(doc_uuid: str) -> Optional[str]:
    """获取文档内容（通过raw content接口）"""
    success, output = run_mcporter('dingtalk-docs.get_document_content_by_url', {
        'docUrl': f'https://alidocs.dingtalk.com/i/nodes/{doc_uuid}'
    })

    if not success:
        print(f"❌ 获取文档内容失败：{output}")
        return None

    result = parse_response(output)
    if result is None:
        print(f"❌ 解析响应失败：{output}")
        return None

    content = result.get('content', '')
    return content

def create_in_target(title: str, parent_uuid: str, content: str) -> Optional[str]:
    """在目标目录创建文档"""
    success, output = run_mcporter('dingtalk-docs.create_doc_under_node', {
        'name': title,
        'parentDentryUuid': parent_uuid
    })

    if not success:
        print(f"❌ 创建文档失败：{output}")
        return None

    result = parse_response(output)
    if result is None:
        print(f"❌ 解析响应失败：{output}")
        return None

    doc_uuid = result.get('dentryUuid')
    url = result.get('pcUrl') or result.get('url', 'N/A')
    print(f"✅ 文档创建成功：{title}")
    print(f"   文档 ID: {doc_uuid}")
    print(f"   访问链接：{url}")

    # 写入内容
    success, output = run_mcporter('dingtalk-docs.write_content_to_document', {
        'content': content,
        'updateType': 0,
        'targetDentryUuid': doc_uuid
    })

    if not success:
        print(f"❌ 写入内容失败：{output}")
        return None

    print(f"✅ 内容写入成功")
    return doc_uuid

def main():
    if len(sys.argv) != 3:
        print(__doc__)
        print("错误：需要提供原文档ID和目标目录ID")
        sys.exit(1)

    doc_uuid = sys.argv[1].strip()
    target_parent = sys.argv[2].strip()

    print(f"📦 开始迁移文档")
    print(f"   原文档ID: {doc_uuid}")
    print(f"   目标目录: {target_parent}")
    print("-" * 50)

    # 1. 获取原文档内容
    print("步骤 1: 获取原文档内容...")
    content = get_document_content(doc_uuid)
    if not content:
        sys.exit(1)
    print(f"   内容长度: {len(content)} 字符")

    # 2. 在目标目录创建新文档
    print("\n步骤 2: 在目标目录创建新文档...")
    new_uuid = create_in_target("机器人&AI硬件决策简报（2026）", target_parent, content)
    if not new_uuid:
        sys.exit(1)

    print("-" * 50)
    print("✅ 迁移完成！")
    print(f"\n新文档链接：https://alidocs.dingtalk.com/i/nodes/{new_uuid}")

if __name__ == '__main__':
    main()