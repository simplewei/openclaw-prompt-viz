# Long-Term Memory

## Cron Jobs Created
- `daily-reflection` (ID: e6922629-6331-4ae3-976b-6b09bfc8f1f7)
  - Schedule: 0 21 * * * (Asia/Shanghai)
  - Target: DingTalk group "杭州余杭钛酷贸易中心"
  - Message: "【每日复盘】请进行今日复盘反思，并说明是否需要帮助。"
  - Next run: 2026-03-20 21:00 北京时间

- `002310每日跟踪` (ID: ec23f3a3-8ce1-4cca-844f-84f45d13730d)
  - Schedule: 37 0 * * * (UTC)
  - Target: Current group chat
  - Task: 东方新能(002310)每日跟踪
  - Status: ⚠️ 2026-03-20执行失败（数据源访问受限）
  - Issue: web_search缺API密钥，agent-browser多页面超时，网站反爬虫
  - Action required: 配置Tavily搜索（已完成），使用agent-browser headed模式，文档见 docs/website-access-solution.md

## Technical Issues
- 2026-03-20: 财经数据源访问失败
  - Affected tasks: 东方新能每日跟踪
  - Causes: Gemini API missing,东方财富/雪球反爬,网络不稳定
  - Workaround: 已生成带框架的离线报告，手动数据查询链接已提供
  - Solutions:
    - ✅ Configured Tavily Search (优先搜索工具)
    - ✅ Created website access solution guide (agent-browser headed mode, user-data-dir persistence)
    - Pending: install akshare library (可选，用于金融数据)