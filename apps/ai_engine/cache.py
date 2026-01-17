"""
Caching utilities for CitySense.

Implements caching strategies for:
- Weather data (expensive API calls, slow changes)
- City suggestions (static data, high query frequency)
"""

from django.core.cache import cache
from django.conf import settings
import hashlib
import logging

logger = logging.getLogger(__name__)


def cache_weather(lat, lon, get_function):
    """
    Cache weather data for a specific location.
    
    Args:
        lat (float): Latitude
        lon (float): Longitude
        get_function (callable): Function to call if cache miss
    
    Returns:
        dict: Weather data
    """
    # Create cache key from coordinates
    cache_key = f"weather:{lat}:{lon}"
    timeout = settings.CACHE_TIMEOUTS.get("weather", 3600)
    
    # Try to get from cache
    cached_data = cache.get(cache_key)
    if cached_data:
        logger.debug(f"Weather cache hit for ({lat}, {lon})")
        return cached_data
    
    logger.debug(f"Weather cache miss for ({lat}, {lon})")
    try:
        # Call the actual function
        data = get_function(lat, lon)
        # Store in cache
        cache.set(cache_key, data, timeout)
        return data
    except Exception as e:
        logger.error(f"Weather fetch error: {str(e)}")
        raise


def cache_city_suggestions(query, get_function):
    """
    Cache city suggestion results.
    
    Args:
        query (str): City search query
        get_function (callable): Function to call if cache miss
    
    Returns:
        list: City suggestion results
    """
    # Create cache key from query (normalized)
    query_normalized = query.lower().strip()
    query_hash = hashlib.md5(query_normalized.encode()).hexdigest()
    cache_key = f"cities:{query_hash}"
    timeout = settings.CACHE_TIMEOUTS.get("city_suggestions", 86400)
    
    # Try to get from cache
    cached_results = cache.get(cache_key)
    if cached_results is not None:
        logger.debug(f"City suggestions cache hit for '{query}'")
        return cached_results
    
    logger.debug(f"City suggestions cache miss for '{query}'")
    try:
        # Call the actual function
        results = get_function(query)
        # Store in cache
        cache.set(cache_key, results, timeout)
        return results
    except Exception as e:
        logger.error(f"City suggestions error: {str(e)}")
        raise


def invalidate_weather_cache(lat, lon):
    """
    Invalidate weather cache for a specific location.
    
    Args:
        lat (float): Latitude
        lon (float): Longitude
    """
    cache_key = f"weather:{lat}:{lon}"
    cache.delete(cache_key)
    logger.debug(f"Weather cache invalidated for ({lat}, {lon})")


def invalidate_city_suggestions_cache(query):
    """
    Invalidate city suggestions cache for a query.
    
    Args:
        query (str): City search query
    """
    query_normalized = query.lower().strip()
    query_hash = hashlib.md5(query_normalized.encode()).hexdigest()
    cache_key = f"cities:{query_hash}"
    cache.delete(cache_key)
    logger.debug(f"City suggestions cache invalidated for '{query}'")


def clear_all_cache():
    """Clear all application cache."""
    cache.clear()
    logger.warning("All application cache cleared")
