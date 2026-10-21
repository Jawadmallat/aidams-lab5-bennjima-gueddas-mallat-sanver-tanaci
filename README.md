# AIDAMS Lab 5: Put Uncertainty Into Your Project

Group: Adem Ben Njima, Kenza Gueddas, Jawad Mallat, Erdem Sanver, Deha Tanaci

Project: Oil & Gas, sustainability consultant. Key quantity: upstream methane (kt CH4/yr) embedded in EU27
natural-gas imports from Qatar, Russia, the United States, Norway, Algeria and Nigeria.

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync                 # core dependencies, enough to run the notebook
uv sync --extra fetch   # optional: certifi, only needed to re-download data/ with fetch_data.py
```

## Run

Open `lab5.ipynb` in VS Code / Jupyter and select the `.venv` kernel, or:

```bash
uv run --with jupyter jupyter lab lab5.ipynb
```

## Data

The notebook reads the CSVs in `data/` (committed, so no download is needed). They were produced by
`uv run --extra fetch python fetch_data.py` from public sources:

| File | Source | Content |
|---|---|---|
| `climate_trace_emissions.csv` | [Climate TRACE API v6](https://api.climatetrace.org) | CH4 / CO2 / CO2e (t) by country and year, 2015-2025, subsectors oil-and-gas production and transport |
| `eu_gas_imports.csv` | [Eurostat `nrg_ti_gas`](https://ec.europa.eu/eurostat/databrowser/view/nrg_ti_gas/default/table) | EU27 natural-gas imports by partner, million m3, 2015-2024 |
| `hydrocarbon_production.csv` | [Our World in Data energy data](https://github.com/owid/energy-data) (Energy Institute Statistical Review) | Gas and oil production, TWh, 2015-2024 |
| `suppliers.csv` | - | Country names and ISO codes of the six suppliers |
