# ATL Events — Glide App Setup Guide

## 1. Import Your Data

1. Go to [glideapps.com](https://www.glideapps.com) and create a new app
2. Choose **"Glide Table"** as the data source
3. Click **Import CSV** and upload `events_glide.csv`
4. Glide will auto-detect columns — verify `Latitude`/`Longitude` are set to **Number** type

## 2. Main Screen — Collection Layout

Create a **Collection** component on your home screen:

| Setting | Value |
|---|---|
| **Data source** | Your imported table |
| **Sort by** | `Sort_Order` → Ascending |
| **Style** | Cards |

### Card bindings:

| Card element | Bind to column |
|---|---|
| Title | `Title` |
| Subtitle / Details | `Subtitle` |
| Top-right badge | `Star_Display` |
| Chip / Tag | `Chip_Label` |
| Accent color | `Category_Color` |

### Conditional card size (Niche = large, Mainstream = compact):

Glide doesn't have a native large/compact toggle per card, so use **two collections with visibility conditions**:

**Collection 1 — "For You" (niche events)**
- Filter: `Is_Niche` is `true`
- Style: **Cards** (large, image-capable)
- Show `Chip_Label` as a prominent tag
- This appears at the top of the screen

**Collection 2 — "All Events" (everything else)**
- Filter: `Is_Niche` is `false`
- Style: **List** (compact, single-line)
- No chip needed — saves screen space

## 3. Detail Screen

When a user taps an event card, show a detail screen with:

| Component | Bind to |
|---|---|
| **Title** | `Title` |
| **Date/Time** | `Display_Date` + `Display_Time` |
| **Location** | `Location` |
| **Map** | `Latitude` + `Longitude` (Glide has a built-in Map component) |
| **Star Rating** | `Star_Display` |
| **Distance** | `Distance_Miles` (add suffix " miles from home") |
| **Category badge** | `Category` with background color from `Category_Color` |
| **Niche tag** | `Chip_Label` (only visible when non-empty) |

## 4. Tabs / Filters

Add **inline filter chips** at the top of the main screen, or use Glide's **Tab** layout:

| Tab | Filter |
|---|---|
| **All** | No filter, sorted by `Sort_Order` |
| **For You** ★ | `Star_Rating` >= 4 |
| **This Week** | `Date_Start` within 7 days |
| **Niche** | `Is_Niche` = true |
| **Music** | `Category` = "Music" |
| **Sports** | `Category` = "Sports" |
| **Food** | `Category` = "Food" |

## 5. Map View

Add a **Map** screen/tab:

- Data source: same table
- Latitude: `Latitude`
- Longitude: `Longitude`
- Pin title: `Title`
- Pin description: `Subtitle`
- Pin color: `Category_Color`

## 6. Color Reference

| Category | Hex | Swatch |
|---|---|---|
| Music | `#6C5CE7` | Purple |
| Sports | `#00B894` | Green |
| Niche | `#E17055` | Coral |
| Community | `#0984E3` | Blue |
| Food | `#FDCB6E` | Yellow |
| Arts | `#A29BFE` | Lavender |
| Entertainment | `#E84393` | Pink |

## 7. Keeping It Updated

When you have new events:

1. Add rows to `events_raw.csv`
2. Run `python3 normalize.py`
3. Re-import `events_glide.csv` into Glide (or sync via Google Sheets)

To add a new "auto-5★" interest, edit the `INTEREST_TAGS` list in `normalize.py`.
