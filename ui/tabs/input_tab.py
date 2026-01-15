"""
components/input_tab.py - Input tab for file upload and prompt selection
"""

import streamlit as st
import pandas as pd
from core.config import Config
from core.prompts import Prompts
from ui.tabs.utils import load_prompt_from_file


def render_input_tab():
    """
    Render the input tab for file upload and prompt selection.

    This includes:
    - Excel file upload with preview
    - Prompt type selection (Lab, Radiology, Service)
    - Token estimation
    - Process button with validation
    """
    st.header("Data Input")

    col1, col2 = st.columns(2)

    # ===== Left Column: File Upload =====
    with col1:
        st.subheader("📄 Excel File")
        uploaded_file = st.file_uploader(
            "Upload Excel file with 'First Group' and 'Second Group' sheets",
            type=['xlsx', 'xls'],
            help="Excel file must contain two sheets: 'First Group' and 'Second Group'"
        )

        if uploaded_file:
            try:
                # Store the file content in session state
                st.session_state.uploaded_file_content = uploaded_file.read()
                uploaded_file.seek(0)  # Reset file pointer for preview

                # Preview the uploaded file
                excel_data = pd.ExcelFile(uploaded_file)
                st.success(f"✅ File uploaded: {uploaded_file.name}")
                st.info(f"Sheets found: {', '.join(excel_data.sheet_names)}")

                # Show preview of data
                # Initialize for token estimation
                total_chars = 0

                if 'First Group' in excel_data.sheet_names:
                    df_first = pd.read_excel(excel_data, sheet_name='First Group', header=None)
                    st.write("**First Group Preview:**")
                    st.dataframe(df_first.head().astype(str), width='stretch')
                    st.caption(f"Total rows: {len(df_first)}")
                    # Estimate chars from data
                    total_chars += df_first.astype(str).apply(lambda x: x.str.len().sum()).sum()

                if 'Second Group' in excel_data.sheet_names:
                    df_second = pd.read_excel(excel_data, sheet_name='Second Group', header=None)
                    st.write("**Second Group Preview:**")
                    st.dataframe(df_second.head().astype(str), width='stretch')
                    st.caption(f"Total rows: {len(df_second)}")
                    # Estimate chars from data
                    total_chars += df_second.astype(str).apply(lambda x: x.str.len().sum()).sum()

                # Estimate tokens (roughly 4 chars per token, plus overhead for JSON/prompt)
                estimated_tokens = int(total_chars / 3.5) + 2000  # Add overhead for prompt/formatting
                st.session_state.estimated_input_tokens = estimated_tokens
                st.info(f"Estimated input tokens: ~{estimated_tokens:,} (includes prompt overhead)")

                excel_data.close()  # Close the ExcelFile object

            except Exception as e:
                st.error(f"Error reading Excel file: {str(e)}")

    # ===== Right Column: Prompt Selection =====
    with col2:
        st.subheader("📝 Prompt Selection")
        st.info("Select the type of mapping to load the appropriate prompt")

        # Create three columns for the selection buttons
        button_col1, button_col2, button_col3 = st.columns(3)

        with button_col1:
            if st.button("🧪 Lab", width='stretch', type="primary"):
                st.session_state.selected_prompt_type = "Lab"

        with button_col2:
            if st.button("📷 Radiology", width='stretch', type="primary"):
                st.session_state.selected_prompt_type = "Radiology"

        with button_col3:
            if st.button("🔧 Service", width='stretch', type="primary"):
                st.session_state.selected_prompt_type = "Service"

        # Alternative: Radio buttons
        st.divider()
        st.write("**Or select using radio buttons:**")
        prompt_type_radio = st.radio(
            "Select Prompt Type:",
            Prompts.get_all_types(),
            horizontal=True,
            index=None
        )

        if prompt_type_radio:
            st.session_state.selected_prompt_type = prompt_type_radio

        # Display selected prompt type and load prompt
        if st.session_state.selected_prompt_type:
            # Get prompt info from Prompts class
            prompt_info = Prompts.get_prompt_info(st.session_state.selected_prompt_type)

            st.success(f"✅ Selected: **{prompt_info.get('icon', '')} {prompt_info.get('name', st.session_state.selected_prompt_type)}**")

            # Show description
            if prompt_info.get('description'):
                st.caption(prompt_info['description'])

            # Load and display prompt
            prompt_text = load_prompt_from_file(st.session_state.selected_prompt_type)
            if prompt_text:
                st.write("**Prompt Preview:**")
                with st.expander("View Full Prompt", expanded=False):
                    st.text_area(
                        "Prompt Content",
                        value=prompt_text[:500] + "..." if len(prompt_text) > 500 else prompt_text,
                        height=150,
                        disabled=True
                    )
                st.caption(f"Prompt length: {len(prompt_text)} characters")

                # Show focus areas
                if prompt_info.get('focus_areas'):
                    with st.expander("📋 Focus Areas", expanded=False):
                        for area in prompt_info['focus_areas']:
                            st.write(f"- {area}")
            else:
                st.error(f"Failed to load prompt for {st.session_state.selected_prompt_type}")
        else:
            st.warning("⚠️ Please select a prompt type")

    st.divider()

    # ===== Process Button =====
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Check if appropriate API key is set based on provider
        has_api_key = (Config.provider == "OpenAI" and Config.api_key) or \
                      (Config.provider == "OpenRouter" and Config.openrouter_api_key)

        if st.button(
            "🚀 Start Mapping Process",
            type="primary",
            width='stretch',
            disabled=not (uploaded_file and st.session_state.selected_prompt_type and has_api_key)
        ):
            if not has_api_key:
                st.error(f"❌ Please enter your {Config.provider} API key in the sidebar")
            elif not uploaded_file:
                st.error("❌ Please upload an Excel file")
            elif not st.session_state.selected_prompt_type:
                st.error("❌ Please select a prompt type (Lab, Radiology, or Service)")
            else:
                st.session_state.processing = True
                st.rerun()
