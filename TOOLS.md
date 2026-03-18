# Tool Capability Matrix

## Web & Network
- **agent-browser**: 浏览器自动化，可打开任何网站、点击、填写表单、截图、获取动态渲染内容
  - 适用：需要登录/交互的网站、JS 渲染的页面、需要视觉验证的场景
  - 命令示例: `agent-browser open <url>`, `snapshot`, `click`, `eval`
- **curl / wget**: 简单 HTTP 请求，获取静态内容或 API
  - 适用：RSS feeds、JSON APIs、不需要 JS 的静态页面
- **blogwatcher**: RSS/Atom 订阅监控
  - 适用：跟踪博客更新、新闻源（如果订阅已配置）
- **xurl**: X (Twitter) API 客户端
  - 适用：搜索/读取推文、发布内容

## Coding & Agents
- **coding-agent** (skill): 调用 Codex/Claude Code/Pi
  - 适用：编写/重构/审查代码、批量任务
- **oracle**: 提示工程工具
  - 适用：优化 prompt、测试 LLM 响应

## Media & Communication
- **sag**: ElevenLabs TTS，语音合成
- **camsnap**: 摄像头拍照
- **video-frames**: 从视频提取帧
- **wacli**: WhatsApp 第三方消息
- **discord/slack**: 聊天平台集成

## Home & IoT
- **openhue**: Philips Hue 灯光控制
- **sonoscli**: Sonos 音响控制
- **voice-call**: 语音通话

## Productivity
- **apple-notes / apple-reminders / bear-notes / obsidian / things-mac**: 笔记与任务管理
- **notion**: Notion API
- **trello**: Trello 看板
- **goplaces**: 地点/地图
- **weather**: 天气查询

## System & Dev
- **tmux**: 远程控制 tmux 会话
- **github / gh-issues**: GitHub 集成
- **healthcheck**: 系统安全检查
- **session-logs**: 会话日志查看
- **model-usage**: 模型用量追踪

## Games & Fun
- **gog**: GOG 商店
- **songsee**: 歌曲识别
- **gifgrep**: 搜索 GIF

---

## Decision Rules

When user asks for something, pick tool by this priority:

1. **明确提及工具名** → 直接用那个工具（先 which 确认存在）
2. **需要浏览器交互** → agent-browser (首选), curl (备选)
3. **需要编码** → coding-agent, 或直接 edit/write/exec
4. **需要语音** → sag
5. **需要 IoT** → 对应技能 (openhue, sonoscli, etc.)
6. **需要笔记/任务** → 对应技能
7. **不确定** → 快速 which 扫描，或 ask user

## Fallback Strategy

如果首选工具不可用或失败：
- 浏览器 auto-blocked? → 尝试 curl 或用 agent-browser 的 --headed 模式
- 网站需要登录? → 使用 agent-browser 的 --profile 持久会话
- API 限流? → 加入等待后重试
- 工具不存在? → 检查 PATH 或建议安装

## Quick Decision Guide (User Intent → Tool)

| 用户需求 | 首选工具 | 备选方案 |
|---------|---------|---------|
| "搜索/查看新闻" | agent-browser | curl + grep |
| "抓取网页内容" | agent-browser | curl/w3m/lynx |
| "填写表单/登录" | agent-browser | N/A |
| "截图网页" | agent-browser screenshot | N/A |
| "发推/读推" | xurl | N/A |
| "写代码/重构" | coding-agent | 直接 edit |
| "生成图片" | openai-image-gen | N/A |
| "查天气" | weather | curl wttr.in |
| "控制灯光" | openhue | N/A |
| "播放音乐" | sonoscli / spotify-player | N/A |
| "发 WhatsApp 给他人" | wacli | N/A |
| "监控 RSS" | blogwatcher | curl + cron |
| "OCR/PDF" | nano-pdf | N/A |
| "与 GitHub 交互" | github / gh-issues | gh CLI |
| "系统安全检查" | healthcheck | 手动检查 |

## Checklist for Autonomous Tool Selection

