"""
Redis caching layer for Resume Analyzer.
Caches:
1. Analysis results by JD hash (avoid re-processing same JD)
2. Company intel by company name (avoid re-scraping)
3. LLM responses by prompt hash (reduce API costs)
"""
import redis
import json
import hashlib
import os
from typing import Optional, Any
from functools import wraps

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


class RedisCache:
    def __init__(self):
        self.client = None
        self.enabled = False
        self._memory_cache = {}
        self._connect()
    
    def _connect(self):
        try:
            self.client = redis.from_url(REDIS_URL, decode_responses=True)
            self.client.ping()
            self.enabled = True
            print("Redis cache connected")
        except Exception as e:
            print(f"Redis unavailable, using in-memory fallback: {e}")
            self.enabled = False
    
    def get(self, key: str) -> Optional[Any]:
        try:
            if self.enabled:
                value = self.client.get(key)
                if value:
                    return json.loads(value)
            else:
                return self._memory_cache.get(key)
        except Exception as e:
            print(f"Cache get error: {e}")
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        try:
            if self.enabled:
                self.client.setex(key, ttl, json.dumps(value, default=str))
            else:
                self._memory_cache[key] = value
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        try:
            if self.enabled:
                self.client.delete(key)
            else:
                self._memory_cache.pop(key, None)
            return True
        except Exception:
            return False
    
    def get_stats(self) -> dict:
        if self.enabled:
            try:
                info = self.client.info()
                return {
                    "type": "redis",
                    "connected": True,
                    "keys": self.client.dbsize(),
                    "memory_used": info.get("used_memory_human", "unknown"),
                    "hits": info.get("keyspace_hits", 0),
                    "misses": info.get("keyspace_misses", 0),
                }
            except Exception:
                pass
        return {
            "type": "memory",
            "connected": False,
            "keys": len(self._memory_cache),
        }


cache = RedisCache()


def analysis_cache_key(jd_hash: str, resume_hash: str) -> str:
    return f"analysis:{jd_hash}:{resume_hash}"


def company_cache_key(company_name: str) -> str:
    return f"company:{company_name.lower().replace(' ', '_')}"


def jd_parse_cache_key(jd_hash: str) -> str:
    return f"jd_parsed:{jd_hash}"


def llm_cache_key(prompt_hash: str) -> str:
    return f"llm:{prompt_hash}"


def hash_content(content: str) -> str:
    return hashlib.md5(content.encode()).hexdigest()


def cached(key_func, ttl: int = 3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = key_func(*args, **kwargs)
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                print(f"Cache HIT: {cache_key[:50]}...")
                return cached_result
            print(f"Cache MISS: {cache_key[:50]}...")
            result = func(*args, **kwargs)
            if result is not None:
                cache.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator



# LLM Response Caching
def cache_llm_response(prompt: str, model: str = "default") -> Optional[str]:
    """Get cached LLM response if available."""
    prompt_hash = hash_content(f"{model}:{prompt}")
    cache_key = llm_cache_key(prompt_hash)
    return cache.get(cache_key)


def store_llm_response(prompt: str, response: str, model: str = "default", ttl: int = 7200) -> bool:
    """Store LLM response in cache (default 2 hours)."""
    prompt_hash = hash_content(f"{model}:{prompt}")
    cache_key = llm_cache_key(prompt_hash)
    return cache.set(cache_key, response, ttl)


# Analysis Result Caching
def cache_analysis_result(resume_text: str, jd_text: str, result: dict, ttl: int = 3600) -> bool:
    """Cache full analysis result for resume+JD combination."""
    resume_hash = hash_content(resume_text[:5000])
    jd_hash = hash_content(jd_text[:2000])
    cache_key = analysis_cache_key(jd_hash, resume_hash)
    return cache.set(cache_key, result, ttl)


def get_cached_analysis(resume_text: str, jd_text: str) -> Optional[dict]:
    """Get cached analysis result if available."""
    resume_hash = hash_content(resume_text[:5000])
    jd_hash = hash_content(jd_text[:2000])
    cache_key = analysis_cache_key(jd_hash, resume_hash)
    return cache.get(cache_key)


# Cache warming for common JDs
def warm_cache_for_jd(jd_text: str, parsed_result: dict) -> bool:
    """Pre-cache parsed JD for faster subsequent analyses."""
    jd_hash = hash_content(jd_text[:2000])
    cache_key = jd_parse_cache_key(jd_hash)
    return cache.set(cache_key, parsed_result, ttl=86400)


# Cache invalidation helpers
def invalidate_company_cache(company_name: str) -> bool:
    """Invalidate cached company intel."""
    cache_key = company_cache_key(company_name)
    return cache.delete(cache_key)


def clear_all_llm_cache() -> int:
    """Clear all LLM response cache."""
    if cache.enabled:
        try:
            keys = cache.client.keys("llm:*")
            if keys:
                cache.client.delete(*keys)
            return len(keys)
        except Exception as e:
            print(f"Error clearing LLM cache: {e}")
    return 0
