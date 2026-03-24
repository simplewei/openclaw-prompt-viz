#!/bin/bash
# 创建钉钉文档（默认存入openclaw文件夹）
# 用法: create_dingtalk_doc.sh "文档名称" "内容文件路径"

CONFIG_FILE="/root/.openclaw/workspace/config/dingtalk_folders.json"
PARENT_UUID=$(jq -r '.default_parent_dentry_uuid' "$CONFIG_FILE" 2>/dev/null || echo "ndMj49yWjXNaR09OIDDmZwy3J3pmz5aA")

if [ $# -lt 1 ]; then
  echo "用法: $0 \"文档名称\" [内容文件路径]"
  echo "如果内容文件省略，将从stdin读取"
  exit 1
fi

DOC_NAME="$1"
CONTENT_FILE="$2"

if [ -n "$CONTENT_FILE" ]; then
  CONTENT=$(cat "$CONTENT_FILE")
else
  CONTENT=$(cat)
fi

# 创建文档
RESULT=$(mcporter call dingtalk-docs.create_doc_under_node name="$DOC_NAME" parentDentryUuid="$PARENT_UUID")
DENTRY_UUID=$(echo "$RESULT" | jq -r '.result.dentryUuid')

if [ -z "$DENTRY_UUID" ] || [ "$DENTRY_UUID" = "null" ]; then
  echo "❌ 创建文档失败"
  echo "$RESULT"
  exit 1
fi

# 写入内容
mcporter call dingtalk-docs.write_content_to_document targetDentryUuid="$DENTRY_UUID" content="$CONTENT" updateType=0 >/dev/null

PC_URL="https://alidocs.dingtalk.com/i/nodes/$DENTRY_UUID"
echo "✅ 文档已创建: $DOC_NAME"
echo "🔗 访问链接: $PC_URL"
echo "📝 dentryUuid: $DENTRY_UUID"
