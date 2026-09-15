# Merge Notes

## What changed

- Added more dashboard indicators from UNDP HDI and ITU data sources.
- Added a source filter above the indicator filter.
- The indicator filter now only shows indicators for the selected source.
- Added a `Summary` button that opens a dashboard summary dialog.
- The summary dialog can use AI when `OPENAI_API_KEY` is configured.
- If AI is unavailable, the dashboard uses a local calculated summary instead.
- Prediction/forecasting was tested and removed for now.

## Files your colleague should review

- `dashboard/app.py`
- `requirements.txt`
- `src/analysis/indicators.py`
- `src/ingestion/undp_hdi.py`
- `src/ingestion/itu_datahub.py`
- `src/cleaning/clean_undp_hdi.py`
- `src/cleaning/clean_itu_datahub.py`
- `src/database/load_undp_hdi.py`
- `src/database/load_itu_datahub.py`
- `sql/undp_indicators.sql`
- `sql/itu_indicators.sql`

## Local setup

Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a local `.env` file from `.env.example`:

```powershell
Copy-Item .env.example .env
```

Update the database values in `.env` to match the local PostgreSQL setup.

AI summaries are optional. To enable them, add:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

If those values are missing or there is no internet connection, the dashboard still works with the built-in fallback summary.

## Run the dashboard

```powershell
.\.venv\Scripts\python.exe -m streamlit run dashboard\app.py
```

## Notes before merging

- The `.env` file should not be committed.
- Commit the pipeline scripts.
- The raw and processed ITU/UNDP CSV files can be generated from the pipeline commands below.
- After merging, confirm the database has the UNDP and ITU indicator data loaded before testing the new source filter.

## Regenerate ITU and UNDP data

Run these commands after pulling the branch to generate the raw and processed ITU/UNDP CSV files:

```powershell
python src/ingestion/itu_datahub.py
python src/cleaning/clean_itu_datahub.py

python src/ingestion/undp_hdi.py
python src/cleaning/clean_undp_hdi.py
```

This recreates:

- `data/raw/itu_datahub_source.csv`
- `data/raw/itu_datahub_raw.csv`
- `data/processed/itu_datahub_clean.csv`
- `data/raw/undp_hdi_source.csv`
- `data/raw/undp_hdi_raw.csv`
- `data/processed/undp_hdi_clean.csv`

Then load the generated data into PostgreSQL:

```powershell
python src/database/load_itu_datahub.py
python src/database/load_undp_hdi.py
```
