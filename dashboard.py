import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Air Quality Dashboard",
    page_icon="🌫️",
    layout="wide"
)

st.title("🌫️ Air Quality Dashboard")
st.caption("Exploratory analysis of air pollution and weather data | March 2013 – February 2017")

POLLUTANTS = ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3"]
WEATHER = ["TEMP", "PRES", "DEWP", "RAIN", "WSPM"]

@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    # Use an existing datetime column when available; otherwise construct it.
    if "datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    elif {"year", "month", "day", "hour"}.issubset(df.columns):
        df["datetime"] = pd.to_datetime(
            df[["year", "month", "day", "hour"]], errors="coerce"
        )
    else:
        raise ValueError("Dataset harus memiliki kolom 'datetime' atau year, month, day, dan hour.")

    for col in POLLUTANTS + WEATHER:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["datetime"]).sort_values("datetime")
    return df

with st.sidebar:
    st.header("Dataset")
    uploaded = st.file_uploader("Upload file CSV", type=["csv"])
    st.caption("Jika tidak mengunggah file, aplikasi akan mencoba membaca CSV di folder yang sama.")
    st.divider()

try:
    if uploaded is not None:
        df = load_data(uploaded)
    else:
        try:
            df = load_data("PRSA_Data_Changping_20130301-20170228.csv")
        except FileNotFoundError:
            st.info("Silakan upload file PRSA_Data_Changping_20130301-20170228.csv melalui sidebar.")
            st.stop()
except Exception as exc:
    st.error(f"Gagal membaca dataset: {exc}")
    st.stop()

available_pollutants = [c for c in POLLUTANTS if c in df.columns]
available_weather = [c for c in WEATHER if c in df.columns]

if "PM2.5" not in df.columns:
    st.error("Kolom PM2.5 tidak ditemukan. Periksa nama kolom pada CSV.")
    st.stop()

min_date = df["datetime"].min().date()
max_date = df["datetime"].max().date()

