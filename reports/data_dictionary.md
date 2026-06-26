
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
