# streamlit_app.py - UPDATED VERSION (Using prompts.py)
import streamlit as st
import pandas as pd
import io
import sys
import time
import json
import base64
from datetime import datetime
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import tempfile
import os

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import our modules
from core.config import Config
from services.input_handler import SendInputParts
from services.result_processor import get_dataframes, reset_dataframes, save_dataframes_to_excel
from core.prompts import Prompts  # NEW: Import the unified Prompts class

# Set page config
st.set_page_config(
    page_title="Mapping Medical Services",
    page_icon="🩺",  # stethoscope = general medical services
    layout="wide",
    initial_sidebar_state="expanded"
)
# Custom CSS
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        height: 50px;
        font-size: 18px;
    }
    .success-box {
        padding: 10px;
        border-radius: 5px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 10px;
        border-radius: 5px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .info-box {
        padding: 10px;
        border-radius: 5px;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
    pre {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #dee2e6;
    }
    /* Processing Tab Styles */
    .processing-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .processing-header h2 {
        margin: 0;
        font-size: 24px;
    }
    .processing-header p {
        margin: 5px 0 0 0;
        opacity: 0.9;
    }
    .terminal-container {
        background-color: #1e1e1e;
        border-radius: 10px;
        padding: 0;
        margin: 15px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        overflow: hidden;
    }
    .terminal-header {
        background-color: #323232;
        padding: 10px 15px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .terminal-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        display: inline-block;
    }
    .terminal-dot.red { background-color: #ff5f56; }
    .terminal-dot.yellow { background-color: #ffbd2e; }
    .terminal-dot.green { background-color: #27ca40; }
    .terminal-title {
        color: #888;
        font-size: 13px;
        margin-left: 10px;
    }
    .terminal-body {
        padding: 15px;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        font-size: 13px;
        color: #00ff00;
        max-height: 600px;
        overflow-y: auto;
        line-height: 1.5;
    }
    .terminal-body .log-info { color: #00bfff; }
    .terminal-body .log-success { color: #00ff00; }
    .terminal-body .log-warning { color: #ffcc00; }
    .terminal-body .log-error { color: #ff6b6b; }
    .terminal-body .log-time { color: #888; }
    .stage-card {
        background: white;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .stage-card.active {
        border-left-color: #27ca40;
        background: linear-gradient(90deg, #f0fff0 0%, white 100%);
    }
    .stage-card.completed {
        border-left-color: #27ca40;
        opacity: 0.7;
    }
    .stage-card.pending {
        border-left-color: #ddd;
        opacity: 0.5;
    }
    .stage-number {
        display: inline-block;
        width: 28px;
        height: 28px;
        background: #667eea;
        color: white;
        border-radius: 50%;
        text-align: center;
        line-height: 28px;
        font-weight: bold;
        margin-right: 10px;
    }
    .stage-card.completed .stage-number {
        background: #27ca40;
    }
    .metrics-container {
        display: flex;
        gap: 15px;
        margin: 20px 0;
    }
    .metric-card {
        flex: 1;
        background: white;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-top: 3px solid #667eea;
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        color: #333;
    }
    .metric-label {
        color: #666;
        font-size: 14px;
        margin-top: 5px;
    }
    .status-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 500;
    }
    .status-badge.running {
        background: #fff3cd;
        color: #856404;
    }
    .status-badge.success {
        background: #d4edda;
        color: #155724;
    }
    .status-badge.error {
        background: #f8d7da;
        color: #721c24;
    }
    /* Progress Stats Cards */
    .progress-stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
        margin: 20px 0;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s;
    }
    .stat-card:hover {
        transform: translateY(-5px);
    }
    .stat-card.success {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    .stat-card.warning {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .stat-card.info {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    .stat-card-value {
        font-size: 36px;
        font-weight: bold;
        margin: 10px 0;
    }
    .stat-card-label {
        font-size: 14px;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stat-card-detail {
        font-size: 12px;
        opacity: 0.8;
        margin-top: 8px;
    }
    /* Deduplication Summary Card */
    .summary-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
    }
    .summary-card h4 {
        margin: 0 0 15px 0;
        color: #667eea;
        font-size: 18px;
    }
    .summary-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 12px;
    }
    .summary-item {
        padding: 10px;
        background: #f8f9fa;
        border-radius: 8px;
    }
    .summary-item-label {
        font-size: 12px;
        color: #666;
        margin-bottom: 4px;
    }
    .summary-item-value {
        font-size: 20px;
        font-weight: bold;
        color: #333;
    }
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: #f8f9fa;
        padding: 10px 20px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: white;
        border-radius: 8px;
        font-size: 18px;
        font-weight: 600;
        color: #667eea;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #f0f2ff;
        border-color: #667eea;
        transform: translateY(-2px);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)

class StreamlitConsoleCapture:
    """Capture console output for Streamlit display with terminal styling"""
    def __init__(self, text_element):
        self.text_element = text_element
        self.output = []
        self.old_stdout = sys.stdout

    def write(self, text):
        # Write to original stdout
        self.old_stdout.write(text)

        # Remove ANSI color codes for display
        import re
        clean_text = re.sub(r'\x1b\[[0-9;]*m', '', text)

        # Capture for Streamlit
        if clean_text.strip():
            # Add timestamp
            timestamp = datetime.now().strftime("%H:%M:%S")

            # Determine log type for styling
            log_class = "log-info"
            if "error" in clean_text.lower() or "failed" in clean_text.lower():
                log_class = "log-error"
            elif "success" in clean_text.lower() or "completed" in clean_text.lower() or "[+]" in clean_text:
                log_class = "log-success"
            elif "warning" in clean_text.lower() or "[!]" in clean_text:
                log_class = "log-warning"

            formatted_line = f'<span class="log-time">[{timestamp}]</span> <span class="{log_class}">{clean_text}</span>'
            self.output.append(formatted_line)

            # Build terminal HTML
            terminal_html = self._build_terminal_html()
            self.text_element.markdown(terminal_html, unsafe_allow_html=True)

    def _build_terminal_html(self):
        """Build styled terminal HTML output"""
        lines = self.output[-100:]  # Last 100 lines
        content = "<br>".join(lines)

        return f'''
        <div class="terminal-container">
            <div class="terminal-header">
                <span class="terminal-dot red"></span>
                <span class="terminal-dot yellow"></span>
                <span class="terminal-dot green"></span>
                <span class="terminal-title">Processing Output - Live Console (Last 100 lines)</span>
            </div>
            <div class="terminal-body">
                {content}
            </div>
        </div>
        '''

    def flush(self):
        self.old_stdout.flush()

    def get_final_html(self):
        """Get final terminal output for display after processing"""
        return self._build_terminal_html()


def load_prompt_from_file(prompt_type):
    """
    Load prompt text from the Prompts class.

    UPDATED: Now uses the unified prompts.py instead of separate .txt files.
    This function maintains the same interface for backward compatibility.

    Args:
        prompt_type: One of "Lab", "Radiology", or "Service"

    Returns:
        The prompt text string, or None if error
    """
    try:
        # Get prompt from the unified Prompts class
        prompt_text = Prompts.get(prompt_type)

        if not prompt_text:
            st.warning(f"⚠️ Prompt for '{prompt_type}' is empty!")
            return None

        return prompt_text

    except ValueError as e:
        st.error(f"❌ Error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error loading prompt: {str(e)}")
        return None


def display_progress_stats(stats_dict):
    """
    Display progress statistics in beautiful cards.

    Args:
        stats_dict: Dictionary with batch progress information
    """
    if not stats_dict:
        return ""

    batches_completed = stats_dict.get('batches_completed', 0)
    total_batches = stats_dict.get('total_batches', 0)
    batches_remaining = total_batches - batches_completed
    avg_time = stats_dict.get('avg_batch_time', 0)
    estimated_remaining = batches_remaining * avg_time

    # Convert estimated time to readable format
    if estimated_remaining > 0:
        mins = int(estimated_remaining // 60)
        secs = int(estimated_remaining % 60)
        time_str = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"
    else:
        time_str = "Calculating..."

    # Get mapping statistics
    total_mappings = stats_dict.get('total_mappings', 0)
    mapped_count = stats_dict.get('mapped_count', 0)
    unmapped_count = stats_dict.get('unmapped_count', 0)
    avg_score = stats_dict.get('avg_score', 0)

    # Get token statistics
    total_tokens = stats_dict.get('total_tokens', 0)

    html = f'''
    <div class="progress-stats-container">
        <div class="stat-card">
            <div class="stat-card-label">Batches Progress</div>
            <div class="stat-card-value">{batches_completed}/{total_batches}</div>
            <div class="stat-card-detail">{batches_remaining} remaining</div>
        </div>
        <div class="stat-card info">
            <div class="stat-card-label">Est. Time Left</div>
            <div class="stat-card-value">{time_str}</div>
            <div class="stat-card-detail">Avg: {avg_time:.1f}s per batch</div>
        </div>
        <div class="stat-card success">
            <div class="stat-card-label">Total Mappings</div>
            <div class="stat-card-value">{total_mappings:,}</div>
            <div class="stat-card-detail">Mapped: {mapped_count} | Unmapped: {unmapped_count}</div>
        </div>
        <div class="stat-card warning">
            <div class="stat-card-label">Avg Score</div>
            <div class="stat-card-value">{avg_score:.1f}%</div>
            <div class="stat-card-detail">Tokens: {total_tokens:,}</div>
        </div>
    </div>
    '''

    # Add deduplication and mapping details if available
    if 'dedup_stats' in stats_dict:
        dedup = stats_dict['dedup_stats']
        html += f'''
        <div class="summary-card">
            <h4>📊 Latest Batch Statistics</h4>
            <div class="summary-grid">
                <div class="summary-item">
                    <div class="summary-item-label">Mappings Received</div>
                    <div class="summary-item-value">{dedup.get('received', 0)}</div>
                </div>
                <div class="summary-item">
                    <div class="summary-item-label">New Added</div>
                    <div class="summary-item-value" style="color: #11998e;">{dedup.get('new', 0)}</div>
                </div>
                <div class="summary-item">
                    <div class="summary-item-label">Updated (Better Score)</div>
                    <div class="summary-item-value" style="color: #4facfe;">{dedup.get('updated', 0)}</div>
                </div>
                <div class="summary-item">
                    <div class="summary-item-label">Duplicates Ignored</div>
                    <div class="summary-item-value" style="color: #f5576c;">{dedup.get('ignored', 0)}</div>
                </div>
            </div>
        </div>
        '''

    return html


def main():
    # Header
    st.title("🩺 Mapping Medical Services")
    st.markdown("### AI-Powered Mapping System with Batch Processing")
    
    # Initialize session state
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'console_output' not in st.session_state:
        st.session_state.console_output = []
    if 'selected_prompt_type' not in st.session_state:
        st.session_state.selected_prompt_type = None
    if 'uploaded_file_content' not in st.session_state:
        st.session_state.uploaded_file_content = None
    if 'estimated_input_tokens' not in st.session_state:
        st.session_state.estimated_input_tokens = 0
    if 'batch_stats' not in st.session_state:
        st.session_state.batch_stats = {
            'batches_completed': 0,
            'total_batches': 0,
            'avg_batch_time': 0,
            'total_mappings': 0,
            'mapped_count': 0,
            'unmapped_count': 0,
            'avg_score': 0,
            'total_tokens': 0,
            'batch_times': []
        }

    # Sidebar Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Provider Selection
        st.subheader("🌐 API Provider")
        provider = st.selectbox(
            "Select Provider",
            Config.PROVIDERS,
            index=Config.PROVIDERS.index(Config.provider) if Config.provider in Config.PROVIDERS else 0,
            help="Choose between OpenAI or OpenRouter"
        )
        Config.provider = provider

        # API Key inputs based on provider
        if provider == "OpenAI":
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                value=Config.api_key,
                help="Enter your OpenAI API key"
            )
            if api_key:
                Config.api_key = api_key
        else:  # OpenRouter
            openrouter_key = st.text_input(
                "OpenRouter API Key",
                type="password",
                value=Config.openrouter_api_key,
                help="Enter your OpenRouter API key (from openrouter.ai)"
            )
            if openrouter_key:
                Config.openrouter_api_key = openrouter_key

        st.divider()

        # Model Settings
        st.subheader("🤖 Model Settings")

        # Get models for selected provider
        available_models = Config.get_models_for_provider(provider)
        model_names = list(available_models.keys())

        # Find current model index or default to first
        try:
            current_model_index = model_names.index(Config.model)
        except ValueError:
            current_model_index = 0

        model = st.selectbox(
            "Model",
            model_names,
            index=current_model_index,
            format_func=lambda x: f"{x} ({available_models[x]['description']})",
            help="Select the AI model to use"
        )
        Config.model = model

        # Display model context info
        model_info = available_models.get(model, {})
        max_context = model_info.get("max_context", 8192)
        st.caption(f"Max context: {max_context:,} tokens")

        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=Config.temperature,
            step=0.1,
            help="Controls randomness (0=focused, 1=creative)"
        )
        Config.temperature = temperature

        top_p = st.slider(
            "Top P",
            min_value=0.1,
            max_value=1.0,
            value=Config.top_p,
            step=0.1,
            help="Controls diversity of output"
        )
        Config.top_p = top_p

        # Max tokens with validation
        max_output_tokens = st.number_input(
            "Max Output Tokens",
            min_value=1000,
            max_value=min(128000, max_context - 1000),  # Cap at context limit
            value=min(Config.max_tokens, max_context - 1000),
            step=1000,
            help=f"Maximum tokens for response (model max: {max_context:,})"
        )
        Config.max_tokens = max_output_tokens

        # Token validation warning
        if 'estimated_input_tokens' in st.session_state and st.session_state.estimated_input_tokens > 0:
            is_valid, msg, recommended = Config.validate_token_limit(
                st.session_state.estimated_input_tokens,
                max_output_tokens,
                model,
                provider
            )
            if not is_valid:
                st.error(f"⚠️ {msg}")
                if st.button("Apply Recommended", key="apply_recommended"):
                    Config.max_tokens = recommended
                    st.rerun()
            else:
                st.success(f"[OK] {msg}")

        threshold = st.slider(
            "Similarity Threshold",
            min_value=0,
            max_value=100,
            value=Config.threshold,
            step=5,
            help="Minimum similarity score for valid mapping"
        )
        Config.threshold = threshold

        st.divider()
        
        # Batch Settings
        st.subheader("📦 Batch Settings")
        
        max_batch_size = st.number_input(
            "Max Batch Size",
            min_value=50,
            max_value=500,
            value=Config.max_batch_size,
            step=50,
            help="Maximum rows per batch"
        )
        Config.max_batch_size = max_batch_size
        
        wait_time = st.number_input(
            "Wait Between Batches (seconds)",
            min_value=0,
            max_value=300,
            value=Config.wait_between_batches,
            step=30,
            help="Delay between API calls (deprecated with async processing)"
        )
        Config.wait_between_batches = wait_time

        max_concurrent_batches = st.number_input(
            "Max Concurrent Batches",
            min_value=1,
            max_value=10,
            value=Config.max_concurrent_batches,
            step=1,
            help="Maximum number of batches processed simultaneously (with rate limiting)"
        )
        Config.max_concurrent_batches = max_concurrent_batches

        st.caption("💡 Async processing with automatic rate limiting (RPM/TPM)")

        st.divider()
        
        # Optimization Settings
        st.subheader("⚡ Optimization")
        
        use_compact = st.checkbox(
            "Use Compact JSON",
            value=Config.use_compact_json,
            help="Reduces token usage by ~60%"
        )
        Config.use_compact_json = use_compact
        
        abbreviate = st.checkbox(
            "Abbreviate Keys",
            value=Config.abbreviate_keys,
            help="Use short key names (c/n instead of code/name)"
        )
        Config.abbreviate_keys = abbreviate
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["📁 Input", "🔄 Processing", "📊 Results", "📈 Analytics"])
    
    with tab1:
        st.header("Data Input")
        
        col1, col2 = st.columns(2)
        
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
                Prompts.get_all_types(),  # UPDATED: Use Prompts class
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
                                st.write(f"• {area}")
                else:
                    st.error(f"Failed to load prompt for {st.session_state.selected_prompt_type}")
            else:
                st.warning("⚠️ Please select a prompt type")
        
        st.divider()
        
        # Process button
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
    
    with tab2:
        if st.session_state.processing:
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

                    def update_stage(placeholder, number, title, status="pending"):
                        status_icon = {"pending": "⏳", "active": "🔄", "completed": "✅", "error": "❌"}
                        status_class = status
                        placeholder.markdown(f'''
                        <div class="stage-card {status_class}">
                            <span class="stage-number">{number}</span>
                            <strong>{title}</strong>
                            <span style="float: right;">{status_icon.get(status, "⏳")}</span>
                        </div>
                        ''', unsafe_allow_html=True)

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

            # Progress Statistics Cards
            stats_placeholder = st.empty()

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

                # Capture console output
                console_capture = StreamlitConsoleCapture(console_output)
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

                        # Update batch stats display
                        stats = results.get("statistics", {})
                        batch_meta = results.get("batch_metadata", {})

                        if batch_meta:
                            # Extract batch statistics
                            display_stats = {
                                'batches_completed': batch_meta.get('batches_processed', 0),
                                'total_batches': batch_meta.get('total_batches', 0),
                                'avg_batch_time': 0,  # Would need to track this
                                'total_mappings': len(results.get("mappings", [])),
                                'mapped_count': stats.get("mapped_count", 0),
                                'unmapped_count': stats.get("unmapped_count", 0),
                                'avg_score': stats.get("avg_score", 0),
                                'total_tokens': stats.get("total_tokens", 0)
                            }
                            stats_html = display_progress_stats(display_stats)
                            stats_placeholder.markdown(stats_html, unsafe_allow_html=True)

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
                except:
                    pass

                try:
                    if os.path.exists(temp_prompt_path):
                        os.unlink(temp_prompt_path)
                except:
                    pass
        else:
            # Idle state - show instructions
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

            st.info("Go to the **Input** tab to upload data and select a prompt type to start processing.")
    
    with tab3:
        st.header("Results")
        
        if st.session_state.results:
            # Get DataFrames
            dataframes = get_dataframes()
            
            # Display mapping results
            st.subheader("📊 Mapping Results")
            df_mappings = dataframes.get('ApiMapping')
            
            if df_mappings is not None and not df_mappings.empty:
                # Filter options
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
                
                st.dataframe(
                    filtered_df,
                    width='stretch',
                    height=400
                )
                
                # Download buttons
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
    
    with tab4:
        st.header("Analytics")
        
        if st.session_state.results:
            dataframes = get_dataframes()
            df_mappings = dataframes.get('ApiMapping')
            df_calls = dataframes.get('ApiCall')
            
            if df_mappings is not None and not df_mappings.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Score distribution
                    st.subheader("📊 Score Distribution")
                    fig = px.histogram(
                        df_mappings,
                        x='Similarity Score',
                        nbins=20,
                        title="Distribution of Similarity Scores"
                    )
                    st.plotly_chart(fig, width='stretch')
                
                with col2:
                    # Mapping status
                    st.subheader("🎯 Mapping Status")
                    mapped_count = df_mappings['Second Group Code'].notna().sum()
                    unmapped_count = df_mappings['Second Group Code'].isna().sum()
                    
                    fig = go.Figure(data=[go.Pie(
                        labels=['Mapped', 'Unmapped'],
                        values=[mapped_count, unmapped_count],
                        hole=.3
                    )])
                    fig.update_layout(title="Mapping Status Distribution")
                    st.plotly_chart(fig, width='stretch')
                
                # API Call Statistics
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
                    
                    # Token usage over time
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
                        st.plotly_chart(fig, width='stretch')
        else:
            st.info("👈 No analytics data available. Please process data first.")
    
    # Footer
    st.divider()
    st.markdown(
        f"""
        <div style='text-align: center; color: gray;'>
            Medical Mapping Service v2.0 | Mode: {st.session_state.selected_prompt_type or 'None'} |
            Provider: {Config.provider} | Model: {Config.model} | Threshold: {Config.threshold}%
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()