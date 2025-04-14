"""
Proxy Rotation Module
===================
Handles proxy rotation and management for distributed scraping
"""

import random
import requests
import time
from typing import Optional, List, Dict

class ProxyRotator:
    def __init__(self):
        self.proxies: List[Dict[str, str]] = []
        self.current_index = 0
        self.last_refresh = 0
        self.refresh_interval = 3600  # Refresh proxy list every hour
        
    def refresh_proxies(self):
        """Refresh the proxy list from your proxy provider"""
        try:
            # Replace with your proxy provider's API
            response = requests.get('YOUR_PROXY_PROVIDER_API')
            if response.status_code == 200:
                self.proxies = response.json()
                self.last_refresh = time.time()
        except Exception as e:
            print(f"Error refreshing proxies: {e}")
    
    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        """Get the next proxy from the rotation"""
        if not self.proxies or time.time() - self.last_refresh > self.refresh_interval:
            self.refresh_proxies()
            
        if not self.proxies:
            return None
            
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy
        
    def mark_proxy_failed(self, proxy: Dict[str, str]):
        """Mark a proxy as failed and remove it from rotation"""
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            
    def get_proxy_count(self) -> int:
        """Get the number of available proxies"""
        return len(self.proxies)
