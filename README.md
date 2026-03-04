# Excel Dashboard Builder (Template)

A starter Streamlit app that turns arbitrary Excel files into interactive dashboards.

## Features

- Upload one or many Excel workbooks (`.xlsx`, `.xlsm`, `.xls`)
- Choose file + sheet
- Automatic type detection for numeric, date, categorical, and boolean columns
- Sidebar filtering for dates/categorical values
- Auto-generated KPI cards and charts
- Custom chart builder (bar, line, scatter, histogram, box)

## Can I launch it from this environment?

Short answer: **you should run it locally**.

- In this hosted execution environment, required Python packages (`streamlit`, `pandas`, `plotly`, `openpyxl`) are not installed.
- Installing them here is currently blocked by package-index/proxy restrictions.
- Because of that, the app server cannot be launched from this session.

## Run locally (recommended)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then open: `http://localhost:8501`

## How to test it (manual smoke test)

1. **Create test data**:

   ```bash
   python tools/create_sample_excel.py
   ```

2. **Run the app**:

   ```bash
   streamlit run app.py
   ```

3. **In the browser** (usually `http://localhost:8501`):
   - Upload `sample_data.xlsx`.
   - Switch between `Sales` and `Support` sheets.
   - Verify KPI cards update.
   - Use sidebar filters (date, category/boolean values).
   - Check that default charts appear when numeric/date/category columns exist.
   - Use **Custom Chart Builder** and click **Generate chart**.

4. **Expected results**:
   - Data preview loads without errors.
   - Column type summary shows inferred types.
   - Filtering reduces row counts.
   - Charts update without exceptions.

## Notes

- The app uses best-effort type coercion for mixed Excel inputs.
- For large workbooks, you may want to load partial rows or pre-convert to parquet.
