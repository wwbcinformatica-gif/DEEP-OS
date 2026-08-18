# Viewport

## Get Viewport Size

```python
from browser.helpers import js

size = js("JSON.stringify({w: innerWidth, h: innerHeight, dpr: devicePixelRatio})")
```

## Resize Viewport

```python
from browser.helpers import cdp

cdp("Emulation.setDeviceMetricsOverride", width=1920, height=1080, deviceScaleFactor=1, mobile=False)
```

## Reset Viewport

```python
cdp("Emulation.clearDeviceMetricsOverride")
```

## Mobile Viewport

```python
cdp("Emulation.setDeviceMetricsOverride",
    width=375, height=812,
    deviceScaleFactor=3, mobile=True,
    screenWidth=375, screenHeight=812)
```
