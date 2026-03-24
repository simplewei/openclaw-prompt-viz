# 国内AI媒体动态监控 - 运维概览

## 🎯 目标
自动抓取国内主流科技媒体的AI相关报道，生成竞争态势简报。

## 📊 数据源（14家媒体）
- **头部**: 36氪、虎嗅、量子位、机器之心、雷锋网
- **垂直**: 钛媒体、界面新闻、品玩、极客公园、爱范儿
- **综合**: InfoQ、CSDN、开源中国

## 🔧 核心脚本
- `scripts/ai_media_monitor.py` - 主程序（无需pip依赖）
- `scripts/health_check_ai_media.py` - 媒体连通性检查（可选）

## 🚀 运行方式
```bash
# 手动测试
cd /root/.openclaw/workspace
python3 scripts/ai_media_monitor.py

# 输出文件: ai_media_report_YYYY-MM-DD.txt
```

## 📈 输出内容
- 领域分布（大模型进展、商业竞争、融资动态、应用落地等）
- 核心要闻（Top 8-10，带来源链接）
- 关键洞察（自动总结趋势）
- 媒体覆盖状态

## ⚙️ 配置
- **API**: TAVILY_API_KEY 环境变量
- **查询范围**: 最近7天（time_range=week）
- **结果数量**: 20条（max_results=20）
- **超时**: 22秒

## 🛠️ 故障排查
- API不可用 → 检查 TAVILY_API_KEY
- 新闻少 → 扩大 site: 域名或增加 max_results
- 分类不准 → 调整 `categorize()` 函数的关键词

## 📝 待优化
- [ ] 集成钉钉文档自动发布（mcporter）
- [ ] 添加热量排序（基于媒体权威性）
- [ ] 支持自定义时间范围和媒体列表

---

**创建**: 2026-03-24 | **版本**: v1.0
