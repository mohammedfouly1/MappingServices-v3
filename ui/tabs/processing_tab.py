"""
components/processing_tab.py - Processing tab with stages and live output
"""

import streamlit as st
import sys
import time
import tempfile
import os
from core.config import Config
from core.prompts import Prompts
from ui.tabs.utils import StreamlitConsoleCapture, load_prompt_from_file
from services.input_handler import SendInputParts
from services.result_processor import reset_dataframes
from core.logger import get_logger, log_exception

logger = get_logger(__name__)


def update_stage(placeholder, number: int, title: str, status: str = "pending"):
    """
    Update a stage card with current status.

    Args:
        placeholder: Streamlit placeholder for the stage card
        number: Stage number (1-4)
        title: Stage title text
        status: One of "pending", "active", "completed", "error"
    """
    status_icon = {"pending": "⏳", "active": "🔄", "completed": "✅", "error": "❌"}
    status_class = status
    placeholder.markdown(f'''
    <div class="stage-card {status_class}">
        <span class="stage-number">{number}</span>
        <strong>{title}</strong>
        <span style="float: right;">{status_icon.get(status, "⏳")}</span>
    </div>
    ''', unsafe_allow_html=True)


def render_processing_tab():
    """
    Render the processing tab with stages, progress, and live console output.

    This handles:
    - Processing stages visualization
    - Progress tracking
    - Live console output capture
    - Temp file management
    - Results storage
    """
    if st.session_state.processing:
        # ===== Active Processing State =====

        # Load prompt based on selection
        prompt_text = load_prompt_from_file(st.session_state.selected_prompt_type)

        if not prompt_text:
            st.error(f"Failed to load {st.session_state.selected_prompt_type} prompt")
            st.session_state.processing = False
            st.stop()

        # Styled Processing Header
        prompt_info = Prompts.get_prompt_info(st.session_state.selected_prompt_type)
        st.markdown(f'''
        <div class="processing-header">
            <h2>{prompt_info.get('icon', '🔄')} Processing: {st.session_state.selected_prompt_type} Mapping</h2>
            <p>AI-powered medical service mapping in progress...</p>
        </div>
        ''', unsafe_allow_html=True)

        # Create two columns for stages and configuration
        col_stages, col_config = st.columns([2, 1])

        with col_config:
            # Configuration Summary Card
            st.markdown('''
            <div style="background: white; border-radius: 10px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h4 style="margin: 0 0 10px 0; color: #667eea;">Configuration</h4>
            </div>
            ''', unsafe_allow_html=True)

            st.markdown(f"""
            | Setting | Value |
            |---------|-------|
            | **Provider** | `{Config.provider}` |
            | **Model** | `{Config.model}` |
            | **Temperature** | `{Config.temperature}` |
            | **Max Tokens** | `{Config.max_tokens:,}` |
            | **Batch Size** | `{Config.max_batch_size}` |
            | **Threshold** | `{Config.threshold}%` |
            """)

        with col_stages:
            # Processing Stages
            stages_container = st.container()
            with stages_container:
                st.markdown("#### Processing Stages")

                # Stage placeholders
                stage1_placeholder = st.empty()
                stage2_placeholder = st.empty()
                stage3_placeholder = st.empty()
                stage4_placeholder = st.empty()

                # Initialize stages
                update_stage(stage1_placeholder, 1, "Initializing & Loading Data", "pending")
                update_stage(stage2_placeholder, 2, "Preparing Batches", "pending")
                update_stage(stage3_placeholder, 3, "Processing with AI", "pending")
                update_stage(stage4_placeholder, 4, "Finalizing Results", "pending")

        st.divider()

        # Progress Section
        st.markdown("#### Overall Progress")
        progress_bar = st.progress(0)
        status_placeholder = st.empty()

        # Progress Metrics Dashboard
        st.markdown("#### Processing Metrics")
        metrics_placeholder = st.empty()

        # Terminal Console Output
        st.markdown("#### Live Console Output")
        console_output = st.empty()

        # Create temporary files using tempfile module
        temp_excel_fd, temp_excel_path = tempfile.mkstemp(suffix='.xlsx')
        temp_prompt_fd, temp_prompt_path = tempfile.mkstemp(suffix='.txt')

        try:
            # Write Excel content to temp file
            with os.fdopen(temp_excel_fd, 'wb') as f:
                f.write(st.session_state.uploaded_file_content)

            # Write prompt to temp file
            with os.fdopen(temp_prompt_fd, 'w', encoding='utf-8') as f:
                f.write(prompt_text)

            # Reset DataFrames
            reset_dataframes()

            # Capture console output with metrics tracking
            console_capture = StreamlitConsoleCapture(console_output, metrics_placeholder)
            old_stdout = sys.stdout
            sys.stdout = console_capture

            try:
                # Stage 1: Initializing
                update_stage(stage1_placeholder, 1, "Initializing & Loading Data", "active")
                status_placeholder.markdown('<span class="status-badge running">Initializing...</span>', unsafe_allow_html=True)
                progress_bar.progress(10)
                time.sleep(0.5)
                update_stage(stage1_placeholder, 1, "Initializing & Loading Data", "completed")

                # Stage 2: Preparing
                update_stage(stage2_placeholder, 2, "Preparing Batches", "active")
                status_placeholder.markdown('<span class="status-badge running">Preparing batches...</span>', unsafe_allow_html=True)
                progress_bar.progress(20)

                # Stage 3: Processing
                update_stage(stage2_placeholder, 2, "Preparing Batches", "completed")
                update_stage(stage3_placeholder, 3, "Processing with AI", "active")
                status_placeholder.markdown('<span class="status-badge running">Processing with AI model...</span>', unsafe_allow_html=True)
                progress_bar.progress(30)

                # Call the processing function
                results = SendInputParts(
                    excel_path=temp_excel_path,
                    prompt_path=temp_prompt_path,
                    verbose=True
                )

                update_stage(stage3_placeholder, 3, "Processing with AI", "completed")
                progress_bar.progress(85)

                # Stage 4: Finalizing
                update_stage(stage4_placeholder, 4, "Finalizing Results", "active")
                status_placeholder.markdown('<span class="status-badge running">Finalizing results...</span>', unsafe_allow_html=True)
                progress_bar.progress(95)

                if results:
                    st.session_state.results = results
                    update_stage(stage4_placeholder, 4, "Finalizing Results", "completed")
                    progress_bar.progress(100)
                    status_placeholder.markdown('<span class="status-badge success">Completed Successfully!</span>', unsafe_allow_html=True)

                    st.divider()

                    # Success Summary with styled metrics
                    st.markdown("#### Results Summary")
                    stats = results.get("statistics", {})

                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Mappings", len(results.get("mappings", [])))
                    with col2:
                        st.metric("Mapped Items", stats.get("mapped_count", 0))
                    with col3:
                        st.metric("Unmapped Items", stats.get("unmapped_count", 0))
                    with col4:
                        st.metric("Avg Score", f"{stats.get('avg_score', 0):.1f}%")

                    st.success(f"Processing completed! Go to the **Results** tab to view and download your mappings.")

                else:
                    update_stage(stage4_placeholder, 4, "Finalizing Results", "error")
                    status_placeholder.markdown('<span class="status-badge error">Processing Failed</span>', unsafe_allow_html=True)
                    st.error("Processing failed. Check the console output for details.")

            except Exception as e:
                status_placeholder.markdown('<span class="status-badge error">Error Occurred</span>', unsafe_allow_html=True)
                st.error(f"Error during processing: {str(e)}")
                import traceback
                with st.expander("Error Details", expanded=True):
                    st.code(traceback.format_exc())
            finally:
                # Restore stdout
                sys.stdout = old_stdout
                st.session_state.processing = False

        finally:
            # Clean up temp files
            try:
                if os.path.exists(temp_excel_path):
                    os.unlink(temp_excel_path)
            except FileNotFoundError:
                pass  # File already deleted
            except PermissionError as e:
                logger.warning(f"Could not delete temp Excel file: {e}")
            except Exception as e:
                log_exception(logger, "Error deleting temp Excel file", e)

            try:
                if os.path.exists(temp_prompt_path):
                    os.unlink(temp_prompt_path)
            except FileNotFoundError:
                pass  # File already deleted
            except PermissionError as e:
                logger.warning(f"Could not delete temp prompt file: {e}")
            except Exception as e:
                log_exception(logger, "Error deleting temp prompt file", e)

    else:
        # ===== Idle State - Show Instructions =====
        st.markdown('''
        <div class="processing-header" style="background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);">
            <h2>🔄 Processing Center</h2>
            <p>Ready to process your medical service mappings</p>
        </div>
        ''', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown('''
            <div class="stage-card">
                <span class="stage-number">1</span>
                <strong>Upload Data</strong>
                <p style="margin: 10px 0 0 38px; color: #666; font-size: 14px;">
                    Upload your Excel file with First Group and Second Group sheets
                </p>
            </div>
            ''', unsafe_allow_html=True)

        with col2:
            st.markdown('''
            <div class="stage-card">
                <span class="stage-number">2</span>
                <strong>Select Prompt</strong>
                <p style="margin: 10px 0 0 38px; color: #666; font-size: 14px;">
                    Choose Lab, Radiology, or Service mapping type
                </p>
            </div>
            ''', unsafe_allow_html=True)

        with col3:
            st.markdown('''
            <div class="stage-card">
                <span class="stage-number">3</span>
                <strong>Start Processing</strong>
                <p style="margin: 10px 0 0 38px; color: #666; font-size: 14px;">
                    Click the Start button to begin AI mapping
                </p>
            </div>
            ''', unsafe_allow_html=True)

        st.info("👈 Go to the **Input** tab to upload your data and start processing")
