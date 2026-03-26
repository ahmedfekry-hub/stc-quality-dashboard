# STC Quality Executive Dashboard (Streamlit)

## Files included
- `app.py` — interactive Streamlit dashboard
- `Most common Deviations.xlsx` — source file expected by the app
- `deviations_data.csv` — fallback raw data
- `kpi_snapshot.csv` — editable KPI card values
- `monthly_progress.csv` — editable monthly KPI trend
- `contractor_mapping_template.csv` — fill this file to activate contractor ranking

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## How contractor ranking works
The uploaded raw data does not include a contractor column.
To enable contractor ranking:
1. Open `contractor_mapping_template.csv`
2. Fill `ContractorName` for each `WorkOrderNum`
3. Save the file
4. Restart the Streamlit app

## What the dashboard includes
- KPI snapshot and monthly performance trend
- Most common deviations
- District heatmap
- Top WO ranking
- WO drilldown table
- District owner table per deviation
- Contractor ranking (when contractor mapping is added)
- Recovery action tracker

## Notes
- KPI values are prefilled from the screenshot you shared and can be edited in `kpi_snapshot.csv` and `monthly_progress.csv`.
