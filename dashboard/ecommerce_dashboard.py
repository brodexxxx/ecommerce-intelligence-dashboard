import streamlit as st
import plotly.express as px
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.src.ecommerce_trends import load_data, compute_weekly, find_trending

st.set_page_config(page_title="Trending Products", layout="wide")
st.title("Trending Products (E‑Commerce)")

with st.sidebar:
	st.header("Data")
	file = st.file_uploader("Upload CSV", type=["csv"])
	use_sample = st.checkbox("Use sample file", value=True)

if not file and not use_sample:
	st.info("Upload a CSV or tick 'Use sample file'.")
	st.stop()

path_or_file = file if file else "data/comprehensive_sales_data.csv"
df = load_data(path_or_file)

st.subheader("Raw data")
st.dataframe(df.head(30), use_container_width=True)

weekly = compute_weekly(df)
st.subheader("Weekly rollup")
st.dataframe(weekly.head(30), use_container_width=True)

top_up, top_down = find_trending(weekly)
st.subheader("Top Rising Products (latest week)")
st.dataframe(top_up[["product","week","sales","views","view_to_purchase","trend_score"]],
use_container_width=True)
st.subheader("Top Falling Products (latest week)")
st.dataframe(top_down[["product","week","sales","views","view_to_purchase","trend_score"]],
use_container_width=True)

st.subheader("Chart a product")
products = sorted(weekly["product"].unique().tolist())
pick = st.selectbox("Pick a product", options=products)
sub = weekly[weekly["product"] == pick].sort_values("week")
fig = px.line(sub, x="week", y="sales", markers=True, title=f"{pick} — Weekly Sales")
st.plotly_chart(fig, use_container_width=True)
st.subheader("Export")
st.download_button(
"Download weekly dataset (CSV)",
data=weekly.to_csv(index=False),
file_name="weekly_trends.csv",
mime="text/csv"
)