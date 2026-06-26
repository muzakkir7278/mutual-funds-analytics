# Day 1 Data Quality Summary

## Files Checked

Mention all 10 CSV files loaded from `data/raw`.

## Checks Performed

- Shape of every dataset
- Data types of every column
- First 5 rows using `.head()`
- Missing values
- Duplicate rows
- Fund master unique values
- AMFI/scheme code validation between `fund_master` and `nav_history`

## Observations

Write anomalies here after running `python scripts/data_ingestion.py`.

## Conclusion

Day 1 setup and data ingestion completed.
