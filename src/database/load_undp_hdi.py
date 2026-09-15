from pathlib import Path
import sys

import pandas as pd
from sqlalchemy import text

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from src.database.connection import engine

CLEAN_FILE = PROJECT_ROOT / "data" / "processed" / "undp_hdi_clean.csv"


def load_clean_data():
    if not CLEAN_FILE.exists():
        raise FileNotFoundError(
            f"{CLEAN_FILE} does not exist. Run src/cleaning/clean_undp_hdi.py first."
        )

    df = pd.read_csv(CLEAN_FILE)
    print(f"Loaded {len(df)} cleaned UNDP observations.")
    return df


def ensure_undp_indicator(connection):
    source_id = connection.scalar(
        text(
            """
            SELECT id
            FROM data_sources
            WHERE source_name = 'United Nations Development Programme'
            ORDER BY id
            LIMIT 1
            """
        )
    )

    if source_id is None:
        source_id = connection.scalar(
            text(
                """
                INSERT INTO data_sources (source_name, source_url)
                VALUES (
                    'United Nations Development Programme',
                    'https://hdr.undp.org/data-center'
                )
                RETURNING id
                """
            )
        )

    connection.execute(
        text(
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
                'UNDP.HDI',
                'Human Development Index',
                'Human Development',
                'Composite index measuring average achievement in health, education, and standard of living.',
                'Index, 0 to 1',
                :source_id,
                'Annual',
                'Essential'
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
        ),
        {"source_id": source_id},
    )

    print("UNDP HDI indicator is available in PostgreSQL")


def get_country_mapping(connection):
    result = connection.execute(text("SELECT id, country_code FROM countries"))
    return {row.country_code: row.id for row in result}


def get_indicator_mapping(connection):
    result = connection.execute(
        text("SELECT id, indicator_code FROM indicators WHERE indicator_code = 'UNDP.HDI'")
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

    print(f"Processed {len(df)} UNDP observations")


def main():
    print("\n==================================")
    print("UNDP DATABASE LOADING")
    print("==================================\n")

    df = load_clean_data()

    with engine.begin() as connection:
        print("Connected to PostgreSQL")
        ensure_undp_indicator(connection)

        country_mapping = get_country_mapping(connection)
        indicator_mapping = get_indicator_mapping(connection)

        validate_mappings(df, country_mapping, indicator_mapping)
        insert_data(connection, df, country_mapping, indicator_mapping)

    print("\n==================================")
    print("UNDP DATABASE LOAD COMPLETE")
    print("==================================")


if __name__ == "__main__":
    main()
