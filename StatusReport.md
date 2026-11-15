# Status Report: County Housing Affordability, 2015–2019 vs 2020–2024

**Team:** Anish Bellamkonda, Aron Rista, Eman Siddiqi, Steven Wang

## Overview  

## Workflow  

## Task updates

### 1. Data acquisition: 

### 2. Pre-integration quality assessment: 

### 3. Cleaning: complete  <!-- Anish (ACS, BLS) + Steven (Zillow, FRED) -->
Each raw source was standardized into an analysis-ready table under `data/interim/` using cleaning scripts ([`06_clean_zillow.py`](scripts/06_clean_zillow.py), [`07_clean_acs.py`](scripts/07_clean_acs.py), [`08_clean_bls.py`](scripts/08_clean_bls.py), and [`09_clean_fred.py`](scripts/09_clean_fred.py)) that handle missing values, time alignment, and shared FIPS harmonization.

### 4. Integration: 

### 5. Post-integration quality: complete  <!-- Steven -->
[`11_quality_post.py`](scripts/11_quality_post.py) · [`post_integration_report.md`](results/quality/post_integration_report.md)
Post-integration checks confirm zero duplicate `(fips, period)` keys, strong agreement between Zillow and ACS home values (`r = [X]` in 2015–2019 and `r = [Y]` in 2020–2024), and logged extreme affordability outliers.

### 6. Analysis & 7. Documentation: not started 

## Changes to the project plan  

## Challenges  <!-- Anish (collects from everyone) -->
1. **Census API now requires a key.** Resolved: key read from `CENSUS_API_KEY`; raw JSON committed so reproducers can skip it.
2. **Zillow can't be redistributed.** Resolved: git-ignored raw file, script + checksum committed; [confirming with TA].
3. 

## Individual contributions

### Anish Bellamkonda

### Aron Rista

### Eman Siddiqi

### Steven Wang
Steven developed the cleaning scripts for the Zillow (`scripts/06_clean_zillow.py`) and FRED (`scripts/09_clean_fred.py`) datasets, reshaping Zillow's wide monthly ZHVI format into a long table (`data/interim/zillow_monthly.csv`), filtering to the 2015–2024 analysis window, applying shared FIPS harmonization rules, and aggregating weekly 30-year mortgage rates to monthly averages alongside CPI-U (`data/interim/fred_monthly.csv`). He also built the post-integration quality assessment script (`scripts/11_quality_post.py`) to evaluate the integrated `county_period.csv` table across accuracy, completeness, timeliness, and consistency. This includes cross-validating Zillow home values against ACS median home values, checking U.S. population coverage, and flagging outliers. Finally, Steven added the reproducibility and execution instructions to `README.md`.