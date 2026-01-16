"""
Analysis service layer for location analysis.

Provides city suggestion and fuzzy matching functionality using
the GeoNames database.
"""

from apps.ai_engine.services.analyze import analyze_location
import geonamescache 
from rapidfuzz import process
import logging

logger = logging.getLogger(__name__)


def run_analysis(address: str) -> dict:
    """
    Calls AI engine and returns structured data.
    
    Args:
        address (str): The address or city name to analyze
    
    Returns:
        dict: Structured analysis from AI service
    """
    return analyze_location(address)


# ==============================
# CITY SUGGESTIONS & AUTOCOMPLETE
# ==============================

gc = geonamescache.GeonamesCache()
cities = gc.get_cities()
ALL_CITIES = [
    {
        "name": c["name"],
        "lat": c["latitude"],
        "lon": c["longitude"],
    }
    for c in cities.values()
]
CITY_BY_NAME = {c["name"]: c for c in ALL_CITIES}


def suggest_city_fuzzy(query, limit=10):
    """
    Suggest cities based on fuzzy matching against GeoNames database.
    
    Uses RapidFuzz with default threshold of 65 to find similar city names.
    Results are sorted by similarity score (highest first).
    
    Args:
        query (str): Partial city name or address
        limit (int): Maximum number of suggestions to return (default: 10)
    
    Returns:
        list: List of dicts with 'name', 'lat', 'lon' keys
    
    Example:
        >>> suggest_city_fuzzy("new")
        [
            {"name": "New York", "lat": 40.7128, "lon": -74.0060},
            {"name": "Newcastle", "lat": 54.9783, "lon": -1.6178}
        ]
    """
    try:
        names = CITY_BY_NAME.keys()
        matches = process.extract(query, names, limit=limit)
        results = [CITY_BY_NAME[name] for name, score, _ in matches if score > 65]
        logger.debug(f"City suggestions for '{query}': {len(results)} results")
        return results
    except Exception as e:
        logger.error(f"Error suggesting cities for '{query}': {str(e)}")
        return []