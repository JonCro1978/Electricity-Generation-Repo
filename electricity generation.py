import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


# Setting up the title page 


st.set_page_config(
    page_title="Solar Dashboard",
    page_icon="☀️",
    layout="wide"
)

#setting the data frame and to columns to be read & the totals 


DATA_PATH = r"C:\Users\unake\Downloads\HDF_calckWh_10018112406_19-07-2026.csv"

MPRN_COL = "MPRN"
METER_SERIAL_NUMBER = "Meter Serial Number"
TOTAL_READ_COL = "Read Value"
READ_TYPE_COL = "Read Type"
DATE_COLUMN = "Read Date and End Time"

# Loadin the data to the cache, so that the app does not re-read the app every time the app re-runs 
#removal of unwanted spaces from the colums 
#tidying up the date field to datetime type to extract hour, month and year

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.strip()
    df[DATE_COLUMN] = pd.to_datetime(df[DATE_COLUMN])

    # Create a Total column
    
    #import stays positive 
  df["Import_kWh"] = np.where(
    df["READ_TYPE_COL"] == "Active Import Interval kWh",
    df["TOTAL_READ_COL"],
    0,
)

#export becomes negative
df["Export_kWh"] = np.where(
    df["READ_TYPE_COL"] == "Active Export Interval kWh",
    -df["TOTAL_READ_COL"],
    0,
)

df["Total_kWh"] = df["Import_kWh"] + df["Export_kWh"]

return df

data = load_data()

# Titles

st.title("Solar PV Dashboard ☀️")
st.metric("Solar Generation (kWh)", 1234, delta="+12%", help="Today's PV output ☀️")
st.write("Panel status 🌞🔆") 


# Checkbox to show hide raw data frame


if st.checkbox("Show Raw Data"):
    st.write(data)


# Setting the page up into 3 columns on the first row to show the widgets and labeling same 

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Import Records", len(data))
col2.metric("Total Import", f"{int(data['Import_kWh'].sum()):,}")
col3.metric("Total Export", f"{int(data['Export_kWh'].sum()):,}")
col4.metric("Average Import Interval (KWh)", round(data["Import_kWh"].mean(), 3))

#First divider - mid section 

st.divider()

# Hourly average code, setting hourly group and datetime to hour, creating average 

data["Hour"] = data[DATE_COLUMN].dt.hour

hourly_import = (
    data.groupby("hour")["Import_kWh"]
    .mean()
    .reset_index()
)

hourly_export = (
    data.groupby("hour")["Export_kWH"]

#Plotly express creating the bar chart

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

col_left, col_right = st.columns(2)
with col_left:
    st.plotly_chart(fig_hourly_import, use_container_width=True)
with col_right:
    st.plotly_chart(fig_hourly_export, use_container_width=True)

# ----- DAILY IMPORT / EXPORT (GROUP BY DATE) -----

# Create a pure date column from datetime
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


# ----- MONTHLY IMPORT / EXPORT (GROUP BY MONTH) -----

# Create a year-month label for grouping
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


# ----- MONTHLY NET IMPORT/EXPORT LINE CHART -----

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
#Code for plotly 

#East vs West line graph
#Grouped data by data column by datetime hour, east and west sidewalk data sets

importexport = (
    data.groupby(data[DATE_COLUMN].dt.month)[[Import_kWh, Export_kWh ]]
    .mean()
    .reset_index()
)

importexport = importexport.rename(columns={DATE_COLUMN: "month"})

fig_side = px.line(
    importexport,
    x="month",
    y=[Import_kWh, Export_kWh],
    title="Average Import/Export(by month of year)"
)

fig_side.update_layout(
    xaxis_title="Hour of day (0–23)",
    yaxis_title="Average Import/Export"
)
fig_side.show()

#Dashboard layout design, setting the columns for the widgets to sit in, divider then lower row columns

st.divider()

# ----- LAYOUT: HOURLY CHARTS -----

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_hourly_import, use_container_width=True)

with col2:
    st.plotly_chart(fig_hourly_export, use_container_width=True)

st.divider()

# ----- LAYOUT: DAILY CHARTS -----

col3, col4 = st.columns(2)

with col3:
    st.plotly_chart(fig_daily_import, use_container_width=True)

with col4:
    st.plotly_chart(fig_daily_export, use_container_width=True)

st.divider()

# ----- LAYOUT: MONTHLY CHARTS -----

col5, col6 = st.columns(2)

with col5:
    st.plotly_chart(fig_monthly_import, use_container_width=True)

with col6:
    st.plotly_chart(fig_monthly_export, use_container_width=True)

st.divider()

# ----- LAYOUT: MONTHLY IMPORT / EXPORT / NET LINE -----

st.plotly_chart(fig_import_export_line, use_container_width=True)

st.divider()

# ----- DATA SUMMARY -----

if st.checkbox("Show Dataset Summary"):
    st.write(data.describe())
#Data Summary details & addition of the checkbox 

if st.checkbox("Show Dataset Summary"):
    st.write(data.describe())


