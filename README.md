# Capstone Project 1 - Mutual Fund Analytics

## Day 1: Project Setup + Data Ingestion (ETL)

This project contains the Day 1 files for setting up a Mutual Fund Analytics ETL workflow.

## Folder Structure

```text
mutual_fund_analytics_day1/
├── data/
│   ├── raw/              # Keep original CSV files here
│   └── processed/        # Cleaned/processed files will be saved here
├── notebooks/            # Jupyter notebooks
├── sql/                  # SQL scripts
├── dashboard/            # Dashboard files
├── reports/              # Data quality and summary reports
├── scripts/              # Python scripts
├── requirements.txt
├── README.md
└── .gitignore
```

## Setup Instructions

### 1. Create virtual environment

```bash
python -m venv .venv
```

### 2. Activate virtual environment

Windows:

```bash
.venv\Scripts\activate
```

Mac/Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add datasets

Place all 10 provided CSV files inside:

```text
data/raw/
```

Expected important files, if available:

```text
fund_master.csv
nav_history.csv
```

### 5. Run data ingestion

```bash
python scripts/data_ingestion.py
```

### 6. Fetch live NAV data

```bash
python scripts/live_nav_fetch.py
```

### 7. Check generated reports

Reports will be saved in:

```text
reports/
```

## Git Commands

```bash
git init
git add .
git commit -m "Day 1: Data ingestion complete"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```
