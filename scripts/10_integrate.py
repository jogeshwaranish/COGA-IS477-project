"""Stage 4: integrate cleaned Zillow + ACS + BLS (+ FRED) into one county x period table.

Join key: 5-digit county FIPS + period ("2015-2019", "2020-2024"). All dollars in 2024 dollars.
Output: data/processed/county_period.csv and results/quality/integration_log.json"""
import pandas as pd

from utils import ACS_VINTAGE, INTERIM, PROCESSED, ensure_dirs, write_log, year_to_period

DOWN_PAYMENT, TERM_MONTHS = 0.20, 360


def annual_payment(price: pd.Series, rate_pct: pd.Series) -> pd.Series:
    loan, r = price * (1 - DOWN_PAYMENT), rate_pct / 100 / 12
    return 12 * loan * r / (1 - (1 + r) ** -TERM_MONTHS)


if __name__ == "__main__":
    ensure_dirs()
    log = {}

    zil = pd.read_csv(INTERIM / "zillow_monthly.csv", dtype={"fips": str}, parse_dates=["date"])
    acs = pd.read_csv(INTERIM / "acs_clean.csv", dtype={"fips": str})
    bls = pd.read_csv(INTERIM / "bls_annual_clean.csv", dtype={"fips": str})
    fred = pd.read_csv(INTERIM / "fred_monthly.csv", parse_dates=["date"])

    fred["year"] = fred["date"].dt.year
    fred["period"] = fred["year"].map(year_to_period)
    cpi_2024 = fred.loc[fred["year"] == 2024, "cpi"].mean()
    cpi_by_year = fred.groupby("year")["cpi"].mean()

    # Zillow: deflate each month to 2024 dollars, then average within each period.
    zil = zil.merge(fred[["date", "cpi"]], on="date", how="left")
    zil["zhvi_2024usd"] = zil["zhvi"] * cpi_2024 / zil["cpi"]
    zil["period"] = zil["date"].dt.year.map(year_to_period)
    zp = (zil.groupby(["fips", "period"])
          .agg(zhvi_2024usd=("zhvi_2024usd", "mean"), zillow_months=("zhvi", "size"),
               zillow_county_name=("zillow_county_name", "first"), state_abbr=("state_abbr", "first"))
          .reset_index())

    # ACS: 2015-2019 estimates are in 2019 dollars -> scale to 2024 dollars.
    factor = acs["period"].map({p: cpi_2024 / cpi_by_year[v] for p, v in ACS_VINTAGE.items()})
    for col in ["median_hh_income", "median_gross_rent", "acs_median_home_value"]:
        acs[col + "_2024usd"] = acs[col] * factor

    # BLS: pool years within a period (rate = total unemployed / total labor force).
    bls["period"] = bls["year"].map(year_to_period)
    bp = (bls.groupby(["fips", "period"])
          .agg(labor_force=("labor_force", "mean"), unemployed_sum=("unemployed", "sum"),
               lf_sum=("labor_force", "sum"), bls_years=("year", "nunique"))
          .reset_index())
    bp["unemp_rate"] = 100 * bp["unemployed_sum"] / bp["lf_sum"]
    bp = bp.drop(columns=["unemployed_sum", "lf_sum"])

    rates = fred.groupby("period", as_index=False)["mortgage_rate"].mean()

    # Join, logging what each step loses.
    m = acs.merge(zp, on=["fips", "period"], how="outer", indicator="acs_zillow")
    log["acs_zillow_join"] = m["acs_zillow"].value_counts().to_dict()
    m = m[m["acs_zillow"] == "both"].drop(columns="acs_zillow")

    m = m.merge(bp, on=["fips", "period"], how="outer", indicator="with_bls")
    log["with_bls_join"] = m["with_bls"].value_counts().to_dict()
    m = m[m["with_bls"] == "both"].drop(columns="with_bls")

    m = m.merge(rates, on="period", how="left")

    # Keep only counties observed in BOTH periods so period-to-period change is defined.
    both = m.groupby("fips")["period"].transform("nunique") == 2
    log["rows_dropped_single_period"] = int((~both).sum())
    m = m[both]

    m["price_to_income"] = m["zhvi_2024usd"] / m["median_hh_income_2024usd"]
    m["annual_payment_2024usd"] = annual_payment(m["zhvi_2024usd"], m["mortgage_rate"])
    m["payment_to_income"] = m["annual_payment_2024usd"] / m["median_hh_income_2024usd"]

    cols = ["fips", "period", "acs_name", "state_abbr", "population", "median_hh_income_2024usd",
            "income_cv", "income_low_reliability", "median_gross_rent_2024usd", "acs_median_home_value_2024usd",
            "renter_share", "zhvi_2024usd", "zillow_months", "labor_force", "unemp_rate", "bls_years",
            "mortgage_rate", "price_to_income", "annual_payment_2024usd", "payment_to_income"]
    out = m[cols].sort_values(["fips", "period"])
    out.to_csv(PROCESSED / "county_period.csv", index=False)

    log.update(rows_out=len(out), counties_out=out["fips"].nunique(), cpi_2024_base=round(cpi_2024, 3))
    write_log("integration_log", log)
    print(log)