from pathlib import Path
import re

import pandas as pd
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SOURCE_URL = (
    "https://hdr.undp.org/sites/default/files/2025_HDR/"
    "HDR25_Composite_indices_complete_time_series.csv"
)

SOURCE_FILE = PROJECT_ROOT / "data" / "raw" / "undp_hdi_source.csv"
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "undp_hdi_raw.csv"

COUNTRIES = ["CMR", "GHA", "KEN", "NGA", "RWA", "ZAF"]

INDICATORS = {
    "hdi": "UNDP.HDI",
}


def download_source_file():
    SOURCE_FILE.parent.mkdir(parents=True, exist_ok=True)

    if SOURCE_FILE.exists():
        print(f"Using existing source file: {SOURCE_FILE}")
        return SOURCE_FILE

    headers = {
        "User-Agent": "digital-transformation-monitoring-system/0.1"
    }

    attempts = (
        (SOURCE_URL, True, True),
        (SOURCE_URL, False, True),
        (SOURCE_URL, False, False),
    )

    last_error = None

    for url, verify_ssl, trust_env in attempts:
        try:
            session = requests.Session()
            session.trust_env = trust_env
            response = session.get(
                url,
                headers=headers,
                verify=verify_ssl,
                timeout=60,
            )
            response.raise_for_status()
            SOURCE_FILE.write_bytes(response.content)
            print(f"Downloaded UNDP source data to: {SOURCE_FILE}")
            return SOURCE_FILE
        except requests.RequestException as error:
            last_error = error

    raise ConnectionError(
        "Could not download the UNDP HDR CSV. If the URL opens in your "
        "browser, download it manually and save it as data/raw/undp_hdi_source.csv."
    ) from last_error


def find_country_column(df):
    candidates = ["iso3", "country_code", "code"]
    lookup = {column.lower().strip(): column for column in df.columns}

    for candidate in candidates:
        if candidate in lookup:
            return lookup[candidate]

    raise ValueError(
        "Could not find a country code column. Expected one of: iso3, country_code, code."
    )


def fetch_undp_hdi_data():
    source_file = download_source_file()
    for encoding in ("utf-8-sig", "latin1", "cp1252"):
        try:
            df = pd.read_csv(source_file, encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise UnicodeDecodeError(
            "utf-8",
            b"",
            0,
            1,
            "Could not read UNDP source file with supported encodings.",
        )

    country_column = find_country_column(df)
    df[country_column] = df[country_column].astype(str).str.strip().str.upper()
    df = df[df[country_column].isin(COUNTRIES)].copy()

    rows = []
    year_column_pattern = re.compile(r"^(?P<prefix>[a-z]+)_(?P<year>\d{4})$", re.I)

    for column in df.columns:
        match = year_column_pattern.match(column.strip())

        if not match:
            continue

        prefix = match.group("prefix").lower()

        if prefix not in INDICATORS:
            continue

        year = int(match.group("year"))
        indicator_code = INDICATORS[prefix]

        values = pd.to_numeric(df[column], errors="coerce")

        for country_code, value in zip(df[country_column], values):
            rows.append(
                {
                    "country_code": country_code,
                    "indicator_code": indicator_code,
                    "year": year,
                    "value": value,
                }
            )

    result = pd.DataFrame(rows)

    if result.empty:
        raise ValueError(
            "No HDI year columns were found in the UNDP source file."
        )

    result.to_csv(RAW_FILE, index=False)
    print(f"Raw UNDP HDI data saved to: {RAW_FILE}")
    print(f"Total observations: {len(result)}")

    return result


if __name__ == "__main__":
    fetch_undp_hdi_data()
