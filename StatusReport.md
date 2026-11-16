# Status Report: County Housing Affordability, 2015–2019 vs 2020–2024

**Team:** Anish Bellamkonda, Aron Rista, Eman Siddiqi, Steven Wang

## Overview  
Our main objective is still on measuring how housing affordability changed across U.S. counties between 2015–2024 using Zillow home values, ACS income and housing data, BLS labor data, and FRED mortgage rates and CPI. Since the day we released the plan, we built the workflow as separate single scripts tied together by [`run_all.py`](run_all.py): acquisition (01–04), pre-integration profiling (05), one cleaning script per source (06–09), integration (10), and post-integration quality assessment (11). Final Analysis is planned for the final milestone.
## Workflow  

The project is organized as a set of single-purpose scripts tied together by a run_all.py orchestrator, which runs them in order through subprocess calls. The goal is to measure how housing affordability changed across U.S. counties between 2015 and 2024, using Zillow home values, ACS income and housing data, BLS labor data, and FRED mortgage rates and CPI.

The workflow starts with data acquisition (scripts 01 to 04). Zillow’s county-level ZHVI comes from 01_acquire_zillow.py. ACS 5-year estimates for the 2019 and 2024 vintages come from the Census API through 02_acquire_acs.py, with the key read from the CENSUS_API_KEY environment variable so it is never committed. BLS county annual unemployment averages for 2015 to 2024 come from 03_acquire_bls.py, which sends a descriptive User-Agent because BLS rejects requests without one. FRED’s weekly 30-year mortgage rate and monthly CPI-U come from 04_acquire_fred.py, and no key is needed. Every file’s SHA-256, source URL, and retrieval time are recorded in its folder’s MANIFEST.json. The raw ACS, BLS, and FRED files are committed so others can skip the download. Zillow’s raw CSV is git-ignored because its terms of use prohibit redistribution, so only the script and checksum manifest are committed.

Next is the pre-integration quality assessment, which is new compared to the earlier report. 05_profile_raw.py profiles every raw file before cleaning and writes results/quality/pre_integration_report.md. It covers four dimensions:

Accuracy: It recalculates each county’s BLS unemployment rate from the raw counts and compares it to the reported rate. It also treats ACS income estimates with a coefficient of variation over 30% as unreliable.
Completeness: It counts months missing from Zillow’s 2015 to 2024 data, ACS placeholder values such as −666666666, and counties present in each year of BLS data.
Timeliness: It records each dataset’s first and last date to confirm full coverage of 2015 to 2024.
Consistency: It checks that each county appears once per period and that every county code has exactly five digits.

The script also counts how many counties appear in all three datasets and lists those that appear in only one, which shows whether the sources can be joined.

Cleaning (scripts 06 to 09) is complete. Each raw source becomes an analysis-ready table under data/interim/, with missing values handled, time periods aligned, and FIPS codes harmonized. Zillow’s wide monthly format is reshaped into a long table, and weekly mortgage rates are averaged to monthly values alongside CPI-U. ACS sentinel values like −666666666 are converted to nulls so they don’t distort averages.

Integration is scripted, but the final run is pending until the ACS and BLS cleaning scripts are in. 10_integrate.py merges the cleaned Zillow, ACS, and BLS tables on 5-digit county FIPS and period (2015 to 2019 and 2020 to 2024), then adds each period’s average FRED mortgage rate. It keeps only counties present in both periods and calculates price-to-income and payment-to-income, assuming 20% down on a 30-year fixed loan. It also logs matched and unmatched counts for each join to results/quality/integration_log.json. Dollar adjustment follows two rules: Zillow values are deflated month by month with CPI-U, and 2015 to 2019 ACS values (in 2019 dollars) are scaled to 2024 dollars.

Post-integration quality (11_quality_post.py) is complete. It checks the integrated county_period.csv for accuracy, completeness, timeliness, and consistency. It confirms zero duplicate (fips, period) keys, cross-validates Zillow against ACS home values, checks U.S. population coverage, and logs extreme affordability outliers. Analysis and documentation have not started and are planned for the final milestone.

Compared with the original plan, three things changed:

Puerto Rico, Connecticut, and Alaska’s Valdez-Cordova area (split in 2019) are excluded.
The CPI-based dollar adjustment was defined as described above.
Separate pre- and post-integration quality scripts and the run_all.py orchestrator replaced the single command described in the plan.

