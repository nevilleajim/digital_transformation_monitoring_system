import pandas as pd
from pathlib import Path
import sys
from sqlalchemy import text

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from src.database.connection import engine

def get_indicator_data(indicator_code, country_code=None):

    query = """
        SELECT c.country_code, c.country_name, i.indicator_code, i.indicator_name, i.dimension, iv.year, iv.value, i.unit
        FROM indicator_values iv 
        JOIN countries c ON iv.country_id = c.id
        JOIN indicators i ON iv.indicator_id = i.id
        WHERE i.indicator_code = :indicator_code
    """

    params = {
        "indicator_code" : indicator_code
    }

    if country_code:
        query += """ AND c.country_code = :country_code"""

        params["country_code"] = country_code

    query += """ ORDER BY c.country_name, iv.year"""

    with engine.connect() as connection:

        df = pd.read_sql(text(query), connection, params=params)

    return df


def summarize_indicator(indicator_code):
    df = get_indicator_data(indicator_code)

    if df.empty:
        print(f"No database records found for {indicator_code}")
        return

    print("\n==============================")
    print("INDICATOR EDA")
    print("==============================")
    print(f"Indicator: {df['indicator_name'].iloc[0]}")
    print(f"Code: {indicator_code}")
    print(f"Rows: {len(df)}")
    print(f"Countries: {df['country_code'].nunique()}")
    print(f"Year range: {df['year'].min()} - {df['year'].max()}")

    print("\nSummary statistics:")
    print(df["value"].describe())

    latest_year = df["year"].max()
    latest = (
        df[df["year"] == latest_year]
        .sort_values("value", ascending=False)
        [["country_code", "country_name", "year", "value"]]
    )

    print(f"\nLatest values ({latest_year}):")
    print(latest.to_string(index=False))


if __name__ == "__main__":
    summarize_indicator("IT.NET.USER.ZS")
