# Tabs

## List Tabs

```python
from browser.helpers import list_tabs

tabs = list_tabs()
for t in tabs:
    print(f"{t['title']} - {t['url']}")
```

## New Tab

```python
from browser.helpers import new_tab

# Open new tab with URL
target_id = new_tab("https://google.com")

# Open blank tab
target_id = new_tab()
```

## Switch Tab

```python
from browser.helpers import switch_tab, current_tab

# Get current
cur = current_tab()

# Switch to specific tab
switch_tab("target-id-here")

# Switch without changing visible Chrome tab
switch_tab("target-id", activate=False)

# Make tab visible in Chrome
switch_tab("target-id", activate=True)
```

## Close Tab

```python
from browser.helpers import close_tab

# Close current tab
close_tab()

# Close specific tab
close_tab("target-id")
```

## Ensure Real Tab

```python
from browser.helpers import ensure_real_tab

# Switch away from chrome:// or internal pages
ensure_real_tab()
```
