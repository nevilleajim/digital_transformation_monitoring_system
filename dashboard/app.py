import os
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.analysis.indicators import get_indicator_data

load_dotenv(PROJECT_ROOT / ".env")

st.set_page_config(page_title="Digital Transformation Monitoring", layout="wide")

st.title("Digital Transformation Monitoring & Insights Platform")

st.markdown("""Monitor selected digital transformation indicators across countries using publicly available development data.""")

INDICATORS = {
    "IT.NET.USER.ZS": "Internet Usage",
    "IT.CEL.SETS.P2": "Mobile Cellular Subscriptions",
    "IT.NET.BBND.P2": "Fixed Broadband Subscriptions",
    "EG.ELC.ACCS.ZS": "Access to Electricity",
    "NY.GDP.PCAP.CD": "GDP per Capita",
    "UNDP.HDI": "Human Development Index",
    "ITU.IT_NET_USER": "ITU Internet Usage",
    "ITU.IT_CEL_SETS_P2": "ITU Mobile Cellular Subscriptions",
    "ITU.IT_NET_BBND_P2": "ITU Fixed Broadband Subscriptions",
    "ITU.IT_MLT_MAIN_P2": "ITU Fixed Telephone Subscriptions",
    "ITU.IT_NET_USER_M": "ITU Male Internet Usage",
    "ITU.IT_NET_USER_F": "ITU Female Internet Usage"
}

DATA_SOURCES = {
    "World Bank": [
        "IT.NET.USER.ZS",
        "IT.CEL.SETS.P2",
        "IT.NET.BBND.P2",
        "EG.ELC.ACCS.ZS",
        "NY.GDP.PCAP.CD",
    ],
    "United Nations Development Programme": [
        "UNDP.HDI",
    ],
    "International Telecommunication Union": [
        "ITU.IT_NET_USER",
        "ITU.IT_CEL_SETS_P2",
        "ITU.IT_NET_BBND_P2",
        "ITU.IT_MLT_MAIN_P2",
        "ITU.IT_NET_USER_M",
        "ITU.IT_NET_USER_F",
    ],
}

SOURCE_NOTES = {
    "World Bank": "World Bank indicators are useful for comparing national development, infrastructure, and economic conditions across countries.",
    "United Nations Development Programme": "UNDP indicators help explain broader human development outcomes, including health, education, and living standards.",
    "International Telecommunication Union": "ITU indicators focus on connectivity, telecommunications access, and digital inclusion.",
}

INDICATOR_EXPLANATIONS = {
    "IT.NET.USER.ZS": "This measures the share of people using the internet. Higher values usually suggest broader digital access and stronger connectivity.",
    "IT.CEL.SETS.P2": "This measures mobile cellular subscriptions per 100 people. It helps show how widely mobile connectivity is available.",
    "IT.NET.BBND.P2": "This measures fixed broadband subscriptions per 100 people. It reflects household or business access to stable wired internet services.",
    "EG.ELC.ACCS.ZS": "This measures the share of the population with access to electricity, which is a foundation for digital transformation.",
    "NY.GDP.PCAP.CD": "This measures average economic output per person in current US dollars. It provides context for a country's economic capacity.",
    "UNDP.HDI": "This summarizes human development using health, education, and income dimensions. Higher values indicate stronger overall human development.",
    "ITU.IT_NET_USER": "This measures internet use from ITU data and helps compare digital adoption across countries.",
    "ITU.IT_CEL_SETS_P2": "This measures mobile cellular subscriptions from ITU data and helps show mobile connectivity access.",
    "ITU.IT_NET_BBND_P2": "This measures fixed broadband subscriptions from ITU data and reflects stable broadband access.",
    "ITU.IT_MLT_MAIN_P2": "This measures fixed telephone subscriptions, which can provide historical context for communications infrastructure.",
    "ITU.IT_NET_USER_M": "This measures male internet use and helps reveal gender patterns in digital access.",
    "ITU.IT_NET_USER_F": "This measures female internet use and helps reveal gender patterns in digital inclusion.",
}


def format_country_list(country_names):
    if len(country_names) <= 3:
        return ", ".join(country_names)

    return f"{', '.join(country_names[:3])}, and {len(country_names) - 3} more"


def describe_change(row, unit_label):
    if row["absolute_change"] > 0:
        direction = "increased"
    elif row["absolute_change"] < 0:
        direction = "declined"
    else:
        direction = "did not change"

    return (
        f"{row['country_name']} {direction} by "
        f"{abs(row['absolute_change']):,.2f} {unit_label} "
        f"from {int(row['first_year'])} to {int(row['last_year'])}."
    )


def build_fallback_summary(
    indicator_name,
    selected_source,
    selected_indicator,
    selected_years,
    selected_country_names,
    top_country,
    bottom_country,
    largest_change,
    unit_label,
):
    country_text = format_country_list(selected_country_names)

    return [
        (
            f"You are viewing **{indicator_name}** from **{selected_source}** "
            f"for **{country_text}** between **{selected_years[0]}** and "
            f"**{selected_years[1]}**."
        ),
        INDICATOR_EXPLANATIONS.get(
            selected_indicator,
            "This indicator helps compare digital transformation progress across the selected countries.",
        ),
        SOURCE_NOTES.get(
            selected_source,
            "This source provides public development data for comparison.",
        ),
        (
            f"The highest latest value is **{top_country['country_name']}** "
            f"with **{top_country['value']:,.2f} {unit_label}**."
        ),
        (
            f"The lowest latest value is **{bottom_country['country_name']}** "
            f"with **{bottom_country['value']:,.2f} {unit_label}**."
        ),
        f"**Interpretation:** {describe_change(largest_change, unit_label)}",
        "Note: differences in data availability by country or year can affect comparisons.",
    ]


