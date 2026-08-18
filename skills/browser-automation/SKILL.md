---
name: browser-automation
description: "Use browser-automation for any web interaction: automation, scraping, testing, or site/app work via CDP."
---

# browser-automation

Direct browser control via CDP (Chrome DevTools Protocol). Connects to the user's real Chrome/Chromium browser.

## When to Use

- Web automation, scraping, testing
- Tasks requiring user's logged-in session
- JS-rendered pages
- Bot-protected sites
- Any task needing interaction (click, type, navigate)

## When NOT to Use

- Simple HTTP fetch of public info (use http_get instead)
- API calls (use http_get instead)

## Usage

```python
from browser.helpers import goto_url, page_info, click_at_xy, js, capture_screenshot

# Navigate
goto_url("https://google.com")

# Get page info
info = page_info()
print(info["url"], info["title"])

# Click at coordinates
click_at_xy(100, 200)

# Execute JavaScript
title = js("document.title")

# Screenshot
path = capture_screenshot("/tmp/shot.png")
```

## Key Functions

### Navigation
- `goto_url(url)` — Navigate to URL
- `page_info()` — Get {url, title, w, h, sx, sy, pw, ph}
- `wait_for_load(timeout)` — Wait for page load

### Input
- `click_at_xy(x, y, button, clicks)` — Click at coordinates
- `type_text(text)` — Type text
- `fill_input(selector, text)` — Fill input (React/Vue compatible)
- `press_key(key, modifiers)` — Press key (1=Alt, 2=Ctrl, 4=Cmd, 8=Shift)
- `scroll(x, y, dy, dx)` — Scroll
- `dispatch_key(selector, key)` — DOM keyboard event

### Visual
- `capture_screenshot(path, full, max_dim)` — PNG screenshot
- `js(expression)` — Execute JavaScript

### Tabs
- `list_tabs()` — List all tabs
- `current_tab()` — Get current tab
- `new_tab(url)` — Open new tab
- `switch_tab(target, activate)` — Switch tab
- `close_tab(target)` — Close tab
- `ensure_real_tab()` — Switch to real user tab

### Utilities
- `wait(seconds)` — Sleep
- `wait_for_element(selector, timeout)` — Wait for DOM element
- `wait_for_network_idle(timeout)` — Wait for network idle
- `iframe_target(url_substr)` — Find iframe target
- `upload_file(selector, path)` — Upload file
- `http_get(url, headers, timeout)` — Pure HTTP fetch

## Setup

Chrome must be running with remote debugging enabled:
1. Open `chrome://inspect/#remote-debugging`
2. Tick "Allow remote debugging for this browser instance"
3. The daemon connects automatically

## Architecture

```
Agent/Charon → helpers.py → IPC socket → daemon.py → CDP WebSocket → Chrome
```

- **daemon.py**: Long-lived process holding CDP connection
- **helpers.py**: Python API imported by agents
- **ipc.py**: Unix socket (POSIX) or TCP loopback (Windows)
- **admin.py**: Diagnostics and daemon lifecycle
- **recorder.py**: Session recording (screenshots + traces)
