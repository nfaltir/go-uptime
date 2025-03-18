import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

API_URL = "http://localhost:8080/data"  # Your API endpoint
SITE_NAME = "Test Site"

st.set_page_config(
    page_title="Website Latency Monitor", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling
st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            margin-top: 5rem;
        }
        .metric-card {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 1.2rem;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            text-align: center;
        }
        .metric-title {
            font-size: 1rem;
            color: #6b7280;
            margin-bottom: 0.5rem;
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: 600;
        }
        .metric-site {
            color: #4b5563;
        }
        .metric-latency {
            color: #8b5cf6;
        }
        .metric-online {
            color: #10b981;
        }
        .metric-offline {
            color: #ef4444;
        }
        .stPlotlyChart {
            background-color: white;
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }
        div[data-testid="stDataFrame"] {
            background-color: white;
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }
        .section-header {
            font-size: 1.5rem;
            font-weight: 600;
            margin: 2rem 0 1rem 0;
            color: #1f2937;
        }
        /* Fix Streamlit's default styling */
        .block-container {
            padding-top: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=10)  # Cache for 10 seconds
def fetch_data():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return []

# Dashboard Header
st.markdown('<hr>', unsafe_allow_html=True)
st.markdown('<p class="main-header">Website Latency Monitor</p>', unsafe_allow_html=True)
st.markdown(f'<p>Last updated: {datetime.now().strftime("%B %d, %Y %H:%M:%S")}</p>', unsafe_allow_html=True)

# Load data
data = fetch_data()

if data:
    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])  # Convert to datetime
    
    # Calculate metrics
    avg_latency = round(df["latency"].mean(), 1)
    is_online = df.iloc[-1]["online"]
    current_status = "Online" if is_online else "Offline"
    latest_latency = df.iloc[-1]["latency"]
    uptime_percentage = round((df["online"].sum() / len(df)) * 100, 1)
    
    # Metric Cards Layout
    st.markdown('<p class="section-header">System Overview</p>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-title">SITE</p>
            <p class="metric-value metric-site">{SITE_NAME}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-title">AVERAGE LATENCY</p>
            <p class="metric-value metric-latency">{avg_latency} ms</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        status_class = "metric-online" if is_online else "metric-offline"
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-title">CURRENT STATUS</p>
            <p class="metric-value {status_class}">{current_status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-title">UPTIME</p>
            <p class="metric-value metric-latency">{uptime_percentage}%</p>
        </div>
        """, unsafe_allow_html=True)

    # Latency Line Chart with Plotly
    st.markdown('<p class="section-header">Latency Trends</p>', unsafe_allow_html=True)
    
    fig = px.line(
        df, 
        x="timestamp", 
        y="latency",
        labels={"timestamp": "Time", "latency": "Latency (ms)"},
        line_shape="linear"
    )
    
    fig.update_traces(line_color="#8b5cf6", line_width=2)
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(t=30, l=0, r=0, b=0),
        height=400,
        hovermode="x unified"
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="#f3f4f6")
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="#f3f4f6")
    
    st.plotly_chart(fig, use_container_width=True)

    # Status History
    st.markdown('<p class="section-header">Status History</p>', unsafe_allow_html=True)
    
    # Format dataframe for display
    display_df = df.copy()
    display_df["timestamp"] = display_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    display_df["online"] = display_df["online"].apply(lambda x: "✅ Online" if x else "❌ Offline")
    display_df.rename(columns={
        "timestamp": "Timestamp",
        "online": "Status",
        "latency": "Latency (ms)"
    }, inplace=True)
    
    st.dataframe(
        display_df[["Timestamp", "Status", "Latency (ms)"]],
        hide_index=True,
        use_container_width=True
    )
else:
    st.warning("No data available. Please check your API connection.")
    
    # Example data for preview
    st.markdown("### Preview (Example Data)")
    example_df = pd.DataFrame({
        "Timestamp": ["2025-03-17 10:00:00", "2025-03-17 10:10:00", "2025-03-17 10:20:00"],
        "Status": ["✅ Online", "✅ Online", "✅ Online"],
        "Latency (ms)": [120, 145, 118]
    })
    st.dataframe(example_df, hide_index=True, use_container_width=True)