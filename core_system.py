# core_system.py

import streamlit as st
import pandas as pd
import altair as alt
import requests
from io import StringIO
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose

# -------------------------
# Inline Configuration
# -------------------------
APP_TITLE = "Trade Data Dashboard"

# Single-user credentials (for demo only; in production, use secure methods)
SINGLE_USER = {
    "username": "admin",
    "password": "admin_password",  # Plaintext for demonstration only
    "name": "Admin User"
}

DEFAULT_SHEET_NAME = "Sheet1"
OPEN_METEO_API_URL = "https://api.open-meteo.com/v1/forecast"

# -------------------------
# Custom CSS for UI/UX
# -------------------------
st.set_page_config(page_title=APP_TITLE, layout="wide")
st.markdown(
    """
    <style>
    .main {font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;}
    .sidebar .sidebar-content {background-color: #f5f5f5; padding: 10px;}
    </style>
    """,
    unsafe_allow_html=True
)
st.title(APP_TITLE)

# -------------------------
# Authentication (Inline)
# -------------------------
def authenticate():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if not st.session_state.logged_in:
        st.markdown("<h2 style='text-align: center;'>Login</h2>", unsafe_allow_html=True)
        username_input = st.text_input("Username", key="username_input")
        password_input = st.text_input("Password", type="password", key="password_input")
        if st.button("Login"):
            if username_input == SINGLE_USER["username"] and password_input == SINGLE_USER["password"]:
                st.success(f"Welcome, {SINGLE_USER['name']}!")
                st.session_state.logged_in = True
            else:
                st.error("🚨 Incorrect username or password. Please try again.")
    return st.session_state.logged_in

if not authenticate():
    st.stop()

# -------------------------
# Data Upload (Inline)
# -------------------------
def upload_data():
    st.markdown("<h2 style='text-align: center;'>📂 Upload or Link Data</h2>", unsafe_allow_html=True)
    upload_option = st.radio("📥 Choose Data Source:", ("Upload CSV", "Google Sheet Link"), index=0)
    df = None
    if upload_option == "Upload CSV":
        uploaded_file = st.file_uploader("Upload CSV File", type=["csv"],
                                         help="Upload your CSV file with your trade data.")
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file, low_memory=False)
            except Exception as e:
                st.error(f"🚨 Error processing CSV file: {e}")
                df = pd.DataFrame()
    else:
        sheet_url = st.text_input("🔗 Enter Google Sheet Link:")
        if sheet_url and st.button("Load Google Sheet"):
            try:
                sheet_id = sheet_url.split("/d/")[1].split("/")[0]
                csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={DEFAULT_SHEET_NAME}"
                response = requests.get(csv_url)
                response.raise_for_status()
                df = pd.read_csv(StringIO(response.text), low_memory=False)
            except Exception as e:
                st.error(f"🚨 Error loading Google Sheet: {e}")
    if df is not None and not df.empty:
        if "Year" in df.columns and "Month" in df.columns:
            df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
            df["Month"] = pd.to_numeric(df["Month"], errors="coerce")
            df["Date"] = pd.to_datetime(df["Year"].astype(str) + "-" + df["Month"].astype(str) + "-01")
        return df
    else:
        st.warning("No data loaded. Please upload a CSV file or provide a valid Google Sheet link.")
        return pd.DataFrame()

if "data" not in st.session_state or st.sidebar.button("Reset Data"):
    data = upload_data()
    st.session_state["data"] = data
else:
    data = st.session_state["data"]

if data.empty:
    st.warning("No data available.")
    st.stop()
else:
    st.write("Data loaded successfully! Here's a preview:")
    st.dataframe(data.head())

# -------------------------
# Filtering (Inline)
# -------------------------
def add_filters(df):
    st.sidebar.header("Filter Data")
    years = sorted(df['Year'].dropna().unique().tolist())
    selected_years = st.sidebar.multiselect("Select Year(s)", options=years, default=years)
    months = sorted(df['Month'].dropna().unique().tolist())
    selected_months = st.sidebar.multiselect("Select Month(s)", options=months, default=months)
    reporters = sorted(df['Reporter'].dropna().unique().tolist())
    selected_reporters = st.sidebar.multiselect("Select Reporter(s)", options=reporters, default=reporters)
    partners = sorted(df['Partner'].dropna().unique().tolist())
    selected_partners = st.sidebar.multiselect("Select Partner(s)", options=partners, default=partners)
    codes = sorted(df['Code'].dropna().unique().tolist())
    selected_codes = st.sidebar.multiselect("Select Code(s)", options=codes, default=codes)
    filtered = df[
        (df['Year'].isin(selected_years)) &
        (df['Month'].isin(selected_months)) &
        (df['Reporter'].isin(selected_reporters)) &
        (df['Partner'].isin(selected_partners)) &
        (df['Code'].isin(selected_codes))
    ]
    return filtered

