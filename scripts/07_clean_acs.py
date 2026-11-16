#clean ACS 
import numpy as np

from loaders import ACS_VARS, read_acs_raw
from utils import INTERIM, ensure_dirs, harmonize_fips, write_log

if __name__ == "__main__":
    ensure_dirs()
    log = {}
    df = read_acs_raw()
    log["rows_raw"] = len(df)
    # Census API uses large negative sentinels (e.g. -666666666) for "estimate not available".
    cols = list(ACS_VARS)
    log["sentinel_values_set_to_null"] = int((df[cols] < 0).sum().sum())
    df[cols] = df[cols].mask(df[cols] < 0)
    df = df.rename(columns={**ACS_VARS, "NAME": "acs_name"})
    df["period"] = np.where(df["vintage"] == 2019, "2015-2019", "2020-2024")
    df = harmonize_fips(df, ["fips", "period"], log)
    df["renter_share"] = df["renter_units"] / df["occupied_units"]
    df["income_cv"] = (df["median_hh_income_moe"] / 1.645) / df["median_hh_income"]
    df["income_low_reliability"] = df["income_cv"] > 0.30  # flagged, not dropped
    log["rows_flagged_income_cv_gt_0.30"] = int(df["income_low_reliability"].sum())
    log["rows_dropped_missing_income"] = int(df["median_hh_income"].isna().sum())
    df = df.dropna(subset=["median_hh_income"])
    keep = ["fips", "period", "vintage", "acs_name", "population", "median_hh_income", "median_hh_income_moe",
            "income_cv", "income_low_reliability", "median_gross_rent", "acs_median_home_value",
            "acs_median_home_value_moe", "occupied_units", "owner_units", "renter_units", "renter_share"]
    df[keep].sort_values(["fips", "period"]).to_csv(INTERIM / "acs_clean.csv", index=False)
    log["rows_out"] = len(df)
    write_log("cleaning_log_acs", log)
    print(log)
