from groq import Groq
from django.conf import settings
import json
import re
from jsonschema import validate
from .prompt import SYSTEM_PROMPT
from .schema import analysis_schema

client = Groq(api_key=settings.GROQ_API_KEY)


def analyze_location_ai( lat, lng):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Analyze this real-world location:\n"
                    f"Latitude: {lat}\n"
                    f"Longitude: {lng}"
                )
            }
        ],
        temperature=0.3
    )

    raw = response.choices[0].message.content.strip()

   
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError("AI response does not contain valid JSON")

    data = json.loads(match.group())

    validate(instance=data, schema=analysis_schema)

    return data