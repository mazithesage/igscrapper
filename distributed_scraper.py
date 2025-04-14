"""
Distributed Instagram Reels Scraper
=================================
Scales to 3M+ reels per day using distributed architecture
"""

import os
import time
import json
import logging
import asyncio
import aiohttp
from redis import Redis
from rq import Queue, Worker, Connection
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor
from proxy_rotation import ProxyRotator  # Custom proxy rotation
from database import DatabaseManager  # Custom database management
from main import get_reel_info, setup_driver  # Reusing core scraping logic

# Configuration
MAX_WORKERS = 50  # Number of parallel browser instances
REEL_BATCH_SIZE = 100  # Number of reels per batch
RATE_LIMIT_REELS = 20  # Reels per minute per worker
PROXY_ROTATION_INTERVAL = 100  # Rotate proxy every N requests

# Redis configuration for job queue
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
redis_conn = Redis(host=REDIS_HOST, port=REDIS_PORT)
job_queue = Queue(connection=redis_conn)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('distributed_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DistributedScraper:
    def __init__(self):
        self.db = DatabaseManager()
        self.proxy_rotator = ProxyRotator()
        self.executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
        
    async def process_reel_batch(self, reel_urls):
        """Process a batch of reels using multiple workers"""
        tasks = []
        for url in reel_urls:
            if not self.db.is_reel_processed(url):
                tasks.append(self.scrape_single_reel(url))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        successful_results = [r for r in results if isinstance(r, dict)]
        self.db.bulk_insert_reels(successful_results)
        
    async def scrape_single_reel(self, reel_url):
        """Scrape a single reel with proxy rotation and rate limiting"""
        try:
            proxy = self.proxy_rotator.get_next_proxy()
            driver = setup_driver(proxy=proxy)
            
            # Rate limiting
            await asyncio.sleep(60 / RATE_LIMIT_REELS)
            
            reel_data = get_reel_info(driver, reel_url)
            if reel_data:
                reel_data['scraped_at'] = time.time()
                reel_data['proxy_used'] = proxy
                return reel_data
                
        except Exception as e:
            logger.error(f"Error scraping reel {reel_url}: {str(e)}")
            return None
        finally:
            if driver:
                driver.quit()

    def enqueue_reel_batches(self, reel_urls):
        """Split reels into batches and enqueue for processing"""
        for i in range(0, len(reel_urls), REEL_BATCH_SIZE):
            batch = reel_urls[i:i + REEL_BATCH_SIZE]
            job_queue.enqueue(self.process_reel_batch, batch)

def start_worker():
    """Start a worker process to handle jobs from the queue"""
    with Connection(redis_conn):
        worker = Worker([job_queue])
        worker.work()

if __name__ == "__main__":
    # Calculate required throughput
    DAILY_TARGET = 3_000_000
    HOURLY_TARGET = DAILY_TARGET / 24
    MINUTE_TARGET = HOURLY_TARGET / 60
    
    logger.info(f"Starting distributed scraper targeting {DAILY_TARGET:,} reels per day")
    logger.info(f"Required throughput: {HOURLY_TARGET:,.0f} reels/hour ({MINUTE_TARGET:,.0f} reels/minute)")
    
    # Start the distributed system
    scraper = DistributedScraper()
    
    # Start worker processes
    worker_processes = []
    for _ in range(MAX_WORKERS):
        worker_processes.append(start_worker())
