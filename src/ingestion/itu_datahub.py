from pathlib import Path

import pandas as pd
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SOURCE_URL = (
    "https://datacatalogfiles.worldbank.org/ddh-published/0067055/DR0095955/"
    "WBG_WDI_ITU_INDICATORS.csv"
)

SOURCE_FILE = PROJECT_ROOT / "data" / "raw" / "itu_datahub_source.csv"
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "itu_datahub_raw.csv"

COUNTRIES = ["CMR", "GHA", "KEN", "NGA", "RWA", "ZAF"]

INDICATORS = {
    "IT_NET_USER": "ITU.IT_NET_USER",
    "IT_CEL_SETS_P2": "ITU.IT_CEL_SETS_P2",
    "IT_NET_BBND_P2": "ITU.IT_NET_BBND_P2",
    "IT_MLT_MAIN_P2": "ITU.IT_MLT_MAIN_P2",
    "IT_NET_USER_M": "ITU.IT_NET_USER_M",
    "IT_NET_USER_F": "ITU.IT_NET_USER_F",
}


def download_source_file():
    SOURCE_FILE.parent.mkdir(parents=True, exist_ok=True)

    if SOURCE_FILE.exists():
        print(f"Using existing ITU source file: {SOURCE_FILE}")
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
            print(f"Downloaded ITU source data to: {SOURCE_FILE}")
            return SOURCE_FILE
        except requests.RequestException as error:
            last_error = error

    raise ConnectionError(
        "Could not download the ITU Data Hub CSV. If the URL opens in your "
        "browser, download it manually and save it as data/raw/itu_datahub_source.csv."
    ) from last_error


def read_source_file(source_file):
    for encoding in ("utf-8-sig", "latin1", "cp1252"):
        try:
            return pd.read_csv(source_file, encoding=encoding)
        except UnicodeDecodeError:
            continue

    raise ValueError("Could not read ITU source file with supported encodings.")


def fetch_itu_data():
    source_file = download_source_file()
    df = read_source_file(source_file)

    required_columns = {"REF_AREA", "INDICATOR", "TIME_PERIOD", "OBS_VALUE"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(f"Missing ITU source columns: {missing_columns}")

    df = df[
        df["REF_AREA"].isin(COUNTRIES)
        & df["INDICATOR"].isin(INDICATORS.keys())
    ].copy()

    result = pd.DataFrame(
        {
            "country_code": df["REF_AREA"].astype(str).str.strip().str.upper(),
            "indicator_code": df["INDICATOR"].map(INDICATORS),
            "year": pd.to_numeric(df["TIME_PERIOD"], errors="coerce"),
            "value": pd.to_numeric(df["OBS_VALUE"], errors="coerce"),
        }
    )

    if result.empty:
        raise ValueError("No selected ITU observations were found.")

    RAW_FILE.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(RAW_FILE, index=False)

    print(f"Raw ITU data saved to: {RAW_FILE}")
    print(f"Total observations: {len(result)}")

    return result


if __name__ == "__main__":
    fetch_itu_data()
