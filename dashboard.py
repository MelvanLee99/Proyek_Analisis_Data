import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Page Configuration
st.set_page_config(
    page_title="Changping Air Quality Dashboard",
    page_icon="🌫️",
    layout="wide"
)

# Konstanta
POLLUTANTS = ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3"]

# Load Data
@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    # Create datetime column
    if "datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    elif {"year", "month", "day", "hour"}.issubset(df.columns):
        df["datetime"] = pd.to_datetime(df[["year", "month", "day", "hour"]], errors="coerce")
    else:
        raise ValueError(
            "Dataset harus memiliki kolom datetime "
            "atau year, month, day, dan hour."
        )
    # Convert pollutants to numeric
    for col in POLLUTANTS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    # Remove invalid datetime
    df = df.dropna(subset=["datetime"])
    # Sort data
    df = df.sort_values("datetime")
    return df
# Sidebar
st.sidebar.title("⚙️ Dashboard Controls")
uploaded_file = st.sidebar.file_uploader("Upload dataset CSV", type=["csv"])
if uploaded_file is None:
    st.info(
        "Silakan upload file "
        "`PRSA_Data_Changping_20130301-20170228.csv` "
        "melalui sidebar."
    )
    st.stop()


# Load Data
try:
    df = load_data(uploaded_file)
except Exception as e:
    st.error(f"Gagal membaca dataset: {e}")
    st.stop()
if "PM2.5" not in df.columns:
    st.error("Kolom PM2.5 tidak ditemukan.")
    st.stop()
# Filter tanggal
min_date = df["datetime"].min().date()
max_date = df["datetime"].max().date()
date_range = st.sidebar.date_input(
    "📅 Pilih rentang tanggal",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)
if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = min_date
    end_date = max_date

# Filter dataset
filtered = df[
    (df["datetime"].dt.date >= start_date)
    &
    (df["datetime"].dt.date <= end_date)
].copy()

if filtered.empty:
    st.warning("Tidak ada data pada periode yang dipilih.")
    st.stop()


# Dashboard Header
st.title("🌫️ Changping Air Quality Dashboard")
st.caption(
    "Analisis konsentrasi PM2.5 dan hubungannya dengan polutan lain "
    "| Changping, Beijing | 2013–2017"
)
st.divider()


# KPI Metrics
st.subheader("📊 Ringkasan Data")
col1, col2, col3, col4 = st.columns(4)
col1.metric(
    "Jumlah Observasi",
    f"{len(filtered):,}"
)
col2.metric(
    "Rata-rata PM2.5",
    f"{filtered['PM2.5'].mean():.2f} µg/m³"
)
col3.metric(
    "Median PM2.5",
    f"{filtered['PM2.5'].median():.2f} µg/m³"
)
col4.metric(
    "PM2.5 Maksimum",
    f"{filtered['PM2.5'].max():.2f} µg/m³"
)


# Pertanyaan Bisnis 1
st.divider()
st.header("Pertanyaan Bisnis 1")
st.subheader(
    "Bagaimana pola perubahan rata-rata konsentrasi PM2.5 "
    "berdasarkan waktu?"
)

