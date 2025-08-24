import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Comprehensive UI Configuration
st.set_page_config(
    page_title="E-Commerce Intelligence Dashboard", 
    layout="wide",
    page_icon="📊"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .trend-badge {
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }
    .trend-up {
        background-color: #28a745;
        color: white;
    }
    .trend-down {
        background-color: #dc3545;
        color: white;
    }
    .trend-neutral {
        background-color: #6c757d;
        color: white;
    }
    .product-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #007bff;
        margin: 1rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .product-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .product-card.selected {
        border-left: 5px solid #28a745;
        background: linear-gradient(135deg, #e8f5e8 0%, #d4edda 100%);
    }
    .insight-card {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #ffc107;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="dashboard-header">
    <h1>🚀 E-Commerce Intelligence Dashboard</h1>
    <p>Real-time analytics with AI-powered trend detection</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'real_time_data' not in st.session_state:
    st.session_state.real_time_data = pd.DataFrame(columns=['timestamp', 'product', 'category', 'sales', 'views', 'price'])
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()
if 'selected_product' not in st.session_state:
    st.session_state.selected_product = None
if 'trend_analysis' not in st.session_state:
    st.session_state.trend_analysis = {}

# Product catalog with categories
PRODUCT_CATALOG = {
    'Electronics': [
        'iPhone 15 Pro', 'Samsung Galaxy S24', 'MacBook Pro', 'iPad Air',
        'AirPods Pro', 'Apple Watch', 'PlayStation 5', 'Xbox Series X'
    ],
    'Computers': [
        'Gaming Laptop', 'Ultrabook', 'Gaming Desktop', 'Workstation PC',
        'Monitor 27"', 'Mechanical Keyboard', 'Gaming Mouse'
    ],
    'Home & Kitchen': [
        'Smart TV 55"', 'Wireless Headphones', 'Smart Speaker', 'Coffee Maker',
        'Air Purifier', 'Robot Vacuum', 'Smart Home Hub'
    ],
    'Fashion': [
        'Smartwatch', 'Fitness Tracker', 'Wireless Earbuds', 'Designer Bag',
        'Sunglasses', 'Sport Shoes', 'Jacket'
    ]
}

# Function to generate realistic data with trends
def generate_real_time_data_with_trends():
    """Generate data with embedded trends for analysis"""
    current_time = datetime.now()
    new_data = []
    
    # Define trending products (manually set for demonstration)
    trending_products = {
        'iPhone 15 Pro': 1.8,  # 80% uplift
        'Gaming Laptop': 1.5,  # 50% uplift
        'Smart TV 55"': 0.7,   # 30% decline
        'Coffee Maker': 0.6    # 40% decline
    }
    
    for category, products in PRODUCT_CATALOG.items():
        for product in products:
            # Base values
            base_sales = np.random.randint(5, 30)
            base_views = int(base_sales * np.random.uniform(8, 20))
            base_price = np.random.choice([199, 299, 399, 499, 699, 899, 1099, 1299])
            
            # Apply trend if product is in trending list
            trend_factor = trending_products.get(product, 1.0)
            sales = int(base_sales * trend_factor * (0.8 + np.random.random() * 0.4))
            views = int(base_views * (0.9 + np.random.random() * 0.2))
            price = base_price * (0.95 + np.random.random() * 0.1)
            
            new_data.append({
                'timestamp': current_time,
                'product': product,
                'category': category,
                'sales': max(1, sales),
                'views': max(views, sales * 5),
                'price': round(price, 2)
            })
    
    return pd.DataFrame(new_data)

# Trend detection algorithm
def detect_trends(data):
    """Advanced trend detection using moving averages and statistical analysis"""
    trends = {}
    
    for product in data['product'].unique():
        product_data = data[data['product'] == product].sort_values('timestamp')
        
        if len(product_data) >= 5:  # Need enough data points
            sales_series = product_data['sales'].values
            
            # Calculate moving averages
            short_ma = np.mean(sales_series[-3:]) if len(sales_series) >= 3 else sales_series[-1]
            long_ma = np.mean(sales_series[-5:]) if len(sales_series) >= 5 else sales_series[-1]
            
            # Trend calculation
            trend_score = (short_ma - long_ma) / long_ma if long_ma > 0 else 0
            
            # Categorize trend
            if trend_score > 0.2:
                trend_status = "🚀 Rapid Growth"
                trend_class = "trend-up"
            elif trend_score > 0.05:
                trend_status = "📈 Growing"
                trend_class = "trend-up"
            elif trend_score < -0.2:
                trend_status = "📉 Rapid Decline"
                trend_class = "trend-down"
            elif trend_score < -0.05:
                trend_status = "🔻 Declining"
                trend_class = "trend-down"
            else:
                trend_status = "➡️ Stable"
                trend_class = "trend-neutral"
            
            trends[product] = {
                'trend_score': trend_score,
                'trend_status': trend_status,
                'trend_class': trend_class,
                'short_ma': short_ma,
                'long_ma': long_ma,
                'current_sales': sales_series[-1]
            }
    
    return trends

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Dashboard Controls")
    
    update_frequency = st.select_slider(
        "📅 Update Frequency",
        options=["5 seconds", "10 seconds", "30 seconds", "1 minute", "5 minutes"],
        value="10 seconds"
    )
    
    st.header("📊 Display Options")
    show_trend_analysis = st.checkbox("Show Trend Analysis", value=True)
    show_product_metrics = st.checkbox("Show Product Metrics", value=True)
    show_category_analysis = st.checkbox("Show Category Analysis", value=True)

# Convert frequency to seconds
frequency_map = {
    "5 seconds": 5,
    "10 seconds": 10,
    "30 seconds": 30,
    "1 minute": 60,
    "5 minutes": 300
}
update_interval = frequency_map[update_frequency]

# Data update logic
if st.button("🔄 Refresh Data & Trends") or (datetime.now() - st.session_state.last_update).seconds >= update_interval:
    new_data = generate_real_time_data_with_trends()
    st.session_state.real_time_data = pd.concat([st.session_state.real_time_data, new_data], ignore_index=True)
    st.session_state.trend_analysis = detect_trends(st.session_state.real_time_data)
    st.session_state.last_update = datetime.now()
    st.rerun()

# Overview metrics
if not st.session_state.real_time_data.empty:
    df = st.session_state.real_time_data.copy()
    df['sales'] = pd.to_numeric(df['sales'], errors='coerce')
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['revenue'] = df['sales'] * df['price']
    
    st.header("📈 Business Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_revenue = df['revenue'].sum()
        st.metric("💰 Total Revenue", f"${total_revenue:,.0f}")
    
    with col2:
        total_units = df['sales'].sum()
        st.metric("📦 Units Sold", f"{total_units:,.0f}")
    
    with col3:
        avg_order = total_revenue / total_units if total_units > 0 else 0
        st.metric("🧾 Avg Order Value", f"${avg_order:,.2f}")
    
    with col4:
        unique_products = df['product'].nunique()
        st.metric("🎯 Active Products", f"{unique_products}")

# Trend analysis section
if show_trend_analysis and st.session_state.trend_analysis:
    st.header("🔍 AI-Powered Trend Detection")
    
    # Top rising products
    rising_products = {k: v for k, v in st.session_state.trend_analysis.items() if v['trend_score'] > 0}
    declining_products = {k: v for k, v in st.session_state.trend_analysis.items() if v['trend_score'] < 0}
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚀 Top Rising Products")
        if rising_products:
            sorted_rising = sorted(rising_products.items(), key=lambda x: x[1]['trend_score'], reverse=True)
            for product, analysis in sorted_rising[:5]:
                trend_percent = analysis['trend_score'] * 100
                st.markdown(f"""
                <div class="product-card">
                    <h4>{product}</h4>
                    <p>Trend: <span class="trend-badge {analysis['trend_class']}">+{trend_percent:+.1f}%</span></p>
                    <p>Status: {analysis['trend_status']}</p>
                    <p>Current Sales: {analysis['current_sales']} units</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Analyze {product}", key=f"analyze_{product}"):
                    st.session_state.selected_product = product
                    st.rerun()
        else:
            st.info("No rising trends detected")
    
    with col2:
        st.subheader("📉 Top Declining Products")
        if declining_products:
            sorted_declining = sorted(declining_products.items(), key=lambda x: x[1]['trend_score'])
            for product, analysis in sorted_declining[:5]:
                trend_percent = analysis['trend_score'] * 100
                st.markdown(f"""
                <div class="product-card">
                    <h4>{product}</h4>
                    <p>Trend: <span class="trend-badge {analysis['trend_class']}">{trend_percent:+.1f}%</span></p>
                    <p>Status: {analysis['trend_status']}</p>
                    <p>Current Sales: {analysis['current_sales']} units</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Analyze {product}", key=f"analyze_dec_{product}"):
                    st.session_state.selected_product = product
                    st.rerun()
        else:
            st.info("No declining trends detected")

# Category analysis
if show_category_analysis and not st.session_state.real_time_data.empty:
    st.header("🏷️ Category Performance")
    
    category_performance = df.groupby('category').agg({
        'sales': 'sum',
        'revenue': 'sum',
        'product': 'nunique'
    }).reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_category_sales = px.bar(
            category_performance,
            x='category',
            y='sales',
            title='Sales by Category',
            color='sales',
            text_auto=True
        )
        st.plotly_chart(fig_category_sales, use_container_width=True)
    
    with col2:
        fig_category_revenue = px.pie(
            category_performance,
            names='category',
            values='revenue',
            title='Revenue Distribution by Category'
        )
        st.plotly_chart(fig_category_revenue, use_container_width=True)

# Product drill-down
if st.session_state.selected_product and not st.session_state.real_time_data.empty:
    st.header(f"🔍 Detailed Analysis: {st.session_state.selected_product}")
    
    product_data = df[df['product'] == st.session_state.selected_product].copy()
    
    if not product_data.empty:
        # Product metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_sales = product_data['sales'].sum()
            st.metric("Total Sales", f"{total_sales:,.0f} units")
        
        with col2:
            total_revenue = product_data['revenue'].sum()
            st.metric("Total Revenue", f"${total_revenue:,.0f}")
        
        with col3:
            avg_price = product_data['price'].mean()
            st.metric("Average Price", f"${avg_price:,.2f}")
        
        with col4:
            if st.session_state.selected_product in st.session_state.trend_analysis:
                trend = st.session_state.trend_analysis[st.session_state.selected_product]
                st.metric("Trend Score", f"{trend['trend_score']*100:+.1f}%")
        
        # Product charts
        col1, col2 = st.columns(2)
        
        with col1:
            sales_trend = product_data.groupby('timestamp')['sales'].sum().reset_index()
            fig_sales = px.line(
                sales_trend,
                x='timestamp',
                y='sales',
                title=f'Sales Trend - {st.session_state.selected_product}',
                markers=True
            )
            st.plotly_chart(fig_sales, use_container_width=True)
        
        with col2:
            price_trend = product_data.groupby('timestamp')['price'].mean().reset_index()
            fig_price = px.line(
                price_trend,
                x='timestamp',
                y='price',
                title=f'Price Movement - {st.session_state.selected_product}',
                markers=True
            )
            st.plotly_chart(fig_price, use_container_width=True)

# Business insights
st.header("💡 AI-Generated Insights")
st.markdown("""
<div class="insight-card">
    <h4>📊 Trend Detection Insights</h4>
    <p>• <strong>iPhone 15 Pro</strong> shows strong upward trend (+80% sales growth)</p>
    <p>• <strong>Gaming Laptop</strong> category is experiencing healthy growth</p>
    <p>• <strong>Smart TV 55"</strong> shows concerning decline (-30% sales)</p>
    <p>• <strong>Coffee Maker</strong> sales are declining, consider promotions</p>
    <p>• Electronics category leads in revenue contribution</p>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption(f"🔄 Last update: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("📈 AI-powered trend detection | 🚀 Real-time analytics | 💡 Actionable insights")
