# Long-Term Memory

## Cron Jobs Created
- `daily-reflection` (ID: e6922629-6331-4ae3-976b-6b09bfc8f1f7)
  - Schedule: 0 21 * * * (Asia/Shanghai)
  - Target: DingTalk group "杭州余杭钛酷贸易中心"
  - Message: "【每日复盘】请进行今日复盘反思，并说明是否需要帮助。"
  - Next run: 2026-03-25 21:00 北京时间

- `002310每日跟踪` (ID: ec23f3a3-8ce1-4cca-844f-84f45d13730d)
  - Schedule: 37 0 * * * (UTC) → 08:30 Asia/Shanghai (周一至周五)
  - Target: Current group chat
  - Task: 东方新能(002310)每日跟踪
  - Status: ✅ 2026-03-21手动执行成功（Tavily Search数据源）
  - Previous failure: 2026-03-20（Gemini web_search缺API，网站反爬）
  - Solution: 切换至Tavily Search，已发布钉钉文档
  - **Upgrade (2026-03-24)**: 增强版脚本已开发（健康检查+多源冗余+优雅降级），待集成到cron

## Technical Issues
- 2026-03-20: 财经数据源访问失败
  - Affected tasks: 东方新能每日跟踪
  - Causes: Gemini API missing,东方财富/雪球反爬,网络不稳定
  - Workaround: 已生成带框架的离线报告，手动数据查询链接已提供
  - Solutions:
    - ✅ Configured Tavily Search (优先搜索工具)
    - ✅ Created website access solution guide (agent-browser headed mode, user-data-dir persistence)
    - Pending: install akshare library (可选，用于金融数据)
- 已解决（2026-03-21）: Tavily Search完全替代Gemini，财经数据获取恢复，首份完整东方新能报告发布
- **预防性升级（2026-03-24）**: 部署三层防护机制（健康检查+多源冗余+优雅降级），未来单点故障不再导致任务完全失败

## Deliverables (2026-03-20)
- **决策简报**：《机器人&AI硬件决策简报（2026）》
  - Type: 1页PPT式决策简报
  - Content: 市场洞察、机会图谱、风险分析、战略建议
  - Format: Markdown → 钉钉文档
  - Target Directory: 1R7q3QmWee9XZaQbfXGzMRQmWxkXOEP2
  - DingTalk Doc ID: QPGYqjpJYrlev9qkIo2zem6w8akx1Z5N
  - Access URL: https://alidocs.dingtalk.com/i/nodes/QPGYqjpJYrlev9qkIo2zem6w8akx1Z5N
  - Sources: Tavily Search (36氪、虎嗅、Lex Fridman、a16z、投资界等)
  - Key findings:
    - 7家百亿独角兽聚焦"具身大脑"（VLA）
    - AI硬件市场2026: $4.158B，智能眼镜$5.6B
    - 推理成本年降10倍，目标<人力成本1%
    - 制造暗线：先进封装/末端执行器成瓶颈
    - 三巨头布局：阿里ATH、字节AI手机、腾讯微信Agent

## Deliverables (2026-03-21)
- **东方新能(002310)每日跟踪报告**
  - Type: 深度分析报告（2936字节）
  - Content: 连续两日涨停分析、龙虎榜资金流向、资产收购进展、风险提示、操作建议
  - Format: Markdown → 钉钉文档
  - DingTalk Doc ID: DnRL6jAJMGREo2qluw3Gqkn6WyMoPYe1
  - Access URL: https://alidocs.dingtalk.com/i/nodes/DnRL6jAJMGREo2qluw3Gqkn6WyMoPYe1
  - Data Source: Tavily Search
  - Key findings:
    - 3月19-20日连续涨停（3.16→3.48元，+21.25%）
    - 量化打板净买入1.33亿，深股通净买入4895万
    - 拟2.76亿收购风电资产（海城锐海+电投瑞享）
    - 风险：限售解禁7亿股、业绩亏损、涨幅过大
    - 建议：短线观望，中线3.0-3.2元分批建仓

## Deliverables (2026-03-24)
- **东方新能(002310)每日跟踪系统改进**
  - Type: 系统加固（预防性开发）
  - Components:
    - `scripts/health_check_002310.py` - 健康检查脚本（80%健康度阈值）
    - `scripts/daily_002310_enhanced.py` - 增强版跟踪脚本（零依赖+优雅降级）
    - `scripts/README_002310.md` - 运维手册
  - Test result: ✅ 成功生成报告 `daily_report_002310_2026-03-24.txt`
  - Key improvements:
    - 前置健康检查（Tavily API + 网站连通性）
    - 多源冗余矩阵（主: Tavily, 备: agent-browser）
    - 优雅降级：任何失败都输出可用框架报告
    - 零 pip 依赖（使用 urllib 标准库）

## Research Notes
- Tavily Search 已验证可用，API Key配置正确（需使用 Authorization Bearer header）
- 文档自动存储到钉钉文档流程已打通（mcporter工具）
- 高质量信息源建立：36氪、虎嗅、Lex Fridman、a16z、投资界
- **系统健壮性提升**: 通过健康检查+冗余+降级，单点故障不再导致任务失败