Three challenges came up. The Census API now requires a key, which was resolved with the environment variable and committed raw JSON. Zillow can’t be redistributed, which was resolved with the git-ignored raw file plus script and checksum, though the team is still confirming this with the TA. ACS sentinel values that look like real numbers were converted to nulls during cleaning.

## Task updates

### 1. Data acquisition: 
**ACS 5-year (2019 and 2024 vintages) via the Census API:** [`02_acquire_acs.py`](scripts/02_acquire_acs.py) → [`data/raw/acs/`](data/raw/acs/), with [N] counties in the 2019 vintage and [N] in the 2024 vintage. The API key is read from the `CENSUS_API_KEY` environment variable and is never written to the repo or the manifest. The raw JSON is public domain and committed, so reproducers can skip the download.
- **BLS LAUS county annual averages, 2015–2024:** [`03_acquire_bls.py`](scripts/03_acquire_bls.py) → [`data/raw/bls/`](data/raw/bls/) ([10] yearly files). BLS rejects requests without a descriptive User-Agent, so the shared downloader sends one.
- Every file has a SHA-256, source URL, and retrieval time in its folder's `MANIFEST.json` ([ACS](data/raw/acs/MANIFEST.json), [BLS](data/raw/bls/MANIFEST.json), [FRED](data/raw/fred/MANIFEST.json)).
- **Zillow ZHVI, county level (all homes, mid-tier, smoothed, seasonally adjusted):** [`01_acquire_zillow.py`](scripts/01_acquire_zillow.py). Zillow's Terms of Use don't allow redistribution, so the raw CSV is git-ignored and only the script and its checksum manifest are committed.
- **FRED 30-year mortgage rate (MORTGAGE30US, weekly) and CPI-U (CPIAUCSL, monthly):** [`04_acquire_fred.py`](scripts/04_acquire_fred.py) → `data/raw/fred/`. FRED doesn't require an API key for these downloads.


### 2. Pre-integration quality assessment:
[`05_profile_raw.py`](scripts/05_profile_raw.py) profiles every raw file before cleaning and writes `results/quality/pre_integration_report.md`. It checks the four required dimensions:
- **Accuracy:** We recalculate each county's BLS unemployment rate from its raw counts against the rate BLS reports.ACS income estimates with a large margin of error (CV over 30%) are considered as unreliable.
- **Completeness:** We count the months missing from Zillow's 2015–2024 data, the placeholder values in the ACS (such as −666666666), and the counties in each year of BLS data.
- **Timeliness:** We record the first and last date in each dataset to confirm it covers the full 2015–2024 period.
- **Consistency:** We check that every county appears only once in each period and that every county code has exactly five digits.

To see if the datasets can be joined,it counts how many counties appear in all three and lists any that appear in only one.

### 3. Cleaning: complete  <!-- Anish (ACS, BLS) + Steven (Zillow, FRED) -->
Each raw source was standardized into an analysis-ready table under `data/interim/` using cleaning scripts ([`06_clean_zillow.py`](scripts/06_clean_zillow.py), [`07_clean_acs.py`](scripts/07_clean_acs.py), [`08_clean_bls.py`](scripts/08_clean_bls.py), and [`09_clean_fred.py`](scripts/09_clean_fred.py)) that handle missing values, time alignment, and shared FIPS harmonization. 

### 4. Integration: script complete, final run pending
[`10_integrate.py`](scripts/10_integrate.py) merges the cleaned Zillow, ACS, and BLS tables on 5-digit county FIPS and period (2015-2019 and 2020-2024), then adds each period's average FRED mortgage rate. All dollar values are converted to 2024 dollars with CPI-U. We keep only counties that appear in both periods, since the analysis compares the two. The script also calculates price-to-income and payment-to-income (assuming 20% down on a 30-year fixed loan) and writes each join's matched and unmatched counts to `results/quality/integration_log.json`. We'll run it once the ACS and BLS cleaning scripts are in, and add the join counts here.

