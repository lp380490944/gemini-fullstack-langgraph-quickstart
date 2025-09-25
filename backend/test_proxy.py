#!/usr/bin/env python3
"""Test script to verify SOCKS5 proxy configuration for Google Generative AI."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_direct_connection():
    """Test direct connection without proxy."""
    print("=" * 60)
    print("Testing DIRECT connection (without proxy)...")
    print("=" * 60)
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0,
            api_key=os.getenv("GEMINI_API_KEY"),
        )
        
        response = llm.invoke("Say 'Hello, direct connection works!' in exactly 5 words")
        print("✅ Direct connection successful!")
        print(f"Response: {response.content}")
        return True
    except Exception as e:
        print(f"❌ Direct connection failed: {str(e)}")
        return False

def test_proxy_connection():
    """Test connection through SOCKS5 proxy using transport='rest'."""
    print("\n" + "=" * 60)
    print("Testing PROXY connection (with SOCKS5)...")
    print("=" * 60)
    
    # Check if proxy is configured
    proxy = os.getenv("ALL_PROXY") or os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
    if not proxy:
        print("⚠️  No proxy configured in environment variables!")
        print("   Please uncomment proxy settings in .env file")
        return False
    
    print(f"📡 Using proxy: {proxy.split('@')[-1] if '@' in proxy else proxy}")
    print("📡 Using transport='rest' for proxy compatibility")
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0,
            api_key=os.getenv("GEMINI_API_KEY"),
            transport="rest"  # Use REST transport for better proxy support
        )
        
        response = llm.invoke("Say 'Hello, proxy connection works!' in exactly 5 words")
        print("✅ Proxy connection successful!")
        print(f"Response: {response.content}")
        return True
    except Exception as e:
        print(f"❌ Proxy connection failed: {str(e)}")
        if "location is not supported" in str(e).lower():
            print("   💡 This suggests the proxy may not be working.")
            print("      Check your SOCKS5 proxy server and credentials.")
        return False

def test_google_genai_client():
    """Test google.genai Client with proxy via environment variables."""
    print("\n" + "=" * 60)
    print("Testing google.genai Client...")
    print("=" * 60)
    
    proxy = os.getenv("ALL_PROXY") or os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
    
    try:
        from google.genai import Client
        
        if proxy:
            print(f"📡 Proxy configured in environment: {proxy.split('@')[-1] if '@' in proxy else proxy}")
            print("   Note: google.genai Client uses environment proxy variables automatically")
        else:
            print("⚠️  No proxy configured, using direct connection")
        
        # google.genai Client will automatically use proxy from environment variables
        client = Client(api_key=os.getenv("GEMINI_API_KEY"))
        
        # Test with a simple generation
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents="What is 2+2? Answer with just the number.",
        )
        
        print("✅ google.genai Client connection successful!")
        print(f"Response: {response.text}")
        return True
    except Exception as e:
        print(f"❌ google.genai Client connection failed: {str(e)}")
        if "location is not supported" in str(e).lower():
            print("   💡 This error suggests the proxy is not being used.")
            print("      google.genai Client should use environment proxy automatically.")
        return False

def check_network_connectivity():
    """Check basic network and proxy connectivity."""
    print("\n" + "=" * 60)
    print("Checking network connectivity...")
    print("=" * 60)
    
    import httpx
    
    # Test basic internet connectivity
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get("https://www.google.com")
        print("✅ Direct internet connection: OK")
    except Exception as e:
        print(f"❌ Direct internet connection: Failed - {str(e)}")
    
    # Test proxy connectivity if configured
    proxy = os.getenv("ALL_PROXY") or os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
    if proxy:
        try:
            with httpx.Client(proxy=proxy, timeout=10.0) as client:
                response = client.get("https://www.google.com")
            print(f"✅ Proxy connection ({proxy.split('@')[-1] if '@' in proxy else proxy}): OK")
        except Exception as e:
            print(f"❌ Proxy connection: Failed - {str(e)}")

def main():
    """Main test function."""
    print("\n🔧 Google Generative AI Proxy Configuration Test")
    print("=" * 60)
    
    # Check API key
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ GEMINI_API_KEY not found in environment!")
        print("   Please set it in your .env file")
        sys.exit(1)
    else:
        print(f"✅ GEMINI_API_KEY found: {os.getenv('GEMINI_API_KEY')[:10]}...")
    
    # Check proxy configuration
    proxy_vars = {
        "ALL_PROXY": os.getenv("ALL_PROXY"),
        "HTTPS_PROXY": os.getenv("HTTPS_PROXY"),
        "HTTP_PROXY": os.getenv("HTTP_PROXY"),
        "NO_PROXY": os.getenv("NO_PROXY")
    }
    
    print("\n📋 Current proxy configuration:")
    for var, value in proxy_vars.items():
        if value:
            if "proxy" in var.lower() and var != "NO_PROXY" and "@" in str(value):
                # Hide credentials in proxy URL
                display_value = value.split("@")[-1] if "@" in value else value
                print(f"   {var}: ***@{display_value}")
            else:
                print(f"   {var}: {value}")
        else:
            print(f"   {var}: [Not set]")
    
    # Run tests
    print("\n🧪 Running connection tests...")
    
    # Check basic network connectivity first
    check_network_connectivity()
    
    # Test without proxy (comment out proxy vars temporarily)
    original_proxy = os.environ.pop("ALL_PROXY", None)
    original_https = os.environ.pop("HTTPS_PROXY", None)
    original_http = os.environ.pop("HTTP_PROXY", None)
    
    direct_result = test_direct_connection()
    
    # Restore proxy vars if they existed
    if original_proxy:
        os.environ["ALL_PROXY"] = original_proxy
    if original_https:
        os.environ["HTTPS_PROXY"] = original_https
    if original_http:
        os.environ["HTTP_PROXY"] = original_http
    
    # Test with proxy
    proxy_result = test_proxy_connection()
    genai_result = test_google_genai_client()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Direct connection: {'✅ PASS' if direct_result else '❌ FAIL'}")
    print(f"Proxy connection (langchain): {'✅ PASS' if proxy_result else '❌ FAIL'}")
    print(f"Proxy connection (google.genai): {'✅ PASS' if genai_result else '❌ FAIL'}")
    
    if not (direct_result or proxy_result or genai_result):
        print("\n⚠️  All connections failed!")
        print("   Possible issues:")
        print("   1. Check your GEMINI_API_KEY is valid")
        print("   2. Check your internet connection")
        print("   3. If using proxy, verify proxy server is accessible")
        print("   4. Ensure proxy credentials are correct")
    elif proxy_result or genai_result:
        print("\n✅ Proxy configuration is working correctly!")
    else:
        print("\n⚠️  Proxy not working, but direct connection works.")
        print("   Check your proxy configuration in .env file")

if __name__ == "__main__":
    main()