with st.sidebar:
    st.header("Filter")
    date_range = st.date_input(
        "Rentang tanggal",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    selected_pollutant = st.selectbox(
        "Polutan untuk analisis tren",
        available_pollutants,
        index=available_pollutants.index("PM2.5")
    )
    aggregation = st.selectbox(
        "Agregasi tren",
        ["Harian", "Bulanan", "Tahunan"],
        index=1
    )

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered = df[
    (df["datetime"].dt.date >= start_date) &
    (df["datetime"].dt.date <= end_date)
].copy()

if filtered.empty:
    st.warning("Tidak ada data pada rentang tanggal yang dipilih.")
    st.stop()

# Summary metrics
st.subheader("Ringkasan Kualitas Udara")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Jumlah observasi", f"{len(filtered):,}")
c2.metric("Rata-rata PM2.5", f"{filtered['PM2.5'].mean():.2f} µg/m³")
c3.metric("Median PM2.5", f"{filtered['PM2.5'].median():.2f} µg/m³")
c4.metric("Maksimum PM2.5", f"{filtered['PM2.5'].max():.2f} µg/m³")

st.caption(
    f"Periode data terpilih: {start_date.strftime('%d %b %Y')} – "
    f"{end_date.strftime('%d %b %Y')}. Nilai agregat mengabaikan missing values."
)

# Tabs
tab_overview, tab_pollutants, tab_weather, tab_quality = st.tabs(
    ["Overview", "Pollutant Analysis", "Weather Analysis", "Data Quality"]
)

with tab_overview:
    st.subheader(f"Tren {selected_pollutant}")
    if aggregation == "Harian":
        trend = filtered.set_index("datetime")[selected_pollutant].resample("D").mean().dropna()
    elif aggregation == "Bulanan":
        trend = filtered.set_index("datetime")[selected_pollutant].resample("MS").mean().dropna()
    else:
        trend = filtered.set_index("datetime")[selected_pollutant].resample("YS").mean().dropna()

    if not trend.empty:
        trend_df = trend.rename("Concentration").reset_index()
        fig = px.line(
            trend_df, x="datetime", y="Concentration",
            title=f"Rata-rata {selected_pollutant} — {aggregation}",
            labels={"datetime": "Tanggal", "Concentration": f"{selected_pollutant}"}
        )
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Tidak cukup data untuk menampilkan tren.")

    st.subheader("Rata-rata konsentrasi polutan")
    means = filtered[available_pollutants].mean().sort_values(ascending=False)
    mean_df = means.rename_axis("Pollutant").reset_index(name="Mean concentration")
    fig_bar = px.bar(
        mean_df, x="Pollutant", y="Mean concentration", color="Pollutant",
        title="Rata-rata konsentrasi setiap polutan"
    )
    fig_bar.update_layout(showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

with tab_pollutants:
    st.subheader("Hubungan antarpolutan")
    corr_cols = [c for c in available_pollutants if c in filtered.columns]
    corr = filtered[corr_cols].corr(method="spearman")
    fig_corr = px.imshow(
        corr, text_auto=".2f", aspect="auto", color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1, title="Spearman Correlation — Air Pollutants"
    )
    st.plotly_chart(fig_corr, use_container_width=True)

    st.subheader("Hubungan PM2.5 dengan polutan lain")
    candidates = [c for c in ["PM10", "CO", "NO2", "SO2", "O3"] if c in filtered.columns]
    if candidates:
        x_pollutant = st.selectbox("Pilih polutan pembanding", candidates)
        plot_df = filtered[["PM2.5", x_pollutant]].dropna()
        rho = plot_df.corr(method="spearman").iloc[0, 1] if len(plot_df) > 1 else np.nan
        fig_scatter = px.scatter(
            plot_df, x=x_pollutant, y="PM2.5", opacity=0.35,
            title=f"{x_pollutant} vs PM2.5 | Spearman ρ = {rho:.2f}",
            labels={"PM2.5": "PM2.5", x_pollutant: x_pollutant}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        st.write(
            f"**Interpretasi:** Korelasi Spearman antara {x_pollutant} dan PM2.5 "
            f"adalah **{rho:.2f}**. Korelasi menggambarkan asosiasi monotonik, "
            "bukan hubungan sebab-akibat."
        )

with tab_weather:
    st.subheader("Variabel meteorologi")
    if available_weather:
        weather_var = st.selectbox("Pilih variabel meteorologi", available_weather)
        weather_trend = (
            filtered.set_index("datetime")[weather_var]
            .resample("MS").mean().dropna().rename("Mean value").reset_index()
        )
        fig_weather = px.line(
            weather_trend, x="datetime", y="Mean value",
            title=f"Rata-rata bulanan {weather_var}",
            labels={"datetime": "Bulan", "Mean value": weather_var}
        )
        st.plotly_chart(fig_weather, use_container_width=True)

        if weather_var in filtered.columns:
            pair = filtered[["PM2.5", weather_var]].dropna()
            rho_weather = pair.corr(method="spearman").iloc[0, 1] if len(pair) > 1 else np.nan
            st.metric(f"Spearman correlation: PM2.5 vs {weather_var}", f"{rho_weather:.2f}")
    else:
        st.info("Kolom meteorologi tidak ditemukan pada dataset.")

with tab_quality:
    st.subheader("Kualitas dan kelengkapan data")
    missing = filtered.isna().sum()
    missing_pct = (missing / len(filtered) * 100).round(2)
    quality = pd.DataFrame({
        "Missing count": missing,
        "Missing percentage (%)": missing_pct
    }).query("`Missing count` > 0").sort_values("Missing percentage (%)", ascending=False)

    q1, q2 = st.columns(2)
    q1.metric("Total missing values", f"{int(filtered.isna().sum().sum()):,}")
    q2.metric("Duplicate rows", f"{int(filtered.duplicated().sum()):,}")

    if not quality.empty:
        st.dataframe(quality, use_container_width=True)
        fig_missing = px.bar(
            quality.reset_index(), x="index", y="Missing percentage (%)",
            title="Persentase missing values per kolom",
            labels={"index": "Kolom"}
        )
        st.plotly_chart(fig_missing, use_container_width=True)
    else:
        st.success("Tidak ditemukan missing values pada data terpilih.")

    st.subheader("Preview data")
    st.dataframe(filtered.head(100), use_container_width=True)

st.divider()
st.caption(
    "Sumber data: PRSA Data — Changping, Beijing (2013–2017). "
    "Dashboard ini ditujukan untuk eksplorasi data, bukan diagnosis kesehatan atau "
    "penilaian kepatuhan terhadap standar kualitas udara."
)