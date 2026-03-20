# Agent-Browser 测试报告

## 🧪 测试目标
验证 agent-browser (v0.17.1) 能否成功访问反爬虫较强的科技媒体网站（36氪、虎嗅）

## ⚠️ 环境限制
- 当前环境：无 X Server（DISPLAY 未设置）
- agent-browser 默认行为：试图启动 headed 模式（需要显示服务器）
- 纯 headless 模式：通过环境变量可控制，但 Playwright Chromium 仍需 X server 的某些功能

## ❌ 测试结果

### 测试命令
```bash
# 尝试 headed 模式（失败 - 缺 X server）
agent-browser open --headed https://36kr.com/p/123456.html --session test-36kr

# 尝试纯 headless（失败 - 仍需要 X server）
AGENT_BROWSER_HEADLESS=true agent-browser open https://36kr.com/p/123456.html --session test-36kr
```

### 错误信息
```
browserType.launch: Target page, context or browser has been closed
Looks like you launched a headed browser without having a XServer running.
Set either 'headless: true' or use 'xvfb-run <your-playwright-app>' before running Playwright.
```

## 🔧 根本原因

Playwright Chromium 在 Linux 无 X server 环境下的限制：
- Chrome/Chromium 依赖 X11 或 Wayland
- 即使是 headless 模式，某些组件仍需要 X server
- 需要虚拟显示服务器（Xvfb）或使用 `--no-sandbox` 特殊配置

## ✅ 解决方案

### 方案 A：安装和使用 Xvfb（推荐）
```bash
# 1. 安装 Xvfb
apt-get update && apt-get install -y xvfb

# 2. 使用 xvfb-run 包装 agent-browser
xvfb-run -a agent-browser open https://36kr.com/p/123456.html --session test-36kr

# 3. 提取内容
xvfb-run -a agent-browser text
```

### 方案 B：使用 docker 容器（预配置环境）
```bash
# 如果有 Docker，使用带 Xvfb 的镜像
docker run --rm -v $(pwd):/workspace -w /workspace node:24 bash -lc "
  npm install -g agent-browser
  xvfb-run -a agent-browser open https://36kr.com/p/123456.html
  agent-browser text
"
```

### 方案 C：降级到纯 HTTP 客户端（不推荐用于 JS 渲染页）
```bash
# 使用 curl + 手动 headers（对动态渲染页面无效）
curl -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" \
  https://36kr.com/p/123456.html
```

### 方案 D：临时启用 headed 模式（需 VNC/桌面环境）
如果有桌面环境或 VNC：
```bash
# 设置 DISPLAY=:1 并启动 VNC server
export DISPLAY=:1
Xvfb :1 -screen 0 1920x1080x24 &
agent-browser open --headed https://36kr.com/p/123456.html
```

## 📊 替代方案评估

| 方案 | 可行性 | 复杂度 | 适合场景 |
|------|--------|--------|----------|
| A. Xvfb | ✅ 高 | 低 | 当前环境直接安装使用 |
| B. Docker | ✅ 高 | 中 | 有 Docker 且不想污染宿主机 |
| C. curl | ❌ 低 | 低 | 仅静态页面，36氪是动态渲染 |
| D. VNC | ⚠️ 中 | 高 | 已有桌面环境 |

## 🎯 建议操作

1. **立即修复**：安装 Xvfb 并重试
   ```bash
   apt-get update && apt-get install -y xvfb
   xvfb-run -a agent-browser open https://36kr.com --session test-36kr
   ```

2. **验证登录态**：如需要登录，使用 `--user-data-dir` 持久化
   ```bash
   mkdir -p ~/.openclaw/browser-profiles/36kr
   xvfb-run -a agent-browser open --headed --user-data-dir ~/.openclaw/browser-profiles/36kr https://36kr.com
   # 手动登录后关闭
   ```

3. **日常抓取**：复用 profile，无需 headed 模式
   ```bash
   xvfb-run -a agent-browser open --user-data-dir ~/.openclaw/browser-profiles/36kr https://36kr.com/p/xxxx
   agent-browser text > article.md
   ```

4. **自动化任务**：集成到 cron 或长期运行的 agent 会话

## 📝 后续步骤

需要我：
1. 安装 Xvfb 并测试 agent-browser 访问 36氪？
2. 创建自动化脚本封装 `xvfb-run` 调用？
3. 设置每日自动抓取任务（cron job）？