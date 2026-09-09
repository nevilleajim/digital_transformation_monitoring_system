import os
import pandas as pd

RAW_FILE = "data/raw/world_bank_raw.csv"
PROCESSED_FILE = "data/processed/world_bank_clean.csv"

START_YEAR = 2010
END_YEAR = 2025

EXPECTED_INDICATORS = {
    "IT.NET.USER.ZS": {
        "name": "Individuals using the internet",
        "min": 0,
        "max": 100
    },
    "IT.CEL.SETS.P2": {
        "name": "Mobile cellular subscriptions",
        "min": 0,
        "max": None
    },
    "IT.NET.BBND.P2": {
        "name": "Fixed broadband subscriptions",
        "min": 0,
        "max": None
    },
    "EG.ELC.ACCS.ZS": {
        "name": "Access to electricity",
        "min": 0,
        "max": None
    },
    "NY.GDP.PCAP.CD": {
        "name": "GDP per capita",
        "min": 0,
        "max": None
    },
}

def load_raw_data():

    if not os.path.exists(RAW_FILE):
        raise FileNotFoundError (
            f"This file {RAW_FILE} doesn't exist."
        )

    df = pd.read_csv(RAW_FILE)

    print(f"Raw data loaded: {len(df)}")

    return df

def validate_columns(df):

    required_columns = {
        "country_code",
        "indicator_code",
        "year",
        "value"
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    print("Required columns validated")

    return df

def clean_data_types(df):
    """
    Convert columns into appropriate data types.
    """

    df["country_code"] = (
        df["country_code"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    df["indicator_code"] = (
        df["indicator_code"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    df["year"] = pd.to_numeric(
        df["year"],
        errors="coerce"
    )

    df["value"] = pd.to_numeric(
        df["value"],
        errors="coerce"
    )

    print("Data types cleaned")

    return df

def filter_years(df):

    before = len(df)

    df = df[
        (df["year"] >= START_YEAR) & 
        (df["year"] <= END_YEAR)
    ].copy()

    after = len(df)

    print(
        f"Year filter: removed {before - after} rows"
    )

    return df

def check_missing_values(df):

    missing = df.isnull().sum()

    print("Missing values:")
    print(missing)

    missing_rows = df[
        df["country_code"].isnull() |
        df["indicator_code"].isnull() |
        df["year"].isnull() | 
        df["value"].isnull()
    ]

    print(f"\nRows containing missing values: {len(missing_rows)}")

    return df

def remove_invalid_records(df):

    before = len(df)

    df = df.dropna(
        subset=[
            "country_code",
            "indicator_code",
            "year"
        ]
    )

    df = df.dropna(subset=["value"])

    after = len(df)

    print(f"Removed {before - after} invalid/missing rows")

    return df

def validate_indicators(df):

    unknown_indicators = set(df["indicator_code"]) - set(EXPECTED_INDICATORS.keys())

    if unknown_indicators:
        print("\nWARNING: Unknown indicators found:")
        print(unknown_indicators)

    else:
        print("All indicators are recognized")

    return df

def validate_values(df):

    invalid_count = 0

    for indicator_code, rules in EXPECTED_INDICATORS.items():

        indicator_mask = (df["indicator_code"] == indicator_code)

        if rules["min"] is not None:

            invalid_min = (indicator_mask & (df["value"] < rules["min"]))
            count = invalid_min.sum()

            if count > 0:
                print(f"WARNING: {count} invalid values for {indicator_code} (below minimum)")

                invalid_count += count

        if rules["max"] is not None:

            invalid_max = (
                indicator_mask & (df["value"] > rules["max"])
            )

            count = invalid_max.sum()

            if count > 0:
                print(f"WARNING: {count} invalid values for {indicator_code} (above maximum)")

                invalid_count += count

    if invalid_count == 0:
        print("Indicator value validation passed")
    else:
        print(f"WARNING: {invalid_count} potentially invalid observations found")

    return df

def remove_duplicates(df):

    before = len(df)

    duplicates = df.duplicated(
        subset=[
            "country_code",
            "indicator_code",
            "year"
        ],
        keep="first"
    )

    duplicate_count = duplicates.sum()

    if duplicate_count > 0:
        print(f"WARNING: Found {duplicate_count} duplicates")

    df = df.drop_duplicates(
        subset=[
            "country_code",
            "indicator_code",
            "year"
        ],
        keep = "first"
    )

    after = len(df)

    print(f"Removed {before-after} duplicate rows")

    return df

def finalize_types(df):

    df["year"] = df["year"].astype(int)

    df["value"] = df["value"].astype(float)

    return df

def sort_data(df):

    df = df.sort_values(
        by=[
            "country_code",
            "indicator_code",
            "year"
        ]
    ).reset_index(drop=True)

    return df

def save_processed_data(df):

    os.makedirs(
        os.path.dirname(PROCESSED_FILE),
        exist_ok=True
    )

    df.to_csv(
        PROCESSED_FILE,
        index=False
    )

    print(f"\n Cleaned data saved to: {PROCESSED_FILE}")

def clean_pipeline():

    print("\n==========================")
    print("WORLD BANK DATA CLEANING")
    print("============================\n")

    # 1. Load
    df = load_raw_data()

    # 2. Validate structure
    df = validate_columns(df)

    # 3. Clean data types
    df = clean_data_types(df)

    # 4. Filter years
    df = filter_years(df)

    # 5. Check missing values
    df = check_missing_values(df)

    # 6. Remove invalid records
    df = remove_invalid_records(df)

    # 7. Validate indicators
    df = validate_indicators(df)

    # 8. Validate values
    df = validate_values(df)

    # 9. Remove duplicates
    df = remove_duplicates(df)

    # 10. Finalize types
    df = finalize_types(df)

    # 11. Sort
    df = sort_data(df)

    # 12. Save
    save_processed_data(df)


    print("\n========================")
    print("CLEANING COMPLETE")
    print("==========================")

    print(f"Total rows: {len(df)}")
    print(
        f"Countries: {df['country_code'].nunique()}"
    )
    print(
        f"Indicators: {df['indicator_code'].nunique()}"
    )
    print(
        f"Year range: {df['year'].min()} - {df['year'].max()}"
    )

    print("\nRows per country:")
    print(
        df["country_code"]
        .value_counts()
        .sort_index()
    )

    print("\nRows per indicator:")
    print(
        df["indicator_code"]
        .value_counts()
    )

    print("\nFirst 10 cleaned rows:")
    print(df.head(10))

if __name__ == "__main__":
    clean_pipeline()