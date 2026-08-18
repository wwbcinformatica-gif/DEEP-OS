"""Config helper — compatibilidade com actions do WBC-Mark-L."""
import platform

def get_os() -> str:
    return platform.system().lower()

def is_windows() -> bool:
    return get_os() == "windows"

def is_mac() -> bool:
    return get_os() == "mac"

def is_linux() -> bool:
    return get_os() == "linux"
