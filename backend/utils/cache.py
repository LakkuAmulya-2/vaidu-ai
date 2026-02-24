"""
utils/cache.py
Simple in-memory cache for LLM responses (1 hour TTL).
"""
from cachetools import TTLCache
import hashlib
import json

cache = TTLCache(maxsize=1000, ttl=3600)

def get_cache_key(*args, **kwargs) -> str:
    """Generate cache key from function arguments."""
    key = hashlib.md5(json.dumps((args, kwargs), sort_keys=True).encode()).hexdigest()
    return key

def cached_predict_text(model_name: str, prompt: str, **kwargs) -> str:
    """Cached version of predict_text."""
    key = get_cache_key(model_name, prompt, kwargs)
    if key in cache:
        return cache[key]
    from utils.vertex_client import predict_text
    result = predict_text(model_name, prompt, **kwargs)
    cache[key] = result
    return result