def build_ai_prompt(
    indicator_name,
    selected_source,
    selected_years,
    selected_country_names,
    top_country,
    bottom_country,
    largest_change,
    unit_label,
):
    country_text = format_country_list(selected_country_names)

    return f"""
Write a short plain-language dashboard summary for a digital transformation indicator.
Use only the facts below. Do not invent causes, policy claims, or missing data.

Indicator: {indicator_name}
Source: {selected_source}
Countries: {country_text}
Year range: {selected_years[0]} to {selected_years[1]}
Highest latest value: {top_country['country_name']} ({top_country['value']:,.2f} {unit_label})
Lowest latest value: {bottom_country['country_name']} ({bottom_country['value']:,.2f} {unit_label})
Largest movement: {largest_change['country_name']} changed by {largest_change['absolute_change']:,.2f} {unit_label}
Movement period: {int(largest_change['first_year'])} to {int(largest_change['last_year'])}

Return 2 concise paragraphs and 3 bullet insights.
"""


@st.cache_data(ttl=3600, show_spinner=False)
def generate_ai_summary(prompt):
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return None

    response = requests.post(
        "https://api.openai.com/v1/responses",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            "input": prompt,
        },
        timeout=12,
    )
    response.raise_for_status()
    result = response.json()

    if result.get("output_text"):
        return result["output_text"]

    output = result.get("output", [])
    text_parts = []
    for item in output:
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                text_parts.append(content["text"])

    return "\n\n".join(text_parts) or None


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
available_indicators = set(df["indicator_code"].unique())
source_options = [
    source
    for source, source_indicators in DATA_SOURCES.items()
    if any(indicator_code in available_indicators for indicator_code in source_indicators)
]
selected_source = st.sidebar.selectbox("Select source", source_options)
indicator_options = [
    indicator_code
    for indicator_code in DATA_SOURCES[selected_source]
    if indicator_code in available_indicators
]
selected_indicator = st.sidebar.selectbox("Select indicator", indicator_options, format_func=lambda x: INDICATORS[x])

filtered_df = df[
    df["country_name"].isin(selected_countries) & (df["indicator_code"] == selected_indicator)
].copy()

if filtered_df.empty:
    st.warning("No data is available for the selected filters.")
    st.stop()

min_year = int(filtered_df["year"].min())
max_year = int(filtered_df["year"].max())

selected_years = st.sidebar.slider("Year range", min_value=min_year, max_value=max_year, value=(min_year, max_year))

filtered_df = filtered_df[filtered_df["year"].between(selected_years[0], selected_years[1])]

if filtered_df.empty:
    st.warning("No data is available for the selected year range.")
    st.stop()

indicator_name = (filtered_df["indicator_name"].iloc[0])

unit = (filtered_df["unit"].iloc[0])

st.subheader(indicator_name)
st.caption(f"Unit: {unit}")

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
    / change["first_value"].replace(0, pd.NA)
) * 100

top_country = latest.iloc[0]
bottom_country = latest.iloc[-1]
largest_change = change.reindex(change["absolute_change"].abs().sort_values(ascending=False).index).iloc[0]
selected_country_names = sorted(filtered_df["country_name"].unique())

fallback_summary = build_fallback_summary(
    indicator_name,
    selected_source,
    selected_indicator,
    selected_years,
    selected_country_names,
    top_country,
    bottom_country,
    largest_change,
    unit,
)
ai_prompt = build_ai_prompt(
    indicator_name,
    selected_source,
    selected_years,
    selected_country_names,
    top_country,
    bottom_country,
    largest_change,
    unit,
)


@st.dialog("Dashboard summary", width="large", dismissible=True)
def show_dashboard_summary():
    ai_summary = None

    try:
        with st.spinner("Generating summary..."):
            ai_summary = generate_ai_summary(ai_prompt)
    except Exception:
        ai_summary = None

    if ai_summary:
        st.markdown(ai_summary)
        st.caption("AI-generated summary based on the currently selected dashboard view.")
    else:
        for paragraph in fallback_summary:
            st.markdown(paragraph)

    insight_col1, insight_col2, insight_col3 = st.columns(3)
    insight_col1.metric(
        "Highest latest value",
        top_country["country_name"],
        f"{top_country['value']:,.2f} {unit}",
        border=True,
    )
    insight_col2.metric(
        "Lowest latest value",
        bottom_country["country_name"],
        f"{bottom_country['value']:,.2f} {unit}",
        border=True,
    )
    insight_col3.metric(
        "Largest movement",
        largest_change["country_name"],
        f"{largest_change['absolute_change']:,.2f} {unit}",
        border=True,
    )


if st.button("Summary", icon=":material/summarize:"):
    show_dashboard_summary()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Countries", filtered_df["country_name"].nunique())
col2.metric("Observations", len(filtered_df))
col3.metric("Latest Year", filtered_df["year"].max())
col4.metric("Average Value", f"{filtered_df['value'].mean():,.2f}")

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
    width="stretch"
)

st.subheader("Latest Available Values")

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
    width="stretch"
)

st.subheader("Change Over Selected Period")

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
    width="stretch"
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
    width="stretch"
)
