"""
Day 1 - Data Ingestion Script
Capstone Project 1: Mutual Fund Analytics

This script:
1. Reads all CSV files from data/raw
2. Prints shape, dtypes, and head for each dataset
3. Finds basic anomalies such as missing values and duplicate rows
4. Explores fund_master if available
5. Validates AMFI/scheme codes between fund_master and nav_history if available
6. Writes a data quality summary report
"""

from pathlib import Path
from datetime import datetime
from typing import List
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
REPORTS_DIR = BASE_DIR / "reports"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def read_csv_safely(file_path: Path) -> pd.DataFrame:
    """Read CSV file with safe fallback encodings."""
    encodings = ["utf-8", "utf-8-sig", "latin1"]
    last_error = None

    for encoding in encodings:
        try:
            return pd.read_csv(file_path, encoding=encoding)
        except Exception as error:
            last_error = error

    raise RuntimeError(f"Could not read {file_path.name}. Last error: {last_error}")


def basic_profile(df, file_name):
    """Create basic profile text for a dataframe."""
    lines = []
    lines.append(f"\n{'=' * 80}")
    lines.append(f"FILE: {file_name}")
    lines.append(f"{'=' * 80}")
    lines.append(f"Shape: {df.shape}")
    lines.append("\nDtypes:")
    lines.append(str(df.dtypes))
    lines.append("\nHead:")
    lines.append(str(df.head()))
    lines.append("\nMissing values per column:")
    lines.append(str(df.isna().sum()))
    lines.append(f"\nDuplicate rows: {df.duplicated().sum()}")
    return lines


def find_column(df: pd.DataFrame, possible_names: list) -> str :
    """Find a column using case-insensitive matching."""
    normalized = {col.lower().strip(): col for col in df.columns}
    for name in possible_names:
        key = name.lower().strip()
        if key in normalized:
            return normalized[key]
    return None


def explore_fund_master(df: pd.DataFrame) -> list:
    """Print unique fund houses, categories, sub-categories, and risk grades."""
    lines = []
    lines.append("\nFUND MASTER EXPLORATION")
    lines.append("-" * 80)

    column_groups = {
        "Fund houses": ["fund_house", "fund house", "amc", "AMC", "asset_management_company"],
        "Categories": ["category", "scheme_category", "scheme category"],
        "Sub-categories": ["sub_category", "sub category", "subcategory", "scheme_sub_category"],
        "Risk grades": ["risk_grade", "risk grade", "riskometer", "risk"],
    }

    for label, names in column_groups.items():
        col = find_column(df, names)
        if col:
            values = sorted(df[col].dropna().astype(str).unique())
            lines.append(f"\n{label} ({col}) - Count: {len(values)}")
            lines.append(str(values[:50]))
        else:
            lines.append(f"\n{label}: Column not found")

    return lines


def validate_amfi_codes(fund_master: pd.DataFrame, nav_history: pd.DataFrame) -> list:
    """Validate every scheme code in fund_master exists in nav_history."""
    lines = []
    lines.append("\nAMFI / SCHEME CODE VALIDATION")
    lines.append("-" * 80)

    fund_code_col = find_column(
        fund_master,
        ["scheme_code", "scheme code", "amfi_code", "amfi code", "code"],
    )
    nav_code_col = find_column(
        nav_history,
        ["scheme_code", "scheme code", "amfi_code", "amfi code", "code"],
    )

    if not fund_code_col or not nav_code_col:
        lines.append("Could not validate because scheme code column was not found in one or both files.")
        lines.append(f"fund_master code column: {fund_code_col}")
        lines.append(f"nav_history code column: {nav_code_col}")
        return lines

    fund_codes = set(fund_master[fund_code_col].dropna().astype(str).str.strip())
    nav_codes = set(nav_history[nav_code_col].dropna().astype(str).str.strip())

    missing_codes = sorted(fund_codes - nav_codes)
    matched_codes = sorted(fund_codes & nav_codes)

    lines.append(f"Total fund_master codes: {len(fund_codes)}")
    lines.append(f"Total nav_history codes: {len(nav_codes)}")
    lines.append(f"Matched codes: {len(matched_codes)}")
    lines.append(f"Missing codes from nav_history: {len(missing_codes)}")

    if missing_codes:
        lines.append("Missing code sample:")
        lines.append(str(missing_codes[:50]))
    else:
        lines.append("Validation passed: every fund_master code exists in nav_history.")

    return lines


def main() -> None:
    csv_files = sorted(RAW_DIR.glob("*.csv"))
    report_lines = []
    report_lines.append("Day 1 Data Quality Summary")
    report_lines.append(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"Raw data folder: {RAW_DIR}")
    report_lines.append(f"CSV files found: {len(csv_files)}")

    if not csv_files:
        report_lines.append("\nNo CSV files found. Please place all 10 datasets inside data/raw/.")
        report_path = REPORTS_DIR / "data_quality_summary.txt"
        report_path.write_text("\n".join(report_lines), encoding="utf-8")
        print("No CSV files found. Add CSV files to data/raw and run again.")
        print(f"Report saved to: {report_path}")
        return

    datasets: dict[str, pd.DataFrame] = {}

    for file_path in csv_files:
        print(f"\nReading: {file_path.name}")
        df = read_csv_safely(file_path)
        datasets[file_path.stem.lower()] = df

        profile_lines = basic_profile(df, file_path.name)
        report_lines.extend(profile_lines)

        print(f"Shape: {df.shape}")
        print("Dtypes:")
        print(df.dtypes)
        print("Head:")
        print(df.head())

    fund_master = datasets.get("fund_master")
    nav_history = datasets.get("nav_history")

    if fund_master is not None:
        report_lines.extend(explore_fund_master(fund_master))
    else:
        report_lines.append("\nfund_master.csv not found. Skipping fund master exploration.")

    if fund_master is not None and nav_history is not None:
        report_lines.extend(validate_amfi_codes(fund_master, nav_history))
    else:
        report_lines.append("\nCould not run AMFI validation because fund_master.csv or nav_history.csv is missing.")

    report_path = REPORTS_DIR / "data_quality_summary.txt"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    print("\nData ingestion complete.")
    print(f"Data quality report saved to: {report_path}")


if __name__ == "__main__":
    main()
