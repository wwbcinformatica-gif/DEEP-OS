# Screenshots

## Basic Screenshot

```python
from browser.helpers import capture_screenshot

# Save to default location
path = capture_screenshot()

# Save to specific path
path = capture_screenshot("/tmp/screenshot.png")

# Full page screenshot
path = capture_screenshot(full=True)

# Limit dimensions (for LLMs with size limits)
path = capture_screenshot(max_dim=1800)
```

## Screenshot via CDP

```python
from browser.helpers import cdp
import base64

# Viewport screenshot
shot = cdp("Page.captureScreenshot", format="png")
data = base64.b64decode(shot["data"])
open("shot.png", "wb").write(data)

# Full page
shot = cdp("Page.captureScreenshot", format="png", captureBeyondViewport=True)

# JPEG with quality
shot = cdp("Page.captureScreenshot", format="jpeg", quality=80)
```

## Element Screenshot

```python
js("""
const el = document.querySelector('.target-element');
el.scrollIntoView();
// Return element bounds for cropping
const rect = el.getBoundingClientRect();
JSON.stringify({x: rect.x, y: rect.y, w: rect.width, h: rect.height});
""")
```
