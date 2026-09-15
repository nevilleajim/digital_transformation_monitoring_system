from pathlib import Path
import sys

import pandas as pd
from sqlalchemy import text

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from src.database.connection import engine

CLEAN_FILE = PROJECT_ROOT / "data" / "processed" / "itu_datahub_clean.csv"

INDICATORS = {
    "ITU.IT_NET_USER": {
        "indicator_name": "Individuals using the Internet",
        "dimension": "Digital Access",
        "definition": "Percentage of individuals using the Internet.",
        "unit": "Percentage of population",
        "priority": "Essential",
    },
    "ITU.IT_CEL_SETS_P2": {
        "indicator_name": "Mobile cellular subscriptions",
        "dimension": "Digital Access",
        "definition": "Mobile cellular subscriptions per 100 people.",
        "unit": "Per 100 people",
        "priority": "Essential",
    },
    "ITU.IT_NET_BBND_P2": {
        "indicator_name": "Fixed broadband subscriptions",
        "dimension": "Digital Access",
        "definition": "Fixed broadband subscriptions per 100 people.",
        "unit": "Per 100 people",
        "priority": "Essential",
    },
    "ITU.IT_MLT_MAIN_P2": {
        "indicator_name": "Fixed telephone subscriptions",
        "dimension": "Digital Access",
        "definition": "Fixed telephone subscriptions per 100 people.",
        "unit": "Per 100 people",
        "priority": "Important",
    },
    "ITU.IT_NET_USER_M": {
        "indicator_name": "Male individuals using the Internet",
        "dimension": "Digital Inclusion",
        "definition": "Percentage of male individuals using the Internet.",
        "unit": "Percentage of male population",
        "priority": "Important",
    },
    "ITU.IT_NET_USER_F": {
        "indicator_name": "Female individuals using the Internet",
        "dimension": "Digital Inclusion",
        "definition": "Percentage of female individuals using the Internet.",
        "unit": "Percentage of female population",
        "priority": "Important",
    },
}


def load_clean_data():
    if not CLEAN_FILE.exists():
        raise FileNotFoundError(
            f"{CLEAN_FILE} does not exist. Run src/cleaning/clean_itu_datahub.py first."
        )

    df = pd.read_csv(CLEAN_FILE)
    print(f"Loaded {len(df)} cleaned ITU observations.")
    return df


def ensure_itu_source(connection):
    source_id = connection.scalar(
        text(
            """
            SELECT id
            FROM data_sources
            WHERE source_name = 'International Telecommunication Union'
            ORDER BY id
            LIMIT 1
            """
        )
    )

    if source_id is not None:
        return source_id

    return connection.scalar(
        text(
            """
            INSERT INTO data_sources (source_name, source_url)
            VALUES (
                'International Telecommunication Union',
                'https://datahub.itu.int/'
            )
            RETURNING id
            """
        )
    )


def ensure_itu_indicators(connection, source_id):
    query = text(
        """
        INSERT INTO indicators (
            indicator_code,
            indicator_name,
            dimension,
            definition,
            unit,
            source_id,
            frequency,
            priority
        )
        VALUES (
            :indicator_code,
            :indicator_name,
            :dimension,
            :definition,
            :unit,
            :source_id,
            'Annual',
            :priority
        )
        ON CONFLICT (indicator_code)
        DO UPDATE SET
            indicator_name = EXCLUDED.indicator_name,
            dimension = EXCLUDED.dimension,
            definition = EXCLUDED.definition,
            unit = EXCLUDED.unit,
            source_id = EXCLUDED.source_id,
            frequency = EXCLUDED.frequency,
            priority = EXCLUDED.priority
        """
    )

    for indicator_code, metadata in INDICATORS.items():
        connection.execute(
            query,
            {
                "indicator_code": indicator_code,
                "source_id": source_id,
                **metadata,
            },
        )

    print("ITU indicators are available in PostgreSQL")


def get_country_mapping(connection):
    result = connection.execute(text("SELECT id, country_code FROM countries"))
    return {row.country_code: row.id for row in result}


def get_indicator_mapping(connection):
    result = connection.execute(
        text(
            """
            SELECT id, indicator_code
            FROM indicators
            WHERE indicator_code LIKE 'ITU.%'
            """
        )
    )
    return {row.indicator_code: row.id for row in result}


def validate_mappings(df, country_mapping, indicator_mapping):
    missing_countries = set(df["country_code"].unique()) - set(country_mapping)

    if missing_countries:
        raise ValueError(f"Countries missing from database: {missing_countries}")

    missing_indicators = set(df["indicator_code"].unique()) - set(indicator_mapping)

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

    for _, row in df.iterrows():
        connection.execute(
            insert_query,
            {
                "country_id": country_mapping[row["country_code"]],
                "indicator_id": indicator_mapping[row["indicator_code"]],
                "year": int(row["year"]),
                "value": float(row["value"]),
            },
        )

    print(f"Processed {len(df)} ITU observations")


def main():
    print("\n==================================")
    print("ITU DATABASE LOADING")
    print("==================================\n")

    df = load_clean_data()

    with engine.begin() as connection:
        print("Connected to PostgreSQL")
        source_id = ensure_itu_source(connection)
        ensure_itu_indicators(connection, source_id)

        country_mapping = get_country_mapping(connection)
        indicator_mapping = get_indicator_mapping(connection)

        validate_mappings(df, country_mapping, indicator_mapping)
        insert_data(connection, df, country_mapping, indicator_mapping)

    print("\n==================================")
    print("ITU DATABASE LOAD COMPLETE")
    print("==================================")


if __name__ == "__main__":
    main()
