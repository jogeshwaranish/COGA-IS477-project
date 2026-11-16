"""Stage 1b: download ACS 5-year county estimates (2015-2019 and 2020-2024) from the Census API.
Needs a free key: https://api.census.gov/data/key_signup.html -> export CENSUS_API_KEY=...
The raw JSON is public domain and committed, so later runs skip the download."""
import os
import sys

from loaders import ACS_FILES, ACS_VARS
from utils import download, ensure_dirs

if __name__ == "__main__":
    ensure_dirs()
    key = os.environ.get("CENSUS_API_KEY")
    for year, dest in ACS_FILES.items():
        if not dest.exists() and not key:
            sys.exit("CENSUS_API_KEY is not set and raw ACS files are missing. "
                     "Get a key at https://api.census.gov/data/key_signup.html")
        url = f"https://api.census.gov/data/{year}/acs/acs5"
        params = {"get": "NAME," + ",".join(ACS_VARS), "for": "county:*", "in": "state:*", "key": key}
        download(url, dest, params=params)
