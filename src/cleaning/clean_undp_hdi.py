from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_FILE = PROJECT_ROOT / "data" / "raw" / "undp_hdi_raw.csv"
PROCESSED_FILE = PROJECT_ROOT / "data" / "processed" / "undp_hdi_clean.csv"

START_YEAR = 2010
END_YEAR = 2025

EXPECTED_INDICATORS = {
    "UNDP.HDI": {
        "name": "Human Development Index",
        "min": 0,
        "max": 1,
    },
}


def load_raw_data():
    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"{RAW_FILE} does not exist. Run src/ingestion/undp_hdi.py first."
        )

    df = pd.read_csv(RAW_FILE)
    print(f"Raw UNDP data loaded: {len(df)}")
    return df


def validate_columns(df):
    required_columns = {"country_code", "indicator_code", "year", "value"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    print("Required columns validated")
    return df


def clean_data_types(df):
    df["country_code"] = df["country_code"].astype(str).str.strip().str.upper()
    df["indicator_code"] = df["indicator_code"].astype(str).str.strip().str.upper()
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    print("Data types cleaned")
    return df


def filter_years(df):
    before = len(df)
    df = df[(df["year"] >= START_YEAR) & (df["year"] <= END_YEAR)].copy()
    print(f"Year filter: removed {before - len(df)} rows")
    return df


def remove_invalid_records(df):
    before = len(df)
    df = df.dropna(
        subset=["country_code", "indicator_code", "year", "value"]
    ).copy()
    print(f"Removed {before - len(df)} invalid/missing rows")
    return df


def validate_indicators(df):
    unknown = set(df["indicator_code"]) - set(EXPECTED_INDICATORS)

    if unknown:
        raise ValueError(f"Unknown UNDP indicators found: {unknown}")

    print("All UNDP indicators are recognized")
    return df


def validate_values(df):
    invalid_count = 0

    for indicator_code, rules in EXPECTED_INDICATORS.items():
        mask = df["indicator_code"] == indicator_code

        if rules["min"] is not None:
            invalid_count += (mask & (df["value"] < rules["min"])).sum()

        if rules["max"] is not None:
            invalid_count += (mask & (df["value"] > rules["max"])).sum()

    if invalid_count:
        raise ValueError(f"Found {invalid_count} invalid HDI values.")

    print("UNDP value validation passed")
    return df


def remove_duplicates(df):
    before = len(df)
    df = df.drop_duplicates(
        subset=["country_code", "indicator_code", "year"],
        keep="first",
    ).copy()
    print(f"Removed {before - len(df)} duplicate rows")
    return df


def finalize_data(df):
    df["year"] = df["year"].astype(int)
    df["value"] = df["value"].astype(float)
    return df.sort_values(
        ["country_code", "indicator_code", "year"]
    ).reset_index(drop=True)


def save_processed_data(df):
    PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_FILE, index=False)
    print(f"Cleaned UNDP data saved to: {PROCESSED_FILE}")


def clean_pipeline():
    print("\n==========================")
    print("UNDP HDI DATA CLEANING")
    print("==========================\n")

    df = load_raw_data()
    df = validate_columns(df)
    df = clean_data_types(df)
    df = filter_years(df)

    print("Missing values:")
    print(df.isnull().sum())

    df = remove_invalid_records(df)
    df = validate_indicators(df)
    df = validate_values(df)
    df = remove_duplicates(df)
    df = finalize_data(df)
    save_processed_data(df)

    print("\n==========================")
    print("UNDP CLEANING COMPLETE")
    print("==========================")
    print(f"Total rows: {len(df)}")
    print(f"Countries: {df['country_code'].nunique()}")
    print(f"Indicators: {df['indicator_code'].nunique()}")
    print(f"Year range: {df['year'].min()} - {df['year'].max()}")


if __name__ == "__main__":
    clean_pipeline()
