# 美伊战争每日简报自动化配置

## ✅ 配置状态

**Cron Job**: `daily-iran-briefing`
**ID**: `a766f7b6-3a01-40aa-965b-204ee4391a1f`
**状态**: ✅ 启用
**时区**: Asia/Shanghai (北京时间)
**推送时间**: 每日 09:00 (北京时间)

## 📅 推送内容

- **来源**: BBC, Reuters, AP, CNN 四渠道最新信息
- **格式**: 中英文双语简报
- **去重**: 自动识别并避免重复内容
- **目标**: DingTalk群组 "杭州余杭钛酷贸易中心" (conversationId: cidJ1WlEiEZwDpcgkEkpmAywQ==)

## 🔧 技术实现

```
openclaw cron add \
  --name "daily-iran-briefing" \
  --cron "0 9 * * *" \
  --tz Asia/Shanghai \
  --message "请生成今日美伊战争最新战况简报（整合BBC、Reuters、AP、CNN四渠道），避免重复内容，中英文双语，发送到当前DingTalk群组。" \
  --channel dingtalk \
  --to "cidJ1WlEiEZwDpcgkEkpmAywQ==" \
  --deliver \
  --best-effort-deliver
```

## 📊 监控与故障排查

### 查看任务状态
```bash
openclaw cron list
openclaw cron runs --id a766f7b6-3a01-40aa-965b-204ee4391a1f --limit 10
```

### 手动触发测试
```bash
openclaw cron run a766f7b6-3a01-40aa-965b-204ee4391a1f
```

### 查看日志
```bash
tail -f /root/.openclaw/workspace/logs/briefing_*.log
```

## 🎯 预期输出格式

简报将包含：
- 📋 执行摘要（最新动态）
- 🔥 各渠道独特视角（BBC事实、Reuters数据、AP官方、CNN评论）
- 😟 人道状况
- 🌍 国际反应
- 📊 关键指标
- ❓ 未解之谜
- 🔮 未来展望

## ⚠️ 注意事项

- 任务在隔离会话（isolated）中运行，不继承当前会话记忆
- 每次运行会重新采集信息，依赖网络可用性
- 如某渠道访问失败，会基于可用信息生成简报
- 设置了 `--best-effort-deliver`，发送失败不影响任务完成

## 🚨 应急处理

如需临时停用：
```bash
openclaw cron disable a766f7b6-3a01-40aa-965b-204ee4391a1f
```

恢复启用：
```bash
openclaw cron enable a766f7b6-3a01-40aa-965b-204ee4391a1f
```

删除任务：
```bash
openclaw cron rm a766f7b6-3a01-40aa-965b-204ee4391a1f
```

---

**创建时间**: 2026-03-13
**创建者**: OpenClaw Assistant
**下次运行**: 2026-03-14 09:00 北京时间
