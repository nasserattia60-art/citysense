"""
Groq AI service for location analysis.

Uses Groq's LLaMA model to generate structured analysis of locations
with JSON schema validation.
"""

from groq import Groq
from django.conf import settings
import json
import re
from jsonschema import validate
from .prompt import SYSTEM_PROMPT
from .schema import analysis_schema
import logging

logger = logging.getLogger(__name__)

client = Groq(api_key=settings.GROQ_API_KEY)


def analyze_location_ai(address, lat, lng):
    """
    Analyze a location using Groq's LLaMA model.
    
    Args:
        address (str): The address or city name being analyzed
        lat (float): Latitude coordinate
        lng (float): Longitude coordinate
    
    Returns:
        dict: Validated JSON response with keys:
            - safety_score, noise_level, rent_level, water_quality
            - ai_score, summary, city_name, tourism_score
            - top_attractions, historical_landmarks, cultural_notes
    
    Raises:
        ValueError: If AI response doesn't contain valid JSON
        jsonschema.ValidationError: If JSON doesn't match schema
        groq.APIError: If API call fails
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Analyze this real-world location:\n"
                        f"Address: {address}\n"
                        f"Latitude: {lat}\n"
                        f"Longitude: {lng}"
                    )
                }
            ],
            temperature=0.3
        )

        raw = response.choices[0].message.content.strip()

        # Extract JSON from response
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            logger.error(f"AI response invalid JSON for {address}: {raw[:200]}")
            raise ValueError("AI response does not contain valid JSON")

        data = json.loads(match.group())

        # Validate against schema
        validate(instance=data, schema=analysis_schema)

        logger.info(f"Successfully analyzed location: {address}")
        return data
        
    except Exception as e:
        logger.error(f"Error analyzing location {address}: {str(e)}")
        raise