import datetime as dt
import hashlib
from importlib.resources import path
import json
import time
from pathlib import Path

import pandas as pd

# project folders
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
PROCESSED = ROOT / "data" / "processed"
QUALITY = ROOT / "results" / "quality"

# the two 5 year periods we compare, and which ACS year goes with each one
PERIODS = {"2015-2019": range(2015, 2020), "2020-2024": range(2020, 2025)}
ACS_VINTAGE = {"2015-2019": 2019, "2020-2024": 2024}

# BLS dosen't return anythin if the user agent isn't defined well.
HEADERS = {"User-Agent": "IS477-COGA-project/1.0"}

#Mentioned in the gaps section of plan report
# puerto rico isn't in the zillow/LAUS county files so we dropping it
EXCLUDED_STATE_FIPS = {"72"}
# connecticut switched from counties to planning regions in newer data files
EXCLUDED_STATE_PREFIXES = {"09"}
# counties that got renamed/merged, old fips -> new fips
FIPS_RECODE = {
    "46113": "46102",  # Shannon County SD -> Oglala Lakota County in 2015
    "02270": "02158",  # Wade Hampton AK -> Kusilvak Census Area in 2015
    "51515": "51019",  # Bedford city VA got merged into Bedford County
}
# Valdez-Cordova AK split in 2019 and there's no clean 1 to 1 mapping, so drop these
FIPS_EXCLUDE = {"02261", "02063", "02066"}


def ensure_dirs():
    for d in [RAW, INTERIM, PROCESSED, QUALITY]:
        d.mkdir(parents=True, exist_ok=True)


def year_to_period(year):
    for label in PERIODS:
        if year in PERIODS[label]:
            return label
    return None


def sha256(path):
#1mb limit
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def record_checksum(path, source_url):
    manifest_path = path.parent / "MANIFEST.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
    else:
        manifest = {}

    digest = sha256(path)
    old = None
    if path.name in manifest:
        old = manifest[path.name].get("sha256")
    if old and old != digest:
        print(f"[warn] {path.name}: checksum changed since last run (upstream data revised?)")

    manifest[path.name] = {
        "sha256": digest,
        "bytes": path.stat().st_size,
        "source_url": source_url,
        "retrieved_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True))
    print(f"[ok] {path.relative_to(ROOT)}  sha256={digest[:16]}...")


def download(url, dest, params=None, force=False):
    import requests
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and not force:
        print(f"[skip] {dest.relative_to(ROOT)} already present")
    else:
        r = requests.get(url, params=params, headers=HEADERS, timeout=180)
        r.raise_for_status()
        dest.write_bytes(r.content)
        time.sleep(1)  # wait a sec so we don't spam the public APIs

    record_checksum(dest, url)


def harmonize_fips(df, key_cols, log):
    # drops unwanted counties and modifies that got renamed or merged
    n0 = len(df)
    state = df["fips"].str[:2]
    excl = state.isin(EXCLUDED_STATE_FIPS | EXCLUDED_STATE_PREFIXES) | df["fips"].isin(FIPS_EXCLUDE)
    log["rows_excluded_geography"] = int(excl.sum())
    df = df[~excl].copy()
    recoded = df["fips"].isin(FIPS_RECODE.keys())
    log["rows_fips_recoded"] = int(recoded.sum())
    df["_recoded"] = recoded
    df["fips"] = df["fips"].replace(FIPS_RECODE)
    df = df.sort_values("_recoded")
    df = df.drop_duplicates(key_cols, keep="first")
    df = df.drop(columns="_recoded")
    log["rows_dropped_duplicate_after_recode"] = n0 - log["rows_excluded_geography"] - len(df)
    return df

#logging
def write_log(name, log):
    QUALITY.mkdir(parents=True, exist_ok=True)
    out_path = QUALITY / f"{name}.json"
    out_path.write_text(json.dumps(log, indent=2, default=str))