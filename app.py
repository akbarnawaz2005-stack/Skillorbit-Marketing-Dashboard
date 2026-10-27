import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Marketing Performance Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Marketing Performance Dashboard")
st.caption("SkillOrbit Project | Campaign Analytics & Business Insights")

st.sidebar.header("Dashboard Controls")
uploaded_file = st.sidebar.file_uploader(
    "Upload campaign CSV (optional)", type=["csv"]
)

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
else:
    data = pd.DataFrame({
        "Campaign": [
            "Summer Sale", "Winter Offer", "Brand Awareness",
            "Email Promotion", "Search Campaign", "Festive Sale",
            "New Product Launch", "Retargeting Ads",
            "Influencer Campaign", "Flash Sale",
            "Customer Loyalty", "Video Advertising"
        ],
        "Channel": [
            "Social Media", "Email", "Social Media", "Email",
            "Search", "Search", "Social Media", "Display",
            "Social Media", "Email", "Email", "Display"
        ],
        "Impressions": [
            10000, 8000, 15000, 6000, 12000, 18000,
            14000, 11000, 20000, 7500, 9000, 16000
        ],
        "Clicks": [
            650, 720, 900, 540, 960, 1260,
            840, 440, 1500, 600, 630, 560
        ],
        "Conversions": [
            65, 90, 108, 81, 144, 189,
            84, 44, 180, 90, 126, 56
        ],
        "Spend": [
            500, 300, 700, 200, 600, 900,
            650, 400, 1000, 250, 300, 550
        ],
        "Revenue": [
            1300, 1800, 2160, 1620, 2880, 3780,
            1680, 880, 3600, 1800, 2520, 1120
        ]
    })
    st.info("Showing illustrative sample data. Upload your own CSV to analyze real campaign data.")

required = [
    "Campaign", "Channel", "Impressions", "Clicks",
    "Conversions", "Spend", "Revenue"
]

if not all(col in data.columns for col in required):
    st.error("CSV must contain: " + ", ".join(required))
    st.stop()

for col in required[2:]:
    data[col] = pd.to_numeric(data[col], errors="coerce")

data = data.dropna(subset=required).copy()
data = data[
    (data["Impressions"] > 0)
    & (data["Clicks"] >= 0)
    & (data["Clicks"] <= data["Impressions"])
    & (data["Conversions"] >= 0)
    & (data["Conversions"] <= data["Clicks"])
    & (data["Spend"] >= 0)
    & (data["Revenue"] >= 0)
].copy()

if data.empty:
    st.error("No valid campaign records found in the data.")
    st.stop()

channels = st.sidebar.multiselect(
    "Filter by channel",
    options=sorted(data["Channel"].unique()),
    default=sorted(data["Channel"].unique())
)
data = data[data["Channel"].isin(channels)].copy()

if data.empty:
    st.warning("Select at least one channel.")
    st.stop()

data["CTR (%)"] = data["Clicks"] / data["Impressions"] * 100
data["Conversion Rate (%)"] = (
    data["Conversions"] / data["Clicks"].replace(0, float("nan")) * 100
).fillna(0)
data["Profit"] = data["Revenue"] - data["Spend"]
data["ROI (%)"] = (
    data["Profit"] / data["Spend"].replace(0, float("nan")) * 100
).fillna(0)

impressions = data["Impressions"].sum()
clicks = data["Clicks"].sum()
conversions = data["Conversions"].sum()
spend = data["Spend"].sum()
revenue = data["Revenue"].sum()
profit = revenue - spend
ctr = clicks / impressions * 100 if impressions else 0
conversion_rate = clicks and conversions / clicks * 100 or 0
roi = profit / spend * 100 if spend else 0

st.subheader("Performance Overview")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Impressions", f"{impressions:,.0f}")
m2.metric("Clicks", f"{clicks:,.0f}")
m3.metric("Conversions", f"{conversions:,.0f}")
m4.metric("CTR", f"{ctr:.2f}%")

m5, m6, m7, m8 = st.columns(4)
m5.metric("Total Spend", f"{spend:,.2f}")
m6.metric("Total Revenue", f"{revenue:,.2f}")
m7.metric("Profit", f"{profit:,.2f}")
m8.metric("ROI", f"{roi:.2f}%")

st.divider()
left, right = st.columns(2)

with left:
    st.plotly_chart(
        px.bar(
            data, x="Channel", y="Revenue", color="Channel",
            title="Revenue by Channel"
        ),
        use_container_width=True
    )

with right:
    st.plotly_chart(
        px.bar(
            data, x="Channel", y="CTR (%)", color="Channel",
            title="Click-Through Rate by Channel"
        ),
        use_container_width=True
    )

left, right = st.columns(2)

with left:
    st.plotly_chart(
        px.bar(
            data.sort_values("ROI (%)", ascending=False),
            x="Campaign", y="ROI (%)", color="Channel",
            title="Campaign Return on Investment"
        ),
        use_container_width=True
    )

with right:
    st.plotly_chart(
        px.scatter(
            data, x="Spend", y="Revenue", size="Conversions",
            color="Channel", hover_name="Campaign",
            title="Spend vs Revenue"
        ),
        use_container_width=True
    )

st.subheader("Campaign Details")
st.dataframe(data.round(2), use_container_width=True)

st.download_button(
    "Download filtered campaign analysis",
    data=data.to_csv(index=False).encode("utf-8"),
    file_name="campaign_analysis.csv",
    mime="text/csv"
)

st.subheader("Automated Business Insights")
best_roi = data.loc[data["ROI (%)"].idxmax()]
best_revenue = data.loc[data["Revenue"].idxmax()]
best_ctr = data.loc[data["CTR (%)"].idxmax()]

st.write(
    f"- **Highest ROI:** {best_roi['Campaign']} "
    f"({best_roi['ROI (%)']:.2f}%)."
)
st.write(
    f"- **Highest revenue:** {best_revenue['Campaign']} "
    f"({best_revenue['Revenue']:,.2f})."
)
st.write(
    f"- **Highest CTR:** {best_ctr['Campaign']} "
    f"({best_ctr['CTR (%)']:.2f}%)."
)
st.caption(
    "Note: Findings depend on the selected data and channel filters. "
    "Sample figures are illustrative, not actual business results."
)
