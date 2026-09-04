"""Download image from URL and save locally."""
import os
import requests
from pathlib import Path


def download_image(url: str, save_path: str = "", filename: str = "") -> str:
    """Download image from URL and save to local path."""
    try:
        if not url:
            return "Error: No URL provided"
        
        # Default save directory
        if not save_path:
            save_path = str(Path.home() / "Downloads")
        
        # Generate filename if not provided
        if not filename:
            from datetime import datetime
            filename = f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Ensure save directory exists
        save_dir = Path(save_path)
        if not save_dir.exists():
            save_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine file extension from URL or content-type
        if "." not in filename:
            # Try to get extension from URL
            url_path = url.split("?")[0]
            if "." in url_path.split("/")[-1]:
                ext = "." + url_path.split("/")[-1].split(".")[-1]
            else:
                ext = ".jpg"  # default
            filename = filename + ext
        
        # Full file path
        file_path = save_dir / filename
        
        # Download with timeout and headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()
        
        # Save file
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        file_size = os.path.getsize(file_path)
        return f"Image saved to: {file_path} ({file_size:,} bytes)"
    
    except requests.exceptions.Timeout:
        return "Error: Download timeout (30s)"
    except requests.exceptions.RequestException as e:
        return f"Error downloading image: {str(e)[:200]}"
    except Exception as e:
        return f"Error: {str(e)[:200]}"
