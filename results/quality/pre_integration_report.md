# Pre-integration data quality profile
## zillow

```json
{
  "rows_counties": 3107,
  "first_month": "2000-03-31",
  "last_month": "2026-10-31",
  "months_in_2015_2024_window": 120,
  "missing_values_in_window": 17928,
  "pct_missing_in_window": 4.81,
  "counties_with_any_missing_month": 622,
  "duplicate_fips": 0,
  "invalid_fips": 0,
  "nonpositive_values": 0,
  "max_value": 3077764.040969282
}
```

## acs

```json
{
  "2019": {
    "rows_counties": 3220,
    "duplicate_fips": 0,
    "invalid_fips": 0,
    "null_values": 0,
    "sentinel_values_by_column": {
      "B25064_001E": 4,
      "B25077_001E": 2,
      "B25077_001M": 2
    },
    "income_cv_over_30pct": 2,
    "renter_plus_owner_ne_total": 0,
    "puerto_rico_rows": 78
  },
  "2024": {
    "rows_counties": 3222,
    "duplicate_fips": 0,
    "invalid_fips": 0,
    "null_values": 0,
    "sentinel_values_by_column": {
      "B19013_001E": 1,
      "B19013_001M": 1,
      "B25064_001E": 7,
      "B25077_001E": 5,
      "B25077_001M": 5
    },
    "income_cv_over_30pct": 8,
    "renter_plus_owner_ne_total": 0,
    "puerto_rico_rows": 78
  }
}
```

## bls

```json
{
  "rows": 32205,
  "rows_per_year": {
    "2015": 3220,
    "2016": 3220,
    "2017": 3220,
    "2018": 3220,
    "2019": 3220,
    "2020": 3221,
    "2021": 3221,
    "2022": 3221,
    "2023": 3221,
    "2024": 3221
  },
  "years_present": [
    2015,
    2016,
    2017,
    2018,
    2019,
    2020,
    2021,
    2022,
    2023,
    2024
  ],
  "duplicate_fips_year": 0,
  "invalid_fips": 0,
  "null_numeric": 312,
  "employed_plus_unemployed_ne_labor_force": 0,
  "rate_differs_from_recomputed_by_gt_0.15pt": 0,
  "rate_out_of_0_100": 78
}
```

## fred

```json
{
  "MORTGAGE30US": {
    "first_date": "1971-04-02",
    "last_date": "2026-11-12",
    "obs_in_window": 521,
    "missing_in_window": 0,
    "min": 2.65,
    "max": 7.79
  },
  "CPIAUCSL": {
    "first_date": "1947-01-01",
    "last_date": "2026-10-01",
    "obs_in_window": 120,
    "missing_in_window": 0,
    "min": 234.747,
    "max": 317.604
  }
}
```

## fips_overlap

```json
{
  "2015-2019": {
    "zillow": 3004,
    "acs": 3220,
    "bls": 3220,
    "in_all_three": 2996,
    "acs_not_in_zillow": 216,
    "acs_not_in_bls_sample": [
      "09001",
      "09003",
      "09005",
      "09007",
      "09009",
      "09011",
      "09013",
      "09015",
      "15005"
    ],
    "bls_not_in_acs_sample": [
      "09110",
      "09120",
      "09130",
      "09140",
      "09150",
      "09160",
      "09170",
      "09180",
      "09190"
    ],
    "zillow_not_in_acs_sample": []
  },
  "2020-2024": {
    "zillow": 3087,
    "acs": 3222,
    "bls": 3221,
    "in_all_three": 3079,
    "acs_not_in_zillow": 143,
    "acs_not_in_bls_sample": [
      "15005"
    ],
    "bls_not_in_acs_sample": [],
    "zillow_not_in_acs_sample": [
      "09001",
      "09003",
      "09005",
      "09007",
      "09009",
      "09011",
      "09013",
      "09015"
    ]
  }
}
```
