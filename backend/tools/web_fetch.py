"""
Web Fetch Tool — busca URL e retorna como texto markdown.
Suporta fallback automatico e headers realistas de navegador.
"""
import re
import time

import httpx

_REAL_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}


def _html_to_text(html: str) -> str:
    """Converte HTML para texto limpo."""
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    text = re.sub(r'<nav[^>]*>.*?</nav>', '', text, flags=re.DOTALL)
    text = re.sub(r'<header[^>]*>.*?</header>', '', text, flags=re.DOTALL)
    text = re.sub(r'<footer[^>]*>.*?</footer>', '', text, flags=re.DOTALL)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


async def tool_web_fetch(url: str, prompt: str = "") -> dict:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    start = time.time()

    # Tenta com headers completos primeiro (HTTP/2)
    try:
        async with httpx.AsyncClient(
            timeout=30,
            follow_redirects=True,
            headers=_REAL_HEADERS,
            http2=True,
        ) as client:
            resp = await client.get(url)

            # Se 403, tenta via Google Cache
            if resp.status_code == 403:
                cache_url = f"https://webcache.googleusercontent.com/search?q=cache:{url}"
                try:
                    resp2 = await client.get(cache_url)
                    if resp2.status_code == 200:
                        html = resp2.text
                        text = _html_to_text(html)[:50000]
                        return {
                            "url": url,
                            "content": text,
                            "note": "Conteudo obtido via Google Cache (original retornou 403)",
                            "duration_seconds": round(time.time() - start, 2),
                        }
                except Exception:
                    pass

            resp.raise_for_status()
            html = resp.text
            text = _html_to_text(html)[:50000]

            return {
                "url": url,
                "content": text,
                "status": resp.status_code,
                "duration_seconds": round(time.time() - start, 2),
            }

    except Exception as e:
        # Fallback: tenta sem HTTP/2
        try:
            async with httpx.AsyncClient(
                timeout=30,
                follow_redirects=True,
                headers=_REAL_HEADERS,
                http2=False,
            ) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                html = resp.text
                text = _html_to_text(html)[:50000]
                return {
                    "url": url,
                    "content": text,
                    "status": resp.status_code,
                    "note": "Obtido via HTTP/1.1 (HTTP/2 falhou)",
                    "duration_seconds": round(time.time() - start, 2),
                }
        except Exception:
            pass

        return {
            "url": url,
            "content": "",
            "error": str(e)[:200],
            "duration_seconds": round(time.time() - start, 2),
        }
