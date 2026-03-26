# child-companion 启动脚本

## 启动方式

### 方式1：持久化子代理（推荐）
```bash
# 创建持久化会话（长期运行，可随时交互）
claw sessions_spawn mode="session" \
  label="child-companion" \
  task="你是孩子专属陪伴师，持续记录、分析和引导孩子成长。请等待家长提供更新信息，或主动询问最新章节、行为观察、教师反馈等。" \
  model="openrouter/stepfun/step-3.5-flash:free"
```

### 方式2：一次性任务
```bash
# 处理特定任务后自动退出
claw sessions_spawn mode="run" \
  task="根据最新记录生成本周周报" \
  model="openrouter/stepfun/step-3.5-flash:free"
```

## 工作流程示例

### 初始化会话
```
【欢迎语】
你好，我是孩子专属陪伴师（child-companion），负责记录、分析和引导孩子的成长。
我的职责：
1. 记录语录、行为、在校表现
2. 追踪身心健康与学业进展
3. 规划兴趣发展与实践活动
4. 生成定期报告（周报/月报/季度评估）
5. 提供个性化成长建议

请告诉我：
- 孩子的姓名/昵称（可选）
- 当前年级
- 最近需要记录的事项
- 是否有紧急关注点
```

### 日常更新流程
```
家长：记录今天孩子说的三句话
陪伴师：已记录到 quotes_语录.md，是否需要补充背景情境？

家长：数学作业完成情况不好
陪伴师：已更新 academics_学业发展.md，建议：
1. 检查具体哪类题目错得多
2. 明天与老师沟通是否需要额外辅导
是否生成本周学习计划调整建议？
```

### 主动询问（每3-5天）
```
【主动提醒】
你好！最近有哪些成长点滴值得记录？
- 新语录/有趣对话？
- 行为变化（好的或需要引导的）？
- 学校反馈（老师沟通、作业、考试）？
- 健康状况（睡眠、情绪、饮食）？
- 兴趣活动参与情况？

请分享，我会整理并给出建议。
```

## Heartbeat检查（建议）

在 HEARTBEAT.md 中添加：

```markdown
## 孩子陪伴师每日检查
- 检查 child-companion/session-state.md 是否有待处理任务
- 检查 memories/ 中是否有未分析的新记录
- 判断是否需要主动联系家长（超过3天无更新）
- 生成/发送周报（如果今天是周日）
```

## 消息路由

### 主代理 → 子代理
```bash
claw sessions_send \
  sessionKey="child-companion-持久化ID" \
  message="家长提供的更新内容"
```

### 子代理 → 主代理
子代理完成工作后，直接回复家长（自动路由回原聊天）

## 数据存储规范

- 所有文件存储在 `/root/.openclaw/workspace/child-companion/`
- 生成报告后，使用钉钉文档工具发布（需要家长确认）
- 每次重要更新后，追加到 MEMORY.md 的 Deliverables 部分

## 隐私与权限

- 子代理只能访问 `/child-companion/` 目录
- 禁止自动上传数据，每次外发需家长确认
- 所有敏感信息（孩子姓名、照片）可匿名化处理

## 退出与清理

### 临时暂停
```
家长：暂停陪伴师一周
操作：claw sessions_kill sessionKey="ID"
一周后重新 spawn
```

### 永久终止
```
家长：关闭陪伴师
操作：claw sessions_kill + 删除 child-companion/ 目录
```

---

## 启动清单

- [x] 创建配置文件
- [x] 创建 memories/ 目录及7个文件
- [x] 创建 reports/ 目录及3个模板
- [x] 创建 plans/ 目录及3个文件
- [ ] 创建 session-state.md（运行时生成）
- [ ] 配置 HEARTBEAT.md 检查
- [ ] 测试启动子代理
- [ ] 向家长发送首次欢迎消息

---
创建时间：2026-03-26
版本：v1.0