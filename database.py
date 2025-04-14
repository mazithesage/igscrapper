"""
Database Management Module
========================
Handles database operations for storing scraped reel data
"""

import os
from typing import List, Dict
from pymongo import MongoClient
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        # MongoDB connection
        MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        self.client = MongoClient(MONGO_URI)
        self.db = self.client['instagram_scraper']
        self.reels = self.db['reels']
        
        # Create indexes
        self.reels.create_index('reel_id', unique=True)
        self.reels.create_index('scraped_at')
        
    def is_reel_processed(self, reel_url: str) -> bool:
        """Check if a reel has already been processed"""
        return bool(self.reels.find_one({'reel_url': reel_url}))
        
    def bulk_insert_reels(self, reel_data: List[Dict]):
        """Insert multiple reel records efficiently"""
        if not reel_data:
            return
            
        try:
            self.reels.insert_many(reel_data, ordered=False)
        except Exception as e:
            print(f"Error in bulk insert: {e}")
            
    def get_stats(self) -> Dict:
        """Get scraping statistics"""
        now = datetime.now()
        last_24h = {
            'total_reels': self.reels.count_documents({}),
            'last_24h': self.reels.count_documents({
                'scraped_at': {'$gte': now - timedelta(days=1)}
            }),
            'last_hour': self.reels.count_documents({
                'scraped_at': {'$gte': now - timedelta(hours=1)}
            })
        }
        return last_24h
        
    def cleanup_old_data(self, days: int = 30):
        """Clean up data older than specified days"""
        cutoff = datetime.now() - timedelta(days=days)
        self.reels.delete_many({
            'scraped_at': {'$lt': cutoff}
        })
