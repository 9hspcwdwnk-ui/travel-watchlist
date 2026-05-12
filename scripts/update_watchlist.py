import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone

OUTPUT_FILE = "data/opportunities.json"

HOME_AIRPORTS = ["SJU", "MIA", "FLL"]

DESTINATIONS = [
    "HND","NRT","KIX","CTS",
    "SCL",
    "MAD","BCN","FCO","MXP","ZRH","GVA","CDG",
    "DPS",
    "HNL","OGG",
    "OAX",
    "CPT",
    "AKL","SYD",
    "BGI",
    "LIM",
]

SOURCES = [
    "aeroplan",
    "lifemiles",
    "flyingblue",
    "avios",
    "virginatlantic",
    "ana",
]

def build_error(message):
    return {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "opportunities": [
            {
                "destination": "Seats.aero API issue",
                "archetype": "System",
                "travel_window": "Now",
                "depart_airport": "/".join(HOME_AIRPORTS),
                "routing_quality": "N/A",
                "program": "Seats.aero",
                "cabin_cost": "API error",
                "value": "N/A",
                "two_seats": "Unknown",
                "recommendation": "Monitor",
                "score": 0,
                "notes": message,
            }
        ],
    }

def flatten_results(obj):
    found = []

    if isinstance(obj, dict):
        if "Route" in obj or "route" in obj:
            found.append(obj)

        for value in obj.values():
            found.extend(flatten_results(value))

    elif isinstance(obj, list):
        for item in obj:
            found.extend(flatten_results(item))

    return found

def fetch_seats():
    api_key = os.environ.get("SEATS_AERO_API_KEY", "").strip()

    if not api_key:
        return build_error("Missing SEATS_AERO_API_KEY secret")

    params = {
        "origin_airport": ",".join(HOME_AIRPORTS),
        "destination_airport": ",".join(DESTINATIONS),
        "take": "50",
        "cabin": "business",
    }

    url = "https://seats.aero/partnerapi/search?" + urllib.parse.urlencode(params)

    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")

        data = json.loads(raw)

    except Exception as e:
        return build_error(f"Request failed: {e}")

    routes = flatten_results(data)

    if not routes:
        return build_error(f"No routes found. Raw response: {json.dumps(data)[:500]}")

    opportunities = []

    for route in routes[:25]:
        opportunities.append({
            "destination": route.get("DestinationAirport", "Unknown"),
            "archetype": "Award Flight",
            "travel_window": route.get("Date", "Unknown"),
            "depart_airport": route.get("OriginAirport", "Unknown"),
            "routing_quality": "Good",
            "program": route.get("Source", "Unknown"),
            "cabin_cost": f"{route.get('MileageCost', 'Unknown')} pts",
            "value": "TBD",
            "two_seats": route.get("RemainingSeats", "Unknown"),
            "recommendation": "Book Now",
            "score": 90,
            "notes": route.get("Route", ""),
        })

    return {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "opportunities": opportunities,
    }

def main():
    result = fetch_seats()

    with open(OUTPUT_FILE, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Updated {OUTPUT_FILE} with {len(result['opportunities'])} opportunities")

if __name__ == "__main__":
    main()
