# Project Plan: Housing Affordability

## Overview
Housing has gotten more expensive relative to income in much of the United States, but some counties were hit much harder than others. We want to measure how affordability changed in each county between 2015-2019 and 2020-2024, and find out what the counties that fell furthest behind have in common. 

Our project uses three county-level datasets. Zillow’s Home Value Index gives us typical home values. From the Census Bureau’s American Community Survey 5-year estimates we get household income, population, renter share, and rent, and the Bureau of Labor Statistics’ Local Area Unemployment Statistics cover unemployment and labor force size. We’ll also pull the 30-year mortgage rate and CPI from FRED to estimate mortgage payments and adjust for inflation. The three main datasets join on a five-digit county FIPS code and time period.

Each dataset has its own Python download script that records a checksum, and the raw files stay untouched. Before merging, we’ll check for missing counties, FIPS codes that changed over time, and ACS estimates with large margins of error. After cleaning, we’ll convert dollars to 2024 terms and combine everything into one table with a row per county per period. Then we’ll calculate price-to-income and payment-to-income ratios and answer our questions with summary statistics, county maps, and a regression on local economic conditions. The whole pipeline will run from a single command, so anyone who clones the repo can reproduce our results, and a data dictionary will explain every variable. 

## Team

* **Eman Siddiqi** — Documentation & Data Cleaning

* **Aron Rista** — Data Analysis & Finding

* **Anish Bellamkonda** — Data Cleaning & Analysis

* **Steven Wang** — Data Cleaning & Analysis

## Research Questions

1. How did housing affordability change across U.S. counties between 2015–2019 and 2020–2024?
2. Which counties and regions lost the most affordability?
3. What do the counties with the biggest drops have in common economically?
4. How much of the change came from home prices, and how much from mortgage rates?

## Datasets

### 1. Zillow Home Value Index (ZHVI) — County Level
* Zillow Research ([zillow.com/research/data](https://www.zillow.com/research/data/))

### 2. American Community Survey (ACS) 5-Year Estimates
* U.S. Census Bureau via Census Data API ([api.census.gov](https://api.census.gov))

### 3. Bureau of Labor Statistics (BLS) Local Area Unemployment Statistics (LAUS)
* U.S. Bureau of Labor Statistics ([bls.gov/lau](https://www.bls.gov/lau/))

### 4. Federal Reserve Economic Data (FRED) National Series
* Federal Reserve Bank of St. Louis API ([fred.stlouisfed.org](https://fred.stlouisfed.org/))

## Timeline



## Constraints

* **Data Licensing Restrictions:** Zillow data requires public attribution and limits raw data redistribution, unlike our other public domain federal datasets.
* **Data Gaps in Small Counties:** Smaller counties will have less data available, and potentially more missing or inaccurate data.
* **Mismatched Timeframes:** Zillow is monthly, BLS is annual, and ACS is a 5-year average, making them hard to align directly.
* **Mortgage Calculation Limits:** Mortgage payment estimates may rely on assumptions that don't truly represent an individual's situation.
* **API Rate Limits:** Downloading years of county-level data from the Census and FRED APIs may go over API rate limits. 

## Gaps

