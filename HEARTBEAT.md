# HEARTBEAT.md

# Keep this file empty (or with only comments) to skip heartbeat API calls.

# Add tasks below when you want the agent to check something periodically.

## Self-Improving Check

- Read `./skills/self-improving/heartbeat-rules.md`
- Use `~/self-improving/heartbeat-state.md` for last-run markers and action notes
- If no file inside `~/self-improving/` changed since the last reviewed change, return `HEARTBEAT_OK`

## Proactivity Check

- Read ~/proactivity/heartbeat.md
- Re-check active blockers, promised follow-ups, stale work, and missing decisions
- Ask what useful check-in or next move would help right now
- Message the user only when something changed or needs a decision
- Update ~/proactivity/session-state.md after meaningful follow-through

## Configuration Verification (added 2026-03-19)

- Verify USER.md preferences are up-to-date
- Check if last proactivity session-state is marked completed
- Validate MEMORY.md has recent entries
- Report any configuration drift or missing settings

## 羽毛球俱乐部运营反思检查 (added 2026-03-24)

**检查频率**：每周一上午  
**动作**：
1. 检查是否需要填写本周周报（上周三至本周二的数据）
2. 查看 `/root/.openclaw/workspace/羽毛球俱乐部散客组局运营方案.md` 中的"立即行动清单"
3. 检查群内是否有需要发布的"周总结+下周预告"
4. 评估冷启动进程：是否还需要种子填充？自然报名时间是否<2小时？
5. 检查各平台文案效果：哪个平台转化最高？是否需要调整风格？
6. 如果发现异常（如成局率<80%、新客<10人/周），立即提醒用户

**状态记录**：在 `memory/YYYY-MM-DD.md` 中记录检查结果和行动项

## 钉钉文档存储规范 (added 2026-03-24)

**默认存储路径**：
- 父节点ID：`ndMj49yWjXNaR09OIDDmZwy3J3pmz5aA` (openclaw文件夹)
- 配置位置：`/root/.openclaw/workspace/config/dingtalk_folders.json`

**创建文档规则**：
1. 所有新文档优先创建在 `openclaw` 文件夹下
2. 使用 `mcporter call dingtalk-docs.create_doc_under_node` 时，`parentDentryUuid` 默认使用 `ndMj49yWjXNaR09OIDDmZwy3J3pmz5aA`
3. 文档命名规范：`[业务领域]_[内容描述]_[YYYY-MM-DD]`（如：`羽毛球运营方案_增强版_2026-03-24`）
4. 创建后立即写入内容，并记录到 MEMORY.md

**例外情况**：
- 仅当用户明确要求"存入根目录"或指定其他位置时，才使用其他 parentDentryUuid
- 已有文档（在openclaw文件夹创建前）可保持不变

**检查点**：
- 创建钉钉文档前，先读取 `config/dingtalk_folders.json` 确认默认 parentDentryUuid
- 文档创建成功后，更新 MEMORY.md 的 Deliverables 部分

## 孩子陪伴师周报生成 (added 2026-03-26)

**检查频率**：每周日晚上20:00（Asia/Shanghai）

**动作**：
1. 检查child-companion目录下本周聊天记录（7天）
2. 验证是否至少有5天记录（若不足，提醒家长补录）
3. 调用child-companion子代理生成周报
4. 将周报保存到：`/root/.openclaw/workspace/child-companion/reports/weekly_周报_[本周日日期].md`
5. 自动发布到钉钉文档（openclaw文件夹）
6. 在MEMORY.md中记录本周亮点

**周报内容结构**：
- 本周摘要（100字）
- 分领域评分（情绪、学业、社交、健康）
- 关键成长发现（2-3条）
- 待关注点（1-2条）
- 下周行动建议（3条）
- 家长反思题

**前置条件**：
- 本周聊天记录需在周日前完成
- 周日"回顾与展望"对话必须进行

**失败处理**：
- 若记录不足，发送提醒："本周聊天记录不足5天，请补录后再生成周报"
- 若子代理无响应，手动使用`每周晚间聊天计划表.md`模板生成

**状态记录**：在 `memory/child-companion-weekly.md` 中记录每次周报生成情况
