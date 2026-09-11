import pandas as pd
from sqlalchemy import text

from connection import engine

CLEAN_FILE = "data/processed/world_bank_clean.csv"

def load_clean_data():

    df = pd.read_csv(CLEAN_FILE)

    print(f"Loaded {len(df)} cleaned observations.")

    return df

def get_country_mapping(connection):

    query = text(
        """SELECT id, country_code FROM countries"""
    )

    result = connection.execute(query)

    mapping = {
        row.country_code: row.id
        for row in result
    }

    return mapping

def get_indicator_mapping(connection):

    query = text(
        """SELECT id, indicator_code FROM indicators"""
    )

    result = connection.execute(query)

    mapping = {
        row.indicator_code: row.id
        for row in result
    }

    return mapping

def validate_mappings(df, country_mapping, indicator_mapping):

    csv_countries = set(df["country_code"].unique())
    db_countries = set(country_mapping.keys())

    missing_countries = csv_countries - db_countries

    if missing_countries:
        raise ValueError(f"Countries missing from database: {missing_countries}")

    csv_indicators = set(df["indicator_code"].unique())

    db_indicators = set(indicator_mapping.keys())

    missing_indicators = (csv_indicators - db_indicators)

    if missing_indicators:
        raise ValueError(f"Indicators missing from database: {missing_indicators}")

    print("Country mappings validated")
    print("Indicator mappings validated")

def insert_data(connection, df, country_mapping, indicator_mapping):

    insert_query = text(
        """
        INSERT INTO indicator_values (
            country_id,
            indicator_id,
            year,
            value
        )
        VALUES (
            :country_id,
            :indicator_id,
            :year,
            :value
        )
        ON CONFLICT (
            country_id,
            indicator_id,
            year
        )
        DO UPDATE SET value = EXCLUDED.value
        """
    )

    inserted = 0

    for _, row in df.iterrows():

        country_id = country_mapping[row["country_code"]]

        indicator_id = indicator_mapping[row["indicator_code"]]

        connection.execute(
            insert_query,
            {
                "country_id": country_id,
                "indicator_id": indicator_id,
                "year": int(row["year"]),
                "value": float(row["value"])
            }
        )

        inserted += 1

    print(f"Processed {inserted} observations")

def main():

    print("\n==================================")
    print("DATABASE LOADING")
    print("====================================\n")

    df = load_clean_data()

    with engine.begin() as connection:

        print("Connected to PostgreSQL")

        country_mapping = get_country_mapping(connection)

        indicator_mapping = get_indicator_mapping(connection)

        print(f"Found {len(country_mapping)} countries in database.")
        print(f"Found {len(indicator_mapping)} indicators in database")

        validate_mappings(df, country_mapping, indicator_mapping)

        insert_data(connection, df, country_mapping, indicator_mapping)

    print("\n==================================")
    print("DATABASE LOAD COMPLETE")
    print("====================================")

if __name__ == "__main__":
    main()