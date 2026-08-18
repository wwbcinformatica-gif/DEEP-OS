# iFrames

## Find iframe Target

```python
from browser.helpers import iframe_target, js

# Find iframe by URL substring
target = iframe_target("iframe-url-substring")

# Execute JS in iframe
result = js("document.title", target_id=target)
```

## Cross-Origin iframes

CDP can cross origin boundaries that JavaScript cannot.

```python
from browser.helpers import cdp

# Get all frames
tree = cdp("Page.getFrameTree")
for frame in tree["frameTree"].get("childFrames", []):
    print(frame["frame"]["url"])
```

## Click in iframe

```python
from browser.helpers import cdp, click_at_xy

# Get iframe box model
doc = cdp("DOM.getDocument")
iframe_node = cdp("DOM.querySelector", nodeId=doc["root"]["nodeId"], selector="iframe")
box = cdp("DOM.getBoxModel", nodeId=iframe_node["nodeId"])

# Calculate click position relative to iframe
content = box["model"]["content"]
iframe_x = sum(content[0::2]) / 4
iframe_y = sum(content[1::2]) / 4

# Click at offset within iframe
click_at_xy(iframe_x + 50, iframe_y + 30)
```
