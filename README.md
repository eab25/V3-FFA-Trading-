# FFA Trading Dashboard (Pre-Balmo Revert)

A simple Streamlit dashboard to visualize Baltic Exchange route & TCE indices with bunker fuel prices.

## Features
- CSV upload (Date + index / fuel columns)
- Date range filter
- Four chart panel (Indices, Voyages, Fuel, Fuel Spreads)
- Basic stats (count / min / max / mean)
- Download filtered dataset

## Run
```bash
streamlit run streamlit_app.py
```

## CSV Columns
Expected (any subset is fine):
```
Date, C2, C3, C5, C7, C17, C2TCE, C3TCE, C5TCE, C7TCE, C17TCE,
C8, C9, C10, C14, C16, C5TC, Singapore, Rotterdam, Zhoushan
```

## Notes
This version intentionally excludes Balmo / BOY estimator logic.
