# Drag and Drop

## Native CDP Drag

```python
from browser.helpers import cdp

# Mouse down on source
cdp("Input.dispatchMouseEvent", type="mousePressed", x=100, y=100, button="left", clickCount=1)

# Mouse move to target
cdp("Input.dispatchMouseEvent", type="mouseMoved", x=300, y=300)

# Mouse up on target
cdp("Input.dispatchMouseEvent", type="mouseReleased", x=300, y=300, button="left", clickCount=1)
```

## JavaScript Drag (for frameworks)

```python
js("""
const source = document.querySelector('.draggable');
const target = document.querySelector('.drop-zone');

const dataTransfer = new DataTransfer();
source.addEventListener('dragstart', e => e.dataTransfer = dataTransfer);
target.addEventListener('dragover', e => e.preventDefault());
target.addEventListener('drop', e => e.dataTransfer = dataTransfer);

source.dispatchEvent(new DragEvent('dragstart', {dataTransfer}));
target.dispatchEvent(new DragEvent('dragover', {dataTransfer}));
target.dispatchEvent(new DragEvent('drop', {dataTransfer}));
""")
```