- [ ] 是否已有缓存的工具清单 (`.tools_cache.txt`)？没有则生成
- [ ] 用户需求是否匹配表格中的模式？匹配则直接选用
- [ ] 首选工具是否存在？`which <tool>` 验证
- [ ] 如果不存在，是否在 Skills 列表中？用 skill 方式调用
- [ ] 如果都不行，快速探索 PATH：`ls $PATH_dir | grep -i <keywords>`
- [ ] 仍找不到？诚实告诉用户，并建议安装

## Real-World Examples (How I Think)

### Example 1: User says "帮我看看美伊战争最新情况"

**Thinking:**
- 用户需要最新新闻，可能需要访问新闻网站（动态内容，可能有反爬）
- 工具选择：需要浏览器渲染 → agent-browser (最优) 或 curl (备选)
- 验证：`which agent-browser` → 存在
- Action: 使用 agent-browser 打开 BBC/Google News，snapshot 抓取

### Example 2: User says "搜索 X 上关于 AI 的推文"

**Thinking:**
- 明确需要访问 X/Twitter API
- 工具：xurl (专门封装 X API)
- 验证：xurl 在 skills 列表中且 bin 存在
- Action: `xurl search "AI" -n 10`

### Example 3: User says "把这张照片发给我 WhatsApp"

**Thinking:**
- 需要发送文件到 WhatsApp（非当前聊天）
- 工具：wacli (WhatsApp CLI)
- 验证：`which wacli` → 不存在？检查 skills 列表 → wacli 存在但需 auth
- Action: 先检查 wacli auth 状态，如未认证则提示用户扫码登录

### Example 4: User says "我想查一下我下周的日历"

**Thinking:**
- 需要日历数据
- OpenClaw 技能列表中有 things-mac、apple-reminders，但不一定适配
- 备选：直接读取 ~/Library/Calendars 或调用 `icalBuddy` 等工具
- 如果 PATH 中有 `gcalcli` 或 `khal`，优先使用
- 如果不确定，问用户："你用哪个日历服务？"

### Example 5: User says "帮我写一个贪吃蛇游戏"

**Thinking:**
- 需要生成代码
- 工具：coding-agent (Codex/Claude Code)
- 决定：用 Codex (快速) 或 Claude Code (高质量)
- 默认：`claude --permission-mode bypassPermissions --print '你的任务'`
- 如果项目复杂，用 background + pty 模式

## 🔧 上游错误排查规范（强制执行）

当遇到 "Provider returned error" 或任何上游接口错误时，**必须**按以下步骤排查并结构化输出，不得只返回通用失败信息：

### 排查步骤

1. **判断错误来源**：认证失败 / 权限不足 / 模型不存在 / 限流 / 余额不足 / 网络错误 / 超时 / 参数非法 / 服务端故障
2. **提取错误上下文**：
   - provider 名称、model 名称、base URL
   - HTTP 状态码
   - provider 返回的原始错误消息
   - request id / trace id
3. **检查配置问题**：API key 是否存在、base URL 格式、model 名称拼写、必填参数
4. **检查请求问题**：输入是否过长、不支持的参数、超出上下文长度
5. **检查运行环境**：网络可达性、provider 服务状态、本地服务状态

### 输出格式（必须遵守）

```
- 错误分类：[具体分类]
- 已知信息：[所有可见的错误上下文]
- 可能原因：[按可能性排序]
- 建议操作：[给出下一步可执行操作]
- 仍需补充的信息：[如缺少日志，提示用户获取方法]
```

## Self-Audit Questions (Before Replying)

1. **需求分析**：用户真的需要浏览器吗？还是静态 API 就能搞定？
2. **工具匹配**：我的工具表格里有映射吗？
3. **存在验证**：`which <tool>` 马上跑一下，避免假设
4. **降级方案**：如果这个工具失败，我有什么备选？
5. **结果验证**：工具执行后输出是否符合预期？是否需二次处理？

## Proactive Tool Use

- Prefer safe internal work, drafts, checks, and preparation before escalating
- Use tools to keep work moving when the next step is clear and reversible
- Try multiple approaches and alternative tools before asking for help
- Use tools to test assumptions, verify mechanisms, and uncover blockers early
- For send, spend, delete, reschedule, or contact actions, stop and ask first
- If a tool result changes active work, update ~/proactivity/session-state.md


