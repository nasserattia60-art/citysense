"""
Geocoding service using Nominatim/OpenStreetMap.

Converts addresses to latitude/longitude coordinates.
"""

import requests
import logging

logger = logging.getLogger(__name__)


def geocode_address(address):
    """
    Geocode an address to latitude/longitude using Nominatim.
    
    Args:
        address (str): The address or city name to geocode
    
    Returns:
        dict: Contains 'lat' and 'lng' keys with float values, or None if not found
    
    Raises:
        requests.RequestException: If API call fails
    """
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": address,
            "format": "json",
            "limit": 1
        }
        headers = {
            "User-Agent": "CitySense-App"
        }

        response = requests.get(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()

        if not data:
            logger.warning(f"No geocoding results for: {address}")
            return None

        logger.info(f"Successfully geocoded: {address}")
        return {
            "lat": float(data[0]["lat"]),
            "lng": float(data[0]["lon"])
        }
    except requests.RequestException as e:
        logger.error(f"Geocoding error for {address}: {str(e)}")
        raise