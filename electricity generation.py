import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ----- PAGE CONFIG -----

st.set_page_config(
    page_title="Solar Dashboard",
    page_icon="☀️",
    layout="wide",
)

# ----- CONSTANTS -----

DATA_PATH = "data/HDF_calckWh_sample.csv"

MPRN_COL = "MPRN"
METER_SERIAL_NUMBER = "Meter Serial Number"
TOTAL_READ_COL = "Read Value"
READ_TYPE_COL = "Read Type"
DATE_COLUMN = "Read Date and End Time"  # this must match the CSV header exactly

# ----- DATA LOADING & TRANSFORM -----

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.strip()  # remove spaces around column names

    # parse datetime
    df[DATE_COLUMN] = pd.to_datetime(df[DATE_COLUMN])

    # Import stays positive
    df["Import_kWh"] = np.where(
        df[READ_TYPE_COL] == "Active Import Interval kWh",
        df[TOTAL_READ_COL],
        0,
    )

    # Export becomes negative
    df["Export_kWh"] = np.where(
        df[READ_TYPE_COL] == "Active Export Interval kWh",
        -df[TOTAL_READ_COL],
        0,
    )

    # Net import - export
    df["Total_kWh"] = df["Import_kWh"] + df["Export_kWh"]

    return df

data = load_data()

# ----- TITLES & HEADER METRICS -----

st.title("Solar PV Dashboard ☀️")
st.metric("Solar Generation (kWh)", 1234, delta="+12%", help="Today's PV output ☀️")
st.write("Panel status 🌞🔆")

# Raw data toggle
if st.checkbox("Show Raw Data"):
    st.dataframe(data)

# Metrics row
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Records", len(data))
col2.metric("Total Import (kWh)", f"{data['Import_kWh'].sum():,.1f}")
col3.metric("Total Export (kWh)", f"{data['Export_kWh'].sum():,.1f}")
col4.metric("Avg Interval Import (kWh)", round(data["Import_kWh"].mean(), 3))

st.divider()

# ----- HOURLY IMPORT / EXPORT -----

data["Hour"] = data[DATE_COLUMN].dt.hour

hourly_import = (
    data.groupby("Hour")["Import_kWh"]
    .mean()
    .reset_index()
)

hourly_export = (
    data.groupby("Hour")["Export_kWh"]
    .mean()
    .reset_index()
)

fig_hourly_import = px.bar(
    hourly_import,
    x="Hour",
    y="Import_kWh",
    title="Average Import per Hour",
    labels={"Hour": "Hour of Day", "Import_kWh": "Average Import (kWh)"},
)

fig_hourly_export = px.bar(
    hourly_export,
    x="Hour",
    y="Export_kWh",
    title="Average Export per Hour (negative kWh)",
    labels={"Hour": "Hour of Day", "Export_kWh": "Average Export (kWh)"},
)

col_hi_1, col_hi_2 = st.columns(2)
with col_hi_1:
    st.plotly_chart(fig_hourly_import, use_container_width=True)
with col_hi_2:
    st.plotly_chart(fig_hourly_export, use_container_width=True)

st.divider()

# ----- DAILY IMPORT / EXPORT -----

data["Date"] = data[DATE_COLUMN].dt.date

daily_import = (
    data.groupby("Date")["Import_kWh"]
    .sum()
    .reset_index()
)

daily_export = (
    data.groupby("Date")["Export_kWh"]
    .sum()
    .reset_index()
)

fig_daily_import = px.bar(
    daily_import,
    x="Date",
    y="Import_kWh",
    title="Daily Import (kWh)",
    labels={"Date": "Date", "Import_kWh": "Import (kWh)"},
)

fig_daily_export = px.bar(
    daily_export,
    x="Date",
    y="Export_kWh",
    title="Daily Export (kWh, negative)",
    labels={"Date": "Date", "Export_kWh": "Export (kWh)"},
)

col_di_1, col_di_2 = st.columns(2)
with col_di_1:
    st.plotly_chart(fig_daily_import, use_container_width=True)
with col_di_2:
    st.plotly_chart(fig_daily_export, use_container_width=True)

st.divider()

# ----- MONTHLY IMPORT / EXPORT -----

data["Month"] = data[DATE_COLUMN].dt.to_period("M").astype(str)

monthly_import = (
    data.groupby("Month")["Import_kWh"]
    .sum()
    .reset_index()
)

monthly_export = (
    data.groupby("Month")["Export_kWh"]
    .sum()
    .reset_index()
)

fig_monthly_import = px.bar(
    monthly_import,
    x="Month",
    y="Import_kWh",
    title="Monthly Import (kWh)",
    labels={"Month": "Month", "Import_kWh": "Import (kWh)"},
)

fig_monthly_export = px.bar(
    monthly_export,
    x="Month",
    y="Export_kWh",
    title="Monthly Export (kWh, negative)",
    labels={"Month": "Month", "Export_kWh": "Export (kWh)"},
)

col_mo_1, col_mo_2 = st.columns(2)
with col_mo_1:
    st.plotly_chart(fig_monthly_import, use_container_width=True)
with col_mo_2:
    st.plotly_chart(fig_monthly_export, use_container_width=True)

st.divider()

# ----- MONTHLY IMPORT / EXPORT / NET LINE -----

monthly_net = (
    data.groupby("Month")[["Import_kWh", "Export_kWh", "Total_kWh"]]
    .sum()
    .reset_index()
)

fig_import_export_line = px.line(
    monthly_net,
    x="Month",
    y=["Import_kWh", "Export_kWh", "Total_kWh"],
    title="Monthly Import / Export / Net (kWh)",
    labels={"Month": "Month", "value": "kWh", "variable": "Series"},
)

st.plotly_chart(fig_import_export_line, use_container_width=True)

st.divider()

# ----- DATA SUMMARY -----

if st.checkbox("Show Dataset Summary"):
    st.write(data.describe())
