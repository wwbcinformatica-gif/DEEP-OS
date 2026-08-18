# Cookies

## Reading Cookies

```python
js("JSON.stringify(document.cookie)")
```

## Setting Cookies

```python
js("document.cookie = 'name=value; path=/; max-age=86400'")
```

## Clearing Cookies

```python
js("document.cookie.split(';').forEach(c => { document.cookie = c.trim().split('=')[0] + '=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/' })")
```

## Via CDP

```python
from browser.helpers import cdp

# Get all cookies
cookies = cdp("Network.getCookies")

# Set cookie
cdp("Network.setCookie", name="key", value="val", domain="example.com")

# Clear cookies
cdp("Network.clearBrowserCookies")
```
