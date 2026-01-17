"""
Tests for the AI engine services.

Tests cover:
- Geocoding service (OSM Nominatim API)
- Weather intelligence service (Open-Meteo API)
- Groq AI service
- Prompt validation
- Schema validation
"""

from django.test import TestCase
import json
from unittest.mock import patch, MagicMock
from apps.ai_engine.services.geocoding import geocode_address
from apps.ai_engine.services.weather import get_weather_intelligence
from apps.ai_engine.services.groq_service import analyze_location_ai
from apps.ai_engine.services.schema import analysis_schema
import logging

logger = logging.getLogger(__name__)


class GeocodingServiceTests(TestCase):
    """Tests for geocoding service (Nominatim API)."""

    @patch('apps.ai_engine.services.geocoding.requests.get')
    def test_geocode_valid_address(self, mock_get):
        """Test geocoding a valid address."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"lat": "40.7128", "lon": "-74.0060"}
        ]
        mock_get.return_value = mock_response

        result = geocode_address("New York")
        
        self.assertIsNotNone(result)
        self.assertEqual(result["lat"], 40.7128)
        self.assertEqual(result["lng"], -74.0060)
        mock_get.assert_called_once()

    @patch('apps.ai_engine.services.geocoding.requests.get')
    def test_geocode_invalid_address(self, mock_get):
        """Test geocoding returns None for invalid address."""
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        result = geocode_address("XYZ123NONEXISTENT")
        
        self.assertIsNone(result)

    @patch('apps.ai_engine.services.geocoding.requests.get')
    def test_geocode_has_user_agent(self, mock_get):
        """Test that geocoding includes User-Agent header."""
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        geocode_address("test")
        
        call_args = mock_get.call_args
        self.assertIn("User-Agent", call_args[1]["headers"])


class WeatherServiceTests(TestCase):
    """Tests for weather intelligence service (Open-Meteo API)."""

    @patch('apps.ai_engine.services.weather.requests.get')
    def test_get_weather_valid_coords(self, mock_get):
        """Test getting weather for valid coordinates."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "timezone": "America/New_York",
            "current": {
                "temperature_2m": 20,
                "apparent_temperature": 18,
                "relative_humidity_2m": 60,
                "wind_speed_10m": 10,
                "weather_code": 0
            },
            "daily": {
                "temperature_2m_max": [20, 21, 22, 19, 20, 21, 22, 20, 21, 22, 20, 21, 22, 20],
                "temperature_2m_min": [10, 11, 12, 9, 10, 11, 12, 10, 11, 12, 10, 11, 12, 10],
                "snowfall_sum": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "snow_depth_max": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            },
            "hourly": {
                "freezing_level_height": [2500] * 24 * 14,
                "visibility": [10000] * 24 * 14,
                "wind_gusts_10m": [15] * 24 * 14,
                "pressure_msl": [1013] * 24 * 14
            }
        }
        mock_get.return_value = mock_response

        result = get_weather_intelligence(40.7128, -74.0060)
        
        self.assertIsNotNone(result)
        self.assertIn("location", result)
        self.assertIn("statistics", result)
        self.assertIn("human_feeling_index", result)
        self.assertIn("snow_analysis", result)
        self.assertIn("weather_risk_engine", result)
        self.assertEqual(result["location"]["latitude"], 40.7128)
        self.assertEqual(result["location"]["longitude"], -74.0060)

    @patch('apps.ai_engine.services.weather.requests.get')
    def test_weather_human_feeling_index(self, mock_get):
        """Test human feeling index calculation."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "timezone": "UTC",
            "current": {
                "temperature_2m": -10,
                "apparent_temperature": -15,
                "relative_humidity_2m": 70,
                "wind_speed_10m": 30
            },
            "daily": {
                "temperature_2m_max": [-10] * 14,
                "temperature_2m_min": [-15] * 14,
                "snowfall_sum": [0] * 14,
                "snow_depth_max": [0] * 14
            },
            "hourly": {
                "freezing_level_height": [500] * 24 * 14,
                "visibility": [10000] * 24 * 14,
                "wind_gusts_10m": [40] * 24 * 14,
                "pressure_msl": [1013] * 24 * 14
            }
        }
        mock_get.return_value = mock_response

        result = get_weather_intelligence(0, 0)
        
        # Should detect extreme freeze (feel < -5 and wind > 25)
        self.assertEqual(result["human_feeling_index"]["status"], "EXTREME_FREEZE")
        self.assertEqual(result["human_feeling_index"]["status_color"], "RED")

    @patch('apps.ai_engine.services.weather.requests.get')
    def test_weather_api_error_handling(self, mock_get):
        """Test weather service handles API errors."""
        mock_get.side_effect = Exception("Network error")

        with self.assertRaises(Exception):
            get_weather_intelligence(0, 0)


class GroqServiceTests(TestCase):
    """Tests for Groq AI service."""

    @patch('apps.ai_engine.services.groq_service.client.chat.completions.create')
    def test_analyze_location_valid_response(self, mock_create):
        """Test Groq service with valid response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "safety_score": 7.5,
            "noise_level": "Medium",
            "rent_level": "High",
            "water_quality": "Good",
            "ai_score": 78,
            "summary": "Test summary"
        })
        mock_create.return_value = mock_response

        result = analyze_location_ai("New York", 40.7128, -74.0060)
        
        self.assertEqual(result["safety_score"], 7.5)
        self.assertEqual(result["ai_score"], 78)
        self.assertIn("summary", result)

    @patch('apps.ai_engine.services.groq_service.client.chat.completions.create')
    def test_analyze_location_schema_validation(self, mock_create):
        """Test that response schema is validated."""
        mock_response = MagicMock()
        # Missing required fields
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "safety_score": 7.5
            # Missing other required fields
        })
        mock_create.return_value = mock_response

        with self.assertRaises(Exception):
            # Should fail schema validation
            analyze_location_ai("New York", 40.7128, -74.0060)

    @patch('apps.ai_engine.services.groq_service.client.chat.completions.create')
    def test_analyze_location_json_decode_error(self, mock_create):
        """Test Groq service handles invalid JSON."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Invalid JSON {{"
        mock_create.return_value = mock_response

        with self.assertRaises(json.JSONDecodeError):
            analyze_location_ai("New York", 40.7128, -74.0060)


class SchemaTests(TestCase):
    """Tests for analysis schema validation."""

    def test_valid_analysis_data(self):
        """Test schema accepts valid data."""
        from jsonschema import validate
        
        valid_data = {
            "safety_score": 7.5,
            "noise_level": "Medium",
            "rent_level": "High",
            "water_quality": "Good",
            "ai_score": 78,
            "summary": "Test summary"
        }
        
        # Should not raise exception
        validate(instance=valid_data, schema=analysis_schema)

    def test_invalid_analysis_data_missing_field(self):
        """Test schema rejects data with missing fields."""
        from jsonschema import ValidationError, validate
        
        invalid_data = {
            "safety_score": 7.5
            # Missing required fields
        }
        
        with self.assertRaises(ValidationError):
            validate(instance=invalid_data, schema=analysis_schema)

    def test_invalid_analysis_data_wrong_type(self):
        """Test schema rejects wrong data types."""
        from jsonschema import ValidationError, validate
        
        invalid_data = {
            "safety_score": "not_a_number",  # Should be number
            "noise_level": "Medium",
            "rent_level": "High",
            "water_quality": "Good",
            "ai_score": 78,
            "summary": "Test summary"
        }
        
        with self.assertRaises(ValidationError):
            validate(instance=invalid_data, schema=analysis_schema)