### 5. Post-integration quality: complete  <!-- Steven -->
[`11_quality_post.py`](scripts/11_quality_post.py) · [`post_integration_report.md`](results/quality/post_integration_report.md)
Post-integration checks confirm zero duplicate `(fips, period)` keys, strong agreement between Zillow and ACS home values (`r = [X]` in 2015–2019 and `r = [Y]` in 2020–2024), and logged extreme affordability outliers.

### 6. Analysis & 7. Documentation: not started 

## Changes to the project plan
- **Geography rules:** Puerto Rico, Connecticut  and Alaska's Valdez-Cordova area (split in 2019) are not included;
- **Dollar adjustment:** Zillow values are deflated month by month with CPI-U; 2015–2019 ACS values (2019 dollars) are scaled to 2024 dollars.
- Added separate pre- and post-integration quality scripts and a `run_all.py` orchestrator, replacing the single command described in the plan.

## Challenges  <!-- Anish (collects from everyone) -->
1. **Census API now requires a key.** Resolved: key read from `CENSUS_API_KEY`; raw JSON committed so reproducers can skip it.
2. **Zillow can't be redistributed.** Resolved: git-ignored raw file, script + checksum committed; [confirming with TA].
3. **ACS sentinel values** look like real numbers (e.g. −666666666) and would distort averages. Resolved by converting them to nulls during cleaning.

## Individual contributions

### Anish Bellamkonda
Anish set up the shared foundation of the pipeline: `requirements.txt`, `.gitignore`, `scripts/utils.py`  and `scripts/loaders.py` (readers for data), plus the `run_all.py` which ran all the scripts using subprocess. He wrote the pre-integration quality profile (`scripts/05_profile_raw.py`) and the ACS and BLS cleaning scripts (`scripts/07_clean_acs.py`, `scripts/08_clean_bls.py`). He also added the Gaps section to `ProjectPlan.md` to address the issue mentioned in previous assignemnt. For this report he wrote the overview, the pre-integration quality and ACS/BLS cleaning updates and the challenges section.
### Aron Rista

Aron wrote the Zillow and FRED acquisition scripts (`scripts/01_acquire_zillow.py` and `scripts/04_acquire_fred.py`) and checked that both download links return live data. Both scripts go through the shared downloader, so each file's checksum, source URL, and retrieval time end up in its folder's `MANIFEST.json`. The raw Zillow CSV stays out of the repo because Zillow's Terms of Use don't allow redistribution. He also wrote the integration script (`scripts/10_integrate.py`). It joins the cleaned Zillow, ACS, and BLS tables on county FIPS and period, attaches the average FRED mortgage rate for each period, and puts every dollar figure in 2024 terms using CPI-U. Counties missing from either period are dropped, and the log records how many rows each join loses. The output includes price-to-income and payment-to-income ratios for the analysis stage. Earlier in the semester, Aron wrote the Constraints section of the project plan, and for this report he wrote the Zillow and FRED acquisition bullets and the integration update.


### Eman Siddiqi

Eman wrote the ACS and BLS acquisition scripts (`scripts/02_acquire_acs.py` and `scripts/03_acquire_bls.py`). She obtained the Census API key, set up the `CENSUS_API_KEY` environment-variable workflow so the key is never committed, and added a User-Agent so BLS accepts script requests. She ran the acquisition stages against the live sources and committed the raw ACS, BLS, and FRED files together with their `MANIFEST.json` checksum files. She also ran a fresh-clone test of `run_all.py` to confirm the pipeline reproduces end to end. For this report she wrote the workflow diagram, the Data acquisition bullets for ACS and BLS, and the updated timeline.

### Steven Wang
Steven developed the cleaning scripts for the Zillow (`scripts/06_clean_zillow.py`) and FRED (`scripts/09_clean_fred.py`) datasets, reshaping Zillow's wide monthly ZHVI format into a long table (`data/interim/zillow_monthly.csv`), filtering to the 2015–2024 analysis window, applying shared FIPS harmonization rules, and aggregating weekly 30-year mortgage rates to monthly averages alongside CPI-U (`data/interim/fred_monthly.csv`). He also built the post-integration quality assessment script (`scripts/11_quality_post.py`) to evaluate the integrated `county_period.csv` table across accuracy, completeness, timeliness, and consistency. This includes cross-validating Zillow home values against ACS median home values, checking U.S. population coverage, and flagging outliers. Finally, Steven added the reproducibility and execution instructions to `README.md`.
