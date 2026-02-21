#!/usr/bin/env python3
"""
ATL Events Normalizer
---------------------
Reads events_raw.csv, enriches each row with:
  - Distance from the home point (haversine miles)
  - Star Rating (1-5) based on interest-match + proximity
Outputs events_glide.csv ready for Glide import.
"""

import csv
import math
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
HOME_LAT = 33.98
HOME_LON = -84.43
INTEREST_TAGS = ["hyper-local hobby", "woodworking", "the big bonspiel", "local community"]
INPUT_FILE = Path(__file__).parent / "events_raw.csv"
OUTPUT_FILE = Path(__file__).parent / "events_glide.csv"

# ---------------------------------------------------------------------------
# Haversine (returns miles)
# ---------------------------------------------------------------------------
def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 3958.8  # Earth radius in miles
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# ---------------------------------------------------------------------------
# Star Rating Logic
# ---------------------------------------------------------------------------
def compute_star_rating(niche_factor: str, is_niche: bool, distance_mi: float) -> int:
    """
    5 stars: Niche_Factor tag matches a core interest AND is niche
    4 stars: Niche event within 10 miles of home
    3 stars: Niche event farther than 10 miles, OR non-niche within 5 miles
    2 stars: Non-niche within 15 miles
    1 star:  Everything else
    """
    tag_lower = niche_factor.lower()
    tag_hit = any(t in tag_lower for t in INTEREST_TAGS)

    if tag_hit and is_niche:
        return 5
    if is_niche and distance_mi <= 10:
        return 4
    if is_niche or distance_mi <= 5:
        return 3
    if distance_mi <= 15:
        return 2
    return 1

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else INPUT_FILE
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else OUTPUT_FILE

    with open(input_path, newline="", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        rows = list(reader)

    out_fields = [
        "Title", "Date_Start", "Date_End", "Time", "Location",
        "Latitude", "Longitude", "Category", "Is_Niche", "Niche_Factor",
        "Distance_Miles", "Star_Rating",
    ]

    enriched = []
    for row in rows:
        lat = float(row["Latitude"])
        lon = float(row["Longitude"])
        is_niche = row["Is_Niche"].strip().upper() == "TRUE"
        dist = round(haversine(HOME_LAT, HOME_LON, lat, lon), 1)
        stars = compute_star_rating(row["Niche_Factor"], is_niche, dist)

        enriched.append({
            "Title": row["Title"],
            "Date_Start": row["Date_Start"],
            "Date_End": row.get("Date_End", ""),
            "Time": row["Time"],
            "Location": row["Location"],
            "Latitude": lat,
            "Longitude": lon,
            "Category": row["Category"],
            "Is_Niche": is_niche,
            "Niche_Factor": row["Niche_Factor"],
            "Distance_Miles": dist,
            "Star_Rating": stars,
        })

    with open(output_path, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(enriched)

    # Print summary
    print(f"Wrote {len(enriched)} events to {output_path}\n")
    print(f"{'Stars':>5}  {'Dist':>6}  Title")
    print("-" * 60)
    for r in sorted(enriched, key=lambda x: (-x["Star_Rating"], x["Distance_Miles"])):
        print(f"  {r['Star_Rating']}★   {r['Distance_Miles']:5.1f}mi  {r['Title']}")


if __name__ == "__main__":
    main()
