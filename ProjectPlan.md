# Project Idea: Housing Affordability

## Team Responsibilities

- **Eman Siddiqi** – Data acquisition/integration/findings
- **Aron Rista** – Data acquisition/integration/findings
- **Anish Bellamkonda** – Data Cleaning/Analysis/findings
- **Steven Wang** – Data Cleaning/Analysis/analysis

## Overview
Housing has become more expensive relative to income across much of the U.S., but some counties were hit much harder than others. We want to measure how affordability changed in each county between 2015-2019 and 2020-2024, and identify what the hardest-hit counties have in common.

The project uses three county-level datasets. Zillow’s Home Value Index provides typical home values. The Census Bureau’s American Community Survey 5-year estimates supply household income, population, renter share, and rent. The Bureau of Labor Statistics’ Local Area Unemployment Statistics cover unemployment and labor force size. We’ll also pull the 30-year mortgage rate and CPI from FRED to estimate mortgage payments and adjust for inflation. The three main datasets join on a five-digit county FIPS code and time period.

Each dataset has its own Python download script that records a checksum, and the raw files remain untouched. Before merging, we’ll check for missing counties, FIPS codes that changed over time, and ACS estimates with large margins of error. After cleaning, we’ll convert dollars to 2024 terms and combine everything into one table with a row per county per period. We’ll then calculate price-to-income and payment-to-income ratios and answer our questions using summary statistics, county maps, and a regression on local economic conditions. The whole pipeline will run from a single command, so anyone who clones the repo can reproduce our results, and a data dictionary will explain every variable.

## Research Questions

1. **How did housing affordability change across U.S. counties between 2015-2019 and 2020-2024?** Our main measure is the typical home value from Zillow divided by median household income from the ACS. We'll also estimate the yearly mortgage payment on that home and divide it by income.

2. **Which regions lost the most affordability?** We'll rank regions by how much their price-to-income ratio changed, then check whether the biggest changes cluster by state, by region, or in urban versus rural regions.

3. **What do the counties with the biggest drops have in common economically?** We'll test whether changes in unemployment, income, population, and renter share help explain why affordability fell more in some places than others.

4. **How much of the change came from home prices, and how much from mortgage rates?** The price-to-income ratio only moves when prices or incomes change, while the payment-to-income ratio also moves with interest rates. Comparing the two lets us separate the two effects.

## Datasets

### Datasets in Your Plan

| Dataset in your plan | Where it is on the class list | Direct link |
|---|---|---|
| ACS 5-year estimates | census.gov (Aggregators) | <https://data.census.gov>, with API access at <https://api.census.gov> |
| BLS Local Area Unemployment Statistics | data.gov (Aggregators), which catalogs the BLS LAUS dataset | <https://catalog.data.gov/dataset/local-area-unemployment-statistics>, data files at <https://www.bls.gov/lau/> |
| FRED mortgage rate and CPI | fred.stlouisfed.org (Economics and Finance) | <https://fred.stlouisfed.org/series/MORTGAGE30US> and <https://fred.stlouisfed.org/series/CPIAUCSL> |
| Zillow Home Value Index | Not on the list | <https://www.zillow.com/research/data/> |

### 1. Zillow Home Value Index (ZHVI), County Level

- **Source:** Zillow Research, <https://www.zillow.com/research/data/>
- **File:** County-level ZHVI for all homes (single-family and condo), middle tier, smoothed and seasonally adjusted, monthly CSV
- **Contents:** Typical home value by county and month, from 2000 to present
- **Key fields:** StateCodeFIPS, MunicipalCodeFIPS, RegionName, State, monthly value columns
- **Role in project:** Provides the home price side of affordability
- **License:** Free for public and academic use under Zillow's Terms of Use; attribution to Zillow is required

### 2. American Community Survey (ACS) 5-Year Estimates

