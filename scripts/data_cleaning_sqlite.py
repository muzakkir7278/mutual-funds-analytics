import sqlite3
from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
SQL_DIR = BASE_DIR / "sql"
DB_PATH = BASE_DIR / "bluestock_mf.db"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
SQL_DIR.mkdir(parents=True, exist_ok=True)


def read_csv(file_name):
    file_path = RAW_DIR / file_name
    if not file_path.exists():
        print("Missing file:", file_name)
        return pd.DataFrame()
    return pd.read_csv(file_path)


def save_clean(df, file_name):
    output_path = PROCESSED_DIR / file_name
    df.to_csv(output_path, index=False)
    print("Saved:", output_path)


def clean_fund_master():
    df = read_csv("fund_master.csv")
    if df.empty:
        return df

    df = df.drop_duplicates()
    df.columns = df.columns.str.strip().str.lower()

    text_cols = ["scheme_name", "fund_house", "category", "sub_category", "risk_grade"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    if "scheme_code" in df.columns:
        df["scheme_code"] = pd.to_numeric(df["scheme_code"], errors="coerce")
        df = df.dropna(subset=["scheme_code"])
        df["scheme_code"] = df["scheme_code"].astype(int)

    if "launch_date" in df.columns:
        df["launch_date"] = pd.to_datetime(df["launch_date"], errors="coerce")

    save_clean(df, "fund_master_cleaned.csv")
    return df


def clean_nav_history():
    df = read_csv("nav_history.csv")
    if df.empty:
        return df

    df = df.drop_duplicates()
    df.columns = df.columns.str.strip().str.lower()

    df["scheme_code"] = pd.to_numeric(df["scheme_code"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")

    df = df.dropna(subset=["scheme_code", "date", "nav"])
    df = df[df["nav"] > 0]
    df["scheme_code"] = df["scheme_code"].astype(int)

    df = df.sort_values(["scheme_code", "date"])
    df["nav"] = df.groupby("scheme_code")["nav"].ffill()

    save_clean(df, "nav_history_cleaned.csv")
    return df


def clean_investor_transactions():
    df = read_csv("investor_transactions.csv")
    if df.empty:
        return df

    df = df.drop_duplicates()
    df.columns = df.columns.str.strip().str.lower()

    df["scheme_code"] = pd.to_numeric(df["scheme_code"], errors="coerce")
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    df["transaction_type"] = df["transaction_type"].astype(str).str.strip().str.title()
    allowed_types = ["Sip", "Lumpsum", "Redemption"]
    df = df[df["transaction_type"].isin(allowed_types)]

    df["kyc_status"] = df["kyc_status"].astype(str).str.strip().str.title()
    allowed_kyc = ["Verified", "Pending", "Rejected"]
    df = df[df["kyc_status"].isin(allowed_kyc)]

    df = df.dropna(subset=["scheme_code", "transaction_date", "amount"])
    df = df[df["amount"] > 0]
    df["scheme_code"] = df["scheme_code"].astype(int)

    save_clean(df, "investor_transactions_cleaned.csv")
    return df


def clean_scheme_performance():
    df = read_csv("scheme_performance.csv")
    if df.empty:
        return df

    df = df.drop_duplicates()
    df.columns = df.columns.str.strip().str.lower()

    numeric_cols = [
        "scheme_code",
        "one_month_return",
        "three_month_return",
        "six_month_return",
        "one_year_return",
        "three_year_return",
        "expense_ratio",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["scheme_code"])
    df["scheme_code"] = df["scheme_code"].astype(int)

    if "expense_ratio" in df.columns:
        df = df[(df["expense_ratio"] >= 0.1) & (df["expense_ratio"] <= 2.5)]

    save_clean(df, "scheme_performance_cleaned.csv")
    return df


def clean_aum_history():
    df = read_csv("aum_history.csv")
    if df.empty:
        return df

    df = df.drop_duplicates()
    df.columns = df.columns.str.strip().str.lower()

    df["scheme_code"] = pd.to_numeric(df["scheme_code"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["aum_crore"] = pd.to_numeric(df["aum_crore"], errors="coerce")

    df = df.dropna(subset=["scheme_code", "date", "aum_crore"])
    df = df[df["aum_crore"] > 0]
    df["scheme_code"] = df["scheme_code"].astype(int)

    save_clean(df, "aum_history_cleaned.csv")
    return df


def clean_expense_ratio():
    df = read_csv("expense_ratio.csv")
    if df.empty:
        return df

    df = df.drop_duplicates()
    df.columns = df.columns.str.strip().str.lower()

    df["scheme_code"] = pd.to_numeric(df["scheme_code"], errors="coerce")
    df["expense_ratio"] = pd.to_numeric(df["expense_ratio"], errors="coerce")

    df = df.dropna(subset=["scheme_code", "expense_ratio"])
    df = df[(df["expense_ratio"] >= 0.1) & (df["expense_ratio"] <= 2.5)]
    df["scheme_code"] = df["scheme_code"].astype(int)

    save_clean(df, "expense_ratio_cleaned.csv")
    return df


def create_dim_date(nav_df, trans_df, aum_df):
    dates = []

    if not nav_df.empty and "date" in nav_df.columns:
        dates.extend(nav_df["date"].dropna().tolist())

    if not trans_df.empty and "transaction_date" in trans_df.columns:
        dates.extend(trans_df["transaction_date"].dropna().tolist())

    if not aum_df.empty and "date" in aum_df.columns:
        dates.extend(aum_df["date"].dropna().tolist())

    dim_date = pd.DataFrame({"date": pd.to_datetime(pd.Series(dates).drop_duplicates())})
    dim_date = dim_date.dropna().sort_values("date")
    dim_date["date_id"] = dim_date["date"].dt.strftime("%Y%m%d").astype(int)
    dim_date["year"] = dim_date["date"].dt.year
    dim_date["month"] = dim_date["date"].dt.month
    dim_date["day"] = dim_date["date"].dt.day
    dim_date["month_name"] = dim_date["date"].dt.month_name()

    save_clean(dim_date, "dim_date_cleaned.csv")
    return dim_date


def create_schema_sql():
    schema = """
DROP TABLE IF EXISTS fact_aum;
DROP TABLE IF EXISTS fact_performance;
DROP TABLE IF EXISTS fact_transactions;
DROP TABLE IF EXISTS fact_nav;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_fund;

CREATE TABLE dim_fund (
    scheme_code INTEGER PRIMARY KEY,
    scheme_name TEXT,
    fund_house TEXT,
    category TEXT,
    sub_category TEXT,
    risk_grade TEXT,
    launch_date TEXT
);

CREATE TABLE dim_date (
    date_id INTEGER PRIMARY KEY,
    date TEXT,
    year INTEGER,
    month INTEGER,
    day INTEGER,
    month_name TEXT
);

CREATE TABLE fact_nav (
    nav_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scheme_code INTEGER,
    date TEXT,
    nav REAL,
    FOREIGN KEY (scheme_code) REFERENCES dim_fund(scheme_code)
);

CREATE TABLE fact_transactions (
    transaction_id TEXT PRIMARY KEY,
    investor_id TEXT,
    scheme_code INTEGER,
    transaction_date TEXT,
    transaction_type TEXT,
    amount REAL,
    state TEXT,
    kyc_status TEXT,
    FOREIGN KEY (scheme_code) REFERENCES dim_fund(scheme_code)
);

CREATE TABLE fact_performance (
    performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scheme_code INTEGER,
    one_month_return REAL,
    three_month_return REAL,
    six_month_return REAL,
    one_year_return REAL,
    three_year_return REAL,
    expense_ratio REAL,
    FOREIGN KEY (scheme_code) REFERENCES dim_fund(scheme_code)
);

CREATE TABLE fact_aum (
    aum_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scheme_code INTEGER,
    date TEXT,
    aum_crore REAL,
    FOREIGN KEY (scheme_code) REFERENCES dim_fund(scheme_code)
);
"""
    schema_path = SQL_DIR / "schema.sql"
    schema_path.write_text(schema)
    print("Saved:", schema_path)


def create_queries_sql():
    queries = """
-- 1. Top 5 funds by AUM
SELECT f.scheme_name, a.aum_crore
FROM fact_aum a
JOIN dim_fund f ON a.scheme_code = f.scheme_code
ORDER BY a.aum_crore DESC
LIMIT 5;

-- 2. Average NAV per month
SELECT scheme_code, strftime('%Y-%m', date) AS month, AVG(nav) AS avg_nav
FROM fact_nav
GROUP BY scheme_code, strftime('%Y-%m', date);

-- 3. SIP transaction amount by state
SELECT state, SUM(amount) AS total_sip_amount
FROM fact_transactions
WHERE transaction_type = 'Sip'
GROUP BY state
ORDER BY total_sip_amount DESC;

-- 4. Funds with expense ratio below 1%
SELECT f.scheme_name, p.expense_ratio
FROM fact_performance p
JOIN dim_fund f ON p.scheme_code = f.scheme_code
WHERE p.expense_ratio < 1
ORDER BY p.expense_ratio;

-- 5. Top funds by one year return
SELECT f.scheme_name, p.one_year_return
FROM fact_performance p
JOIN dim_fund f ON p.scheme_code = f.scheme_code
ORDER BY p.one_year_return DESC
LIMIT 5;

-- 6. Category-wise fund count
SELECT category, COUNT(*) AS total_funds
FROM dim_fund
GROUP BY category;

-- 7. Risk grade-wise fund count
SELECT risk_grade, COUNT(*) AS total_funds
FROM dim_fund
GROUP BY risk_grade;

-- 8. Total transaction amount by transaction type
SELECT transaction_type, SUM(amount) AS total_amount
FROM fact_transactions
GROUP BY transaction_type;

-- 9. Category-wise AUM
SELECT f.category, SUM(a.aum_crore) AS total_aum
FROM fact_aum a
JOIN dim_fund f ON a.scheme_code = f.scheme_code
GROUP BY f.category
ORDER BY total_aum DESC;

-- 10. NAV trend by scheme
SELECT f.scheme_name, n.date, n.nav
FROM fact_nav n
JOIN dim_fund f ON n.scheme_code = f.scheme_code
ORDER BY f.scheme_name, n.date;
"""
    queries_path = SQL_DIR / "queries.sql"
    queries_path.write_text(queries)
    print("Saved:", queries_path)


def load_to_sqlite(fund_df, nav_df, trans_df, perf_df, aum_df, dim_date_df):
    conn = sqlite3.connect(DB_PATH)

    schema_path = SQL_DIR / "schema.sql"
    schema_sql = schema_path.read_text()
    conn.executescript(schema_sql)

    fund_df.to_sql("dim_fund", conn, if_exists="append", index=False)
    dim_date_df.to_sql("dim_date", conn, if_exists="append", index=False)
    nav_df.to_sql("fact_nav", conn, if_exists="append", index=False)
    trans_df.to_sql("fact_transactions", conn, if_exists="append", index=False)
    perf_df.to_sql("fact_performance", conn, if_exists="append", index=False)
    aum_df.to_sql("fact_aum", conn, if_exists="append", index=False)

    tables = ["dim_fund", "dim_date", "fact_nav", "fact_transactions", "fact_performance", "fact_aum"]
    print("\nSQLite row count verification:")
    for table in tables:
        count = pd.read_sql_query("SELECT COUNT(*) AS count FROM " + table, conn)
        print(table, ":", int(count["count"][0]))

    conn.close()
    print("\nDatabase created:", DB_PATH)


def create_data_dictionary():
    content = """
# Data Dictionary - Mutual Fund Analytics

## dim_fund

| Column | Data Type | Business Meaning | Source |
|---|---|---|---|
| scheme_code | INTEGER | Unique AMFI scheme code | fund_master.csv |
| scheme_name | TEXT | Mutual fund scheme name | fund_master.csv |
| fund_house | TEXT | Asset management company name | fund_master.csv |
| category | TEXT | Main fund category | fund_master.csv |
| sub_category | TEXT | Fund sub-category | fund_master.csv |
| risk_grade | TEXT | Risk classification | fund_master.csv |
| launch_date | TEXT | Scheme launch date | fund_master.csv |

## dim_date

| Column | Data Type | Business Meaning | Source |
|---|---|---|---|
| date_id | INTEGER | Date key in YYYYMMDD format | Generated |
| date | TEXT | Calendar date | nav_history.csv, investor_transactions.csv, aum_history.csv |
| year | INTEGER | Calendar year | Generated |
| month | INTEGER | Calendar month | Generated |
| day | INTEGER | Calendar day | Generated |
| month_name | TEXT | Month name | Generated |

## fact_nav

| Column | Data Type | Business Meaning | Source |
|---|---|---|---|
| nav_id | INTEGER | Auto-generated NAV record ID | Generated |
| scheme_code | INTEGER | Fund scheme code | nav_history.csv |
| date | TEXT | NAV date | nav_history.csv |
| nav | REAL | Net Asset Value | nav_history.csv |

## fact_transactions

| Column | Data Type | Business Meaning | Source |
|---|---|---|---|
| transaction_id | TEXT | Unique transaction ID | investor_transactions.csv |
| investor_id | TEXT | Investor identifier | investor_transactions.csv |
| scheme_code | INTEGER | Fund scheme code | investor_transactions.csv |
| transaction_date | TEXT | Transaction date | investor_transactions.csv |
| transaction_type | TEXT | SIP, Lumpsum, or Redemption | investor_transactions.csv |
| amount | REAL | Transaction amount | investor_transactions.csv |
| state | TEXT | Investor state | investor_transactions.csv |
| kyc_status | TEXT | Investor KYC status | investor_transactions.csv |

## fact_performance

| Column | Data Type | Business Meaning | Source |
|---|---|---|---|
| performance_id | INTEGER | Auto-generated performance ID | Generated |
| scheme_code | INTEGER | Fund scheme code | scheme_performance.csv |
| one_month_return | REAL | 1 month return percentage | scheme_performance.csv |
| three_month_return | REAL | 3 month return percentage | scheme_performance.csv |
| six_month_return | REAL | 6 month return percentage | scheme_performance.csv |
| one_year_return | REAL | 1 year return percentage | scheme_performance.csv |
| three_year_return | REAL | 3 year return percentage | scheme_performance.csv |
| expense_ratio | REAL | Fund expense ratio percentage | scheme_performance.csv |

## fact_aum

| Column | Data Type | Business Meaning | Source |
|---|---|---|---|
| aum_id | INTEGER | Auto-generated AUM record ID | Generated |
| scheme_code | INTEGER | Fund scheme code | aum_history.csv |
| date | TEXT | AUM date | aum_history.csv |
| aum_crore | REAL | Assets under management in crore | aum_history.csv |
"""
    path = BASE_DIR / "reports" / "data_dictionary.md"
    path.write_text(content)
    print("Saved:", path)


def main():
    print("Starting Day 2 cleaning and SQLite loading...\n")

    fund_df = clean_fund_master()
    nav_df = clean_nav_history()
    trans_df = clean_investor_transactions()
    perf_df = clean_scheme_performance()
    aum_df = clean_aum_history()
    clean_expense_ratio()

    dim_date_df = create_dim_date(nav_df, trans_df, aum_df)

    create_schema_sql()
    create_queries_sql()
    create_data_dictionary()

    if fund_df.empty or nav_df.empty or trans_df.empty or perf_df.empty or aum_df.empty:
        print("\nSome required files are missing or empty. Database loading skipped.")
    else:
        load_to_sqlite(fund_df, nav_df, trans_df, perf_df, aum_df, dim_date_df)

    print("\nDay 2 completed successfully.")


if __name__ == "__main__":
    main()
