from loaders import read_fred_raw
from utils import INTERIM, ensure_dirs, write_log

if __name__ == "__main__":
    ensure_dirs()
    log = {}
    cpi = read_fred_raw("CPIAUCSL").rename(columns={"value": "cpi"})
    mort = read_fred_raw("MORTGAGE30US")
    log["mortgage_weeks_missing"] = int(mort["value"].isna().sum())
    mort = mort.dropna()
    mort["date"] = mort["date"].dt.to_period("M").dt.to_timestamp()
    mort = mort.groupby("date", as_index=False)["value"].mean().rename(columns={"value": "mortgage_rate"})
    df = cpi.merge(mort, on="date", how="inner")
    df = df[(df["date"] >= "2015-01-01") & (df["date"] <= "2024-12-31")]
    log["months_out"] = len(df)
    log["months_expected"] = 120
    df.to_csv(INTERIM / "fred_monthly.csv", index=False)
    write_log("cleaning_log_fred", log)
    print(log)