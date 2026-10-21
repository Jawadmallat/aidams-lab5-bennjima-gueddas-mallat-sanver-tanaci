"""Download the public project data for lab5 into data/ (run: uv run --extra fetch python fetch_data.py).

Sources
- Climate TRACE API v6: country emissions (CH4, CO2, CO2e) for oil-and-gas production and transport.
- Eurostat nrg_ti_gas: EU27 natural gas imports by partner country (million m3).
- Our World in Data energy dataset (Energy Institute Statistical Review): gas and oil production (TWh).
"""

import io
import json
import ssl
import urllib.request
from pathlib import Path

import certifi
import pandas as pd

DATA = Path(__file__).parent / "data"
SUPPLIERS = pd.DataFrame(
    {
        "country": ["Qatar", "Russia", "United States", "Norway", "Algeria", "Nigeria"],
        "iso3": ["QAT", "RUS", "USA", "NOR", "DZA", "NGA"],
        "iso2": ["QA", "RU", "US", "NO", "DZ", "NG"],
    }
)
YEARS = range(2015, 2026)
SUBSECTORS = ["oil-and-gas-production", "oil-and-gas-transport"]


# uv's Python does not see the macOS keychain; certifi's CA bundle covers Eurostat's chain.
SSL_CTX = ssl.create_default_context(cafile=certifi.where())


def get(url):
    with urllib.request.urlopen(url, timeout=120, context=SSL_CTX) as r:
        return r.read()


def get_json(url):
    return json.loads(get(url))


def climate_trace():
    # The API sums over [since, to], so query one year at a time.
    rows = []
    countries = ",".join(SUPPLIERS.iso3)
    for sub in SUBSECTORS:
        for y in YEARS:
            url = (
                "https://api.climatetrace.org/v6/country/emissions"
                f"?since={y}&to={y}&countries={countries}&subsectors={sub}"
            )
            for d in get_json(url):
                e = d["emissions"]
                rows.append(
                    {"iso3": d["country"], "year": y, "subsector": sub,
                     "ch4_t": e["ch4"], "co2_t": e["co2"], "co2e_100yr_t": e["co2e_100yr"]}
                )
    return pd.DataFrame(rows).sort_values(["subsector", "iso3", "year"])


def eurostat_imports():
    partners = "".join(f"&partner={p}" for p in SUPPLIERS.iso2)
    url = (
        "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_ti_gas"
        f"?format=JSON&lang=EN&geo=EU27_2020&siec=G3000&unit=MIO_M3&sinceTimePeriod=2015{partners}"
    )
    d = get_json(url)
    cat = {k: list(d["dimension"][k]["category"]["index"]) for k in d["id"]}
    idx = pd.MultiIndex.from_product([cat[k] for k in d["id"]], names=d["id"])
    s = pd.Series({idx[int(i)]: v for i, v in d["value"].items()}, dtype=float)
    s.index = pd.MultiIndex.from_tuples(s.index, names=d["id"])
    out = s.rename("imports_mio_m3").reset_index()[["partner", "time", "imports_mio_m3"]]
    out = out.rename(columns={"partner": "iso2", "time": "year"}).astype({"year": int})
    return out.sort_values(["iso2", "year"])


def owid_production():
    url = "https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv"
    owid = pd.read_csv(io.BytesIO(get(url)), usecols=["iso_code", "year", "gas_production", "oil_production"])
    out = owid[owid.iso_code.isin(SUPPLIERS.iso3) & owid.year.between(YEARS[0], YEARS[-1])]
    out = out.rename(columns={"iso_code": "iso3", "gas_production": "gas_twh", "oil_production": "oil_twh"})
    return out.dropna().sort_values(["iso3", "year"])


if __name__ == "__main__":
    DATA.mkdir(exist_ok=True)
    SUPPLIERS.to_csv(DATA / "suppliers.csv", index=False)
    for name, fn in [("climate_trace_emissions.csv", climate_trace),
                     ("eu_gas_imports.csv", eurostat_imports),
                     ("hydrocarbon_production.csv", owid_production)]:
        df = fn()
        df.to_csv(DATA / name, index=False)
        print(f"{name}: {len(df)} rows, years {df.year.min()}-{df.year.max()}")
