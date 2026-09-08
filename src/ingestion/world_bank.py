import requests
import pandas as pd

COUNTRIES = [
    "CMR",
    "GHA",
    "KEN",
    "NGA",
    "RWA",
    "ZAF"
]

INDICATORS = [
    "IT.NET.USER.ZS",
    "IT.CEL.SETS.P2",
    "IT.NET.BBND.P2",
    "EG.ELC,ACCS.ZS",
    "NY.GDP.PCAP.CD"
]

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

def fetch_all_data():
    all_data = []

    for country in COUNTRIES:
        for indicator in INDICATORS:

            print(f"fetching {indicator}, for {country}...")

            df = fetch_world_bank_data(country, indicator)

            if not df.empty:
                all_data.append(df)

    if not all_data:
        return pd.DataFrame()

    return pd.concat(
        all_data,
        ignore_index=True
    )

if __name__ == "__main__":

    df = fetch_all_data()

    print(df.head())
    print()
    print(df.tail())
    print()
    print(f"Number of observations: {len(df)}")
