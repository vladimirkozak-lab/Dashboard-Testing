# Excel Dashboard Builder (Template)

A starter Streamlit app that turns arbitrary Excel files into interactive dashboards.

## Features

- Upload one or many Excel workbooks (`.xlsx`, `.xlsm`, `.xls`)
- Choose file + sheet
- Automatic type detection for numeric, date, categorical, and boolean columns
- Sidebar filtering for dates/categorical values
- Auto-generated KPI cards and charts
- Custom chart builder (bar, line, scatter, histogram, box)

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Notes

- The app uses best-effort type coercion for mixed Excel inputs.
- For large workbooks, you may want to load partial rows or pre-convert to parquet.
