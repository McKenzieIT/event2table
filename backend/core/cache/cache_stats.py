"""
Cache Statistics Module

Provides cache statistics collection and reporting functionality.
Tracks cache hits, misses, usage patterns, and performance metrics.
"""

import time
import threading
from collections import defaultdict
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class CacheStats:
    """
    Cache Statistics Collector
    
    Collects and analyzes cache performance metrics.
    Thread-safe implementation for concurrent access.
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'evictions': 0,
        }
        self._key_stats = defaultdict(lambda: {
            'hits': 0,
            'misses': 0,
            'last_access': None,
        })
        self._start_time = time.time()
        self._hourly_stats = defaultdict(lambda: {
            'hits': 0,
            'misses': 0,
            'requests': 0,
        })
    
    def record_hit(self, key: str):
        """Record a cache hit"""
        with self._lock:
            self._stats['hits'] += 1
            self._key_stats[key]['hits'] += 1
            self._key_stats[key]['last_access'] = time.time()
            
            # Record hourly stats
            hour = int(time.time() // 3600)
            self._hourly_stats[hour]['hits'] += 1
            self._hourly_stats[hour]['requests'] += 1
    
    def record_miss(self, key: str):
        """Record a cache miss"""
        with self._lock:
            self._stats['misses'] += 1
            self._key_stats[key]['misses'] += 1
            self._key_stats[key]['last_access'] = time.time()
            
            # Record hourly stats
            hour = int(time.time() // 3600)
            self._hourly_stats[hour]['misses'] += 1
            self._hourly_stats[hour]['requests'] += 1
    
    def record_set(self, key: str):
        """Record a cache set operation"""
        with self._lock:
            self._stats['sets'] += 1
    
    def record_delete(self, key: str):
        """Record a cache delete operation"""
        with self._lock:
            self._stats['deletes'] += 1
    
    def record_eviction(self, key: str):
        """Record a cache eviction"""
        with self._lock:
            self._stats['evictions'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current cache statistics"""
        with self._lock:
            total_requests = self._stats['hits'] + self._stats['misses']
            hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            uptime = time.time() - self._start_time
            requests_per_second = total_requests / uptime if uptime > 0 else 0
            
            return {
                'total': {
                    'hits': self._stats['hits'],
                    'misses': self._stats['misses'],
                    'sets': self._stats['sets'],
                    'deletes': self._stats['deletes'],
                    'evictions': self._stats['evictions'],
                    'total_requests': total_requests,
                },
                'rates': {
                    'hit_rate': f"{hit_rate:.2f}%",
                    'miss_rate': f"{100 - hit_rate:.2f}%",
                    'requests_per_second': f"{requests_per_second:.2f}",
                },
                'uptime': {
                    'seconds': int(uptime),
                    'hours': f"{uptime / 3600:.2f}",
                    'start_time': self._start_time,
                },
                'keys': {
                    'total_keys': len(self._key_stats),
                    'top_keys': self._get_top_keys(10),
                },
            }
    
    def get_hourly_stats(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get hourly statistics for the last N hours"""
        with self._lock:
            current_hour = int(time.time() // 3600)
            stats = []
            
            for i in range(hours):
                hour = current_hour - i
                hour_stats = self._hourly_stats.get(hour, {
                    'hits': 0,
                    'misses': 0,
                    'requests': 0,
                })
                
                total = hour_stats['requests']
                hit_rate = (hour_stats['hits'] / total * 100) if total > 0 else 0
                
                stats.append({
                    'hour': hour,
                    'timestamp': hour * 3600,
                    'hits': hour_stats['hits'],
                    'misses': hour_stats['misses'],
                    'requests': total,
                    'hit_rate': f"{hit_rate:.2f}%",
                })
            
            return stats
    
    def _get_top_keys(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top N most accessed keys"""
        sorted_keys = sorted(
            self._key_stats.items(),
            key=lambda x: x[1]['hits'] + x[1]['misses'],
            reverse=True
        )[:limit]
        
        return [
            {
                'key': key,
                'hits': stats['hits'],
                'misses': stats['misses'],
                'total_access': stats['hits'] + stats['misses'],
                'last_access': stats['last_access'],
            }
            for key, stats in sorted_keys
        ]
    
    def reset(self):
        """Reset all statistics"""
        with self._lock:
            self._stats = {
                'hits': 0,
                'misses': 0,
                'sets': 0,
                'deletes': 0,
                'evictions': 0,
            }
            self._key_stats.clear()
            self._hourly_stats.clear()
            self._start_time = time.time()


# Global cache stats instance
_cache_stats = None


def get_cache_stats() -> CacheStats:
    """Get or create cache stats instance"""
    global _cache_stats
    if _cache_stats is None:
        _cache_stats = CacheStats()
    return _cache_stats
