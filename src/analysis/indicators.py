import pandas as pd
from sqlalchemy import text

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
        query += """AND c.country_code = :country_code"""

        params["country_code"] = country_code

    query += """ORDER BY c.country_name, iv.year"""

    with engine.connect() as connection:

        df = pd.read_sql(text(query), connection, params=params)

    return df