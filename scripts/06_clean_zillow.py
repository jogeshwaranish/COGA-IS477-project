import pandas as pd

from loaders import read_zillow_raw, zillow_date_cols
from utils import INTERIM, ensure_dirs, harmonize_fips, write_log

if __name__ == "__main__":
    ensure_dirs()
    log = {}
    df = read_zillow_raw()
    log["counties_raw"] = len(df)
    long = df.melt(id_vars=["fips", "RegionName", "State"], value_vars=zillow_date_cols(df), var_name="date", value_name="zhvi")
    long["date"] = pd.to_datetime(long["date"])
    long = long[(long["date"] >= "2015-01-01") & (long["date"] <= "2024-12-31")]
    log["rows_in_window"] = len(long)
    log["rows_dropped_missing_value"] = int(long["zhvi"].isna().sum())
    long = long.dropna(subset=["zhvi"])
    log["rows_dropped_nonpositive"] = int((long["zhvi"] <= 0).sum())
    long = long[long["zhvi"] > 0]
    long["date"] = long["date"].dt.to_period("M").dt.to_timestamp()
    long = harmonize_fips(long, ["fips", "date"], log)
    long = long.rename(columns={"RegionName": "zillow_county_name", "State": "state_abbr"})
    long = long.sort_values(["fips", "date"])
    long.to_csv(INTERIM / "zillow_monthly.csv", index=False)
    log["rows_out"] = len(long)
    log["counties_out"] = long["fips"].nunique()
    write_log("cleaning_log_zillow", log)
    print(log)