# Dialogs

## Detect Dialog

```python
from browser.helpers import page_info

info = page_info()
if "dialog" in info:
    dialog = info["dialog"]
    print(f"Type: {dialog['type']}, Message: {dialog['message']}")
```

## Accept Dialog

```python
from browser.helpers import cdp

cdp("Page.handleJavaScriptDialog", accept=True)
```

## Dismiss Dialog

```python
cdp("Page.handleJavaScriptDialog", accept=False)
```

## Accept with Prompt Value

```python
cdp("Page.handleJavaScriptDialog", accept=True, promptText="user input")
```
