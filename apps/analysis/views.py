from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import AnalysisForm
from .models import Location, AnalysisResult
from apps.ai_engine.services.analyze import analyze_location
from apps.ai_engine.services.geocoding import geocode_address
from django.http import JsonResponse
from apps.ai_engine.services.groq_service import analyze_location_ai
from apps.ai_engine.services.weather import get_weather_intelligence
from django.contrib import messages
from .services import suggest_city_fuzzy
from django.views.decorators.http import require_GET

@login_required
def analyze_view(request):
    form = AnalysisForm(request.POST or None)

    if form.is_valid():
        address = form.cleaned_data["address"]

        geo = geocode_address(address)
        if not geo:
            return render(request, "analysis/analyze.html", {
                "form": form,
                "error": "Address not found"
            })

        location, _ = Location.objects.get_or_create(
            address=address,
            defaults={
                "latitude": geo["lat"],
                "longitude": geo["lng"]
            }
        )

        try:
            ai_data = analyze_location_ai(
                address,
                location.latitude,
                location.longitude
            )
        except Exception as e:
            return render(request, "analysis/analyze.html", {
                "form": form,
                "error": "AI analysis failed. Try again."
            })
        weather = get_weather_intelligence(geo["lat"], geo["lng"])

        result = AnalysisResult.objects.create(
            user=request.user,
            location=location,
            safety_score=ai_data["safety_score"],
            noise_level=ai_data["noise_level"],
            rent_level=ai_data["rent_level"],
            water_quality=ai_data["water_quality"],
            ai_summary=ai_data["summary"],
            ai_score=ai_data["ai_score"],
            temperature=(
                weather["human_feeling_index"]["apparent_temperature_C"]
                if weather else None
            ),
            windspeed=(
                weather["human_feeling_index"]["wind_speed_kmh"]
                if weather else None
            ),
            weather_code=(
                weather["current_conditions"]["weather_code"]
                if weather else None
            )
        )


        return redirect("analysis:report", result.id)

    return render(request, "analysis/analyze.html", {"form": form})



@login_required
def report_view(request, pk):
    report = AnalysisResult.objects.get(pk=pk, user=request.user)
    return render(request, "analysis/report.html", {"report": report})





def heatmap_data(request):
    layer = request.GET.get("layer", "ai_score")

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

    return JsonResponse(data, safe=False)





@require_GET
def city_suggestions(request):
    query = request.GET.get("q", "").strip()

    if len(query) < 2:
        return JsonResponse([], safe=False)

    results = suggest_city_fuzzy(query)
    return JsonResponse(results, safe=False)

