# UPRVUNL Thermal Plant — Technical & Financial Benchmarking Dashboard

A Streamlit web app for technical and financial analysis of UPRVUNL coal-based
thermal power stations, built from `Book2.xlsx`.

## What's inside

- **`app.py`** — the Streamlit dashboard (6 pages: Overview, Technical Analysis,
  Financial Analysis, 9-Plant Benchmarking, 5-Year Trends, Raw Data)
- **`data/timeseries.csv`** — cleaned FY2019-20 → FY2023-24 technical + financial
  data for the 3 plants with full records in the workbook (Anpara-A, Parichha
  Extn., Obra-B), plus derived metrics (SCC, cost per unit, debt-equity ratio, etc.)
- **`data/benchmark_9plants.csv`** — FY2023-24 snapshot extended to 9 plants
  (adds Jawaharpur, Obra-C, Anpara-B, Harduaganj Extn. II, Parichha Extn. II,
  Harduaganj as reference points) for fleet-wide benchmarking, per the analysis
  brief.
- **`extract_data.py` / `build_datasets.py` / `build_benchmark.py`** — the
  scripts used to derive the CSVs from `Book2.xlsx`. Re-run these if you update
  the source workbook.

> Only Anpara-A, Parichha Extn., and Obra-B have complete parameter data in
> `Book2.xlsx`; the other 6 plants are shown on the benchmarking page as
> reference values only, clearly flagged in the data table.

## Setup & run (using `uv`)

```bash
# 1. Create the virtual environment and install dependencies
uv venv
uv sync          # installs everything listed in pyproject.toml

# 2. Run the app
uv run streamlit run app.py
```

Then open the URL shown in the terminal (usually `http://localhost:8501`).

If you'd rather install ad hoc instead of using the lockfile:

```bash
uv venv
uv pip install streamlit pandas plotly openpyxl statsmodels
uv run streamlit run app.py
```

## Regenerating the data (optional)

If you replace `Book2.xlsx` with an updated workbook:

```bash
uv run --with openpyxl python extract_data.py
uv run --with pandas python build_datasets.py
uv run --with pandas python build_benchmark.py
```

This refreshes `data/timeseries.csv` and `data/benchmark_9plants.csv`, which
`app.py` reads directly.

## Key metrics computed

- **SCC (Specific Coal Consumption)** = SHR ÷ GCV (kg/kWh)
- **Fuel & O&M cost per unit** (paise/kWh) from coal price, oil price, and O&M spend
- **Capital cost intensity** (₹ Cr/MW)
- **Debt-equity ratio** and **net block % of capital cost** (depreciation trend)
- **Composite technical score** normalizing SHR, APC, SCC, and PLF (0–100 scale)
# plant-benchmarking
