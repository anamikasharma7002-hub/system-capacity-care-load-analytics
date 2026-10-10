import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="System Capacity Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("System Capacity & Care Load Analytics")
st.write(
    "Analysis of CBP Custody and HHS Care "
    "for Unaccompanied Children"
)

# Load dataset
@st.cache_data
def load_data():
    data = pd.read_csv("Cleaned_HHS_Unaccompanied_Children.csv")
    data["Date"] = pd.to_datetime(data["Date"])
    return data

df = load_data()

# Convert numeric columns
numeric_columns = [
    "Children apprehended and placed in CBP custody*",
    "Children in CBP custody",
    "Children transferred out of CBP custody",
    "Children in HHS Care",
    "Children discharged from HHS Care"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(
        df[col].astype(str).str.replace(",", ""),
        errors="coerce"
    )

df = df.dropna(subset=["Date"] + numeric_columns)
df = df.sort_values("Date")

# Calculate metrics
df["Total System Load"] = (
    df["Children in CBP custody"]
    + df["Children in HHS Care"]
)

df["Net Intake"] = (
    df["Children apprehended and placed in CBP custody*"]
    - df["Children transferred out of CBP custody"]
    - df["Children discharged from HHS Care"]
)

df["7-Day Average"] = (
    df["Total System Load"].rolling(7).mean()
)

df["14-Day Average"] = (
    df["Total System Load"].rolling(14).mean()
)

average_load = df["Total System Load"].mean()

df["System Strain"] = (
    df["Total System Load"] > average_load
)

# KPI section
st.header("Project KPIs")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Average CBP Custody",
        f"{df['Children in CBP custody'].mean():,.2f}"
    )

    st.metric(
        "Average Total System Load",
        f"{df['Total System Load'].mean():,.2f}"
    )

with col2:
    st.metric(
        "Average HHS Care",
        f"{df['Children in HHS Care'].mean():,.2f}"
    )

    st.metric(
        "System Strain Days",
        f"{int(df['System Strain'].sum())}"
    )

st.metric(
    "System Strain Percentage",
    f"{df['System Strain'].mean() * 100:.2f}%"
)

st.write(
    "Maximum Total System Load:",
    f"{df['Total System Load'].max():,.0f}"
)

st.write(
    "Minimum Total System Load:",
    f"{df['Total System Load'].min():,.0f}"
)

st.write(
    "Average Net Intake:",
    f"{df['Net Intake'].mean():,.2f}"
)

# Date filter
st.header("Explore Data")

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

date_range = st.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range

    filtered_df = df[
        (df["Date"].dt.date >= start_date)
        & (df["Date"].dt.date <= end_date)
    ]
else:
    filtered_df = df.copy()

if filtered_df.empty:
    st.warning("No data available for this date range.")
    st.stop()

# Graph 1
st.subheader("Daily Total System Load")

fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(
    filtered_df["Date"],
    filtered_df["Total System Load"]
)
ax.set_xlabel("Date")
ax.set_ylabel("Children")
ax.grid(True)
plt.xticks(rotation=45)
st.pyplot(fig)
plt.close(fig)

# Graph 2
st.subheader("CBP Custody vs HHS Care")

fig, ax = plt.subplots(figsize=(12, 4))

ax.plot(
    filtered_df["Date"],
    filtered_df["Children in CBP custody"],
    label="CBP Custody"
)

ax.plot(
    filtered_df["Date"],
    filtered_df["Children in HHS Care"],
    label="HHS Care"
)

ax.set_xlabel("Date")
ax.set_ylabel("Children")
ax.legend()
ax.grid(True)
plt.xticks(rotation=45)

st.pyplot(fig)
plt.close(fig)

# Graph 3
st.subheader("Net Intake Over Time")

fig, ax = plt.subplots(figsize=(12, 4))

ax.plot(
    filtered_df["Date"],
    filtered_df["Net Intake"]
)

ax.axhline(0)
ax.set_xlabel("Date")
ax.set_ylabel("Net Intake")
ax.grid(True)
plt.xticks(rotation=45)

st.pyplot(fig)
plt.close(fig)

# Graph 4
st.subheader("Rolling Average Analysis")

fig, ax = plt.subplots(figsize=(12, 4))

ax.plot(
    filtered_df["Date"],
    filtered_df["Total System Load"],
    label="Total Load"
)

ax.plot(
    filtered_df["Date"],
    filtered_df["7-Day Average"],
    label="7-Day Average"
)

ax.plot(
    filtered_df["Date"],
    filtered_df["14-Day Average"],
    label="14-Day Average"
)

ax.set_xlabel("Date")
ax.set_ylabel("Children")
ax.legend()
ax.grid(True)
plt.xticks(rotation=45)

st.pyplot(fig)
plt.close(fig)

# Findings
st.header("Key Findings")

st.write(
    "1. HHS Care represents the major portion of the overall system load."
)

st.write(
    "2. The total system load varies over time."
)

st.write(
    "3. Average Net Intake is negative in the analysed dataset."
)

st.write(
    "4. System load frequently exceeds its overall average."
)

st.write(
    "5. Rolling averages help identify longer-term trends."
)

st.success("Dashboard loaded successfully!")
