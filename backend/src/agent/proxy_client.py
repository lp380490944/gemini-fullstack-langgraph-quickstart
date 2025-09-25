import os
import httpx
from typing import Optional, Dict, Any

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

def get_google_genai_kwargs(base_kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Configure Google Generative AI client with proxy support.
    Since langchain-google-genai has limited proxy support, we use transport='rest'
    and rely on environment variables for proxy configuration.
    """
    proxy = os.getenv("ALL_PROXY") or os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
    
    if proxy:
        # Use REST transport which is more likely to respect environment proxy variables
        base_kwargs["transport"] = "rest"
        
        # Print proxy info for debugging
        print(f"🔧 Proxy detected: {proxy.split('@')[-1] if '@' in proxy else proxy}")
        print("🔧 Using transport='rest' for better proxy compatibility")
    
    return base_kwargs