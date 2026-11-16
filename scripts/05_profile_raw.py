#Covers accuracy, completeness, timeliness, consistency + FIPS overlap (integration feasibility).
import json
import pandas as pd
from loaders import ACS_VARS, read_acs_raw, read_bls_raw, read_fred_raw, read_zillow_raw, zillow_date_cols
from utils import QUALITY, ensure_dirs

#placeholders codes for the census data
ACS_SENTINELS = [-222222222, -333333333, -555555555, -666666666, -777777777, -888888888, -999999999]

def valid_fips(s: pd.Series) -> int:
    return int((~s.str.fullmatch(r"\d{5}")).sum())

def profile_zillow() -> tuple[dict, dict]:
    df = read_zillow_raw()
    dates = zillow_date_cols(df)
    window = [d for d in dates if "2015-01-01" <= d <= "2024-12-31"]
    vals = df[window]
    p = {
        "rows_counties": len(df),
        "first_month": dates[0], "last_month": dates[-1],
        "months_in_2015_2024_window": len(window),
        "missing_values_in_window": int(vals.isna().sum().sum()),
        "pct_missing_in_window": round(100 * vals.isna().mean().mean(), 2),
        "counties_with_any_missing_month": int(vals.isna().any(axis=1).sum()),
        "duplicate_fips": int(df["fips"].duplicated().sum()),
        "invalid_fips": valid_fips(df["fips"]),
        "nonpositive_values": int((vals <= 0).sum().sum()),
        "max_value": float(vals.max().max()),
    }
    fips = {"2015-2019": set(df.loc[df[[d for d in window if d < "2020"]].notna().any(axis=1), "fips"]),
            "2020-2024": set(df.loc[df[[d for d in window if d >= "2020"]].notna().any(axis=1), "fips"])}
    return p, fips


def profile_acs() -> tuple[dict, dict]:
    df = read_acs_raw()
    p, fips = {}, {}
    for vintage, g in df.groupby("vintage"):
        cols = list(ACS_VARS)
        sentinel = g[cols].isin(ACS_SENTINELS)
        cv = (g["B19013_001M"] / 1.645) / g["B19013_001E"]
        p[str(vintage)] = {
            "rows_counties": len(g),
            "duplicate_fips": int(g["fips"].duplicated().sum()),
            "invalid_fips": valid_fips(g["fips"]),
            "null_values": int(g[cols].isna().sum().sum()),
            "sentinel_values_by_column": {c: int(n) for c, n in sentinel.sum().items() if n},
            "income_cv_over_30pct": int((cv[g["B19013_001E"] > 0] > 0.30).sum()),
            "renter_plus_owner_ne_total": int((g["B25003_002E"] + g["B25003_003E"] != g["B25003_001E"]).sum()),
            "puerto_rico_rows": int((g["state"] == "72").sum()),
        }
        fips["2015-2019" if vintage == 2019 else "2020-2024"] = set(g["fips"])
    return p, fips


def profile_bls() -> tuple[dict, dict]:
    df = read_bls_raw()
    recomputed = 100 * df["unemployed"] / df["labor_force"]
    p = {
        "rows": len(df),
        "rows_per_year": {int(k): int(v) for k, v in df["year"].value_counts().sort_index().items()},
        "years_present": sorted(int(y) for y in df["year"].unique()),
        "duplicate_fips_year": int(df.duplicated(["fips", "year"]).sum()),
        "invalid_fips": valid_fips(df["fips"]),
        "null_numeric": int(df[["labor_force", "employed", "unemployed", "unemp_rate"]].isna().sum().sum()),
        "employed_plus_unemployed_ne_labor_force": int(
            ((df["employed"] + df["unemployed"] - df["labor_force"]).abs() > 1).sum()),
        "rate_differs_from_recomputed_by_gt_0.15pt": int(((df["unemp_rate"] - recomputed).abs() > 0.15).sum()),
        "rate_out_of_0_100": int((~df["unemp_rate"].between(0, 100)).sum()),
    }
    fips = {"2015-2019": set(df.loc[df["year"] <= 2019, "fips"]),
            "2020-2024": set(df.loc[df["year"] >= 2020, "fips"])}
    return p, fips

def profile_fred() -> dict:
    out = {}
    for s in ["MORTGAGE30US", "CPIAUCSL"]:
        df = read_fred_raw(s)
        w = df[(df["date"] >= "2015-01-01") & (df["date"] <= "2024-12-31")]
        out[s] = {"first_date": str(df["date"].min().date()), "last_date": str(df["date"].max().date()),
                  "obs_in_window": len(w), "missing_in_window": int(w["value"].isna().sum()),
                  "min": float(w["value"].min()), "max": float(w["value"].max())}
    return out

def overlap(fz: dict, fa: dict, fb: dict) -> dict:
    out = {}
    for period in ["2015-2019", "2020-2024"]:
        z, a, b = fz[period], fa[period], fb[period]
        out[period] = {
            "zillow": len(z), "acs": len(a), "bls": len(b),
            "in_all_three": len(z & a & b),
            "acs_not_in_zillow": len(a - z),
            "acs_not_in_bls_sample": sorted(a - b)[:25],
            "bls_not_in_acs_sample": sorted(b - a)[:25],
            "zillow_not_in_acs_sample": sorted(z - a)[:25],
        }
    return out

def to_markdown(prof: dict) -> str:
    lines = ["# Pre-integration data quality profile"]
    for section, content in prof.items():
        lines += [f"## {section}", "", "```json", json.dumps(content, indent=2, default=list), "```", ""]
    return "\n".join(lines)

if __name__ == "__main__":
    ensure_dirs()
    pz, fz = profile_zillow()
    pa, fa = profile_acs()
    pb, fb = profile_bls()
    prof = {"zillow": pz, "acs": pa, "bls": pb, "fred": profile_fred(), "fips_overlap": overlap(fz, fa, fb)}
    (QUALITY / "pre_integration_profile.json").write_text(json.dumps(prof, indent=2, default=list))
    (QUALITY / "pre_integration_report.md").write_text(to_markdown(prof))
    print(json.dumps(prof["fips_overlap"], indent=2, default=list)[:2000])
