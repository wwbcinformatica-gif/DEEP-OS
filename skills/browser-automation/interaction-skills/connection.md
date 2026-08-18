# Connection

## Local Chrome

The daemon connects to the running Chrome/Chromium CDP endpoint.

### Troubleshooting

1. **Chrome not running**: Start Chrome normally
2. **Remote debugging not enabled**: Open `chrome://inspect/#remote-debugging` and tick the checkbox
3. **Permission popup**: Click "Allow" when Chrome asks "Allow remote debugging?"
4. **macOS permission**: Run `browser-harness mac-approve` or click Allow in the popup

### Diagnostics

```bash
curl http://localhost:8001/browser/doctor
```

## Remote Browsers

Use Browser Use Cloud for headless servers, parallel sub-agents, or isolated work.

```bash
# Authenticate
browser-harness auth login

# Start remote daemon
browser-harness <<'PY'
start_remote_daemon("my-browser")
PY

# Use it
BU_NAME=my-browser browser-harness <<'PY'
print(page_info())
PY
```

## CDP URL Override

Set `BU_CDP_WS` or `BU_CDP_URL` for custom Chrome instances:

```bash
export BU_CDP_URL=http://127.0.0.1:9222
```
