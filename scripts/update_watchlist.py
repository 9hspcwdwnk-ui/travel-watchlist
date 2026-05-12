#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from pathlib import Path
from datetime import datetime, timezone, date, timedelta

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "opportunities.json"

HOME_AIRPORTS = ["SJU", "MIA", "FLL"]

TARGETS = {
    "Europe": ["MAD","BCN","LIS","CDG","AMS","FCO","MXP","ZRH","GVA","MUC","FRA","VIE"],
    "Japan": ["HND","NRT","CTS","KIX"],
    "Chile Snowboard": ["SCL"],
    "Surf / Warm": ["SAL","SJO","OAX","BGI","DPS","CGK","HNL","OGG","RAK","CMN","LIM","MNL","CEB","BKK","HKT","USM","COK","GOI"],
    "Big Expedition": ["CPT","JNB","AKL","CHC","ZQN","SYD","MEL","BNE"],
    "Domestic / Nearby": ["SEA","YVR","BZN","MSO","PDX","RDM","DFW","DAL"],
}

DESTINATION_NAMES = {
    "MAD":"Madrid", "BCN":"Barcelona", "LIS":"Lisbon", "CDG":"Paris", "AMS":"Amsterdam",
    "FCO":"Rome", "MXP":"Milan", "ZRH":"Zurich", "GVA":"Geneva", "MUC":"Munich", "FRA":"Frankfurt", "VIE":"Vienna",
    "HND":"Tokyo Haneda", "NRT":"Tokyo Narita", "CTS":"Sapporo", "KIX":"Osaka",
    "SCL":"Santiago, Chile",
    "SAL":"El Salvador", "SJO":"Costa Rica", "OAX":"Oaxaca", "BGI":"Barbados",
    "DPS":"Bali", "CGK":"Jakarta", "HNL":"Honolulu", "OGG":"Maui",
    "RAK":"Marrakesh", "CMN":"Casablanca", "LIM":"Lima",
    "MNL":"Manila", "CEB":"Cebu", "BKK":"Bangkok", "HKT":"Phuket", "USM":"Koh Samui",
    "COK":"Kochi", "GOI":"Goa",
    "CPT":"Cape Town", "JNB":"Johannesburg",
    "AKL":"Auckland", "CHC":"Christchurch", "ZQN":"Queenstown",
    "SYD":"Sydney", "MEL":"Melbourne", "BNE":"Brisbane",
    "SEA":"Seattle", "YVR":"Vancouver", "BZN":"Bozeman", "MSO":"Missoula",
    "PDX":"Portland", "RDM":"Bend/Redmond", "DFW":"Dallas Fort Worth", "DAL":"Dallas Love Field",
}

SOURCES = "aeroplan,united,virginatlantic,american,alaska,delta,emirates,etihad,jetblue"

def load_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default

def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def get_first(d: dict, keys: list[str], default=""):
    lower = {str(k).lower(): v for k, v in d.items()}
    for k in keys:
        if k in d:
            return d[k]
        if k.lower() in lower:
            return lower[k.lower()]
    return default

def flatten_results(obj):
    found = []
    if isinstance(obj, dict):
        keys = {str(k).lower() for k in obj.keys()}
        if any(k in keys for k in ["originairport","origin_airport","origin"]) and any(k in keys for k in ["destinationairport","destination_airport","destination"]):
            found.append(obj)
        for v in obj.values():
            found.extend(flatten_results(v))
    elif isinstance(obj, list):
        for item in obj:
            found.extend(flatten_results(item))
    return found

