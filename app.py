
import calendar
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# -----------------------------------
# PAGE SETTINGS
# -----------------------------------

st.set_page_config(
    page_title="Weather Insights",
    page_icon="🌦️",
    layout="wide"
)


# -----------------------------------
# COLORS
# -----------------------------------

NAVY = "#172F3A"
DARK_TEAL = "#286B70"
TEAL = "#438C85"
MINT = "#D8E7E3"
CORAL = "#C97867"
GOLD = "#C99B55"
BACKGROUND = "#F7F8F5"
WHITE = "#FFFFFF"
TEXT = "#20343D"
MUTED = "#52656D"
GRID = "#E5EBE7"

CHART_COLORS = [
    "#286B70",
    "#C97867",
    "#C99B55",
    "#7897A1",
    "#82A99B",
    "#8B7898"
]


# -----------------------------------
# LOAD AND PREPARE DATA
# -----------------------------------

@st.cache_data
def load_data():

    file_path = Path(__file__).parent / "weather_data.csv"

    df = pd.read_csv(file_path)

    df["Formatted Date"] = pd.to_datetime(
        df["Formatted Date"],
        errors="coerce",
        utc=True
    )

    df = df.dropna(subset=["Formatted Date"])

    numeric_columns = [
        "Temperature (C)",
        "Apparent Temperature (C)",
        "Wind Speed (km/h)",
        "Wind Bearing (degrees)",
        "Visibility (km)",
        "Pressure (millibars)",
        "Humidity"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    df["Summary"] = df["Summary"].fillna("Unknown")
    df["Precip Type"] = df["Precip Type"].fillna("Unknown")

    df["Year"] = df["Formatted Date"].dt.year
    df["Month"] = df["Formatted Date"].dt.month

    df["Month Name"] = df["Month"].apply(
        lambda month: calendar.month_name[month]
    )

    df["Date"] = df["Formatted Date"].dt.date

    return df


df = load_data()


# -----------------------------------
# SIDEBAR
# -----------------------------------

st.sidebar.title("Weather Insights")
st.sidebar.caption("Explore historical weather data")

st.sidebar.divider()

st.sidebar.subheader("Filters")

# Date filter

min_date = df["Date"].min()
max_date = df["Date"].max()

date_range = st.sidebar.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Weather summary filter

summary_options = sorted(
    df["Summary"].dropna().unique().tolist()
)

selected_summaries = st.sidebar.multiselect(
    "Weather condition",
    options=summary_options,
    default=summary_options
)

# Precipitation type filter

precip_options = sorted(
    df["Precip Type"].dropna().unique().tolist()
)

selected_precip = st.sidebar.multiselect(
    "Precipitation type",
    options=precip_options,
    default=precip_options
)

st.sidebar.divider()

st.sidebar.caption("Dataset overview")

st.sidebar.write(f"Total records: {len(df):,}")

st.sidebar.write(
    f"Available years: {df['Year'].min()}–{df['Year'].max()}"
)


# -----------------------------------
# FILTER DATA
# -----------------------------------

filtered_df = df.copy()

if len(date_range) == 2:

    start_date = date_range[0]
    end_date = date_range[1]

    filtered_df = filtered_df[
        (filtered_df["Date"] >= start_date)
        & (filtered_df["Date"] <= end_date)
    ]

filtered_df = filtered_df[
    filtered_df["Summary"].isin(selected_summaries)
]

filtered_df = filtered_df[
    filtered_df["Precip Type"].isin(selected_precip)
]


# -----------------------------------
# DASHBOARD TITLE
# -----------------------------------

st.title("Weather Insights")

st.caption(
    "An interactive analysis of historical weather patterns from 2006–2016."
)

st.divider()


# -----------------------------------
# CHECK FILTER RESULTS
# -----------------------------------

if filtered_df.empty:

    st.warning(
        "No weather records found for the selected filters. "
        "Please change your filter selections."
    )

    st.stop()


# -----------------------------------
# CHART DESIGN FUNCTION
# -----------------------------------

def style_chart(fig, height=350):

    fig.update_layout(
        height=height,
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        font=dict(
            family="Arial",
            color=TEXT,
            size=12
        ),
        title_font=dict(
            size=17,
            color=NAVY
        ),
        margin=dict(
            l=20,
            r=20,
            t=55,
            b=25
        ),
        hoverlabel=dict(
            bgcolor=WHITE,
            font_color=TEXT
        ),
        legend=dict(
            bgcolor="rgba(255,255,255,0)"
        )
    )

    fig.update_xaxes(
        showgrid=False,
        linecolor=GRID,
        tickfont=dict(color=MUTED)
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor=GRID,
        zeroline=False,
        tickfont=dict(color=MUTED)
    )

    return fig


# -----------------------------------
# SECTION HEADING FUNCTION
# -----------------------------------

def section(title, note):

    st.subheader(title)
    st.caption(note)


# -----------------------------------
# KEY METRICS
# -----------------------------------

section(
    "Weather at a Glance",
    "A quick overview of the selected weather observations."
)

avg_temp = filtered_df["Temperature (C)"].mean()

avg_humidity = filtered_df["Humidity"].mean() * 100

avg_wind = filtered_df["Wind Speed (km/h)"].mean()

total_records = len(filtered_df)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Average Temperature",
        f"{avg_temp:.1f} °C"
    )

