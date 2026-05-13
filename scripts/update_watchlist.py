import json
import os
import urllib.request
from datetime import datetime, timezone

OUTPUT_FILE = "data/opportunities.json"

HOME_AIRPORTS = ["SJU", "MIA", "FLL"]


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


def fetch_seats():
    api_key = os.environ.get("SEATS_AERO_API_KEY", "").strip()
    
    print("API key present:", bool(api_key))
    print("API key starts with pro_:", api_key.startswith("pro_"))
    print("API key length:", len(api_key))

    if not api_key:
        return build_error("Missing SEATS_AERO_API_KEY secret")

    url = "https://seats.aero/partnerapi/routes"

    req = urllib.request.Request(
        url,
        headers={
            "Partner-Authorization": api_key,
            "accept": "application/json"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")

        data = json.loads(raw)

        return {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "opportunities": [
                {
                    "destination": "Seats.aero routes test",
                    "archetype": "System",
                    "travel_window": "Now",
                    "depart_airport": "/".join(HOME_AIRPORTS),
                    "routing_quality": "N/A",
                    "program": "Seats.aero",
                    "cabin_cost": "Connected",
                    "value": "N/A",
                    "two_seats": "Unknown",
                    "recommendation": "Monitor",
                    "score": 100,
                    "notes": json.dumps(data)[:500],
                }
            ],
        }

    except Exception as e:
        return build_error(f"Request failed: {e}")


def main():
    result = fetch_seats()

    with open(OUTPUT_FILE, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Updated {OUTPUT_FILE} with {len(result['opportunities'])} opportunities")


if __name__ == "__main__":
    main()
