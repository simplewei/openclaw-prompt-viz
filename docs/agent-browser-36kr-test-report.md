# Agent-Browser 访问 36氪/虎嗅 测试报告

## 🧪 测试日期
2026-03-20 15:45 UTC

## 📋 测试目标
验证 agent-browser (v0.17.1) 能否成功访问反爬虫较强的科技媒体网站（36氪、虎嗅）

## ⚙️ 环境信息
- **OS**: Linux (Ubuntu/Debian-based)
- **Node.js**: v24.14.0 (via nvm)
- **agent-browser**: 0.17.1 (globally installed)
- **X Server**: Not available (headless environment)
- **Playwright browsers**: Chromium 1208 installed in /root/.cache/ms-playwright/

## 🔄 测试步骤

### 1. 尝试 1: Direct headless (default)
```bash
agent-browser open https://36kr.com --session test-36kr
```
**Result**: ❌ Failed
```
Missing X server or $DISPLAY
```

### 2. 尝试 2: With Xvfb
```bash
# Install Xvfb
apt-get install -y xvfb

# Start Xvfb manually
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99
agent-browser open https://36kr.com --session test-36kr
```
**Result**: ❌ Failed (same error)

### 3. 尝试 3: Using xvfb-run wrapper
```bash
xvfb-run -a agent-browser open https://36kr.com --session test-36kr
```
**Result**: ❌ Failed (same error)

### 4. 尝试 4: Explicit --headed with Xvfb
```bash
xvfb-run -a agent-browser open https://36kr.com --session test-36kr --headed
```
**Result**: ❌ Failed (Chrome requires X11 even in headless mode on some Linux builds)

## 🔍 根本原因分析

1. **Playwright Chromium 在某些 Linux 环境下需要 X server**，即使是 headless 模式也可能会尝试连接 X11
2. **Remote debugging pipe 模式** 可能仍需要某些 X11 库
3. **agent-browser 当前版本** 可能没有正确配置纯 headless 模式
4. **缺少系统依赖**: 某些 X11 库可能未安装

## ✅ 可通过的验证

```bash
# Xvfb itself works
xvfb-run -a xdpyinfo  # ✅ Shows display :99

# DISPLAY is set correctly
echo $DISPLAY  # ✅ :99

# Chromium binary exists
ls -l /root/.cache/ms-playwright/chromium-1208/chrome-linux64/chrome  # ✅
```

## 🛠️ 可能的解决方案

### 方案 A: 安装完整 X11 环境（不推荐在服务器）
```bash
apt-get install -y xorg xserver-xorg-core
# Requires physical or virtual display
```

### 方案 B: 使用 Docker with Xvfb（推荐）
```bash
docker run --rm -v $(pwd):/workspace -e DISPLAY=:99 \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  node:24 bash -lc "
  npm install -g agent-browser
  xvfb-run -a agent-browser open https://36kr.com
  "
```

### 方案 C: 使用不同的浏览器驱动
```bash
# Use Puppeteer directly (might be more tolerant)
npm install -g puppeteer
# But this would require custom script
```

### 方案 D: 降级到 HTTP 客户端 + 解析（对动态页面效果有限）
```bash
# web_fetch 已测试可获取部分内容，但多为 "Please wait..."
web_fetch https://36kr.com
```

### 方案 E: 切换到云函数/有桌面的服务器
- 使用有桌面环境的 VPS
- 或使用云函数服务（如 AWS Lambda with headless Chrome layer）

## 📊 替代方案评估

| 方案 | 可行性 | 复杂度 | 成本 | 效果 |
|------|--------|--------|------|------|
| A. 完整 X11 | ❌ 低 | 高 | 高 | 可能解决但笨重 |
| B. Docker + Xvfb | ✅ 高 | 中 | 低 | 最可靠 |
| C. Puppeteer | ⚠️ 中 | 中 | 低 | 仍需 Xvfb |
| D. web_fetch | ❌ 低 | 低 | 无 | 对 JS 渲染页无效 |
| E. 换服务器 | ✅ 高 | 低 |  varies | 治本方案 |

## 🎯 建议

### 立即行动
1. **使用 Docker 方案进行测试**（最快捷）
2. **或者在有桌面环境的机器上运行** agent-browser

### 长期方案
- **考虑使用云代理服务**（ScrapingBee, ScraperAPI）绕过反爬
- **或迁移到 always-on 的桌面型服务器**（如 Mac mini, 有 GUI 的 VPS）

### 对于 36氪/虎嗅 的具体建议
- 使用 **Tavily Search** 作为主要信息源（已配置）
- 对于必须访问特定文章的场景：
  - 手动复制粘贴到聊天
  - 或使用有桌面的设备临时抓取

## 📝 结论

**当前环境不适合运行 agent-browser**，因为缺乏 X server 且 Chromium 无法在纯 headless 模式下启动。

建议：
1. ✅ **继续使用 Tavily Search** 进行常规信息搜索
2. 🐳 **如需自动化抓取，使用 Docker + Xvfb** 封装脚本
3. 📋 **或将抓取任务迁移到有桌面的服务器**

---

**测试者**: Luna (OpenClaw Assistant)  
**测试时间**: 2026-03-20 15:45 UTC  
**环境**: Racknerd VPS (Linux, no X server)
