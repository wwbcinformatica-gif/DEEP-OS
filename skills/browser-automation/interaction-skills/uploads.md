# Uploads

## File Input Upload

```python
from browser.helpers import upload_file

# Upload to file input element
upload_file('input[type="file"]', '/path/to/file.pdf')

# Upload multiple files
upload_file('input[type="file"]', ['/path/to/file1.pdf', '/path/to/file2.pdf'])
```

## Drag and Drop Upload

```python
js("""
const input = document.querySelector('input[type="file"]');
const dt = new DataTransfer();
const file = new File(['content'], 'file.txt', {type: 'text/plain'});
dt.items.add(file);
input.files = dt.files;
input.dispatchEvent(new Event('change', {bubbles: true}));
""")
```

## Find File Inputs

```python
js("""
Array.from(document.querySelectorAll('input[type="file"]')).map(el => ({
    id: el.id,
    name: el.name,
    accept: el.accept,
    multiple: el.multiple
}))
""")
```
