import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.analysis.indicators import get_indicator_data

st.set_page_config(page_title="Digital Transformation Monitoring", layout="wide")

st.title("Digital Tranformation Monitoring & Insights Platform")

st.markdown("""Monnitor selected digital transformation indicators across countries using publicly available development data.""")

INDICATORS = {
    "IT.NET.USER.ZS": "Internet Usage",
    "IT.CEL.SETS.P2": "Mobile Cellula Subcriptions",
    "IT.NET.BBND.P2": "Fixed Broadbad Subscriptions",
    "EG.ELC,ACCS.ZS": "Access to Electricity",
    "NY.GDP.PCAP.CD": "GDP per Capita"
}

@st.cache_data
def load_all_data():

    data = []

    for indicator_code in INDICATORS:

        indicator_data = get_indicator_data(indicator_code)

        if not indicator_data.empty:
            data.append(indicator_data)

    if not data:
        return pd.DataFrame()

    return pd.concat(data, ignore_index=True)

df = load_all_data()

if df.empty:

    st.error("No data was returned from PostgreSQL")
    st.stop()

st.sidebar.header("Filters")

countries = sorted(df["country_name"].unique())
selected_countries = st.sidebar.multiselect("Select countries", countries, default=countries)
indicator_options = list(INDICATORS.keys())
selected_indicator = st.sidebar.selectbox("Select indicator", indicator_options, format_func=lambda x: INDICATORS[x])

filtered_df = df[
    df["country_name"].isin(selected_countries) & (df["indicator_code"] == selected_indicator)
].copy()

min_year = int(filtered_df["year"].min())
max_year = int(filtered_df["year"].max())

selected_years = st.sidebar.slider("Year range", min_value=min_year, max_value=max_year, value=(min_year, max_year))

filtered_df = filtered_df[filtered_df["year"].between(selected_years[0], selected_years[1])]

indicator_name = (filtered_df["indicator_name"].iloc[0])

unit = (filtered_df["unit"].iloc[0])

st.subheader(indicator_name)
st.caption(f"Unit: {unit}")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Countries", filtered_df["country_name"].nunique())
col2.metric("Observations", len(filtered_df))
col3.metric("Latest Year", filtered_df["year"].max())
col4.metric("Average Value", f"{filtered_df["value"].mean():,.2f}")

st.subheader("Indicator Trend")

fig = px.line(
    filtered_df,
    x="year",
    y="value",
    color="country_name",
    markers=True,
    title=f"{indicator_name} Over Time"
)

fig.update_layout(
    xaxis_title="Year",
    yaxis_title=unit,
    legend_title="Country",
    hovermode="x unified"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.subheader("Latest Available Values")

latest = (
    filtered_df
    .sort_values("year")
    .groupby("country_name")
    .tail(1)
    .sort_values(
        "value",
        ascending=False
    )
)

fig_latest = px.bar(
    latest,
    x="country_name",
    y="value",
    title=f"Latest {indicator_name} by Country",
    text="value"
)

fig_latest.update_layout(
    xaxis_title="Country",
    yaxis_title=unit
)

st.plotly_chart(
    fig_latest,
    use_container_width=True
)

st.subheader("Change Over Selected Period")


change = (
    filtered_df
    .sort_values("year")
    .groupby("country_name")
    .agg(
        first_year=("year", "first"),
        first_value=("value", "first"),
        last_year=("year", "last"),
        last_value=("value", "last")
    )
    .reset_index()
)

change["absolute_change"] = (
    change["last_value"]
    - change["first_value"]
)

change["percentage_change"] = (
    change["absolute_change"]
    / change["first_value"]
) * 100


fig_change = px.bar(
    change.sort_values(
        "absolute_change",
        ascending=False
    ),
    x="country_name",
    y="absolute_change",
    title="Absolute Change",
    text="absolute_change"
)

fig_change.update_layout(
    xaxis_title="Country",
    yaxis_title=f"Change ({unit})"
)

st.plotly_chart(
    fig_change,
    use_container_width=True
)

st.subheader("Underlying Data")

st.dataframe(
    filtered_df[
        [
            "country_name",
            "year",
            "value",
            "unit"
        ]
    ].sort_values(
        ["country_name", "year"]
    ),
    use_container_width=True
)