import os
import httpx
from typing import Optional

def get_proxy_client() -> Optional[httpx.Client]:
    """Create an httpx client with proxy configuration if proxy environment variables are set."""
    proxy = os.getenv("ALL_PROXY") or os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
    
    if proxy:
        # Create httpx client with SOCKS5 proxy support
        return httpx.Client(
            proxy=proxy,
            timeout=httpx.Timeout(30.0),
            verify=True,
            follow_redirects=True
        )
    return None

def get_async_proxy_client() -> Optional[httpx.AsyncClient]:
    """Create an async httpx client with proxy configuration if proxy environment variables are set."""
    proxy = os.getenv("ALL_PROXY") or os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
    
    if proxy:
        # Create async httpx client with SOCKS5 proxy support
        return httpx.AsyncClient(
            proxy=proxy,
            timeout=httpx.Timeout(30.0),
            verify=True,
            follow_redirects=True
        )
    return None