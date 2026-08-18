# Scrolling

## Basic Scroll

```python
from browser.helpers import scroll

# Scroll down 300px at center of viewport
scroll(400, 300, dy=-300)

# Scroll up
scroll(400, 300, dy=300)

# Horizontal scroll
scroll(400, 300, dx=100)
```

## Scroll to Element

```python
js("document.querySelector('.target').scrollIntoView({behavior: 'smooth'})")
```

## Scroll to Top/Bottom

```python
# Top
js("window.scrollTo(0, 0)")

# Bottom
js("window.scrollTo(0, document.body.scrollHeight)")

# By pixels
js("window.scrollBy(0, 500)")
```

## Check Scroll Position

```python
js("JSON.stringify({scrollX: window.scrollX, scrollY: window.scrollY, maxScroll: document.body.scrollHeight - window.innerHeight})")
```
