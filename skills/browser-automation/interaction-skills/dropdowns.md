# Dropdowns

## Select Element

```python
from browser.helpers import js, click_at_xy

# Get select bounds and click to open
js("""
const sel = document.querySelector('select');
const rect = sel.getBoundingClientRect();
// return center coordinates
JSON.stringify({x: rect.x + rect.width/2, y: rect.y + rect.height/2});
""")
# Then click_at_xy with returned coordinates
```

## Programmatic Selection

```python
js("""
const sel = document.querySelector('select');
sel.value = 'option-value';
sel.dispatchEvent(new Event('change', {bubbles: true}));
""")
```

## React/Vue Selects

```python
from browser.helpers import fill_input

# For searchable selects, type to filter
fill_input('input[type="search"]', 'option text')
```
