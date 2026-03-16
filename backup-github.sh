#!/bin/bash
# OpenClaw 自动备份到 GitHub
# 工作区目录
WORKSPACE="/root/.openclaw/workspace"
cd "$WORKSPACE" || exit 1

# 确保有远程仓库
if ! git remote get-url origin >/dev/null 2>&1; then
  echo "错误: 未配置 origin 远程仓库"
  exit 1
fi

# 检查是否有变更（包括未跟踪文件）
if git status --porcelain | grep -q .; then
  echo "发现变更，开始备份..."
  git add -A
  # 使用时间戳作为提交信息
  TIMESTAMP=$(date +"%Y-%m-%d %H:%M")
  git commit -m "每小时自动备份: $TIMESTAMP" || true
  git pull --rebase origin main && git push origin main
  echo "备份完成"
else
  echo "无变更，跳过备份"
fi
