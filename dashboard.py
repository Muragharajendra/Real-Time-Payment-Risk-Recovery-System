import streamlit as st
import pandas as pd
import time
import plotly.express as px
from db_utils import get_db_connection

st.set_page_config(page_title="Payment Risk Dashboard", layout="wide")

st.title("Real-Time Payment Risk & Recovery System")

# Sidebar for navigation
page = st.sidebar.selectbox("Navigate", ["Live Overview", "Bank & PSP Health", "Conversion Funnel", "Risk & Alerts", "Recovery Effectiveness"])

# Global Auto-refresh
auto_refresh = st.sidebar.checkbox("Auto-refresh", value=True)

def load_data(query, params=()):
    conn = get_db_connection()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

if page == "Live Overview":
    st.header("Live Transaction Overview (Last 5 Minutes)")

    query = "SELECT * FROM transactions WHERE timestamp >= datetime('now', 'localtime', '-5 minutes')"
    df = load_data(query)

    if not df.empty:
        col1, col2, col3, col4 = st.columns(4)
        total = len(df)
        success = len(df[df['status'] == 'SUCCESS'])
        failed = len(df[df['status'] == 'FAILURE'])
        avg_latency = df['latency_ms'].mean()

        col1.metric("Total Transactions", total)
        col2.metric("Success Rate", f"{(success/total)*100:.1f}%")
        col3.metric("Failure Rate", f"{(failed/total)*100:.1f}%")
        col4.metric("Avg Latency", f"{avg_latency:.0f} ms")

        st.subheader("Transactions over Time")
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df_grouped = df.groupby(pd.Grouper(key='timestamp', freq='10s')).size().reset_index(name='count')
        fig = px.line(df_grouped, x='timestamp', y='count', title="Transaction Volume (10s buckets)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No recent transactions.")

elif page == "Bank & PSP Health":
    st.header("Entity Health Monitor")
    
    entity_type = st.radio("Select Entity Type", ["BANK", "PSP"])
    
    query = f"SELECT DISTINCT entity_id FROM entity_metrics WHERE entity_type = '{entity_type}'"
    entities = load_data(query)['entity_id'].tolist()
    
    selected_entity = st.selectbox(f"Select {entity_type}", entities)
    
    if selected_entity:
        query = f"SELECT * FROM entity_metrics WHERE entity_type = '{entity_type}' AND entity_id = ? ORDER BY bucket_start_time DESC LIMIT 60"
        df = load_data(query, (selected_entity,))
        
        if not df.empty:
            col1, col2 = st.columns(2)
            
            fig1 = px.line(df, x='bucket_start_time', y='failure_rate', title=f"{selected_entity} Failure Rate")
            col1.plotly_chart(fig1, use_container_width=True)
            
            fig2 = px.line(df, x='bucket_start_time', y='avg_latency_ms', title=f"{selected_entity} Latency")
            col2.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No metrics available for this entity.")

elif page == "Conversion Funnel":
    st.header("Transaction Funnel")
    
    query = "SELECT status, risk_score, decision FROM transactions WHERE timestamp >= datetime('now', 'localtime', '-1 hour')"
    df = load_data(query)
    
    if not df.empty:
        total = len(df)
        high_risk = len(df[df['risk_score'] > 0.7])
        retried = len(df[df['decision'] == 'RETRY'])
        routed = len(df[df['decision'] == 'ROUTE_CHANGE'])
        success = len(df[df['status'] == 'SUCCESS'])
        
        data = dict(
            number=[total, high_risk, retried + routed, success],
            stage=["Initiated", "High Risk Detected", "Recovery Actions", "Final Success"]
        )
        fig = px.funnel(data, x='number', y='stage')
        st.plotly_chart(fig, use_container_width=True)

elif page == "Risk & Alerts":
    st.header("High Risk Transactions & Alerts")
    
    st.subheader("Recent High Risk Transactions")
    query = "SELECT * FROM transactions WHERE risk_score > 0.7 ORDER BY timestamp DESC LIMIT 20"
    df_risk = load_data(query)
    st.dataframe(df_risk)
    
    st.subheader("Recent Alerts")
    query = "SELECT * FROM alerts ORDER BY created_time DESC LIMIT 20"
    df_alerts = load_data(query)
    st.dataframe(df_alerts)

elif page == "Recovery Effectiveness":
    st.header("Recovery Actions Effectiveness")
    
    query = "SELECT * FROM recovery_actions ORDER BY timestamp DESC LIMIT 50"
    df = load_data(query)
    
    if not df.empty:
        st.dataframe(df)
        
        counts = df['action_type'].value_counts().reset_index()
        counts.columns = ['Action', 'Count']
        fig = px.pie(counts, values='Count', names='Action', title="Distribution of Recovery Actions")
        st.plotly_chart(fig)
    else:
        st.info("No recovery actions recorded yet.")

if auto_refresh:
    time.sleep(2)
    st.rerun()
