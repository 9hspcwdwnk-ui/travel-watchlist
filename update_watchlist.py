#!/usr/bin/env python3
"""
Travel Arbitrage Watchlist CSV Updater

Simple/free workflow:
1. Keep index.html and opportunities.csv in a GitHub Pages repository.
2. Run this script locally to add/update an opportunity.
3. Commit/push the updated CSV to GitHub.
4. Your dashboard updates automatically after GitHub Pages republishes.

No paid backend. No Telegram. No Discord.
"""

import csv
from pathlib import Path

CSV_FILE = Path("opportunities.csv")

HEADERS = [
    "rank","destination","archetype","travel_window","depart_airport",
    "routing_quality","program","cabin_cost","value","two_seats",
    "recommendation","notes"
]

def ensure_csv():
    if not CSV_FILE.exists():
        with CSV_FILE.open("w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(HEADERS)

def read_rows():
    ensure_csv()
    with CSV_FILE.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def write_rows(rows):
    with CSV_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        for row in rows:
            writer.writerow({h: row.get(h, "") for h in HEADERS})

def add_opportunity():
    rows = read_rows()
    print("\nAdd a new travel opportunity.\n")
    row = {}
    row["rank"] = input("Rank, e.g. 1: ").strip() or str(len(rows)+1)
    row["destination"] = input("Destination, e.g. MIA → Madrid: ").strip()
    row["archetype"] = input("Archetype, e.g. Surf Mission / Snowboard / Powder / Big Expedition / Luxury/Romantic: ").strip()
    row["travel_window"] = input("Travel window, e.g. Sep-Oct 2026: ").strip()
    row["depart_airport"] = input("Departure airport, SJU/MIA/FLL: ").strip()
    row["routing_quality"] = input("Routing quality, e.g. nonstop / 1-stop acceptable: ").strip()
    row["program"] = input("Program, e.g. Iberia Avios / Aeroplan / LifeMiles / Cash: ").strip()
    row["cabin_cost"] = input("Cabin/cost, e.g. Business 50k + $150: ").strip()
    row["value"] = input("Value, e.g. 3.8 cpp / strong cash fare: ").strip()
    row["two_seats"] = input("Two seats available? Yes/No/Unknown: ").strip()
    row["recommendation"] = input("Recommendation: Book Now / Monitor / Ignore: ").strip()
    row["notes"] = input("Notes: ").strip()
    rows.append(row)
    rows.sort(key=lambda r: float(r.get("rank") or 999))
    write_rows(rows)
    print(f"\nSaved to {CSV_FILE.resolve()}")

def archive_ignored():
    rows = read_rows()
    kept = [r for r in rows if (r.get("recommendation","").lower() != "ignore")]
    write_rows(kept)
    print(f"Removed {len(rows)-len(kept)} ignored rows.")

def main():
    ensure_csv()
    print("Travel Arbitrage Watchlist Updater")
    print("1) Add opportunity")
    print("2) Remove rows marked Ignore")
    choice = input("Choose 1 or 2: ").strip()
    if choice == "2":
        archive_ignored()
    else:
        add_opportunity()

if __name__ == "__main__":
    main()
