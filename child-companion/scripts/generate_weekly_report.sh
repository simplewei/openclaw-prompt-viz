#!/bin/bash
# child-companion 周报自动生成脚本
# 用法：bash scripts/generate_weekly_report.sh [周数] [可选：周日日期]

set -e

WORKDIR="/root/.openclaw/workspace/child-companion"
REPORTS_DIR="$WORKDIR/reports"
MEMORIES_DIR="$WORKDIR/memories"

# 参数处理
WEEK_NUM="${1:-1}"
if [ -n "$2" ]; then
  SUNDAY_DATE="$2"
else
  # 默认使用本周日（如果今天就是周日，用今天）
  SUNDAY_DATE=$(date -d "sunday" +%Y-%m-%d)
fi

REPORT_FILE="$REPORTS_DIR/weekly_周报_$SUNDAY_DATE.md"

echo "📊 开始生成第$WEEK_NUM周周报（截止 $SUNDAY_DATE）"
echo "工作目录: $WORKDIR"

# 确定本周日期范围（周一到周日）
MONDAY_DATE=$(date -d "$SUNDAY_DATE -6 days" +%Y-%m-%d)
echo "本周范围：$MONDAY_DATE 至 $SUNDAY_DATE"

# 检查是否有足够的聊天记录
echo "🔍 扫描聊天记录..."
RECORD_COUNT=0
WEEK_RECORDS=""

