---
name: agent-browser
description: "Headless browser automation for AI agents. Control a headless browser via CLI (based on Playwright/WebDriver). Use when you need to: navigate to a URL, take a screenshot, extract text, click elements, or run scripts in a browser context."
---

# Agent Browser

Use the `agent-browser` CLI to automate browser tasks.

## Requirements

- The `agent-browser` binary must be installed (globally or in PATH). Install with:
  ```bash
  npm install -g agent-browser
  ```

## Commands

Run from the OpenClaw workspace:

```bash
# Navigate to a URL (and wait for load)
agent-browser open https://example.com

# Take a screenshot
agent-browser screenshot --output /tmp/screenshot.png

# Extract page text
agent-browser text

# Click a CSS selector
agent-browser click "button.submit"

# Evaluate JavaScript and return result
agent-browser eval "document.title"

# Run a custom script file
agent-browser run script.js
```

Notes:
- The tool manages a headless Chromium instance via Playwright.
- It supports multiple sessions (contexts). Use `--context` to separate.
- For long-running agents, consider starting a persistent session: `agent-browser start` then reuse with `agent-browser connect`.

See `agent-browser --help` for full options.