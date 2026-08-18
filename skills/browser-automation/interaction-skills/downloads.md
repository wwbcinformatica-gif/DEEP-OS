# Downloads

## Monitoring Downloads

CDP events track download progress:

```python
from browser.helpers import cdp, drain_events

# Enable download events
cdp("Page.setDownloadBehavior", behavior="allow", downloadPath="/tmp/downloads")

# Check events
events = drain_events()
for e in events:
    if e["method"] == "Page.downloadProgress":
        print(f"Download: {e['params']['receivedBytes']} bytes")
```

## Download via JavaScript

```python
js("""
const a = document.createElement('a');
a.href = 'https://example.com/file.pdf';
a.download = 'file.pdf';
document.body.appendChild(a);
a.click();
a.remove();
""")
```

## Save Page as PDF

```python
cdp("Page.printToPDF", landscape=False, printBackground=True)
```
