# F1 Race Intelligence Analysis

An interactive Formula 1 analytics dashboard built with Python, Streamlit, Pandas and Plotly.

## Features

- Driver championship points, wins and podium statistics
- Constructor points comparison
- Grand Prix events grouped by host country
- Race result status and reliability insights
- Interactive season selection and charts

## Technologies

- Python
- Streamlit
- Pandas
- Plotly
- Requests
- Jolpica F1 API

## Run Locally

1. Install Python 3.10 or later.
2. Clone or download this repository.
3. Create and activate a virtual environment.
4. Install dependencies:

   `pip install -r requirements.txt`

5. Start the dashboard:

   `streamlit run app.py`

## Data Source

Race results are retrieved from the Jolpica F1 API. An internet connection is required.

## Limitations

The dashboard currently analyzes race-result data. Recorded non-finish statuses do not necessarily identify mechanical failures. Tyre-compound analysis and cumulative championship trajectories are not currently implemented.

## Purpose

This project demonstrates interactive data analysis and visualization using historical Formula 1 results.