from functools import lru_cache

_cache_registry: list = []

def sim_cache(func):
    cached_func = lru_cache(maxsize=None)(func)
    _cache_registry.append(cached_func)
    return cached_func

def clear_all_caches():
    for cached_func in _cache_registry:
        cached_func.cache_clear()