# -------------------------
# KPI Calculation (Inline)
# -------------------------
def calculate_kpis(df):
    total = df["Tons"].sum() if "Tons" in df.columns else 0
    if "Date" in df.columns:
        monthly = df.groupby(pd.Grouper(key="Date", freq="M"))["Tons"].sum()
        avg = monthly.mean()
    else:
        avg = 0
    return {"total_tons": total, "avg_monthly": avg}

# -------------------------
# Dashboard Modules (Inline)
# -------------------------
def show_market_overview():
    st.header("Market Overview")
    df_filtered = add_filters(data)
    kpis = calculate_kpis(df_filtered)
    col1, col2 = st.columns(2)
    col1.metric("Total Tonnage", f"{kpis['total_tons']:.2f}")
    col2.metric("Average Monthly", f"{kpis['avg_monthly']:.2f}")
    chart = alt.Chart(df_filtered).mark_line(point=True).encode(
        x='Date:T',
        y='sum(Tons):Q',
        tooltip=['Date:T', alt.Tooltip('sum(Tons):Q', title="Tonnage", format=",.2f")]
    ).properties(width=700, height=400).interactive()
    st.altair_chart(chart, use_container_width=True)

def show_detailed_analysis():
    st.header("Detailed Analysis")
    df_filtered = add_filters(data)
    st.dataframe(df_filtered.sort_values("Date", ascending=False))

def show_ai_based_alerts():
    st.header("AI-Based Alerts")
    mean_val = data["Tons"].mean()
    std_val = data["Tons"].std()
    alerts = data[data["Tons"] > mean_val + 2 * std_val]
    if not alerts.empty:
        st.write("Anomalies detected:")
        st.dataframe(alerts)
    else:
        st.write("No anomalies detected.")

def show_forecasting():
    st.header("Forecasting")
    df_sorted = data.sort_values("Date")
    df_sorted["Forecast"] = df_sorted["Tons"].rolling(window=3, min_periods=1).mean()
    actual_chart = alt.Chart(df_sorted).mark_line(point=True).encode(
        x='Date:T',
        y=alt.Y('Tons:Q', title="Actual Tonnage"),
        tooltip=['Date:T', alt.Tooltip('Tons:Q', format=",.2f")]
    )
    forecast_chart = alt.Chart(df_sorted).mark_line(color='red').encode(
        x='Date:T',
        y=alt.Y('Forecast:Q', title="Forecast Tonnage"),
        tooltip=[alt.Tooltip('Forecast:Q', format=",.2f")]
    )
    st.altair_chart(actual_chart + forecast_chart, use_container_width=True)

def show_country_level_insights():
    st.header("Country-Level Insights")
    df_filtered = add_filters(data)
    country_df = df_filtered.groupby("Partner", as_index=False)["Tons"].sum()
    chart = alt.Chart(country_df).mark_bar().encode(
        x=alt.X("Tons:Q", title="Total Tonnage"),
        y=alt.Y("Partner:N", sort='-x', title="Partner"),
        tooltip=["Partner", alt.Tooltip("Tons:Q", format=",.2f")]
    ).properties(width=700, height=400)
    st.altair_chart(chart, use_container_width=True)

def show_segmentation_analysis():
    st.header("Segmentation Analysis")
    df_filtered = add_filters(data)
    df_features = df_filtered[['Tons']].fillna(0)
    from sklearn.cluster import KMeans
    kmeans = KMeans(n_clusters=3, random_state=42)
    df_filtered['Cluster'] = kmeans.fit_predict(df_features)
    st.write("Cluster assignments (first 10 rows):")
    st.dataframe(df_filtered[['Date', 'Partner', 'Tons', 'Cluster']].head(10))
    cluster_chart = alt.Chart(df_filtered).mark_circle(size=60).encode(
        x='Date:T',
        y='Tons:Q',
        color='Cluster:N',
        tooltip=['Date:T', 'Partner', 'Tons', 'Cluster']
    ).properties(width=700, height=400)
    st.altair_chart(cluster_chart, use_container_width=True)

def show_correlation_analysis():
    st.header("Correlation Analysis")
    df_filtered = add_filters(data)
    corr = df_filtered.select_dtypes(include=['float64', 'int64']).corr()
    st.write("Correlation Matrix:")
    st.dataframe(corr)
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
    st.pyplot(fig)

