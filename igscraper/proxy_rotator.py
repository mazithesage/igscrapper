# igscraper/proxy_rotator.py
# Handles loading and rotating proxies from a file.

import random
from itertools import cycle
from pathlib import Path
from typing import List, Optional, Iterator

from .logger import Logger # Use relative import within the package

class ProxyRotator:
    """Loads proxies from a file and provides them in a round-robin fashion."""

    def __init__(self, proxy_file: Optional[str]):
        """Initializes the rotator.

        Args:
            proxy_file: Path to the file containing proxies (one per line).
                        If None or empty, rotation is disabled.
        """
        self.proxies: List[str] = []
        self.proxy_cycler: Optional[Iterator[str]] = None
        self.enabled = False

        if not proxy_file:
            Logger.info("No proxy file provided. Proxy rotation disabled.")
            return

        file_path = Path(proxy_file)
        if not file_path.is_file():
            Logger.warning(f"Proxy file not found at {file_path}. Proxy rotation disabled.")
            return

        try:
            with open(file_path, 'r') as f:
                # Read lines, strip whitespace, filter out empty lines
                self.proxies = [line.strip() for line in f if line.strip()]
            
            if not self.proxies:
                Logger.warning(f"Proxy file {file_path} is empty. Proxy rotation disabled.")
                return

            # Use itertools.cycle for efficient round-robin
            self.proxy_cycler = cycle(self.proxies)
            self.enabled = True
            Logger.info(f"Initialized proxy rotator with {len(self.proxies)} proxies from {file_path}.")
            # Optionally shuffle proxies initially?
            # random.shuffle(self.proxies)
            # self.proxy_cycler = cycle(self.proxies)

        except Exception as e:
            Logger.error(f"Error reading proxy file {file_path}: {e}. Proxy rotation disabled.")
            self.proxies = []
            self.proxy_cycler = None
            self.enabled = False

    def get_next_proxy(self) -> Optional[str]:
        """Returns the next proxy in the rotation, or None if disabled."""
        if not self.enabled or not self.proxy_cycler:
            return None
        
        try:
            # Get the next proxy from the cycle
            next_proxy = next(self.proxy_cycler)
            # Logger.info(f"Using proxy: {next_proxy}") # Log proxy usage (can be verbose)
            return next_proxy
        except StopIteration: # Should not happen with cycle, but as safeguard
            Logger.error("Proxy cycler unexpectedly stopped.")
            self.enabled = False
            return None 