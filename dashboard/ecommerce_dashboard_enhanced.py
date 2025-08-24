import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.src.ecommerce_trends import load_data, compute_weekly, find_trending

# Enhanced UI Configuration
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard", 
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .trend-up {
        color: #28a745;
        font-weight: bold;
    }
    .trend-down {
        color: #dc3545;
        font-weight: bold;
    }
    .prediction-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">📈 E-Commerce Analytics Dashboard</h1>', unsafe_allow_html=True)

# Sidebar with enhanced options
with st.sidebar:
    st.header("📁 Data Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        use_sample = st.checkbox("Use Sample Data", value=True, help="Use pre-loaded sample data for demonstration")
    with col2:
        show_predictions = st.checkbox("Enable Predictions", value=True, help="Show predictive analytics")
    
    file = st.file_uploader("📤 Upload Custom CSV", type=["csv"], 
                          help="Upload your own sales data in CSV format")
    
    st.header("⚙️ Analysis Settings")
    prediction_days = st.slider("Prediction Horizon (days)", 7, 90, 30, 
                              help="Number of days to predict into the future")
    
    confidence_level = st.slider("Confidence Level", 80, 99, 90,
                               help="Confidence interval for predictions")
    
    st.header("📊 Display Options")
    show_raw_data = st.checkbox("Show Raw Data", value=False)
    show_weekly_data = st.checkbox("Show Weekly Aggregations", value=True)

# Data loading and validation
if not file and not use_sample:
    st.info("📋 Please upload a CSV file or enable 'Use Sample Data' to begin analysis.")
    st.stop()

# Load data
try:
    path_or_file = file if file else "data/comprehensive_sales_data.csv"
    df = load_data(path_or_file)
    
    # Calculate basic metrics for dashboard
    total_sales = df['sales'].sum()
    total_views = df['views'].sum()
    conversion_rate = (total_sales / total_views * 100) if total_views > 0 else 0
    unique_products = df['product'].nunique()
    
except Exception as e:
    st.error(f"❌ Error loading data: {str(e)}")
    st.stop()

# Enhanced predictive analytics function
def predict_sales_trends(weekly_data, days_to_predict=30, confidence=0.9):
    """Enhanced prediction using simple exponential smoothing with confidence intervals"""
    predictions = {}
    
    for product in weekly_data['product'].unique():
        product_data = weekly_data[weekly_data['product'] == product].sort_values('week')
        
        if len(product_data) >= 4:  # Minimum data points for prediction
            sales_series = product_data['sales'].values
            
            # Simple exponential smoothing prediction
            alpha = 0.3
            predictions_list = []
            last_value = sales_series[-1]
            
            for _ in range(days_to_predict // 7):  # Convert days to weeks
                next_pred = alpha * last_value + (1 - alpha) * (last_value if not predictions_list else predictions_list[-1])
                predictions_list.append(next_pred)
                last_value = next_pred
            
            # Calculate confidence intervals
            std_dev = np.std(sales_series[-4:]) if len(sales_series) >= 4 else sales_series.std()
            upper_bound = [p + (std_dev * (1 - confidence)) for p in predictions_list]
            lower_bound = [p - (std_dev * (1 - confidence)) for p in predictions_list]
            
            predictions[product] = {
                'predictions': predictions_list,
                'upper_bound': upper_bound,
                'lower_bound': lower_bound,
                'confidence': confidence
            }
    
    return predictions

# Main dashboard layout
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h3>💰 Total Sales</h3>
        <h2>${total_sales:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <h3>👀 Total Views</h3>
        <h2>{total_views:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <h3>📊 Conversion Rate</h3>
        <h2>{conversion_rate:.1f}%</h2>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <h3>🎯 Products</h3>
        <h2>{unique_products}</h2>
    </div>
    """, unsafe_allow_html=True)

# Data processing
weekly = compute_weekly(df)
top_up, top_down = find_trending(weekly)

# Prediction section
if show_predictions:
    st.markdown("---")
    st.header("🔮 Predictive Analytics")
    
    predictions = predict_sales_trends(weekly, prediction_days, confidence_level/100)
    
    if predictions:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="prediction-card">', unsafe_allow_html=True)
            st.subheader("📈 Top Predicted Growth")
            for product, data in list(predictions.items())[:3]:
                growth = ((data['predictions'][-1] - data['predictions'][0]) / data['predictions'][0] * 100)
                st.write(f"**{product}**: {growth:+.1f}% expected growth")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="prediction-card">', unsafe_allow_html=True)
            st.subheader("🎯 Prediction Confidence")
            st.write(f"**Confidence Level**: {confidence_level}%")
            st.write(f"**Horizon**: {prediction_days} days")
            st.write("**Method**: Exponential Smoothing")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Interactive prediction chart
        selected_product = st.selectbox("Select Product for Detailed Prediction", 
                                      options=list(predictions.keys()))
        
        if selected_product:
            product_data = predictions[selected_product]
            fig = go.Figure()
            
            # Add historical data
            hist_data = weekly[weekly['product'] == selected_product].sort_values('week')
            fig.add_trace(go.Scatter(
                x=hist_data['week'], 
                y=hist_data['sales'],
                name='Historical Sales',
                line=dict(color='#1f77b4', width=3)
            ))
            
            # Add predictions
            future_weeks = [f"Week {i+1}" for i in range(len(product_data['predictions']))]
            fig.add_trace(go.Scatter(
                x=future_weeks,
                y=product_data['predictions'],
                name='Predicted Sales',
                line=dict(color='#ff7f0e', width=3, dash='dash')
            ))
            
            # Add confidence interval
            fig.add_trace(go.Scatter(
                x=future_weeks + future_weeks[::-1],
                y=product_data['upper_bound'] + product_data['lower_bound'][::-1],
                fill='toself',
                fillcolor='rgba(255, 127, 14, 0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                name=f'{confidence_level}% Confidence'
            ))
            
            fig.update_layout(
                title=f"Sales Prediction for {selected_product}",
                xaxis_title="Time",
                yaxis_title="Sales",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)

# Trending products section
st.markdown("---")
st.header("📊 Real-time Trends")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🚀 Top Rising Products")
    if not top_up.empty:
        for _, row in top_up.head(5).iterrows():
            trend_icon = "📈" if row['trend_score'] > 0 else "📉"
            trend_class = "trend-up" if row['trend_score'] > 0 else "trend-down"
            st.markdown(f"""
            <div class="metric-card">
                <h4>{trend_icon} {row['product']}</h4>
                <p>Sales: <strong>${row['sales']:,.0f}</strong></p>
                <p>Trend: <span class="{trend_class}">{row['trend_score']:+.2f}</span></p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No rising trends detected")

with col2:
    st.subheader("📉 Top Falling Products")
    if not top_down.empty:
        for _, row in top_down.head(5).iterrows():
            trend_icon = "📈" if row['trend_score'] > 0 else "📉"
            trend_class = "trend-up" if row['trend_score'] > 0 else "trend-down"
            st.markdown(f"""
            <div class="metric-card">
                <h4>{trend_icon} {row['product']}</h4>
                <p>Sales: <strong>${row['sales']:,.0f}</strong></p>
                <p>Trend: <span class="{trend_class}">{row['trend_score']:+.2f}</span></p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No falling trends detected")

# Data exploration section
if show_raw_data:
    st.markdown("---")
    st.header("📋 Raw Data Overview")
    st.dataframe(df.head(50), use_container_width=True, height=300)

if show_weekly_data:
    st.markdown("---")
    st.header("📅 Weekly Aggregations")
    st.dataframe(weekly.head(50), use_container_width=True, height=300)

# Product analysis section
st.markdown("---")
st.header("🔍 Product Analysis")

products = sorted(weekly["product"].unique().tolist())
selected_product = st.selectbox("Select Product for Detailed Analysis", options=products)

if selected_product:
    product_data = weekly[weekly["product"] == selected_product].sort_values("week")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Sales trend chart
        fig_sales = px.line(product_data, x="week", y="sales", 
                          title=f"{selected_product} - Sales Trend",
                          markers=True)
        fig_sales.update_traces(line=dict(width=3))
        st.plotly_chart(fig_sales, use_container_width=True)
    
    with col2:
        # Conversion rate chart
        fig_conversion = px.line(product_data, x="week", y="view_to_purchase",
                               title=f"{selected_product} - Conversion Rate",
                               markers=True)
        fig_conversion.update_traces(line=dict(width=3, color='#2ca02c'))
        st.plotly_chart(fig_conversion, use_container_width=True)

# Export functionality
st.markdown("---")
st.header("💾 Export Results")

col1, col2 = st.columns(2)

with col1:
    st.download_button(
        "📥 Download Weekly Data (CSV)",
        data=weekly.to_csv(index=False),
        file_name="weekly_ecommerce_data.csv",
        mime="text/csv",
        help="Download the aggregated weekly data"
    )

with col2:
    if predictions:
        prediction_df = pd.DataFrame([
            {
                'product': product,
                'predicted_sales': data['predictions'][-1],
                'growth_percentage': ((data['predictions'][-1] - data['predictions'][0]) / data['predictions'][0] * 100),
                'confidence_level': f"{data['confidence']*100:.0f}%"
            }
            for product, data in predictions.items()
        ])
        
        st.download_button(
            "📊 Download Predictions (CSV)",
            data=prediction_df.to_csv(index=False),
            file_name="sales_predictions.csv",
            mime="text/csv",
            help="Download the sales predictions data"
        )

# Footer
st.markdown("---")
st.caption("🔄 Data updated automatically | 📧 Support: analytics@ecommerce.com")