with col2:
    st.metric(
        "Average Humidity",
        f"{avg_humidity:.1f}%"
    )

with col3:
    st.metric(
        "Average Wind Speed",
        f"{avg_wind:.1f} km/h"
    )

with col4:
    st.metric(
        "Observations",
        f"{total_records:,}"
    )


st.divider()


# -----------------------------------
# YEARLY TEMPERATURE TREND
# -----------------------------------

section(
    "Temperature Over the Years",
    "Shows how the average temperature changed from year to year."
)

yearly_temp = (
    filtered_df.groupby("Year")["Temperature (C)"]
    .mean()
    .reset_index()
)

fig_year = px.line(
    yearly_temp,
    x="Year",
    y="Temperature (C)",
    markers=True,
    title="Average Yearly Temperature",
    color_discrete_sequence=[DARK_TEAL]
)

fig_year.update_traces(
    line=dict(width=3),
    marker=dict(size=8)
)

fig_year.update_xaxes(title="Year")
fig_year.update_yaxes(title="Average Temperature (°C)")

st.plotly_chart(
    style_chart(fig_year, 380),
    use_container_width=True
)


# -----------------------------------
# MONTHLY TEMPERATURE
# -----------------------------------

section(
    "Monthly Temperature Patterns",
    "Compare average temperatures across the twelve months."
)

monthly_temp = (
    filtered_df.groupby("Month")["Temperature (C)"]
    .mean()
    .reset_index()
)

monthly_temp["Month Name"] = monthly_temp["Month"].apply(
    lambda month: calendar.month_name[month]
)

fig_month = px.bar(
    monthly_temp,
    x="Month Name",
    y="Temperature (C)",
    title="Average Temperature by Month",
    color="Temperature (C)",
    color_continuous_scale=[
        MINT,
        TEAL,
        DARK_TEAL
    ]
)

fig_month.update_xaxes(
    title="Month",
    categoryorder="array",
    categoryarray=list(calendar.month_name)[1:]
)

fig_month.update_yaxes(
    title="Average Temperature (°C)"
)

st.plotly_chart(
    style_chart(fig_month, 380),
    use_container_width=True
)


st.divider()


# -----------------------------------
# UNIVARIATE ANALYSIS
# -----------------------------------

section(
    "Weather Distribution",
    "Explore the distribution and spread of important weather measurements."
)

col1, col2 = st.columns(2)

# Temperature distribution

with col1:

    fig_temp = px.histogram(
        filtered_df,
        x="Temperature (C)",
        nbins=35,
        title="Temperature Distribution",
        color_discrete_sequence=[DARK_TEAL]
    )

    fig_temp.update_xaxes(
        title="Temperature (°C)"
    )

    fig_temp.update_yaxes(
        title="Number of Observations"
    )

    st.plotly_chart(
        style_chart(fig_temp),
        use_container_width=True
    )


