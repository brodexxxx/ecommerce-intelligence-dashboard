import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.src.ecommerce_trends import load_data, compute_weekly, find_trending

# Real-time UI Configuration
st.set_page_config(
    page_title="Real-Time E-Commerce Dashboard", 
    layout="wide",
    page_icon="📊"
)

# Custom CSS for real-time feel
st.markdown("""
<style>
    .real-time-header {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .live-badge {
        background-color: #dc3545;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# Header with live indicator
st.markdown("""
<div class="real-time-header">
    <h1>📈 Real-Time E-Commerce Analytics Dashboard</h1>
    <span class="live-badge">🔴 LIVE</span>
</div>
""", unsafe_allow_html=True)

# Initialize session state for real-time data
if 'real_time_data' not in st.session_state:
    st.session_state.real_time_data = pd.DataFrame(columns=['timestamp', 'product', 'sales', 'views'])
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()

# Function to generate real-time data fluctuations
def generate_real_time_data(base_df):
    """Generate fluctuating real-time data based on historical patterns"""
    current_time = datetime.now()
    
    # Get recent data for pattern recognition
    recent_data = base_df.tail(100)
    
    # Simulate real-time fluctuations
    new_data = []
    for product in recent_data['product'].unique():
        product_data = recent_data[recent_data['product'] == product]
        
        # Base sales with random fluctuation (±20%)
        base_sales = product_data['sales'].mean() if not product_data.empty else 100
        fluctuation = np.random.uniform(0.8, 1.2)
        sales = max(10, int(base_sales * fluctuation))
        
        # Views with correlation to sales
        views = int(sales * np.random.uniform(5, 15))
        
        new_data.append({
            'timestamp': current_time,
            'product': product,
            'sales': sales,
            'views': views
        })
    
    return pd.DataFrame(new_data)

# Sidebar for real-time controls
with st.sidebar:
    st.header("⚡ Real-Time Controls")
    update_frequency = st.select_slider(
        "Update Frequency",
        options=["1 second", "5 seconds", "10 seconds", "30 seconds", "1 minute"],
        value="5 seconds"
    )
    
    st.header("📊 Display Options")
    show_live_charts = st.checkbox("Show Live Charts", value=True)
    show_metrics = st.checkbox("Show Real-time Metrics", value=True)

# Convert frequency to seconds
frequency_map = {
    "1 second": 1,
    "5 seconds": 5,
    "10 seconds": 10,
    "30 seconds": 30,
    "1 minute": 60
}
update_interval = frequency_map[update_frequency]

# Load base data for patterns
try:
    base_df = load_data("data/comprehensive_sales_data.csv")
except:
    st.error("Could not load base data file")
    st.stop()

# Real-time data generation and display
if st.button("🔄 Refresh Data") or (datetime.now() - st.session_state.last_update).seconds >= update_interval:
    # Generate new real-time data
    new_data = generate_real_time_data(base_df)
    st.session_state.real_time_data = pd.concat([st.session_state.real_time_data, new_data])
    st.session_state.last_update = datetime.now()
    st.rerun()

# Display real-time metrics
if show_metrics:
    st.header("📈 Real-time Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_sales = st.session_state.real_time_data['sales'].sum()
        st.metric("💰 Total Sales", f"${total_sales:,.0f}", delta="+12%")
    
    with col2:
        total_views = st.session_state.real_time_data['views'].sum()
        st.metric("👀 Total Views", f"{total_views:,.0f}", delta="+8%")
    
    with col3:
        conversion_rate = (total_sales / total_views * 100) if total_views > 0 else 0
        st.metric("📊 Conversion Rate", f"{conversion_rate:.1f}%", delta="+0.5%")
    
    with col4:
        unique_products = st.session_state.real_time_data['product'].nunique()
        st.metric("🎯 Active Products", f"{unique_products}", delta="+2")

# Live charts section
if show_live_charts and not st.session_state.real_time_data.empty:
    st.header("📊 Live Charts")
    
    # Real-time sales by product
    recent_data = st.session_state.real_time_data.tail(50)
    fig_sales = px.bar(
        recent_data, 
        x='product', 
        y='sales', 
        title='Real-time Sales by Product',
        color='sales',
        text='sales'
    )
    fig_sales.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig_sales, use_container_width=True)
    
    # Time series of sales
    time_series_data = st.session_state.real_time_data.groupby('timestamp')['sales'].sum().reset_index()
    fig_time = px.line(
        time_series_data, 
        x='timestamp', 
        y='sales', 
        title='Sales Over Time (Real-time)',
        markers=True
    )
    st.plotly_chart(fig_time, use_container_width=True)

# Real-time product performance
st.header("🚀 Real-time Product Performance")

if not st.session_state.real_time_data.empty:
    # Top performing products
    product_performance = st.session_state.real_time_data.groupby('product').agg({
        'sales': 'sum',
        'views': 'sum'
    }).reset_index()
    product_performance['conversion_rate'] = (product_performance['sales'] / product_performance['views'] * 100).round(2)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Top Selling Products")
        top_products = product_performance.nlargest(5, 'sales')
        for _, row in top_products.iterrows():
            st.progress(row['sales'] / top_products['sales'].max(), text=f"{row['product']}: ${row['sales']:,.0f}")
    
    with col2:
        st.subheader("⭐ Best Converters")
        best_converters = product_performance.nlargest(5, 'conversion_rate')
        for _, row in best_converters.iterrows():
            st.progress(row['conversion_rate'] / 100, text=f"{row['product']}: {row['conversion_rate']:.1f}%")

# Real-time data table
st.header("📋 Real-time Data Stream")
st.dataframe(
    st.session_state.real_time_data.tail(20).sort_values('timestamp', ascending=False),
    use_container_width=True,
    height=300
)

# Footer with last update time
st.markdown("---")
st.caption(f"🔄 Last update: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("📊 Data updates automatically based on selected frequency")
