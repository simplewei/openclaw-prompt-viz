#!/bin/bash
# 发布child-companion周报到钉钉文档
# 用法：bash scripts/publish_weekly_report.sh [周报文件路径]

set -e

REPORT_FILE="${1:-/root/.openclaw/workspace/child-companion/reports/weekly_周报_$(date -d 'sunday' +%Y-%m-%d).md}"

if [ ! -f "$REPORT_FILE" ]; then
  echo "❌ 周报文件不存在: $REPORT_FILE"
  echo "请先使用 '@child-companion 生成第X周周报' 创建报告"
  exit 1
fi

# 读取周报内容
CONTENT=$(cat "$REPORT_FILE")

# 提取日期作为文档标题（从文件名）
DOC_DATE=$(basename "$REPORT_FILE" | grep -o '[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}')
DOC_TITLE="孩子成长周报_${DOC_DATE}"

# 默认使用 openclaw 文件夹父节点
PARENT_DENTRY="ndMj49yWjXNaR09OIDDmZwy3J3pmz5aA"

# 检查配置
CONFIG_FILE="/root/.openclaw/workspace/config/dingtalk_folders.json"
if [ -f "$CONFIG_FILE" ]; then
  PARENT_DENTRY=$(jq -r '.defaultParentDentryUuid // "ndMj49yWjXNaR09OIDDmZwy3J3pmz5aA"' "$CONFIG_FILE" 2>/dev/null || echo "ndMj49yWjXNaR09OIDDmZwy3J3pmz5aA")
fi

echo "📤 正在发布周报到钉钉文档..."
echo "文档标题: $DOC_TITLE"
echo "父节点: $PARENT_DENTRY"

# 调用钉钉文档API创建文档
# 使用 mcporter 或 curl（根据环境配置）
if command -v mcporter &>/dev/null; then
  # 使用 mcporter
  RESPONSE=$(mcporter call dingtalk-docs.create_doc_under_node \
    --parent-dentry-uuid "$PARENT_DENTRY" \
    --title "$DOC_TITLE" \
    --content "$CONTENT" \
    --format markdown 2>&1)

  DOC_URL=$(echo "$RESPONSE" | grep -o 'https://alidocs.dingtalk.com/i/nodes/[A-Za-z0-9]*' | head -1)

  if [ -n "$DOC_URL" ]; then
    echo "✅ 周报发布成功！"
    echo "🔗 文档链接: $DOC_URL"

    # 记录到 MEMORY.md
    if [ -f "/root/.openclaw/workspace/MEMORY.md" ]; then
      echo "" >> /root/.openclaw/workspace/MEMORY.md
      echo "## Deliverables ($(date +%Y-%m-%d))" >> /root/.openclaw/workspace/MEMORY.md
      echo "- **孩子成长周报（第__周）**" >> /root/.openclaw/workspace/MEMORY.md
      echo "  - Type: 周度成长报告" >> /root/.openclaw/workspace/MEMORY.md
      echo "  - Format: Markdown → 钉钉文档" >> /root/.openclaw/workspace/MEMORY.md
      echo "  - DingTalk Doc ID: （见链接）" >> /root/.openclaw/workspace/MEMORY.md
      echo "  - Access URL: $DOC_URL" >> /root/.openclaw/workspace/MEMORY.md
      echo "  - Notes: 第__周，覆盖本周聊天记录分析" >> /root/.openclaw/workspace/MEMORY.md
    fi

    exit 0
  else
    echo "❌ 文档创建失败，响应："
    echo "$RESPONSE"
    exit 1
  fi
else
  echo "⚠️ mcporter 未安装，请手动创建钉钉文档："
  echo "1. 打开钉钉文档"
  echo "2. 在'openclaw'文件夹下创建新文档"
  echo "3. 粘贴以下内容："
  echo ""
  echo "$CONTENT"
  echo ""
  echo "4. 将文档链接记录到 MEMORY.md"
  exit 0
fi