# Humidity distribution

with col2:

    humidity_data = filtered_df.copy()

    humidity_data["Humidity (%)"] = (
        humidity_data["Humidity"] * 100
    )

    fig_humidity = px.histogram(
        humidity_data,
        x="Humidity (%)",
        nbins=30,
        title="Humidity Distribution",
        color_discrete_sequence=[CORAL]
    )

    fig_humidity.update_xaxes(
        title="Humidity (%)"
    )

    fig_humidity.update_yaxes(
        title="Number of Observations"
    )

    st.plotly_chart(
        style_chart(fig_humidity),
        use_container_width=True
    )


# Wind speed distribution

fig_wind = px.histogram(
    filtered_df,
    x="Wind Speed (km/h)",
    nbins=35,
    title="Wind Speed Distribution",
    color_discrete_sequence=[GOLD]
)

fig_wind.update_xaxes(
    title="Wind Speed (km/h)"
)

fig_wind.update_yaxes(
    title="Number of Observations"
)

st.plotly_chart(
    style_chart(fig_wind),
    use_container_width=True
)


st.divider()


# -----------------------------------
# BIVARIATE ANALYSIS
# -----------------------------------

section(
    "Relationships Between Weather Variables",
    "Explore how different weather measurements are related to each other."
)

col1, col2 = st.columns(2)


# Temperature vs Humidity

with col1:

    fig_scatter = px.scatter(
        filtered_df,
        x="Humidity",
        y="Temperature (C)",
        title="Temperature vs Humidity",
        opacity=0.35,
        color_discrete_sequence=[DARK_TEAL]
    )

    fig_scatter.update_xaxes(
        title="Humidity"
    )

    fig_scatter.update_yaxes(
        title="Temperature (°C)"
    )

    st.plotly_chart(
        style_chart(fig_scatter),
        use_container_width=True
    )


# Actual vs Apparent Temperature

with col2:

    fig_apparent = px.scatter(
        filtered_df,
        x="Temperature (C)",
        y="Apparent Temperature (C)",
        title="Actual vs Apparent Temperature",
        opacity=0.35,
        color_discrete_sequence=[CORAL]
    )

    fig_apparent.update_xaxes(
        title="Actual Temperature (°C)"
    )

    fig_apparent.update_yaxes(
        title="Apparent Temperature (°C)"
    )

    st.plotly_chart(
        style_chart(fig_apparent),
        use_container_width=True
    )


# -----------------------------------
# CORRELATION HEATMAP
# -----------------------------------

section(
    "Weather Correlation",
    "The heatmap shows the strength and direction of relationships between numerical weather variables."
)

correlation_columns = [
    "Temperature (C)",
    "Apparent Temperature (C)",
    "Humidity",
    "Wind Speed (km/h)",
    "Visibility (km)",
    "Pressure (millibars)"
]

correlation_matrix = filtered_df[
    correlation_columns
].corr()

fig_corr = px.imshow(
    correlation_matrix,
    text_auto=".2f",
    color_continuous_scale=[
        CORAL,
        WHITE,
        DARK_TEAL
    ],
    zmin=-1,
    zmax=1,
    title="Correlation Heatmap"
)

fig_corr.update_layout(
    height=500
)

st.plotly_chart(
    style_chart(fig_corr, 500),
    use_container_width=True
)


st.divider()


# -----------------------------------
# WEATHER CONDITIONS
# -----------------------------------

section(
    "Most Common Weather Conditions",
    "See which weather descriptions appeared most frequently in the selected data."
)

summary_counts = (
    filtered_df["Summary"]
    .value_counts()
    .head(10)
    .reset_index()
)

summary_counts.columns = [
    "Weather Condition",
    "Observations"
]

fig_summary = px.bar(
    summary_counts.sort_values("Observations"),
    x="Observations",
    y="Weather Condition",
    orientation="h",
    title="Top 10 Weather Conditions",
    color="Observations",
    color_continuous_scale=[
        MINT,
        TEAL,
        DARK_TEAL
    ]
)

