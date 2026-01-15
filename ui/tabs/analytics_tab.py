"""
components/analytics_tab.py - Analytics and visualizations tab
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from services.result_processor import get_dataframes


def render_analytics_tab():
    """
    Render the analytics tab with visualizations and metrics.

    This includes:
    - Score distribution histogram
    - Mapping status pie chart
    - API call statistics
    - Token usage over time
    """
    st.header("Analytics")

    if st.session_state.results:
        dataframes = get_dataframes()
        df_mappings = dataframes.get('ApiMapping')
        df_calls = dataframes.get('ApiCall')

        if df_mappings is not None and not df_mappings.empty:
            col1, col2 = st.columns(2)

            with col1:
                # ===== Score Distribution =====
                st.subheader("📊 Score Distribution")
                fig = px.histogram(
                    df_mappings,
                    x='Similarity Score',
                    nbins=20,
                    title="Distribution of Similarity Scores"
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # ===== Mapping Status Pie Chart =====
                st.subheader("🎯 Mapping Status")
                mapped_count = df_mappings['Second Group Code'].notna().sum()
                unmapped_count = df_mappings['Second Group Code'].isna().sum()

                fig = go.Figure(data=[go.Pie(
                    labels=['Mapped', 'Unmapped'],
                    values=[mapped_count, unmapped_count],
                    hole=.3
                )])
                fig.update_layout(title="Mapping Status Distribution")
                st.plotly_chart(fig, use_container_width=True)

            # ===== API Call Statistics =====
            if df_calls is not None and not df_calls.empty:
                st.subheader("📈 API Call Statistics")

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Calls", len(df_calls))
                with col2:
                    st.metric("Avg Latency", f"{df_calls['Latency'].mean():.2f}s")
                with col3:
                    st.metric("Total Tokens", f"{df_calls['Total Tokens'].sum():,}")
                with col4:
                    st.metric("Prompt Type", st.session_state.selected_prompt_type)

                # ===== Token Usage Over Time =====
                if len(df_calls) > 1:
                    st.subheader("🔤 Token Usage")
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_calls.index,
                        y=df_calls['Input Tokens'],
                        mode='lines+markers',
                        name='Input Tokens'
                    ))
                    fig.add_trace(go.Scatter(
                        x=df_calls.index,
                        y=df_calls['Output Tokens'],
                        mode='lines+markers',
                        name='Output Tokens'
                    ))
                    fig.update_layout(
                        title="Token Usage per API Call",
                        xaxis_title="Call Number",
                        yaxis_title="Tokens"
                    )
                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("👈 No analytics data available. Please process data first.")
