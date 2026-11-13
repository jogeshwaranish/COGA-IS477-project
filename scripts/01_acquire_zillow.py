"""Stage 1a: download Zillow county ZHVI (all homes, mid-tier, smoothed, seasonally adjusted)."""
from loaders import ZILLOW_FILE
from utils import download, ensure_dirs

URL = ("https://files.zillowstatic.com/research/public_csvs/zhvi/"
       "County_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv")

if __name__ == "__main__":
    ensure_dirs()
    # Raw Zillow file is git-ignored (Zillow Terms of Use: no redistribution); only MANIFEST.json is committed.
    download(URL, ZILLOW_FILE)