fig_summary.update_xaxes(
    title="Number of Observations"
)

fig_summary.update_yaxes(
    title="Weather Condition"
)

st.plotly_chart(
    style_chart(fig_summary, 430),
    use_container_width=True
)


# -----------------------------------
# PRECIPITATION TYPE
# -----------------------------------

section(
    "Precipitation Type",
    "Compare the frequency of different precipitation categories."
)

precip_counts = (
    filtered_df["Precip Type"]
    .value_counts()
    .reset_index()
)

precip_counts.columns = [
    "Precipitation Type",
    "Observations"
]

fig_precip = px.pie(
    precip_counts,
    names="Precipitation Type",
    values="Observations",
    hole=0.55,
    title="Precipitation Type Distribution",
    color_discrete_sequence=CHART_COLORS
)

fig_precip.update_traces(
    textposition="inside",
    textinfo="percent+label"
)

st.plotly_chart(
    style_chart(fig_precip, 400),
    use_container_width=True
)


st.divider()


# -----------------------------------
# AUTOMATIC FINDINGS
# -----------------------------------

section(
    "Key Findings",
    "A few observations based on the currently selected data."
)

col1, col2 = st.columns(2)

# Warmest and coldest month

with col1:

    monthly_findings = (
        filtered_df.groupby("Month")["Temperature (C)"]
        .mean()
        .dropna()
    )

    if not monthly_findings.empty:

        warmest_month = monthly_findings.idxmax()
        coldest_month = monthly_findings.idxmin()

        warmest_name = calendar.month_name[warmest_month]
        coldest_name = calendar.month_name[coldest_month]

        st.container(border=True)

        st.markdown("**Temperature observations**")

        st.write(
            f"The warmest month in the selected data is "
            f"**{warmest_name}**, with an average temperature of "
            f"**{monthly_findings.max():.1f} °C**."
        )

        st.write(
            f"The coldest month is **{coldest_name}**, "
            f"with an average temperature of "
            f"**{monthly_findings.min():.1f} °C**."
        )


# Most common weather condition

with col2:

    most_common_weather = filtered_df["Summary"].mode()

    if not most_common_weather.empty:

        common_weather = most_common_weather.iloc[0]

        common_percentage = (
            (filtered_df["Summary"] == common_weather).mean() * 100
        )

        st.container(border=True)

        st.markdown("**Most common weather condition**")

        st.write(
            f"**{common_weather}** is the most frequently recorded "
            f"weather condition, making up approximately "
            f"**{common_percentage:.1f}%** of the selected observations."
        )


# Temperature and humidity relationship

temperature_humidity_corr = filtered_df[
    ["Temperature (C)", "Humidity"]
].corr().iloc[0, 1]

st.container(border=True)

st.markdown("**Temperature and humidity relationship**")

if pd.notna(temperature_humidity_corr):

    if temperature_humidity_corr < -0.5:
        relationship = "a strong negative relationship"

    elif temperature_humidity_corr < 0:
        relationship = "a negative relationship"

    elif temperature_humidity_corr > 0.5:
        relationship = "a strong positive relationship"

    elif temperature_humidity_corr > 0:
        relationship = "a positive relationship"

    else:
        relationship = "almost no linear relationship"

    st.write(
        f"The correlation between temperature and humidity is "
        f"**{temperature_humidity_corr:.2f}**, indicating "
        f"{relationship} in the selected observations."
    )


st.divider()


# -----------------------------------
# RAW DATA TABLE
# -----------------------------------

section(
    "Explore the Data",
    "You can view the filtered weather records below."
)

show_data = st.checkbox("Show raw weather data")

if show_data:

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    csv_data = filtered_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download filtered data",
        data=csv_data,
        file_name="filtered_weather_data.csv",
        mime="text/csv"
    )


# -----------------------------------
# FOOTER
# -----------------------------------

st.divider()

st.caption(
    "Weather Insights | Historical Weather Data Analysis | 2006–2016"
)
