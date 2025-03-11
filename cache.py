# from cachetools import TTLCache
# import logging

# logger = logging.getLogger(__name__)

# class TrackCache:
#     def __init__(self, maxsize=100, ttl=3600):
#         self.cache = TTLCache(maxsize=maxsize, ttl=ttl)

#     def get(self, key):
#         try:
#             return self.cache.get(key)
#         except Exception as e:
#             logger.error(f"Cache get error: {str(e)}")
#             return None

#     def set(self, key, value):
#         try:
#             self.cache[key] = value
#         except Exception as e:
#             logger.error(f"Cache set error: {str(e)}")

import shelve
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SpotifyCache:
    def __init__(self, cache_file='spotify_cache.db'):
        self.cache_file = cache_file
        
    def get(self, track_id):
        try:
            with shelve.open(self.cache_file) as cache:
                if track_id in cache:
                    data = cache[track_id]
                    if datetime.now() - data['timestamp'] < timedelta(days=30):
                        return data['track_data']
        except Exception as e:
            logger.warning(f"Cache read error: {e}")
        return None
        
    def set(self, track_id, track_data):
        try:
            with shelve.open(self.cache_file) as cache:
                cache[track_id] = {
                    'track_data': track_data,
                    'timestamp': datetime.now()
                }
        except Exception as e:
            logger.warning(f"Cache write error: {e}")

