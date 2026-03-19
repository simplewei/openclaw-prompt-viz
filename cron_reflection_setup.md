# Daily Reflection Cron Job Configuration

## ✅ 配置状态

**Cron Job**: `daily-reflection`
**ID**: e6922629-6331-4ae3-976b-6b09bfc8f1f7
**状态**: ✅ 启用
**时区**: Asia/Shanghai (北京时间)
**执行时间**: 每日 21:00 (北京时间)
**目标**: DingTalk群组 "杭州余杭钛酷贸易中心"

## 📅 任务描述

每日晚间复盘反思，内容包括：
- 今日主要成就和学习
- 遇到的挑战和解决方案
- 自我改进点
- 如果有需要用户帮助的事项，会主动提出

## 🔧 技术实现

```bash
openclaw cron add \
  --name "daily-reflection" \
  --cron "0 21 * * *" \
  --tz Asia/Shanghai \
  --message "【每日复盘】请进行今日复盘反思，并说明是否需要帮助。" \
  --channel dingtalk \
  --to "cidJ1WlEiEZwDpcgkEkpmAywQ==" \
  --deliver \
  --best-effort-deliver
```

## 📊 监控

- 查看任务状态: `openclaw cron list`
- 手动触发: `openclaw cron run <job-id>`
- 查看日志: `tail -f /root/.openclaw/workspace/logs/reflection_*.log`

## ⚠️ 注意事项

- 任务在隔离会话中运行，不继承当前会话记忆
- 会从 memory/ 和 MEMORY.md 读取当天历史
- 如果无当日活动，会报告"无显著事件"
- 需要帮助的事项会明确@用户并提出

---

**创建时间**: 2026-03-19
**创建者**: Luna (OpenClaw Assistant)
**下次运行**: 2026-03-20 21:00 北京时间 (Asia/Shanghai)