def show_time_series_decomposition():
    st.header("Time Series Decomposition")
    df_filtered = add_filters(data)
    df_sorted = df_filtered.sort_values("Date")
    ts = df_sorted.groupby("Date")["Tons"].sum()
    try:
        result = seasonal_decompose(ts, model='additive', period=12)
        fig, axes = plt.subplots(4, 1, figsize=(10, 8), sharex=True)
        result.observed.plot(ax=axes[0], legend=False)
        axes[0].set_ylabel("Observed")
        result.trend.plot(ax=axes[1], legend=False)
        axes[1].set_ylabel("Trend")
        result.seasonal.plot(ax=axes[2], legend=False)
        axes[2].set_ylabel("Seasonal")
        result.resid.plot(ax=axes[3], legend=False)
        axes[3].set_ylabel("Residual")
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Error in decomposition: {e}")

def show_calendar_insights():
    st.header("Calendar/Business Cycle Insights")
    df_filtered = add_filters(data)
    pivot = df_filtered.pivot_table(index="Month", columns="Year", values="Tons", aggfunc="mean")
    st.write("Average Monthly Tonnage by Year:")
    st.dataframe(pivot)
    df_filtered['Month_Str'] = df_filtered['Month'].astype(str)
    heat = alt.Chart(df_filtered).mark_rect().encode(
        x=alt.X("Year:N", title="Year"),
        y=alt.Y("Month_Str:N", title="Month"),
        color=alt.Color("mean(Tons):Q", title="Avg Tonnage"),
        tooltip=[alt.Tooltip("mean(Tons):Q", format=",.2f")]
    ).properties(width=700, height=400)
    st.altair_chart(heat, use_container_width=True)

def show_climate_insights():
    st.header("Climate Insights")
    df_filtered = add_filters(data)
    if df_filtered.empty:
        st.warning("No business data available for climate correlation.")
        return
    start_date = df_filtered["Date"].min().strftime("%Y-%m-%d")
    end_date = df_filtered["Date"].max().strftime("%Y-%m-%d")
    st.write(f"Fetching climate data from {start_date} to {end_date}...")
    latitude, longitude = 40.0, -100.0  # Fixed coordinates for demo
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "temperature_2m_max,precipitation_sum",
        "timezone": "auto"
    }
    response = requests.get(OPEN_METEO_API_URL, params=params)
    if response.status_code == 200:
        climate_json = response.json()
        dates = climate_json["daily"]["time"]
        temps = climate_json["daily"]["temperature_2m_max"]
        precip = climate_json["daily"]["precipitation_sum"]
        df_climate = pd.DataFrame({
            "Date": pd.to_datetime(dates),
            "Max_Temperature": temps,
            "Precipitation": precip
        })
        st.write("Climate Data:")
        st.dataframe(df_climate)
        temp_chart = alt.Chart(df_climate).mark_line(color="orange").encode(
            x='Date:T',
            y=alt.Y('Max_Temperature:Q', title="Max Temperature (°C)"),
            tooltip=['Date:T', 'Max_Temperature:Q']
        ).properties(width=700, height=300)
        st.altair_chart(temp_chart, use_container_width=True)
    else:
        st.error("Error fetching climate data.")

def simulate_scenario():
    st.header("Scenario Simulation")
    growth_factor = st.slider("Select Growth Factor", 0.5, 2.0, 1.0, 0.1)
    data_sim = data.copy()
    if "Tons" in data_sim.columns:
        data_sim["Simulated_Tons"] = data_sim["Tons"] * growth_factor
        st.write("Simulated Data (first 10 rows):")
        st.dataframe(data_sim.head(10))

def generate_report():
    csv = data.to_csv(index=False).encode('utf-8')
    st.download_button("Download Report as CSV", data=csv, file_name="trade_report.csv", mime="text/csv")

# -------------------------
# Main Navigation
# -------------------------
dashboard_options = [
    "Market Overview",
    "Detailed Analysis",
    "AI-Based Alerts",
    "Forecasting",
    "Country-Level Insights",
    "Segmentation Analysis",
    "Correlation Analysis",
    "Time Series Decomposition",
    "Calendar Insights",
    "Climate Insights",
    "Scenario Simulation",
    "Reporting"
]

selection = st.sidebar.radio("Select Dashboard", dashboard_options)

if selection == "Market Overview":
    show_market_overview()
elif selection == "Detailed Analysis":
    show_detailed_analysis()
elif selection == "AI-Based Alerts":
    show_ai_based_alerts()
elif selection == "Forecasting":
    show_forecasting()
elif selection == "Country-Level Insights":
    show_country_level_insights()
elif selection == "Segmentation Analysis":
    show_segmentation_analysis()
elif selection == "Correlation Analysis":
    show_correlation_analysis()
elif selection == "Time Series Decomposition":
    show_time_series_decomposition()
elif selection == "Calendar Insights":
    show_calendar_insights()
elif selection == "Climate Insights":
    show_climate_insights()
elif selection == "Scenario Simulation":
    simulate_scenario()
elif selection == "Reporting":
    generate_report()
