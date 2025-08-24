import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Real-time UI Configuration
st.set_page_config(
    page_title="Product Analytics Dashboard", 
    layout="wide",
    page_icon="📊"
)

# Custom CSS for enhanced styling
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
    .product-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #007bff;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: transform 0.2s;
    }
    .product-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .product-card.selected {
        border-left: 4px solid #28a745;
        background: linear-gradient(135deg, #e8f5e8 0%, #d4edda 100%);
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
    <h1>📈 Product Analytics Dashboard</h1>
    <span class="live-badge">🔴 LIVE PRODUCT VIEW</span>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'real_time_data' not in st.session_state:
    st.session_state.real_time_data = pd.DataFrame(columns=['timestamp', 'product', 'sales', 'views', 'price'])
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()
if 'selected_product' not in st.session_state:
    st.session_state.selected_product = None

# Function to generate real-time data with more products
def generate_real_time_data():
    """Generate fluctuating real-time data for multiple products"""
    current_time = datetime.now()
    products = [
        'iPhone 15 Pro', 'Samsung Galaxy S24', 'MacBook Pro', 'iPad Air',
        'AirPods Pro', 'Apple Watch', 'PlayStation 5', 'Xbox Series X',
        'Nintendo Switch', 'Smart TV 55"', 'Wireless Headphones', 'Gaming Laptop'
    ]
    
    new_data = []
    for product in products:
        # Generate realistic product data
        base_price = np.random.choice([299, 399, 499, 699, 899, 1099, 1299])
        sales = np.random.randint(1, 50)
        views = int(sales * np.random.uniform(5, 15))
        price = base_price * (0.9 + np.random.random() * 0.2)  # Price fluctuations
        
        new_data.append({
            'timestamp': current_time,
            'product': product,
            'sales': sales,
            'views': views,
            'price': round(price, 2)
        })
    
    return pd.DataFrame(new_data)

# Sidebar for controls
with st.sidebar:
    st.header("⚡ Dashboard Controls")
    update_frequency = st.select_slider(
        "Update Frequency",
        options=["3 seconds", "5 seconds", "10 seconds", "30 seconds", "1 minute"],
        value="5 seconds"
    )
    
    st.header("📊 Display Options")
    show_overview = st.checkbox("Show Overview Metrics", value=True)
    show_product_grid = st.checkbox("Show Product Grid", value=True)
    show_detailed_view = st.checkbox("Show Detailed Product View", value=True)

# Convert frequency to seconds
frequency_map = {
    "3 seconds": 3,
    "5 seconds": 5,
    "10 seconds": 10,
    "30 seconds": 30,
    "1 minute": 60
}
update_interval = frequency_map[update_frequency]

# Real-time data update
if st.button("🔄 Refresh All Data") or (datetime.now() - st.session_state.last_update).seconds >= update_interval:
    new_data = generate_real_time_data()
    st.session_state.real_time_data = pd.concat([st.session_state.real_time_data, new_data], ignore_index=True)
    st.session_state.last_update = datetime.now()
    st.rerun()

# Overview metrics
if show_overview and not st.session_state.real_time_data.empty:
    st.header("📈 Overview Metrics")
    
    df = st.session_state.real_time_data.copy()
    df['sales'] = pd.to_numeric(df['sales'], errors='coerce')
    df['views'] = pd.to_numeric(df['views'], errors='coerce')
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_sales = df['sales'].sum()
        revenue = (df['sales'] * df['price']).sum()
        st.metric("💰 Total Revenue", f"${revenue:,.0f}", delta=f"+{np.random.randint(5, 15)}%")
    
    with col2:
        total_views = df['views'].sum()
        st.metric("👀 Total Views", f"{total_views:,.0f}", delta=f"+{np.random.randint(3, 10)}%")
    
    with col3:
        conversion_rate = (total_sales / total_views * 100) if total_views > 0 else 0
        st.metric("📊 Conversion Rate", f"{conversion_rate:.1f}%", delta=f"+{np.random.uniform(0.1, 1.5):.1f}%")
    
    with col4:
        unique_products = df['product'].nunique()
        st.metric("🎯 Active Products", f"{unique_products}", delta=f"+{np.random.randint(1, 3)}")

# Product grid with clickable cards
if show_product_grid and not st.session_state.real_time_data.empty:
    st.header("🛍️ Product Portfolio")
    
    df = st.session_state.real_time_data.copy()
    df['sales'] = pd.to_numeric(df['sales'], errors='coerce')
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    
    # Get latest data for each product
    latest_data = df.sort_values('timestamp').groupby('product').tail(1)
    
    # Create product cards in a grid
    cols = st.columns(4)
    for idx, (_, row) in enumerate(latest_data.iterrows()):
        col_idx = idx % 4
        with cols[col_idx]:
            is_selected = st.session_state.selected_product == row['product']
            card_class = "product-card selected" if is_selected else "product-card"
            
            st.markdown(f"""
            <div class="{card_class}" onclick="window.streamlit.setComponentValue('{row['product']}')">
                <h4>📦 {row['product']}</h4>
                <p><strong>Sales:</strong> {int(row['sales'])} units</p>
                <p><strong>Price:</strong> ${row['price']:,.2f}</p>
                <p><strong>Revenue:</strong> ${row['sales'] * row['price']:,.0f}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Add click handler using Streamlit's experimental feature
            if st.button(f"Select {row['product']}", key=f"btn_{row['product']}"):
                st.session_state.selected_product = row['product']
                st.rerun()

# Detailed product view
if show_detailed_view and st.session_state.selected_product and not st.session_state.real_time_data.empty:
    st.header(f"🔍 Detailed Analysis: {st.session_state.selected_product}")
    
    df = st.session_state.real_time_data.copy()
    product_data = df[df['product'] == st.session_state.selected_product].copy()
    product_data['sales'] = pd.to_numeric(product_data['sales'], errors='coerce')
    product_data['views'] = pd.to_numeric(product_data['views'], errors='coerce')
    product_data['price'] = pd.to_numeric(product_data['price'], errors='coerce')
    product_data['revenue'] = product_data['sales'] * product_data['price']
    
    if not product_data.empty:
        # Product metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_sales = product_data['sales'].sum()
            st.metric("Total Sales", f"{total_sales:,.0f} units")
        
        with col2:
            avg_price = product_data['price'].mean()
            st.metric("Avg Price", f"${avg_price:,.2f}")
        
        with col3:
            total_revenue = product_data['revenue'].sum()
            st.metric("Total Revenue", f"${total_revenue:,.0f}")
        
        with col4:
            conversion_rate = (product_data['sales'].sum() / product_data['views'].sum() * 100) if product_data['views'].sum() > 0 else 0
            st.metric("Conversion Rate", f"{conversion_rate:.1f}%")
        
        # Product charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Sales trend
            sales_trend = product_data.groupby('timestamp')['sales'].sum().reset_index()
            fig_sales = px.line(
                sales_trend, 
                x='timestamp', 
                y='sales', 
                title=f'{st.session_state.selected_product} - Sales Trend',
                markers=True
            )
            st.plotly_chart(fig_sales, use_container_width=True)
        
        with col2:
            # Price movement
            price_trend = product_data.groupby('timestamp')['price'].mean().reset_index()
            fig_price = px.line(
                price_trend, 
                x='timestamp', 
                y='price', 
                title=f'{st.session_state.selected_product} - Price Movement',
                markers=True,
                line_shape='spline'
            )
            st.plotly_chart(fig_price, use_container_width=True)
        
        # Additional analytics
        st.subheader("📊 Performance Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Sales distribution
            fig_dist = px.histogram(
                product_data, 
                x='sales', 
                title='Sales Distribution',
                nbins=10
            )
            st.plotly_chart(fig_dist, use_container_width=True)
        
        with col2:
            # Revenue by time
            revenue_trend = product_data.groupby('timestamp')['revenue'].sum().reset_index()
            fig_revenue = px.area(
                revenue_trend, 
                x='timestamp', 
                y='revenue', 
                title='Revenue Over Time',
                color_discrete_sequence=['#00cc96']
            )
            st.plotly_chart(fig_revenue, use_container_width=True)
        
        # Raw data for selected product
        st.subheader("📋 Product Data Stream")
        st.dataframe(
            product_data.sort_values('timestamp', ascending=False).head(20),
            use_container_width=True,
            height=300
        )

# Footer
st.markdown("---")
st.caption(f"🔄 Last update: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("📊 Click on any product card to view detailed analytics")
