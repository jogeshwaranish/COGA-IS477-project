"""Readers for the raw data files in data/raw/.
"""
from __future__ import annotations
import json
import re
import pandas as pd
from utils import RAW

# File locations
ZILLOW_FILE = RAW / "zillow" / "County_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv"

# ACS 5-year releases: the 2019 vintage covers 2015-2019, the 2024 vintage covers 2020-2024.
ACS_FILES = {
    2019: RAW / "acs" / "acs5_2019.json",
    2024: RAW / "acs" / "acs5_2024.json",
}
# BLS names its county files by two-digit year: laucnty15.xlsx ... laucnty24.xlsx
BLS_FILES = {year: RAW / "bls" / f"laucnty{str(year)[2:]}.xlsx" for year in range(2015, 2025)}

FRED_FILES = {
    "MORTGAGE30US": RAW / "fred" / "MORTGAGE30US.csv",  # 30-year fixed mortgage rate, weekly
    "CPIAUCSL": RAW / "fred" / "CPIAUCSL.csv",          # CPI-U, monthly (used to inflation-adjust)
}

# "E" = estimate, "M" = margin of error (90% confidence).
ACS_VARS = {
    "B19013_001E": "median_hh_income",           # B19013: median household income
    "B19013_001M": "median_hh_income_moe",
    "B01003_001E": "population",                 # B01003: total population
    "B25003_001E": "occupied_units",             # B25003: tenure (owner vs renter)
    "B25003_002E": "owner_units",
    "B25003_003E": "renter_units",
    "B25064_001E": "median_gross_rent",          # B25064: median gross rent
    "B25077_001E": "acs_median_home_value",      # B25077: median home value (cross-check for Zillow)
    "B25077_001M": "acs_median_home_value_moe",
}

BLS_COLUMNS = ["laus_code", "state_fips", "county_fips", "county_name", "year",
               "labor_force", "employed", "unemployed", "unemp_rate"]

DATE_COLUMN = re.compile(r"\d{4}-\d{2}-\d{2}")


# FIPS helpers
def pad_code(codes: pd.Series, width: int) -> pd.Series:
    return codes.astype(int).astype(str).str.zfill(width)


def make_fips(state: pd.Series, county: pd.Series) -> pd.Series:
    """5-digit county FIPS = 2-digit state + 3-digit county."""
    return pad_code(state, 2) + pad_code(county, 3)


# Readers
def read_zillow_raw() -> pd.DataFrame:
    """ one row per county, one column per month."""
    df = pd.read_csv(ZILLOW_FILE)
    df["fips"] = make_fips(df["StateCodeFIPS"], df["MunicipalCodeFIPS"])
    return df


def zillow_date_cols(df: pd.DataFrame) -> list[str]:
    """Month columns are named like '2015-01-31'; everything else is an ID column."""
    return [col for col in df.columns if DATE_COLUMN.fullmatch(col)]


def read_acs_raw() -> pd.DataFrame:
    frames = []
    for vintage, path in ACS_FILES.items():
        rows = json.loads(path.read_text())
        header, records = rows[0], rows[1:]
        frame = pd.DataFrame(records, columns=header)
        frame["vintage"] = vintage
        frames.append(frame)

    df = pd.concat(frames, ignore_index=True)
    df["fips"] = make_fips(df["state"], df["county"])

    # The API sends every value as text. Negative sentinel codes (e.g. -666666666)
    # stay as numbers here; the ACS cleaning step turns them into nulls.
    for code in ACS_VARS:
        df[code] = pd.to_numeric(df[code], errors="coerce")
    return df


def read_one_bls_file(path) -> pd.DataFrame:
    """Wwe read it without a header and
    keep only the rows that hold a county record."""
    raw = pd.read_excel(path, header=None, dtype=str)
    raw = raw.dropna(axis=1, how="all")  # drop the empty spacer column
    raw = raw.iloc[:, :9]                # the 9 data columns
    raw.columns = BLS_COLUMNS
    # A real county row has numeric state/county codes and a sensible year.
    state = pd.to_numeric(raw["state_fips"], errors="coerce")
    county = pd.to_numeric(raw["county_fips"], errors="coerce")
    year = pd.to_numeric(raw["year"], errors="coerce")
    is_county_row = state.notna() & county.notna() & year.between(1990, 2100)
    data = raw[is_county_row].copy()
    data["state_fips"] = pad_code(state[is_county_row], 2)
    data["county_fips"] = pad_code(county[is_county_row], 3)
    data["year"] = year[is_county_row].astype(int)
    data["source_file"] = path.name
    return data


def read_bls_raw() -> pd.DataFrame:
    """one row per county per year."""
    df = pd.concat([read_one_bls_file(path) for path in BLS_FILES.values()], ignore_index=True)
    df["fips"] = df["state_fips"] + df["county_fips"]

    # Counts use thousands separators ("12,345"), so strip commas before converting.
    for col in ["labor_force", "employed", "unemployed", "unemp_rate"]:
        df[col] = pd.to_numeric(df[col].str.replace(",", ""), errors="coerce")
    return df


def read_fred_raw(series: str) -> pd.DataFrame:
    df = pd.read_csv(FRED_FILES[series])
    df.columns = ["date", "value"]
    df["date"] = pd.to_datetime(df["date"])
    # FRED marks missing observations with '.', which to_numeric turns into NaN.
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df