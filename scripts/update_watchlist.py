#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "opportunities.json"

def load_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default

def save_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def score_opportunity(opp: dict) -> int:
    score = 50
    archetype = (opp.get("archetype") or "").lower()
    rec = (opp.get("recommendation") or "").lower()
    notes = (opp.get("notes") or "").lower()
    cabin = (opp.get("cabin_cost") or "").lower()
    seats = (opp.get("two_seats") or "").lower()
    destination = (opp.get("destination") or "").lower()

    if "business" in cabin:
        score += 15
    if "two" in seats or "yes" in seats or "target" in seats:
        score += 10
    if "japan" in destination:
        score += 10
    if "chile" in destination:
        score += 8
    if "snowboard" in archetype or "powder" in archetype:
        score += 8
    if "surf" in archetype:
        score += 7
    if "transfer bonus" in archetype or "transfer bonus" in notes:
        score += 12
    if "book" in rec:
        score += 15
    if "ignore" in rec:
        score -= 40

    return max(0, min(score, 100))

def main():
    data = load_json(DATA, {"updated_at": None, "opportunities": []})

    for opp in data.get("opportunities", []):
        opp["score"] = score_opportunity(opp)

    data["opportunities"] = sorted(
        data.get("opportunities", []),
        key=lambda x: x.get("score", 0),
        reverse=True
    )
    data["updated_at"] = datetime.now(timezone.utc).isoformat()

    save_json(DATA, data)
    print(f"Updated {DATA}")

if __name__ == "__main__":
    main()
