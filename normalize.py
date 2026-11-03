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
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
HOME_LAT = 34.0
HOME_LON = -84.4
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
# UI Helper Columns
# ---------------------------------------------------------------------------
CATEGORY_COLORS = {
    "Music": "#6C5CE7",
    "Sports": "#00B894",
    "Niche": "#E17055",
    "Community": "#0984E3",
    "Food": "#FDCB6E",
    "Arts": "#A29BFE",
    "Entertainment": "#E84393",
}

def format_display_date(date_start: str, date_end: str) -> str:
    """'Feb 21' or 'Feb 21-22' or 'Mar 3-30'."""
    try:
        ds = datetime.strptime(date_start, "%Y-%m-%d")
    except ValueError:
        return date_start
    if not date_end:
        return ds.strftime("%b %-d")
    try:
        de = datetime.strptime(date_end, "%Y-%m-%d")
    except ValueError:
        return ds.strftime("%b %-d")
    if ds.month == de.month:
        return f"{ds.strftime('%b %-d')}-{de.strftime('%-d')}"
    return f"{ds.strftime('%b %-d')} - {de.strftime('%b %-d')}"

def format_display_time(time_str: str) -> str:
    """'19:00' -> '7:00 PM', '00:00' -> 'All Day', '' -> 'TBD'."""
    if not time_str or time_str.strip() == "":
        return "TBD"
    if time_str == "00:00":
        return "All Day"
    try:
        t = datetime.strptime(time_str, "%H:%M")
        return t.strftime("%-I:%M %p")
    except ValueError:
        return time_str

def star_display(rating: int) -> str:
    return "\u2605" * rating + "\u2606" * (5 - rating)

def card_style(is_niche: bool) -> str:
    return "large" if is_niche else "compact"

def chip_label(is_niche: bool, niche_factor: str) -> str:
    return niche_factor if is_niche else ""

def subtitle(location: str, display_time: str, distance: float) -> str:
    return f"{location} \u00b7 {display_time} \u00b7 {distance:.0f} mi away"

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
        # Glide UI columns
        "Display_Date", "Display_Time", "Star_Display",
        "Card_Style", "Chip_Label", "Subtitle",
        "Category_Color", "Sort_Order",
    ]

    enriched = []
    for i, row in enumerate(rows):
        lat = float(row["Latitude"])
        lon = float(row["Longitude"])
        is_niche = row["Is_Niche"].strip().upper() == "TRUE"
        dist = round(haversine(HOME_LAT, HOME_LON, lat, lon), 1)
        stars = compute_star_rating(row["Niche_Factor"], is_niche, dist)
        d_date = format_display_date(row["Date_Start"], row.get("Date_End", ""))
        d_time = format_display_time(row["Time"])

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
            "Display_Date": d_date,
            "Display_Time": d_time,
            "Star_Display": star_display(stars),
            "Card_Style": card_style(is_niche),
            "Chip_Label": chip_label(is_niche, row["Niche_Factor"]),
            "Subtitle": subtitle(row["Location"], d_time, dist),
            "Category_Color": CATEGORY_COLORS.get(row["Category"], "#636E72"),
            "Sort_Order": (6 - stars) * 1000 + int(dist * 10),
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