for day in $(seq 0 6); do
  DAY_DATE=$(date -d "$MONDAY_DATE + $day days" +%Y-%m-%d)
  DAY_OF_WEEK=$(date -d "$DAY_DATE" +%u)  # 1=周一
  case $DAY_OF_WEEK in
    1) DAY_NAME="周一" ;;
    2) DAY_NAME="周二" ;;
    3) DAY_NAME="周三" ;;
    4) DAY_NAME="周四" ;;
    5) DAY_NAME="周五" ;;
    6) DAY_NAME="周六" ;;
    7) DAY_NAME="周日" ;;
  esac

  # 从聊天记录或memories文件中提取当天的记录
  # 这里简化：尝试从 memories/*.md 中查找 【[星期] 聊天 [日期]】格式
  DAY_RECORD=""
  for mem_file in "$MEMORIES_DIR"/*.md; do
    if [ -f "$mem_file" ]; then
      RECORD=$(grep -A 10 "【$DAY_NAME 聊天 $DAY_DATE】" "$mem_file" | head -15 || true)
      if [ -n "$RECORD" ]; then
        DAY_RECORD="$RECORD"
        RECORD_COUNT=$((RECORD_COUNT + 1))
        break
      fi
    fi
  done

  if [ -n "$DAY_RECORD" ]; then
    WEEK_RECORDS="$WEEK_RECORDS\n### $DAY_NAME ($DAY_DATE)\n$DAY_RECORD\n"
  fi
done

echo "📈 本周找到 $RECORD_COUNT/7 天的记录"

if [ $RECORD_COUNT -lt 5 ]; then
  echo "⚠️  警告：记录不足5天，周报可能不完整"
  echo "请补录后再执行生成"
fi

# 提取关键指标
echo "📊 分析数据..."

# 情绪评分（从"心情：__/10"提取）
MOOD_SCORES=$(echo "$WEEK_RECORDS" | grep -o '心情：[0-9]\{1,2\}/10' | grep -o '[0-9]\{1,2\}' | sort -n)
MOOD_AVG=$(echo "$MOOD_SCORES" | awk '{sum+=$1} END {if(NR>0) printf "%.1f", sum/NR; else print "N/A"}')
MOOD_MAX=$(echo "$MOOD_SCORES" | tail -1)
MOOD_MIN=$(echo "$MOOD_SCORES" | head -1)

# 统计各主题出现频率
echo "$WEEK_RECORDS" > /tmp/week_records.txt

# 生成周报内容
cat > "$REPORT_FILE" <<EOF
# 孩子成长周报（第$WEEK_NUM周）

**报告周期**：$MONDAY_DATE 至 $SUNDAY_DATE
**记录天数**：$RECORD_COUNT/7天
**生成时间**：$(date +%Y-%m-%d\ %H:%M)
**自动生成**：✅

---

## 📋 本周摘要

本周期（第$WEEK_NUM周）孩子整体状态：

- **情绪平均值**：$MOOD_AVG /10分（最高$MOOD_MAX，最低$MOOD_MIN）
- **记录完整度**：$RECORD_COUNT/7天
- **主要亮点**：待从记录中提取
- **待关注点**：待从记录中提取

---

## 📅 每日记录快照

$WEEK_RECORDS

---

## 📊 分领域评估

### 情绪健康 😊
**评分**：$MOOD_AVG /10分

**分析**：
- 情绪词汇丰富度：待分析
- 情绪稳定性：待从记录判断
- 正面情绪触发点：待提取
- 需要关注的负面情绪：待提取

**建议**：
- 

### 学业进展 📚
**观察要点**：
- 学习兴趣：从"学习探索日"记录分析
- 作业完成态度：从teacher feedback推断
- 提问主动性：记录中"提问次数"统计
- 困难应对：如何面对难题

**本周具体表现**：
- （从记录提取1-2个具体事例）

**建议**：
- 

### 社交能力 👫
**观察要点**：
- 主要玩伴：记录中提及频率
- 合作/冲突事件：统计
- 同理心表现：有无帮助他人/安慰他人
- 友谊稳定性：本周和上周玩伴对比

**本周亮点**：
- （从记录提取）

**建议**：
- 

### 家庭连接 👨‍👩‍👧‍👦
**亲子关系质量**：
- 想家时刻频率：__
- 感恩表达：__
- 周末计划参与度：__
- 家庭归属感评分：__

**本周家庭活动**：
- 

**建议**：
- 

---

## 🔍 关键成长发现

1. **发现一**（举例）
   - 现象：__
   - 意义：__
   - 后续关注：__

2. **发现二**
   - 现象：__
   - 意义：__
   - 后续关注：__

---

## ⚠️ 待关注点

1. **风险/问题**：__
   - 严重程度：低/中/高
   - 应对建议：__
   - 家长行动：__

2. **待观察**：__
   - 为什么关注：__
   - 如何验证：__
   - 何时评估：__

---

## 🎯 下周行动建议（3条）

### 家长行动
1. 
2. 
3. 

### 孩子目标（与孩子商量后设定）
1. 
2. 

### 改进的聊天问题
- 针对本周发现的不足，调整下周话题：
  - 

---

## 📈 趋势与对比

### 与上周对比
- 情绪：↑/↓/→ 原因：__
- 社交：↑/↓/→ 原因：__
- 学业：↑/↓/→ 原因：__

### 月度趋势（如有）
- 

---

## 📝 家长反思题

1. 本周我的哪种聊天方式让孩子最开放？
2. 哪个问题孩子最愿意回答？哪个问题孩子回避？
3. 我在对话中是否保持了"倾听>说教"？
4. 孩子哪个瞬间让我感动/惊讶？
5. 下周我想在哪方面做得更好？

---

## 📌 重要事件记录

### 语录（本周金句）
- 

### 里程碑
- [ ] 
- [ ]

### 教师/学校反馈
- 

---

**报告生成完成！**
✅ 保存至：$REPORT_FILE
🔗 请运行发布脚本：\`bash $WORKDIR/scripts/publish_weekly_report.sh $REPORT_FILE\`

---
EOF

echo "✅ 周报生成完成：$REPORT_FILE"
echo ""
echo "📤 下一步：发布到钉钉文档"
echo "   bash $WORKDIR/scripts/publish_weekly_report.sh $REPORT_FILE"
echo ""
echo "📝 请记录本周第$WEEK_NUM周的完整周报到MEMORY.md的Deliverables部分"

exit 0