"""
Day 1 - Live NAV Fetch Script
Capstone Project 1: Mutual Fund Analytics

This script fetches live/historical NAV data from MFAPI and saves the data as raw CSV files.
"""

from pathlib import Path
from datetime import datetime
import requests
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
REPORTS_DIR = BASE_DIR / "reports"

RAW_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

SCHEMES = {
    "125497": "HDFC Top 100 Direct",
    "119551": "SBI Bluechip",
    "120503": "ICICI Bluechip",
    "118632": "Nippon Large Cap",
    "119092": "Axis Bluechip",
    "120841": "Kotak Bluechip",
}


def fetch_nav(scheme_code: str) -> dict:
    """Fetch NAV JSON response from MFAPI."""
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def save_scheme_nav(scheme_code: str, scheme_name: str) -> str:
    """Fetch one scheme and save it as CSV."""
    data = fetch_nav(scheme_code)
    nav_records = data.get("data", [])

    if not nav_records:
        raise ValueError(f"No NAV records found for {scheme_code} - {scheme_name}")

    df = pd.DataFrame(nav_records)
    df.insert(0, "scheme_code", scheme_code)
    df.insert(1, "scheme_name", data.get("meta", {}).get("scheme_name", scheme_name))

    safe_name = scheme_name.lower().replace(" ", "_").replace("/", "_")
    output_path = RAW_DIR / f"live_nav_{scheme_code}_{safe_name}.csv"
    df.to_csv(output_path, index=False)

    return str(output_path)


def main() -> None:
    log_lines = []
    log_lines.append("Live NAV Fetch Summary")
    log_lines.append(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    for scheme_code, scheme_name in SCHEMES.items():
        try:
            print(f"Fetching NAV for {scheme_code} - {scheme_name}")
            output_path = save_scheme_nav(scheme_code, scheme_name)
            print(f"Saved: {output_path}")
            log_lines.append(f"SUCCESS: {scheme_code} - {scheme_name} -> {output_path}")
        except Exception as error:
            print(f"FAILED: {scheme_code} - {scheme_name}: {error}")
            log_lines.append(f"FAILED: {scheme_code} - {scheme_name}: {error}")

    log_path = REPORTS_DIR / "live_nav_fetch_summary.txt"
    log_path.write_text("\n".join(log_lines), encoding="utf-8")
    print(f"\nLive NAV fetch report saved to: {log_path}")


if __name__ == "__main__":
    main()
