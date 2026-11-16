#clean BLS LAUS
from loaders import read_bls_raw
from utils import INTERIM, ensure_dirs, harmonize_fips, write_log

NUM = ["labor_force", "employed", "unemployed"]

if __name__ == "__main__":
    ensure_dirs()
    log = {}
    df = read_bls_raw()
    log["rows_raw"] = len(df)
    log["exact_duplicate_rows_dropped"] = int(df.duplicated(["fips", "year"]).sum())
    df = df.drop_duplicates(["fips", "year"])
    log["rows_dropped_missing_counts"] = int(df[NUM].isna().any(axis=1).sum())
    df = df.dropna(subset=NUM)
    df = harmonize_fips(df, ["fips", "year"], log)
    # Recompute the rate from counts so it is consistent with labor force/unemployed (accuracy check).
    recomputed = 100 * df["unemployed"] / df["labor_force"]
    log["rows_reported_rate_off_by_gt_0.15pt"] = int(((df["unemp_rate"] - recomputed).abs() > 0.15).sum())
    df["unemp_rate"] = recomputed.round(2)
    out = df[["fips", "county_name", "year", "labor_force", "employed", "unemployed", "unemp_rate"]]
    out.sort_values(["fips", "year"]).to_csv(INTERIM / "bls_annual_clean.csv", index=False)
    log["rows_out"] = len(out)
    log["counties_with_all_10_years"] = int((out.groupby("fips")["year"].nunique() == 10).sum())
    write_log("cleaning_log_bls", log)
    print(log)