- **Source:** U.S. Census Bureau, accessed through the Census Data API (<https://api.census.gov>)
- **Periods:** 2015-2019 and 2020-2024 5-year estimates (the 2020-2024 release was published January 29, 2026)
- **Tables:** B19013 (median household income), B01003 (total population), B25003 (tenure: owner versus renter), B25064 (median gross rent), B25077 (median home value, used as a cross-check against Zillow)
- **Key fields:** state and county FIPS codes, GEO_ID
- **Role in project:** Provides the income side of affordability and demographic and housing context
- **License:** U.S. government work, public domain

### 3. BLS Local Area Unemployment Statistics (LAUS), County Annual Averages

- **Source:** U.S. Bureau of Labor Statistics, <https://www.bls.gov/lau/>
- **Files:** County annual average files (`laucntyYY.xlsx`) for 2015 through 2024
- **Contents:** Labor force, employed, unemployed, and unemployment rate by county and year
- **Key fields:** State FIPS Code, County FIPS Code, Year
- **Role in project:** Provides labor market conditions for each county
- **License:** U.S. government work, public domain

### Supporting Dataset: FRED National Series

- **Source:** Federal Reserve Bank of St. Louis, FRED API
- **Series:** MORTGAGE30US (30-year fixed mortgage rate), CPIAUCSL (Consumer Price Index)
- **Role in project:** Mortgage rates feed the payment-to-income calculation; CPI converts 2019 dollars to 2024 dollars so both ACS periods are comparable
- **Key fields:** Date, averaged to each five-year period

### How the Datasets Link Together

| Dataset | Geography key | Time key | Transformation needed |
|---|---|---|---|
| Zillow ZHVI | StateCodeFIPS + MunicipalCodeFIPS | Month | Zero-pad and combine into a 5-digit FIPS; average months into each 5-year period |
| ACS 5-year | state + county | 5-year period | Combine into a 5-digit FIPS; inflation-adjust dollar values |
| BLS LAUS | State FIPS Code + County FIPS Code | Year | Combine into a 5-digit FIPS; average years into each 5-year period |
| FRED | National (no geography) | Week or month | Average into each 5-year period; joined to every county |

## Timeline

1. **Data collection/Acquiring** – Download the datasets we have gathered and commit to GitHub repo (Aron, Eman). *Due Date: Before Status report*
2. **Data Cleaning and validation** – Cleaning the datasets and making sure the data is usable (Anish and Steven). *Due Date: Before Status report*
3. **Integrate all datasets into a single holistic dataset** – Join all the datasets into a single table if possible so we can get one big data set. (Eman, Aron). *Due Date: Before Status report*
4. **Analyze and process (Data analysis, data visualizations)** – Analyzing the holistic dataset that we have processed and trying to find signals in it. (Everyone). *Due Date: Before Final*
5. **Report findings** – Conclude answers for our main questions (Eman, Aron). *Due Date: During or before finals week*
6. **Documentation** – Write down reproduction docs for future uses (Steven, Anish). *Due Date: During or before finals week*

## Constraints

1. **Data Licensing Restrictions:** Zillow's data is free to use, but we have to credit Zillow and we can't republish its raw files. The Census, BLS, and FRED data are all public domain, so this only affects Zillow.
2. **Data Gaps in Small Counties:** Small counties have less data to work with. They're more likely to be missing from Zillow entirely, and their ACS estimates come from smaller samples, so the numbers we do get are less reliable.
3. **Bias and Statistical Significance:** We can't assume the data is unbiased. Zillow and the ACS both cover large counties better, so our results will lean toward bigger, more urban areas. Some findings may also turn out not to be statistically significant, and we'll report that instead of leaving those results out.
4. **Mismatched Timeframes:**  The datasets run on different schedules. Zillow is monthly, BLS is yearly, and the ACS covers five years at a time, so we'll have to average Zillow and BLS into matching periods. That makes them comparable but hides changes within each period.
5.**Mortgage Calculation Limits:** Our mortgage payment estimate depends on assumptions (down payment size, loan length, a national interest rate) that won't match any single household's situation.
6. **API Rate Limits:**  Pulling several years of county-level data from the Census and FRED APIs means a lot of requests, and we could hit their rate limits. We may need to space out requests and save results locally so we don't download the same data twice.
