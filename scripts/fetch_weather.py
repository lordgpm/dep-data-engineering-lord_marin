#!/usr/bin/env python3
"""Pull daily historical weather for Metro Manila from the Open-Meteo archive API.

Metro Manila is 636 km2 and sits inside a single weather catchment, so one grid
point (Manila city proper) stands in for the whole metro area. The result is
written to data/reference/manila_daily_weather.csv and joined to the clean posts
in the M4 analysis notebook on date.

Note: the README lists an OpenWeather API under supplementary data, but that
needs a key and only gives point queries. Open-Meteo serves free historical
daily aggregates for a whole date range with no key, which is what the rainy-day
analysis actually needs.

Usage:
    python3 scripts/fetch_weather.py

Requires only the standard library.
"""

# New in M4: I didn't pull weather during M3 (it was only listed as optional),
# but the rainy-day question needs it, so it's added here.

import csv
import json
import os
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_PATH = os.path.join(ROOT, "data", "reference", "manila_daily_weather.csv")

# Cover the full range of the clean dataset so the join has no gaps.
START_DATE = "2023-01-01"
END_DATE = "2026-08-03"

LATITUDE = 14.587
LONGITUDE = 121.0028

# precip_sum is mm per day. weathercode is the WMO code, temp is degC.
DAILY_VARS = "precipitation_sum,weathercode,temperature_2m_mean"

API_URL = (
    "https://archive-api.open-meteo.com/v1/archive"
    f"?latitude={LATITUDE}&longitude={LONGITUDE}"
    f"&start_date={START_DATE}&end_date={END_DATE}"
    f"&daily={DAILY_VARS}&timezone=Asia%2FManila"
)


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "dep-r4r-project"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def write_csv(payload):
    daily = payload["daily"]
    rows = zip(
        daily["time"],
        daily["precipitation_sum"],
        daily["weathercode"],
        daily["temperature_2m_mean"],
    )
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["date", "precip_sum", "weathercode", "temp_mean"])
        written = 0
        for date, precip, code, temp in rows:
            writer.writerow([date, precip, code, temp])
            written += 1
    return written


def main():
    try:
        payload = fetch(API_URL)
    except urllib.error.HTTPError as err:
        sys.exit(f"Open-Meteo returned HTTP {err.code}. {err.read().decode('utf-8', 'replace')}")
    except urllib.error.URLError as err:
        sys.exit(f"Could not reach Open-Meteo: {err.reason}")

    written = write_csv(payload)

    # Sanity checks on what actually landed in the file.
    with open(OUT_PATH, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    wet = sum(1 for r in rows if r["precip_sum"] not in ("", "None") and float(r["precip_sum"]) > 0)

    print(f"Wrote {written} daily rows to {OUT_PATH}")
    print(f"Date range: {rows[0]['date']} -> {rows[-1]['date']}")
    print(f"Days with measurable rain: {wet}/{len(rows)} ({100.0 * wet / len(rows):.1f}%)")


if __name__ == "__main__":
    main()
