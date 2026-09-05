import requests
import pandas as pd

def fetch_world_bank_data(country_code, indicator_code):

    url = (
        f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}"
    )

    params = {
        "format": "json",
        "per_page": 100
    }

    response = requests.get(url, params=params, timeout=30)

    response.raise_for_status()

    data = response.json()

    if len(data) < 2:
        return pd.DataFrame()

    records = data[1]

    rows = []

    for record in records:
        rows.append({
            "country_code": country_code,
            "indicator_code": indicator_code,
            "year": int(record["date"]),
            "value": record["value"]
        })
        
    return pd.DataFrame(rows)

if __name__ == "__main__":

    df = fetch_world_bank_data(
        "CMR",
        "IT.NET.USER.ZS"
    )

    print(df.head())
    print()
    print(df.tail())
    print()
    print(f"Number of observations: {len(df)}")
