# CollegeMsg Data Detective Dashboard

An interactive Streamlit dashboard for exploring the [SNAP CollegeMsg
dataset](https://snap.stanford.edu/data/CollegeMsg.html), a temporal network
of private messages between college students.

The dashboard analyzes messaging volume, user activity, network influence,
reciprocity, and reply speed using Pandas, Plotly, and NetworkX.

## Features

- Weekday-by-hour activity heatmap
- Daily message volume with a seven-day rolling average
- User activity distributions and top senders
- PageRank-based influence and a configurable network graph
- Reciprocity and reply-time analysis
- Filters for timezone, date range, minimum messages per user, and graph size

## Requirements

- Python 3.9 or newer
- The `CollegeMsg.txt.gz` dataset file in the project root

Install the dependencies in a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

## Dataset

Download `CollegeMsg.txt.gz` from the [SNAP CollegeMsg
page](https://snap.stanford.edu/data/CollegeMsg.html) and place it next to
`app.py`:

```text
dvt-dashboard/
├── app.py
├── visualizations.py
├── CollegeMsg.txt.gz
└── requirements.txt
```

The application removes duplicate rows while loading the data and derives
datetime, date, hour, weekday, user statistics, PageRank, and reply-time
values.

## Run the dashboard

From the project directory, run:

```bash
streamlit run app.py
```

Streamlit will print a local URL, normally
`http://localhost:8501`, which can be opened in a browser.

## Supporting scripts

- `data_discovery.py` prints dataset shape, types, temporal coverage, data
  quality checks, outliers, and basic activity patterns.
- `visualizations.py` contains the reusable data-processing and chart
  functions. Running it directly prints KPI data and exports chart HTML files.
- `DATASET_SUMMARY.md` contains the current exploratory summary and key
  findings.

Run the discovery script with:

```bash
python data_discovery.py
```

## Project structure

| File | Purpose |
| --- | --- |
| `app.py` | Streamlit dashboard |
| `visualizations.py` | Data loading, metrics, and Plotly figures |
| `data_discovery.py` | Command-line exploratory analysis |
| `CollegeMsg.txt.gz` | Input dataset |
| `requirements.txt` | Python dependencies |
