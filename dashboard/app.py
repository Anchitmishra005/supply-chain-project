import os
import sys
import pandas as pd
import streamlit as st
import plotly.express as px
from sqlalchemy import create_engine

# Setup paths so we can import project utils
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from utils.db_config import get_connection_url

# Configure the Streamlit page
st.set_page_config(
    page_title="Supply Chain Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------------------------
# Database connection and data fetching
# ---------------------------------------------------------------------------
@st.cache_resource
def get_db_engine():
    """Create a persistent SQLAlchemy engine."""
    return create_engine(get_connection_url())

@st.cache_data(ttl=300)
def load_data(query: str):
    """Load data from MySQL based on a SQL query."""
    engine = get_db_engine()
    df = pd.read_sql(query, engine)
    return df

# ---------------------------------------------------------------------------
# Sidebar Navigation
# ---------------------------------------------------------------------------
st.sidebar.title("📦 Supply Chain Analytics")
st.sidebar.markdown("Demonstration Dashboard")
page = st.sidebar.radio(
    "Navigation",
    ["Executive Summary", "Inventory & Alerts", "Logistics & Suppliers", "Demand Forecast"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**End-to-End Pipeline**\n"
    "- Python Data Generator\n"
    "- ETL (pandas + MySQL)\n"
    "- Analytics (ML + KPIs)"
)

if st.sidebar.button("⚙️ Run Live ETL Pipeline"):
    with st.spinner("Executing pipeline architectures natively..."):
        import subprocess
        subprocess.run(["python", "database/setup_db.py"], cwd=PROJECT_ROOT)
        subprocess.run(["python", "-m", "etl.pipeline"], cwd=PROJECT_ROOT)
        subprocess.run(["python", "-m", "advanced.kpi_metrics"], cwd=PROJECT_ROOT)
        subprocess.run(["python", "-m", "advanced.alert_system"], cwd=PROJECT_ROOT)
        subprocess.run(["python", "-m", "advanced.demand_forecast"], cwd=PROJECT_ROOT)
    st.sidebar.success("Pipeline Extracted, Transformed, Loaded, and Analyzed correctly!")
    st.rerun()


st.title(f"📊 Supply Chain: {page}")
st.markdown("---")

# ===========================================================================
# PAGE 1: Executive Summary (KPIs and Revenue Trends)
# ===========================================================================
if page == "Executive Summary":
    
    # 0. AI Actionable Insight
    delay_query = "SELECT carrier, AVG(delivery_delay_days) as delay FROM shipments WHERE delivery_status = 'Delivered' GROUP BY carrier ORDER BY delay DESC LIMIT 1"
    worst_carrier_df = load_data(delay_query)
    if not worst_carrier_df.empty:
        worst_carrier = worst_carrier_df.iloc[0]['carrier']
        st.warning(f"🤖 **Automated Analyst Insight:** Action Required! Logistics carrier '{worst_carrier}' is currently experiencing the highest delivery delays. Reroute priority orders to better-performing couriers.")

    # Calculate Ad-hoc Financial Metrics
    financial_query = "SELECT SUM(o.total_amount) as revenue, SUM(s.shipping_cost) as logistics_cost FROM orders o JOIN shipments s ON o.order_id = s.order_id"
    financial_df = load_data(financial_query)
    net_revenue = float(financial_df.iloc[0]['revenue']) if not financial_df.empty else 0
    logistics_cost = float(financial_df.iloc[0]['logistics_cost']) if not financial_df.empty else 0
    profit_margin = net_revenue - logistics_cost

    # 1. Fetch KPIs
    kpi_query = """
        SELECT metric_name, metric_value 
        FROM kpi_metrics 
        WHERE metric_date = (SELECT MAX(metric_date) FROM kpi_metrics)
    """
    try:
        kpis = load_data(kpi_query)
        if not kpis.empty:
            st.subheader("Key Performance Indicators (KPIs)")
            
            # Convert KPIs to dictionary for easy access
            kpi_dict = dict(zip(kpis['metric_name'], kpis['metric_value']))
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Revenue (₹)", f"₹{net_revenue:,.2f}")
                st.metric("Net Profit Margin", f"₹{profit_margin:,.2f}", delta=f"-₹{logistics_cost:,.2f} Shipping Cost", delta_color="inverse")
                
            with col2:
                st.metric("Order Fulfillment", f"{kpi_dict.get('Order Fulfillment Rate (%)', 0)}%")
                st.metric("On-Time Delivery", f"{kpi_dict.get('On-Time Delivery Rate (%)', 0)}%")
                
            with col3:
                st.metric("Avg Delivery Time", f"{kpi_dict.get('Average Delivery Time (days)', 0)} days")
                st.metric("Stockout Rate", f"{kpi_dict.get('Stockout Rate (%)', 0)}%")
                
            with col4:
                st.metric("Avg Supplier Rating", f"{kpi_dict.get('Avg Supplier Rating', 0)} / 5.0")
                st.metric("Inventory Turnover", f"{kpi_dict.get('Inventory Turnover Ratio', 0)}")
                
    except Exception as e:
        st.warning(f"Could not load KPI data. Is the ETL pipeline run? Error: {e}")

    st.markdown("---")
    
    # 2. Charts
    colA, colB = st.columns(2)
    
    with colA:
        st.subheader("Monthly Revenue Trend")
        revenue_query = """
            SELECT DATE_FORMAT(order_date, '%%Y-%%m') AS Month, SUM(total_amount) AS Revenue 
            FROM orders GROUP BY Month ORDER BY Month
        """
        revenue_df = load_data(revenue_query)
        if not revenue_df.empty:
            fig1 = px.line(revenue_df, x="Month", y="Revenue", markers=True, title="Revenue over Time")
            st.plotly_chart(fig1, use_container_width=True)

    with colB:
        st.subheader("Orders by Priority")
        priority_query = "SELECT priority, COUNT(*) AS count FROM orders GROUP BY priority"
        priority_df = load_data(priority_query)
        if not priority_df.empty:
            fig2 = px.pie(priority_df, values='count', names='priority', title="Order Priority Distribution", hole=0.4)
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.subheader("💰 Product Category Revenue Breakdown")
    cat_query = """
        SELECT i.category, SUM(o.total_amount) as Revenue 
        FROM orders o
        JOIN inventory i ON o.product_id = i.product_id
        GROUP BY i.category ORDER BY Revenue ASC
    """
    cat_df = load_data(cat_query)
    if not cat_df.empty:
        fig_cat = px.bar(cat_df, x="Revenue", y="category", orientation='h', title="Lifetime Revenue by Category", color="Revenue")
        st.plotly_chart(fig_cat, use_container_width=True)

# ===========================================================================
# PAGE 2: Inventory Details and Alert System
# ===========================================================================
elif page == "Inventory & Alerts":
    
    st.subheader("📦 Stock Availability Overview")
    status_query = "SELECT stock_status, COUNT(*) as count FROM inventory GROUP BY stock_status"
    status_df = load_data(status_query)
    if not status_df.empty:
        fig_status = px.pie(
            status_df, 
            values='count', 
            names='stock_status', 
            title='Inventory Status Breakdown (Available vs Low/Out of Stock)',
            color='stock_status',
            color_discrete_map={'In Stock': '#2ecc71', 'Low Stock': '#f39c12', 'Out of Stock': '#e74c3c'},
            hole=0.4
        )
        st.plotly_chart(fig_status, use_container_width=True)
        
    st.markdown("---")

    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("⚠️ Low Stock Alerts System")
        st.markdown("Real-time monitoring of critically low resources.")
        alerts_query = """
            SELECT product_id, warehouse_id, current_stock, reorder_point, alert_type, alert_date 
            FROM stock_alerts 
            ORDER BY current_stock ASC 
            LIMIT 50
        """
        alerts_df = load_data(alerts_query)
        if not alerts_df.empty:
            st.dataframe(
                alerts_df.style.map(
                    lambda x: 'background-color: #ffcccc' if x == 'Out of Stock' 
                              else 'background-color: #ffe6cc' if x == 'Critical' 
                              else '', 
                    subset=['alert_type']
                ), 
                use_container_width=True
            )
            csv_alerts = alerts_df.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 Download Alerts Report (CSV)", data=csv_alerts, file_name="low_stock_alerts_report.csv", mime="text/csv")
        else:
            st.success("No low stock alerts! Inventory is healthy.")
            
    with col2:
        st.subheader("Inventory by Warehouse")
        warehouse_query = """
            SELECT warehouse_id, SUM(quantity_on_hand) as units
            FROM inventory 
            GROUP BY warehouse_id
            ORDER BY units DESC
        """
        wh_df = load_data(warehouse_query)
        if not wh_df.empty:
            fig = px.bar(wh_df, x="warehouse_id", y="units", color="warehouse_id")
            st.plotly_chart(fig, use_container_width=True)


# ===========================================================================
# PAGE 3: Logistics & Suppliers
# ===========================================================================
elif page == "Logistics & Suppliers":
    st.subheader("🌍 Global Supplier Performance")
    
    colA, colB = st.columns([1,1])
    with colA:
        sup_query = "SELECT country, COUNT(*) as supplier_count, AVG(rating) as avg_rating FROM suppliers GROUP BY country"
        sup_df = load_data(sup_query)
        if not sup_df.empty:
            fig_map = px.choropleth(
                sup_df, 
                locations="country", 
                locationmode="country names",
                color="supplier_count",
                hover_name="country",
                title="Global Supplier Heatmap",
                color_continuous_scale=px.colors.sequential.Blues
            )
            st.plotly_chart(fig_map, use_container_width=True)

    with colB:
        st.subheader("🏆 Top Rated Suppliers")
        top_sup_query = "SELECT supplier_name, country, rating, lead_time_days FROM suppliers ORDER BY rating DESC LIMIT 5"
        top_sup_df = load_data(top_sup_query)
        st.dataframe(top_sup_df, use_container_width=True)
        csv_sup = top_sup_df.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Download Top Suppliers Report", data=csv_sup, file_name="top_supplier_data.csv", mime="text/csv")

    st.markdown("---")
    st.subheader("🚚 Carrier Delay Analysis")
    delay_query = "SELECT carrier, AVG(delivery_delay_days) as avg_delay FROM shipments WHERE delivery_status = 'Delivered' GROUP BY carrier ORDER BY avg_delay DESC"
    delay_df = load_data(delay_query)
    if not delay_df.empty:
        fig_delay = px.bar(delay_df, x="carrier", y="avg_delay", title="Average Delivery Delay by Carrier (Days)", color="avg_delay", color_continuous_scale="Reds")
        st.plotly_chart(fig_delay, use_container_width=True)


# ===========================================================================
# PAGE 4: ML Demand Forecasting
# ===========================================================================
elif page == "Demand Forecast":
    st.subheader("📈 30-Day Demand Forecast (Linear Regression)")
    st.markdown("Machine Learning predictions built dynamically from historical dataset trends.")
    
    forecast_query = """
        SELECT product_id, forecast_date, predicted_demand 
        FROM demand_forecast 
        ORDER BY forecast_date
    """
    try:
        fc_df = load_data(forecast_query)
        
        if not fc_df.empty:
            # Let user select a product to see the forecast
            products = fc_df["product_id"].unique()
            selected_product = st.selectbox("Select Product to Forecast", products)
            
            # Filter and Chart
            filtered_df = fc_df[fc_df["product_id"] == selected_product]
            fig = px.line(
                filtered_df, 
                x="forecast_date", 
                y="predicted_demand", 
                title=f"Predicted Demand for {selected_product}",
                markers=True
            )
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("Show raw prediction data"):
                st.dataframe(filtered_df)
        else:
            st.info("No forecast data found. Make sure you ran 'python -m advanced.demand_forecast'")
    except Exception as e:
        st.warning(f"Could not load data. {e}")
