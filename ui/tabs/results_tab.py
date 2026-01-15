"""
components/results_tab.py - Results display and download tab
"""

import streamlit as st
import io
import json
from datetime import datetime
from services.result_processor import get_dataframes, save_dataframes_to_excel


def render_results_tab():
    """
    Render the results tab with data display and download options.

    This includes:
    - Mapping results DataFrame display
    - Filter options (mapped only, minimum score)
    - Download buttons (Excel, CSV, JSON)
    """
    st.header("Results")

    if st.session_state.results:
        # Get DataFrames
        dataframes = get_dataframes()

        # ===== Display Mapping Results =====
        st.subheader("📊 Mapping Results")
        df_mappings = dataframes.get('ApiMapping')

        if df_mappings is not None and not df_mappings.empty:
            # ===== Filter Options =====
            col1, col2 = st.columns(2)
            with col1:
                show_mapped = st.checkbox("Show Mapped Only", value=False)
            with col2:
                min_score = st.slider("Minimum Score", 0, 100, 0)

            # Apply filters
            filtered_df = df_mappings.copy()
            if show_mapped:
                filtered_df = filtered_df[filtered_df['Second Group Code'].notna()]
            filtered_df = filtered_df[filtered_df['Similarity Score'] >= min_score]

            # Display filtered DataFrame
            st.dataframe(
                filtered_df,
                width='stretch',
                height=400
            )

            # ===== Download Buttons =====
            st.subheader("📥 Download Results")
            col1, col2, col3 = st.columns(3)

            with col1:
                # Excel download
                excel_buffer = io.BytesIO()
                save_dataframes_to_excel(excel_buffer)
                excel_buffer.seek(0)

                st.download_button(
                    label="📊 Download Excel",
                    data=excel_buffer,
                    file_name=f"{st.session_state.selected_prompt_type}_mapping_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            with col2:
                # CSV download
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="📄 Download CSV",
                    data=csv,
                    file_name=f"{st.session_state.selected_prompt_type}_mappings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

            with col3:
                # JSON download
                json_str = json.dumps(st.session_state.results, indent=2, default=str)
                st.download_button(
                    label="🔧 Download JSON",
                    data=json_str,
                    file_name=f"{st.session_state.selected_prompt_type}_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        else:
            st.info("No mapping results available yet")
    else:
        st.info("👈 No results yet. Please process data first.")
