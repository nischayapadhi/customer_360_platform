import streamlit as st
import pandas as pd
import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# 1. Page Config
st.set_page_config(page_title="Customer 360 AI", layout="wide", page_icon="🛍️")

# --- CUSTOM CSS FOR KPI CARDS ---
st.markdown("""
<style>
    /* Main Background adjustments */
    .block-container {padding-top: 1rem; padding-bottom: 2rem;}
    
    /* KPI Card Style */
    div.kpi-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #333;
        text-align: center;
        margin-bottom: 10px;
    }
    div.kpi-card h3 {
        margin: 0;
        font-size: 16px;
        color: #666;
        font-weight: 600;
    }
    div.kpi-card h2 {
        margin: 5px 0;
        font-size: 28px;
        color: #333;
        font-weight: 700;
    }
    div.kpi-card p {
        margin: 0;
        font-size: 14px;
        color: #888;
    }
</style>
""", unsafe_allow_html=True)

# 2. Load Data
@st.cache_data
def load_data():
    load_dotenv()
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    
    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(connection_string)
    
    query = "SELECT * FROM customer_segments"
    df = pd.read_sql(query, engine)
    
    cluster_map = {
        0: "⚠️ At Risk",
        1: "🛒 Casual Shoppers",
        2: "🏆 VIPs",
        3: "🔄 Loyalists"
    }
    
    df['segment_name'] = df['cluster_id'].map(cluster_map)
    return df

df = load_data()

# 3. Header
st.title("🛍️ Customer 360 Intelligence Platform")
st.markdown("---")

# 4. Improved Filter (Radio Button vs Multiselect)
col_controls, col_toggle = st.columns([4, 1])

with col_toggle:
    # Toggle to switch between "Click & See" (Radio) and "Compare" (Multiselect)
    compare_mode = st.checkbox("Compare Groups")

with col_controls:
    all_segments = sorted(df['segment_name'].unique())
    
    if compare_mode:
        # Classic dropdown if they want to compare
        selected_segments = st.multiselect(
            "Select Segments:",
            options=all_segments,
            default=all_segments
        )
    else:
        # Single click buttons - Much cleaner UX!
        selected_segment = st.radio(
            "Select Segment:",
            options=all_segments,
            horizontal=True,
            label_visibility="collapsed"
        )
        selected_segments = [selected_segment]

if not selected_segments:
    st.warning("Please select a segment.")
    st.stop()

filtered_df = df[df['segment_name'].isin(selected_segments)]

# 5. NEW KPI SECTION (CSS CARDS)

avg_spend = filtered_df['monetary_profit'].mean()
avg_freq = filtered_df['frequency_orders'].mean()
total_customers = filtered_df['customer_id'].nunique()
avg_recency = filtered_df['recency_days'].mean()

# Helper function to render HTML Card
def kpi_card(title, value, subtitle, color):
    st.markdown(f"""
    <div class="kpi-card" style="border-left: 5px solid {color};">
        <h3>{title}</h3>
        <h2>{value}</h2>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

# --- LOGIC: Dynamic Colors & Action Plans ---
# 1. Define the Color Map (Used for both KPIs and Plot)
segment_colors = {
    "🏆 VIPs": "#FFD700",          # Gold
    "⚠️ At Risk": "#FC0202",        # Red
    "🔄 Loyalists": "#00FF08",      # Green
    "🛒 Casual Shoppers": "#8866E7" # Orange
}

# 2. Determine Current Selection State
if len(selected_segments) == 1:
    current_segment = selected_segments[0]
    current_color = segment_colors.get(current_segment, "#333")
    
    # 3. Specific Business Strategies
    if current_segment == "🏆 VIPs":
        rec_text = "💎 **Strategy:** Maintain exclusivity. Offer 'Early Access' to new products and a personal support line."
    elif current_segment == "⚠️ At Risk":
        rec_text = "🛑 **Strategy:** Urgent Win-Back. Send a 'We Miss You' email with a steep time-limited discount (e.g., 20%)."
    elif current_segment == "🔄 Loyalists":
        rec_text = "📢 **Strategy:** Turn into Advocates. Push a Referral Program: 'Refer a friend, get $20 store credit'."
    elif current_segment == "🛒 Casual Shoppers":
        rec_text = "📈 **Strategy:** Increase Basket Size. Use 'Bundle & Save' offers to upsell related items at checkout."
    else:
        rec_text = "🔍 **Strategy:** Monitor behavior."
else:
    # Multiple segments selected
    current_color = "#333" # Default black/grey for mixed view
    rec_text = "⚖️ **Strategy:** Compare groups to allocate budget. Focus on moving 'Casuals' -> 'Loyalists'."

st.markdown("### 📊 Performance Metrics")
k1, k2, k3, k4 = st.columns(4)

with k1: kpi_card("Customers", f"{total_customers}", "Active in segment", current_color)
with k2: kpi_card("Avg Spend", f"${avg_spend:,.0f}", "Lifetime Profit", current_color)
with k3: kpi_card("Avg Frequency", f"{avg_freq:.1f}", "Orders per Customer", current_color)
# KPI 4 is now the Action Plan Box
with k4: 
    st.info(rec_text)

# 6. Visuals
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("🔍 Behavioral Clusters")
    
    # Plotly Scatter Chart with Custom Colors
    fig = px.scatter(
        filtered_df,
        x='frequency_orders',
        y='monetary_profit',
        color='segment_name',
        color_discrete_map=segment_colors, 
        opacity=0.4,
        hover_data=['customer_id', 'recency_days'],
        title="Frequency vs. Profit (Zoom & Hover to Explore)",
        template="plotly_white",
        labels={
            "frequency_orders": "Total Orders", 
            "monetary_profit": "Total Profit ($)",
            "segment_name": "Customer Segment"
        }
    )
    
    fig.update_traces(marker=dict(size=12, line=dict(width=0)))
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("📋 Segment Profile")
    summary = filtered_df.groupby('segment_name')[['recency_days', 'frequency_orders', 'monetary_profit']].mean().reset_index()
    summary = summary.rename(columns={'recency_days': 'Inactive Days', 'frequency_orders': 'Orders', 'monetary_profit': 'Profit'})
    
    st.dataframe(
        summary.style.format(
            subset=['Inactive Days', 'Orders', 'Profit'], 
            formatter="{:.1f}"
        ).background_gradient(cmap="Blues"),
        use_container_width=True,
        hide_index=True
    )

    # Marketing Recommendation Box
    st.info(f"**Action Plan:** Export this list of **{total_customers}** users to your CRM for immediate targeting.")

# 7. Data Export
with st.expander("📥 View & Download Customer List"):
    st.dataframe(filtered_df[['customer_id', 'segment_name', 'recency_days', 'frequency_orders', 'monetary_profit']], use_container_width=True)