# Tren Bulanan
monthly_pm25 = (
    filtered
    .set_index("datetime")["PM2.5"]
    .resample("MS")
    .mean()
    .dropna()
    .reset_index()
)
monthly_pm25.columns = [
    "datetime",
    "Average PM2.5"
]
fig_monthly = px.line(
    monthly_pm25,
    x="datetime",
    y="Average PM2.5",
    title="Monthly Average PM2.5 Concentration",
    labels={
        "datetime": "Month",
        "Average PM2.5": "PM2.5 (µg/m³)"
    }
)
fig_monthly.update_layout(
    hovermode="x unified"
)
st.plotly_chart(
    fig_monthly,
    use_container_width=True
)
# Heatmap Bulan x Jam
st.subheader(
    "Pola PM2.5 Berdasarkan Bulan dan Jam"
)
filtered["month_name"] = (
    filtered["datetime"]
    .dt.month_name()
)
filtered["hour"] = (
    filtered["datetime"]
    .dt.hour
)
month_order = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
]
filtered["month_name"] = pd.Categorical(
    filtered["month_name"],
    categories=month_order,
    ordered=True
)
heatmap_data = (
    filtered
    .pivot_table(
        index="month_name",
        columns="hour",
        values="PM2.5",
        aggfunc="mean"
    )
)
fig_heatmap = px.imshow(
    heatmap_data,
    aspect="auto",
    labels={
        "x": "Hour",
        "y": "Month",
        "color": "Average PM2.5"
    },
    title="Average PM2.5 by Month and Hour"
)
st.plotly_chart(
    fig_heatmap,
    use_container_width=True
)
# Pertanyaan Bisnis 3
st.divider()
st.header("Pertanyaan Bisnis 3")
st.subheader(
    "Polutan apa yang memiliki hubungan paling kuat "
    "dengan konsentrasi PM2.5?"
)
# Korelasi Spearman
available_pollutants = [
    col for col in POLLUTANTS
    if col in filtered.columns
]
correlations = {}
for pollutant in available_pollutants:
    if pollutant != "PM2.5":
        pair = filtered[
            ["PM2.5", pollutant]
        ].dropna()
        if len(pair) > 1:
            correlations[pollutant] = (
                pair
                .corr(method="spearman")
                .iloc[0, 1]
            )

corr_df = pd.DataFrame(
    correlations.items(),
    columns=[
        "Pollutant",
        "Spearman Correlation"
    ]
)
corr_df["Absolute Correlation"] = (
    corr_df["Spearman Correlation"]
    .abs()
)
corr_df = corr_df.sort_values(
    "Absolute Correlation",
    ascending=False
)
fig_corr = px.bar(
    corr_df,
    x="Pollutant",
    y="Spearman Correlation",
    text="Spearman Correlation",
    title="Spearman Correlation Between PM2.5 and Other Pollutants",
    labels={
        "Spearman Correlation":
        "Spearman Correlation (ρ)"
    }
)
fig_corr.update_traces(
    texttemplate="%{text:.2f}",
    textposition="outside"
)
fig_corr.update_yaxes(
    range=[-1, 1]
)
st.plotly_chart(
    fig_corr,
    use_container_width=True
)

# Fitur Interaktif
st.subheader("🔍 Perbandingan Polutan Interaktif")
selected_pollutant = st.selectbox(
    "Pilih polutan untuk dibandingkan dengan PM2.5",
    corr_df["Pollutant"].tolist()
)
plot_df = filtered[
    ["PM2.5", selected_pollutant]
].dropna()
rho = (
    plot_df
    .corr(method="spearman")
    .iloc[0, 1]
)
fig_scatter = px.scatter(
    plot_df,
    x=selected_pollutant,
    y="PM2.5",
    opacity=0.4,
    title=(
        f"{selected_pollutant} vs PM2.5 "
        f"| Spearman ρ = {rho:.2f}"
    ),
    labels={
        selected_pollutant: selected_pollutant,
        "PM2.5": "PM2.5 (µg/m³)"
    }
)
st.plotly_chart(
    fig_scatter,
    use_container_width=True
)
# Insight
st.divider()
st.subheader("💡 Key Insight")
if not corr_df.empty:
    strongest = corr_df.iloc[0]
    st.success(
        f"Polutan dengan hubungan terkuat terhadap PM2.5 "
        f"pada periode yang dipilih adalah "
        f"**{strongest['Pollutant']}** "
        f"dengan korelasi Spearman "
        f"**{strongest['Spearman Correlation']:.2f}**."
    )
st.caption(
    "Catatan: Korelasi menunjukkan hubungan statistik dan "
    "tidak secara langsung menunjukkan hubungan sebab-akibat."
)