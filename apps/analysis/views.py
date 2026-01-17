"""
Analysis views for location research and report generation.

Handles user location searches, AI analysis, weather data,
and report viewing.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import AnalysisForm
from .models import Location, AnalysisResult
from apps.ai_engine.services.analyze import analyze_location
from apps.ai_engine.services.geocoding import geocode_address
from django.http import JsonResponse, Http404
from apps.ai_engine.services.groq_service import analyze_location_ai
from apps.ai_engine.services.weather import get_weather_intelligence
from apps.ai_engine.cache import cache_weather, cache_city_suggestions
from django.contrib import messages
from .services import suggest_city_fuzzy
from django.views.decorators.http import require_GET
import logging

logger = logging.getLogger(__name__)


@login_required
def analyze_view(request):
    """
    Main analysis view - handles location search and analysis request.
    
    GET: Display analysis form with city suggestions autocomplete
    POST: Process location analysis, call AI and weather APIs, create report
    
    On success, redirects to report view.
    On error, re-displays form with error message.
    """
    form = AnalysisForm(request.POST or None)

    if form.is_valid():
        address = form.cleaned_data["address"]

        # Geocode address to coordinates
        geo = geocode_address(address)
        if not geo:
            logger.warning(f"Geocoding failed for: {address}")
            return render(request, "analysis/analyze.html", {
                "form": form,
                "error": "Address not found. Try a different location."
            })

        # Get or create location record
        location, _ = Location.objects.get_or_create(
            address=address,
            defaults={
                "latitude": geo["lat"],
                "longitude": geo["lng"]
            }
        )

        # Call AI analysis
        try:
            ai_data = analyze_location_ai(
                address,
                location.latitude,
                location.longitude
            )
            logger.info(f"AI analysis succeeded for: {address}")
        except Exception as e:
            logger.error(f"AI analysis failed for {address}: {str(e)}")
            return render(request, "analysis/analyze.html", {
                "form": form,
                "error": "AI analysis failed. Please try again later."
            })

        # Fetch weather data (with caching)
        try:
            weather = cache_weather(geo["lat"], geo["lng"], get_weather_intelligence)
            logger.info(f"Weather data retrieved for: {address}")
        except Exception as e:
            logger.error(f"Weather fetch failed for {address}: {str(e)}")
            weather = None

        # Create analysis result
        result = AnalysisResult.objects.create(
            user=request.user,
            location=location,
            safety_score=ai_data.get("safety_score", 5),
            noise_level=ai_data.get("noise_level", "Medium"),
            rent_level=ai_data.get("rent_level", "Medium"),
            water_quality=ai_data.get("water_quality", "Average"),
            ai_summary=ai_data.get("summary", ""),
            ai_score=ai_data.get("ai_score", 50),
            temperature=(
                weather["human_feeling_index"]["apparent_temperature_C"]
                if weather else None
            ),
            windspeed=(
                weather["human_feeling_index"]["wind_speed_kmh"]
                if weather else None
            ),
            weather_code=(
                weather["weather_risk_engine"]["risk_level"]
                if weather else None
            )
        )

        logger.info(f"Analysis result created: {result.id} for user: {request.user.id}")
        return redirect("analysis:report", result.id)

    return render(request, "analysis/analyze.html", {"form": form})


@login_required
def report_view(request, pk):
    """
    Display detailed analysis report for a location.
    
    Only shows reports belonging to the authenticated user.
    Returns 404 if report not found or belongs to different user.
    """
    report = get_object_or_404(AnalysisResult, pk=pk, user=request.user)
    logger.info(f"Report viewed: {pk} by user: {request.user.id}")
    return render(request, "analysis/report.html", {"report": report})


@login_required
@require_GET
def heatmap_data(request):
    """
    AJAX endpoint providing heatmap data for Leaflet map visualization.
    
    Supports multiple data layers:
    - ai_score: Overall AI livability score (default)
    - safety: Safety score
    - noise: Noise level (High=30, Other=15)
    - rent: Rent level (High=30, Other=15)
    
    Returns: JSON list with lat, lng, weight properties
    Requires authentication (login_required).
    """
    layer = request.GET.get("layer", "ai_score")

    try:
        data = []
        reports = AnalysisResult.objects.select_related("location")

        for r in reports:
            if layer == "safety":
                weight = r.safety_score
            elif layer == "noise":
                weight = 30 if r.noise_level == "High" else 15
            elif layer == "rent":
                weight = 30 if r.rent_level == "High" else 15
            else:
                weight = r.ai_score

            data.append({
                "lat": r.location.latitude,
                "lng": r.location.longitude,
                "weight": weight
            })

        logger.debug(f"Heatmap data: {len(data)} points on layer: {layer}")
        return JsonResponse(data, safe=False)
    except Exception as e:
        logger.error(f"Heatmap data error: {str(e)}")
        return JsonResponse([], safe=False)


@require_GET
def city_suggestions(request):
    """
    AJAX endpoint for city autocomplete suggestions.
    
    Requires minimum 2 characters to reduce noise.
    Returns fuzzy-matched city names with coordinates.
    Results are cached for 24 hours to optimize performance.
    
    Query params:
    - q: Search query (minimum 2 chars)
    
    Returns: JSON list of {name, lat, lon} objects
    """
    query = request.GET.get("q", "").strip()

    if len(query) < 2:
        return JsonResponse([], safe=False)

    try:
        results = cache_city_suggestions(query, suggest_city_fuzzy)
        logger.debug(f"City suggestions: '{query}' returned {len(results)} results")
        return JsonResponse(results, safe=False)
    except Exception as e:
        logger.error(f"City suggestions error for '{query}': {str(e)}")
        return JsonResponse([], safe=False)

