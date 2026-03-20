# 解决网站访问受限问题（36氪、虎嗅等反爬虫网站）

## 🔍 问题分析

目标网站（36氪、虎嗅等）常有的反爬虫机制：
- ✅ 检测 headless browser 特征（webdriver 属性）
- ✅ 要求登录或订阅
- ✅ IP/UA 指纹识别
- ✅ 验证码（Cloudflare、reCAPTCHA）
- ✅ 请求频率限制

## ✅ 解决方案

### 方案1：使用 agent-browser headed 模式（推荐）

```bash
# 显示浏览器窗口，模拟真实用户
agent-browser open --headed https://36kr.com
agent-browser open --headed https://huxiu.com

# 首次使用可保存用户数据（登录状态持久化）
agent-browser open --headed --user-data-dir ~/.openclaw/browser-profile https://36kr.com
```

**优点**：
- 绕过 headless 检测
- 可手动登录一次，后续自动复用 cookies
- 完全模拟真人操作

**使用场景**：需要登录、频繁访问、或触发验证码的网站

---

### 方案2：使用 --profile 关联已有浏览器（高级）

如果已有 Chrome/Chromium 用户数据目录：

```bash
# 复制现有 Chrome profile 到临时目录（避免污染）
cp -r ~/.config/google-chrome/Default ~/.openclaw/temp-chrome-profile
# 使用该 profile
agent-browser open --profile ~/.openclaw/temp-chrome-profile https://36kr.com
```

**注意**：profile 文件锁可能导致 Chrome 无法同时运行，建议使用副本

---

### 方案3：Request Interception 自定义 Headers

```bash
# 在 eval 中动态设置 UA
agent-browser open https://36kr.com
agent-browser eval "navigator.userAgent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'"
```

或者在脚本中：

```javascript
// script.js
await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36');
await page.goto('https://36kr.com');
```

运行：
```bash
agent-browser run script.js
```

---

### 方案4：自动处理可能的验证码

agent-browser 可结合 OCR 或手动模式：

```bash
#  headed 模式下，如果出现验证码，人工输入后继续
agent-browser open --headed --wait-for-selector ".content" https://36kr.com
```

---

## 🛠️ 最佳实践组合

对于**36氪/虎嗅**这类媒体网站，建议组合：

```bash
# 1. 首次运行：登录并建立可信 session
agent-browser open --headed --user-data-dir ~/.openclaw/profiles/36kr https://36kr.com
# 手动登录 → 关闭

# 2. 日常抓取：复用登录态
agent-browser open --user-data-dir ~/.openclaw/profiles/36kr https://36kr.com
agent-browser text > article.md
```

---

## 📦 可能需要安装的技能

| Skill | 用途 | Install |
|-------|------|---------|
| `agent-browser` | ✅ 已安装 (0.17.1) | headless browser automation |
| `tavily-search` | 备用搜索API（无需访问目标站） | 已安装 |
| `web-fetch` | 简单HTTP请求（部分静态页） | 内置工具 |

---

## 🔄 快速检查清单

- [ ] agent-browser 是否可执行？ → `which agent-browser` ✅
- [ ] 使用 --headed 模式首次访问
- [ ] 如需要登录，手动完成一次
- [ ] 保存 user-data-dir 供后续复用
- [ ] 测试 `agent-browser text` 能否提取内容

---

## ⚠️ 注意事项

- **不要高频请求**：添加 `setTimeout` 或 `--wait-until=networkidle`
- **遵守 robots.txt**：确保用途合规
- **Rate limit**：建议每请求间隔 2-5 秒
- **验证码**： headed 模式下可手动处理；大量验证码需换IP/UA

---

## 🧪 测试命令

```bash
# 测试是否能访问
agent-browser open --headed https://36kr.com/p/123456.html
# 等待3秒确保加载
sleep 3
# 提取正文
agent-browser text
```

如果仍被拦截，请提供错误信息（截图或日志），我可以进一步调整策略。