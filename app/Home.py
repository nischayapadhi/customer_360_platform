import streamlit as st
import pandas as pd
import plotly.express as px
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# 1. Page Config
st.set_page_config(page_title="Customer 360 AI", layout="wide", page_icon="🛍️")

# --- CUSTOM CSS FOR KPI CARDS ---
st.markdown("""
<style>
    .block-container {padding-top: 1rem; padding-bottom: 2rem;}
    div.kpi-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 10px;
    }
    div.kpi-card h3 {margin: 0; font-size: 16px; color: #666; font-weight: 600;}
    div.kpi-card h2 {margin: 5px 0; font-size: 28px; color: #333; font-weight: 700;}
    div.kpi-card p {margin: 0; font-size: 14px; color: #888;}
</style>
""", unsafe_allow_html=True)

# 2. Optimized Load Data (CSV First for Deployment)
@st.cache_data
def load_data():
    # PATHS
    csv_path = os.path.join("data", "processed", "customer_segments.csv")
    
    # Check if CSV exists (Deployment/Portable Mode)
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    else:
        # Fallback to Database (Local Development Mode)
        load_dotenv()
        DB_USER = os.getenv("DB_USER")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_HOST = os.getenv("DB_HOST")
        DB_PORT = os.getenv("DB_PORT")
        DB_NAME = os.getenv("DB_NAME")
        
        # Security Check
        if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
            st.error("Missing Data: Please run 'clustering.py' to generate data or check .env file.")
            st.stop()
            
        connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(connection_string)
        df = pd.read_sql("SELECT * FROM customer_segments", engine)

    # Apply Mapping
    cluster_map = {
        0: "⚠️ At Risk",
        1: "🛒 Casual Shoppers",
        2: "🏆 VIPs",
        3: "🔄 Loyalists"
    }
    df['segment_name'] = df['cluster_id'].map(cluster_map)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading application data: {e}")
    st.stop()

# 3. Header & Filter Logic
st.title("🛍️ Customer 360 Intelligence Platform")
st.markdown("---")

all_segments = sorted(df['segment_name'].unique())
col_controls, col_toggle = st.columns([4, 1])

with col_toggle:
    compare_mode = st.checkbox("Compare Groups")

with col_controls:
    if compare_mode:
        selected_segments = st.multiselect("Select Segments:", options=all_segments, default=all_segments)
    else:
        selected_segment = st.radio("Select Segment:", options=all_segments, horizontal=True, label_visibility="collapsed")
        selected_segments = [selected_segment]

if not selected_segments:
    st.warning("Please select a segment.")
    st.stop()

filtered_df = df[df['segment_name'].isin(selected_segments)]

# 4. KPI & Strategy Logic
segment_colors = {
    "🏆 VIPs": "#FFD700", "⚠️ At Risk": "#FC0202",
    "🔄 Loyalists": "#00FF08", "🛒 Casual Shoppers": "#FC8804"
}

if len(selected_segments) == 1:
    current_segment = selected_segments[0]
    current_color = segment_colors.get(current_segment, "#333")
    strategies = {
        "🏆 VIPs": "💎 **Strategy:** Maintain exclusivity. Offer 'Early Access' and personal support.",
        "⚠️ At Risk": "🛑 **Strategy:** Urgent Win-Back. Send a steep time-limited discount.",
        "🔄 Loyalists": "📢 **Strategy:** Turn into Advocates. Push a Referral/Loyalty Program.",
        "🛒 Casual Shoppers": "📈 **Strategy:** Increase Basket Size. Use 'Bundle & Save' upsell offers."
    }
    rec_text = strategies.get(current_segment, "Analyze behavior.")
else:
    current_color = "#333"
    rec_text = "⚖️ **Strategy:** Compare groups to allocate budget. Target 'Casuals' to become 'Loyalists'."

# Rendering KPIs
k1, k2, k3, k4 = st.columns(4)
def kpi_card(title, value, subtitle, color):
    st.markdown(f'<div class="kpi-card" style="border-left: 5px solid {color};"><h3>{title}</h3><h2>{value}</h2><p>{subtitle}</p></div>', unsafe_allow_html=True)

with k1: kpi_card("Customers", f"{filtered_df['customer_id'].nunique()}", "In view", current_color)
with k2: kpi_card("Avg Spend", f"${filtered_df['monetary_profit'].mean():,.0f}", "Lifetime Profit", current_color)
with k3: kpi_card("Avg Frequency", f"{filtered_df['frequency_orders'].mean():.1f}", "Total Orders", current_color)
with k4: st.info(rec_text)

st.markdown("---")

# 5. Visuals
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("🔍 Behavioral Clusters")
    fig = px.scatter(
        filtered_df, x='frequency_orders', y='monetary_profit',
        color='segment_name', color_discrete_map=segment_colors, opacity=0.7,
        hover_data=['customer_id', 'recency_days'], template="plotly_white",
        labels={"frequency_orders": "Total Orders", "monetary_profit": "Total Profit ($)", "segment_name": "Segment"}
    )
    fig.update_traces(marker=dict(size=14, line=dict(width=0)))
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("📋 Profile Stats")
    summary = filtered_df.groupby('segment_name')[['recency_days', 'frequency_orders', 'monetary_profit']].mean().reset_index()
    summary.columns = ['Segment', 'Inactive Days', 'Orders', 'Profit']
    st.dataframe(
        summary.style.format(subset=['Inactive Days', 'Orders', 'Profit'], formatter="{:.1f}").background_gradient(cmap="Blues"),
        use_container_width=True, hide_index=True
    )
    st.success(f"Action: Export {len(filtered_df)} users to CRM.")

# 6. Export
with st.expander("📥 Download Customer List"):
    st.dataframe(filtered_df[['customer_id', 'segment_name', 'recency_days', 'frequency_orders', 'monetary_profit']], use_container_width=True)