def seats_cached_search(destinations: list[str], start_date: str, end_date: str, cabins: str = "business,first,premium"):
    api_key = os.environ.get("SEATS_AERO_API_KEY", "").strip()
    if not api_key:
        return []

    params = {
        "origin_airport": ",".join(HOME_AIRPORTS),
        "destination_airport": ",".join(destinations),
        "start_date": start_date,
        "end_date": end_date,
        "take": "1000",
        "order_by": "lowest_mileage",
        "include_trips": "true",
        "minify_trips": "true",
        "cabins": cabins,
        "sources": SOURCES,
    }

    url = "https://seats.aero/partnerapi/search?" + urllib.parse.urlencode(params)

    req = urllib.request.Request(
        url,
        headers={
    "Authorization": api_key,
    "Accept": "application/json"
}
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return flatten_results(json.loads(resp.read().decode("utf-8")))
    except Exception as e:
        return [{"_error": f"Seats.aero request failed: {e}"}]

def infer_archetype(dest: str) -> str:
    if dest in ["HND","NRT","CTS","KIX","AKL","CHC","ZQN","SYD","MEL","BNE","CPT","JNB"]:
        return "Big Expedition"
    if dest in ["SCL","CTS","ZRH","GVA","MUC","BZN","MSO","YVR","RDM"]:
        return "Snowboard / Powder"
    if dest in ["DPS","OAX","SAL","BGI","RAK","CMN","HNL","OGG","MNL","CEB","HKT","USM","COK","GOI"]:
        return "Surf Mission"
    if dest in ["MAD","BCN","LIS","CDG","AMS","FCO","MXP","ZRH","GVA"]:
        return "Luxury/Romantic"
    return "Monitor"

def normalize_to_opportunity(raw: dict):
    if "_error" in raw:
        return {
            "destination": "Seats.aero API issue",
            "archetype": "System",
            "travel_window": "Now",
            "depart_airport": "SJU/MIA/FLL",
            "routing_quality": "N/A",
            "program": "Seats.aero",
            "cabin_cost": "API error",
            "value": "N/A",
            "two_seats": "Unknown",
            "recommendation": "Monitor",
            "score": 10,
            "notes": raw["_error"],
        }

    origin = str(get_first(raw, ["OriginAirport","origin_airport","origin"], "")).upper()
    dest = str(get_first(raw, ["DestinationAirport","destination_airport","destination"], "")).upper()

    if origin not in HOME_AIRPORTS or dest not in DESTINATION_NAMES:
        return None

    date_val = get_first(raw, ["Date","date"], "")
    source = get_first(raw, ["Source","source"], "Seats.aero")
    cabin = str(get_first(raw, ["Cabin","cabin"], "business")).lower()
    mileage = get_first(raw, ["MileageCost","mileage_cost","Miles","miles"], "")
    taxes = get_first(raw, ["Taxes","taxes"], "")
    seats = get_first(raw, ["RemainingSeats","remaining_seats","Seats","seats"], "")

    cabin_cost = f"{cabin.title()}"
    if mileage:
        cabin_cost += f" / {mileage} pts"
    if taxes:
        cabin_cost += f" + ${taxes}"

    two_seats = "Unknown"

    try:
        if int(seats) >= 2:
            two_seats = "Yes"
        else:
            two_seats = "No"
    except:
        pass

    recommendation = "Monitor"

    if "business" in cabin or "first" in cabin:
        recommendation = "Book Now" if two_seats == "Yes" else "Monitor"

    return {
        "destination": f"{origin} → {DESTINATION_NAMES.get(dest, dest)}",
        "archetype": infer_archetype(dest),
        "travel_window": str(date_val),
        "depart_airport": origin,
        "routing_quality": "Check routing",
        "program": str(source),
        "cabin_cost": cabin_cost,
        "value": "API award availability",
        "two_seats": two_seats,
        "recommendation": recommendation,
        "score": 0,
        "notes": "Auto-ingested from Seats.aero cached search",
    }

def score_opportunity(opp: dict) -> int:
    score = 50

    archetype = (opp.get("archetype") or "").lower()
    rec = (opp.get("recommendation") or "").lower()
    cabin = (opp.get("cabin_cost") or "").lower()
    seats = (opp.get("two_seats") or "").lower()
    destination = (opp.get("destination") or "").lower()

    if "business" in cabin:
        score += 18

    if "first" in cabin:
        score += 22

    if "yes" in seats:
        score += 12

    if "japan" in destination or "tokyo" in destination:
        score += 12

    if "chile" in destination:
        score += 9

    if "snowboard" in archetype or "powder" in archetype:
        score += 8

    if "surf" in archetype:
        score += 7

    if "book" in rec:
        score += 10

    return max(0, min(score, 100))

def search_windows():
    today = date.today()
    windows = []

    start = today + timedelta(days=7)

    for offset in range(0, 270, 45):
        a = start + timedelta(days=offset)
        b = a + timedelta(days=44)
        windows.append((a.isoformat(), b.isoformat()))

    return windows

def main():
    existing = load_json(DATA, {"updated_at": None, "opportunities": []})

    manual = [
        o for o in existing.get("opportunities", [])
        if not str(o.get("notes","")).startswith("Auto-ingested")
    ]

    all_dests = sorted(set(sum(TARGETS.values(), [])))

    api_rows = []

    for start, end in search_windows():
        raw_results = seats_cached_search(all_dests, start, end)

        for raw in raw_results:
            opp = normalize_to_opportunity(raw)

            if opp:
                api_rows.append(opp)

    seen = set()
    deduped = []

    for opp in manual + api_rows:
        key = (
            opp.get("destination"),
            opp.get("travel_window"),
            opp.get("program"),
            opp.get("cabin_cost")
        )

        if key in seen:
            continue

        seen.add(key)

        opp["score"] = score_opportunity(opp)

        deduped.append(opp)

    data = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "opportunities": sorted(
            deduped,
            key=lambda x: x.get("score", 0),
            reverse=True
        )[:100]
    }

    save_json(DATA, data)

    print(f"Updated {DATA} with {len(data['opportunities'])} opportunities")

if __name__ == "__main__":
    main()
