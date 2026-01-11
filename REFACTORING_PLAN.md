# Refactoring Plan: Laboratory Mapping Service

> **Generated**: January 2026
> **Project**: MappingServices
> **Status**: Planning Phase

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Phase 1: Critical Fixes](#phase-1-critical-fixes-high-priority)
3. [Phase 2: Code Quality Improvements](#phase-2-code-quality-improvements-medium-priority)
4. [Phase 3: Streamlit App Decomposition](#phase-3-streamlit-app-decomposition-medium-priority)
5. [Phase 4: Architecture Improvements](#phase-4-architecture-improvements-lower-priority)
6. [Phase 5: Files to Delete](#phase-5-files-to-delete)
7. [Implementation Order](#implementation-order)
8. [Summary](#summary)

---

## Project Overview

| File | Lines | Purpose | Action |
|------|-------|---------|--------|
| `config.py` | 62 | Configuration management | **MODIFY** |
| `prompts.py` | 165 | Prompt storage | **MODIFY** |
| `optimization_utils.py` | 30 | Token optimization | **MODIFY** |
| `input_handler.py` | 347 | Data orchestration | **MODIFY** |
| `batch_dispatcher.py` | 345 | Batch processing | **MODIFY** |
| `api_mapping.py` | 242 | OpenAI API integration | **MODIFY** |
| `result_processor.py` | 352 | Deduplication & analytics | **MAJOR REFACTOR** |
| `main.py` | 54 | CLI entry point | **MODIFY** |
| `streamlit_app.py` | 953 | Web UI | **SPLIT INTO MODULES** |

### Current Architecture

```
CLI Interface (main.py)
    │
    ▼
Input Handler (input_handler.py)
    ├── Config (config.py) [settings]
    ├── Optimization Utils (optimization_utils.py) [compact format]
    └── Batch Dispatcher (batch_dispatcher.py)
        ├── Config (config.py) [batch settings]
        ├── API Mapping (api_mapping.py)
        │   ├── Config (config.py) [API settings]
        │   └── Optimization Utils (optimization_utils.py) [expand results]
        └── Result Processor (result_processor.py)
            └── Config (config.py) [threshold]

Web Interface (streamlit_app.py)
    ├── Config (config.py) [all settings]
    ├── Input Handler (input_handler.py) [orchestration]
    ├── Result Processor (result_processor.py) [DataFrame access]
    └── Prompts (prompts.py) [prompt selection/metadata]
```

---

## Phase 1: Critical Fixes (High Priority)

### 1.1 Remove Global State in `result_processor.py`

**Problem**: Global mutable variables make testing impossible and cause hidden bugs.

**Current Code (BAD)**:
```python
# result_processor.py - Lines 10-24
df_api_call = pd.DataFrame(...)  # Global
df_api_mapping = pd.DataFrame(...)  # Global
seen_first_codes = {}  # Global
```

**Refactored (GOOD)**:
```python
# result_processor.py - New Implementation
class ResultProcessor:
    """Handles mapping result processing, deduplication, and analytics"""

    def __init__(self):
        self.df_api_call = pd.DataFrame(columns=[
            'Batch', 'First Group Count', 'Second Group Count',
            'Input Tokens', 'Output Tokens', 'Total Tokens', 'Latency'
        ])
        self.df_api_mapping = pd.DataFrame(columns=[
            'First Group Code', 'First Group Name',
            'Second Group Code', 'Second Group Name',
            'Similarity Score', 'Reasoning'
        ])
        self.seen_first_codes = {}

    def reset(self):
        """Reset all DataFrames and tracking"""
        self.__init__()

    def process_mapping_results(self, mappings, response, elapsed_time, ...):
        """Process and deduplicate mapping results"""
        # Instance method instead of global function
        pass

    def get_dataframes(self):
        """Return dictionary of all DataFrames"""
        return {
            'ApiCall': self.df_api_call,
            'ApiMapping': self.df_api_mapping
        }

    def save_to_excel(self, filepath):
        """Export all DataFrames to Excel"""
        pass
```

**Files Affected**:
- `result_processor.py` - Major rewrite
- `input_handler.py` - Update imports and calls
- `batch_dispatcher.py` - Update imports and calls
- `streamlit_app.py` - Update imports and calls

**Migration Steps**:
1. Create `ResultProcessor` class
2. Move all functions to class methods
3. Update all imports in dependent files
4. Pass `ResultProcessor` instance through call chain
5. Test thoroughly

---

### 1.2 Fix Exception Handling (All Files)

**Problem**: Bare `except:` blocks hide real errors and make debugging difficult.

**Current Code (BAD)**:
```python
try:
    # some code
except:
    pass  # Swallows ALL errors including KeyboardInterrupt!
```

**Refactored (GOOD)**:
```python
import logging

logger = logging.getLogger(__name__)

try:
    # some code
except json.JSONDecodeError as e:
    logger.error(f"JSON parse error: {e}")
    raise ValueError(f"Invalid JSON response: {e}")
except FileNotFoundError as e:
    logger.error(f"File not found: {e}")
    raise
except PermissionError as e:
    logger.error(f"Permission denied: {e}")
    raise
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    raise
```

**Locations to Fix**:

| File | Line(s) | Current | Fix |
|------|---------|---------|-----|
| `input_handler.py` | 149 | `except:` | Specific exceptions |
| `input_handler.py` | 200 | `except:` | Specific exceptions |
| `input_handler.py` | 229 | `except:` | Specific exceptions |
| `api_mapping.py` | 128 | `except Exception` | Specific API exceptions |
| `result_processor.py` | 101 | `except:` | Specific exceptions |
| `streamlit_app.py` | 739, 743 | `except:` | Specific file exceptions |

---

### 1.3 Add Logging Module

**Problem**: Using `print()` everywhere provides no audit trail or log levels.

**Create New File**: `logger.py`

```python
"""
logger.py - Centralized logging configuration for MappingServices
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from colorama import Fore, Style

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colorama colors"""

    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelno, Fore.WHITE)
        record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
        record.msg = f"{color}{record.msg}{Style.RESET_ALL}"
        return super().format(record)


def setup_logger(
    name: str = "MappingService",
    level: int = logging.INFO,
    log_to_file: bool = True,
    log_dir: str = "logs"
) -> logging.Logger:
    """
    Set up and return a configured logger.

    Args:
        name: Logger name
        level: Logging level
        log_to_file: Whether to also log to file
        log_dir: Directory for log files

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(ColoredFormatter(
        '%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%H:%M:%S'
    ))
    logger.addHandler(console_handler)

    # File handler for audit trail
    if log_to_file:
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d')
        file_handler = logging.FileHandler(
            log_path / f"mapping_service_{timestamp}.log",
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s'
        ))
        logger.addHandler(file_handler)

    return logger


# Create default logger instance
logger = setup_logger()
```

**Usage in other files**:
```python
from logger import logger

# Instead of print()
logger.info("Processing started")
logger.warning("Low confidence mapping")
logger.error("API call failed")
logger.debug("Detailed debug info")
```

---

## Phase 2: Code Quality Improvements (Medium Priority)

### 2.1 Fix `config.py` - Remove Redundant Code

**DELETE** lines 48-54 (redundant initialization):
```python
# DELETE THIS BLOCK:
settings = get_settings.__func__()
api_key = get_api_key.__func__()
model = settings.get('model', 'gpt-4o-mini')
temperature = settings.get('temperature', 0.3)
top_p = settings.get('top_p', 0.9)
max_tokens = settings.get('max_tokens', 16000)
threshold = settings.get('threshold', 70)
```

**ADD** validation method:
```python
@classmethod
def validate(cls) -> list:
    """
    Validate all configuration values.

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # API Key validation
    if not cls.api_key:
        errors.append("API key is required")
    elif len(cls.api_key) < 20:
        errors.append("API key appears to be invalid (too short)")

    # Temperature validation
    if not 0.0 <= cls.temperature <= 1.0:
        errors.append(f"Temperature must be between 0.0 and 1.0 (got {cls.temperature})")

    # Top P validation
    if not 0.0 <= cls.top_p <= 1.0:
        errors.append(f"Top P must be between 0.0 and 1.0 (got {cls.top_p})")

    # Batch size validation
    if not 50 <= cls.max_batch_size <= 500:
        errors.append(f"Batch size must be between 50 and 500 (got {cls.max_batch_size})")

    # Threshold validation
    if not 0 <= cls.threshold <= 100:
        errors.append(f"Threshold must be between 0 and 100 (got {cls.threshold})")

    # Max tokens validation
    if not 1000 <= cls.max_tokens <= 128000:
        errors.append(f"Max tokens must be between 1000 and 128000 (got {cls.max_tokens})")

    return errors

@classmethod
def print_summary(cls, title: str = "Configuration", show_api_key: bool = False):
    """Print formatted configuration summary"""
    from colorama import Fore, Style

    print(f"\n{Fore.YELLOW}{'='*50}")
    print(f"{Fore.YELLOW}{title}")
    print(f"{Fore.YELLOW}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  Model:        {Fore.CYAN}{cls.model}")
    print(f"{Fore.WHITE}  Temperature:  {Fore.CYAN}{cls.temperature}")
    print(f"{Fore.WHITE}  Top P:        {Fore.CYAN}{cls.top_p}")
    print(f"{Fore.WHITE}  Max Tokens:   {Fore.CYAN}{cls.max_tokens:,}")
    print(f"{Fore.WHITE}  Threshold:    {Fore.CYAN}{cls.threshold}%")
    print(f"{Fore.WHITE}  Batch Size:   {Fore.CYAN}{cls.max_batch_size}")

    if show_api_key and cls.api_key:
        masked = cls.api_key[:8] + "..." + cls.api_key[-4:]
        print(f"{Fore.WHITE}  API Key:      {Fore.CYAN}{masked}")

    print(f"{Fore.YELLOW}{'='*50}{Style.RESET_ALL}\n")
```

---

### 2.2 Fix `optimization_utils.py` - Remove Dead Code

**Problem**: Identical branches that do the same thing.

**Current Code (DELETE)**:
```python
def create_compact_item(code, name, group_type):
    if group_type == "first":
        return {"c": code, "n": name}  # Same as else!
    else:
        return {"c": code, "n": name}  # Same as if!
```

**Refactored Code (NEW)**:
```python
"""
optimization_utils.py - Token optimization utilities for API calls

These utilities reduce token usage by 60-70% through abbreviated JSON keys.
"""

# Key mappings for compact format
COMPACT_KEYS = {
    "first_code": "fc",
    "first_name": "fn",
    "second_code": "sc",
    "second_name": "sn",
    "similarity_score": "ss",
    "reasoning": "r"
}

EXPANDED_KEYS = {v: k for k, v in COMPACT_KEYS.items()}


def create_compact_item(code: str, name: str) -> dict:
    """
    Create abbreviated JSON for token optimization.

    Args:
        code: Item code
        name: Item name

    Returns:
        Compact dictionary with abbreviated keys
    """
    return {"c": code, "n": name}


def expand_compact_result(item: dict) -> dict:
    """
    Expand abbreviated keys back to full names.

    Args:
        item: Dictionary with compact keys

    Returns:
        Dictionary with full key names
    """
    return {
        "first_code": item.get("fc", item.get("first_code", "")),
        "first_name": item.get("fn", item.get("first_name", "")),
        "second_code": item.get("sc", item.get("second_code")),
        "second_name": item.get("sn", item.get("second_name")),
        "similarity_score": item.get("ss", item.get("similarity_score", 0)),
        "reasoning": item.get("r", item.get("reasoning", ""))
    }


def compact_to_full_keys(data: dict) -> dict:
    """
    Convert any compact keys in a dictionary to full keys.

    Args:
        data: Dictionary potentially containing compact keys

    Returns:
        Dictionary with full key names
    """
    result = {}
    for key, value in data.items():
        full_key = EXPANDED_KEYS.get(key, key)
        result[full_key] = value
    return result
```

---

### 2.3 Fix Pandas Performance in `result_processor.py`

**Problem**: O(n²) performance from concat in loop.

**Current Code (SLOW)**:
```python
# This runs in O(n²) time!
for item in mappings:
    new_row = pd.DataFrame([{
        'First Group Code': item.get('first_code'),
        # ... more fields
    }])
    df_api_mapping = pd.concat([df_api_mapping, new_row], ignore_index=True)
```

**Refactored Code (FAST)**:
```python
def process_mapping_results(self, mappings, ...):
    """Process mappings with O(n) performance"""

    # Collect all rows first
    rows_to_add = []

    for item in mappings:
        first_code = item.get('first_code', '')
        score = item.get('similarity_score', 0)

        # Deduplication logic
        if first_code in self.seen_first_codes:
            existing_score = self.seen_first_codes[first_code]['score']
            if score <= existing_score:
                continue  # Skip lower score
            # Will update existing row later

        row_data = {
            'First Group Code': first_code,
            'First Group Name': item.get('first_name', ''),
            'Second Group Code': item.get('second_code'),
            'Second Group Name': item.get('second_name'),
            'Similarity Score': score,
            'Reasoning': item.get('reasoning', '')
        }

        rows_to_add.append(row_data)
        self.seen_first_codes[first_code] = {'score': score, 'data': row_data}

    # Single concat at end - O(n) instead of O(n²)
    if rows_to_add:
        new_df = pd.DataFrame(rows_to_add)
        self.df_api_mapping = pd.concat(
            [self.df_api_mapping, new_df],
            ignore_index=True
        )
```

---

### 2.4 Extract Duplicate Code - Configuration Printing

**Problem**: Same config printing code appears in 4+ files.

**Files with duplicate code**:
- `input_handler.py` (lines ~80-95)
- `batch_dispatcher.py` (lines ~180-195)
- `api_mapping.py` (lines ~40-55)
- `main.py` (lines ~20-35)

**Solution**: Use `Config.print_summary()` from Phase 2.1

**Before (in each file)**:
```python
print(f"{Fore.WHITE}  • Model: {Config.model}")
print(f"{Fore.WHITE}  • Temperature: {Config.temperature}")
print(f"{Fore.WHITE}  • Top P: {Config.top_p}")
# ... repeated 4 times
```

**After (in each file)**:
```python
Config.print_summary("API Configuration")
```

---

## Phase 3: Streamlit App Decomposition (Medium Priority)

### 3.1 Split `streamlit_app.py` into Modules

**Current**: 953 lines in single file (too large to maintain)

**New Structure**:
```
streamlit_app/
├── __init__.py              # Package init
├── app.py                   # Main entry point (~100 lines)
├── styles.py                # CSS styles (~150 lines)
├── session_state.py         # Session state management (~50 lines)
├── components/
│   ├── __init__.py
│   ├── console_capture.py   # StreamlitConsoleCapture class (~70 lines)
│   ├── sidebar.py           # Sidebar configuration (~100 lines)
│   └── stage_tracker.py     # Processing stage UI (~80 lines)
├── tabs/
│   ├── __init__.py
│   ├── input_tab.py         # File upload, prompt selection (~150 lines)
│   ├── processing_tab.py    # Processing UI (~200 lines)
│   ├── results_tab.py       # Results display (~150 lines)
│   └── analytics_tab.py     # Charts and statistics (~100 lines)
└── utils.py                 # Helper functions (~50 lines)
```

### Example Files:

**`streamlit_app/app.py`** (Main Entry):
```python
"""
Main Streamlit application entry point
"""
import streamlit as st
from .styles import apply_styles
from .session_state import initialize_session_state
from .components.sidebar import render_sidebar
from .tabs.input_tab import render_input_tab
from .tabs.processing_tab import render_processing_tab
from .tabs.results_tab import render_results_tab
from .tabs.analytics_tab import render_analytics_tab

# Page configuration
st.set_page_config(
    page_title="Mapping Medical Services",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application function"""
    # Apply custom styles
    apply_styles()

    # Initialize session state
    initialize_session_state()

    # Header
    st.title("🩺 Mapping Medical Services")
    st.markdown("### AI-Powered Mapping System with Batch Processing")

    # Sidebar
    render_sidebar()

    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📁 Input",
        "🔄 Processing",
        "📊 Results",
        "📈 Analytics"
    ])

    with tab1:
        render_input_tab()

    with tab2:
        render_processing_tab()

    with tab3:
        render_results_tab()

    with tab4:
        render_analytics_tab()

    # Footer
    render_footer()


def render_footer():
    """Render application footer"""
    from config import Config

    st.divider()
    st.markdown(
        f"""
        <div style='text-align: center; color: gray;'>
            Laboratory Mapping Service v2.0 |
            Mode: {st.session_state.get('selected_prompt_type', 'None')} |
            Model: {Config.model}
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
```

**`streamlit_app/styles.py`** (CSS Styles):
```python
"""
CSS styles for the Streamlit application
"""
import streamlit as st

def apply_styles():
    """Apply custom CSS styles to the application"""
    st.markdown(get_css(), unsafe_allow_html=True)


def get_css() -> str:
    """Return all CSS styles as a string"""
    return """
    <style>
        /* Button styles */
        .stButton>button {
            width: 100%;
            height: 50px;
            font-size: 18px;
        }

        /* Alert boxes */
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

        /* Processing header */
        .processing-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        /* Terminal styles */
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

        .terminal-body {
            padding: 15px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 13px;
            color: #00ff00;
            max-height: 350px;
            overflow-y: auto;
        }

        /* Stage cards */
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

        /* Status badges */
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
    </style>
    """
```

**`streamlit_app/tabs/input_tab.py`** (Input Tab):
```python
"""
Input tab for file upload and prompt selection
"""
import streamlit as st
import pandas as pd
from prompts import Prompts
from config import Config


def render_input_tab():
    """Render the complete input tab"""
    st.header("Data Input")

    col1, col2 = st.columns(2)

    with col1:
        render_file_upload()

    with col2:
        render_prompt_selection()

    st.divider()
    render_process_button()


def render_file_upload():
    """Render file upload section"""
    st.subheader("📄 Excel File")

    uploaded_file = st.file_uploader(
        "Upload Excel file with 'First Group' and 'Second Group' sheets",
        type=['xlsx', 'xls'],
        help="Excel file must contain two sheets: 'First Group' and 'Second Group'"
    )

    if uploaded_file:
        try:
            # Store file content
            st.session_state.uploaded_file_content = uploaded_file.read()
            uploaded_file.seek(0)

            # Preview
            excel_data = pd.ExcelFile(uploaded_file)
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            st.info(f"Sheets found: {', '.join(excel_data.sheet_names)}")

            # Show previews
            for sheet_name in ['First Group', 'Second Group']:
                if sheet_name in excel_data.sheet_names:
                    df = pd.read_excel(excel_data, sheet_name=sheet_name, header=None)
                    st.write(f"**{sheet_name} Preview:**")
                    st.dataframe(df.head().astype(str), width='stretch')
                    st.caption(f"Total rows: {len(df)}")

            excel_data.close()

        except Exception as e:
            st.error(f"Error reading Excel file: {str(e)}")


def render_prompt_selection():
    """Render prompt selection section"""
    st.subheader("📝 Prompt Selection")
    st.info("Select the type of mapping to load the appropriate prompt")

    # Button selection
    col1, col2, col3 = st.columns(3)

    buttons = [
        (col1, "🧪 Lab", "Lab"),
        (col2, "📷 Radiology", "Radiology"),
        (col3, "🔧 Service", "Service")
    ]

    for col, label, prompt_type in buttons:
        with col:
            if st.button(label, width='stretch', type="primary"):
                st.session_state.selected_prompt_type = prompt_type

    # Show selected prompt info
    if st.session_state.get('selected_prompt_type'):
        prompt_info = Prompts.get_prompt_info(st.session_state.selected_prompt_type)
        st.success(f"✅ Selected: **{prompt_info.get('icon', '')} {prompt_info.get('name')}**")

        if prompt_info.get('description'):
            st.caption(prompt_info['description'])


def render_process_button():
    """Render the main process button"""
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        can_process = (
            st.session_state.get('uploaded_file_content') and
            st.session_state.get('selected_prompt_type') and
            Config.api_key
        )

        if st.button(
            "🚀 Start Mapping Process",
            type="primary",
            width='stretch',
            disabled=not can_process
        ):
            if not Config.api_key:
                st.error("❌ Please enter your OpenAI API key in the sidebar")
            else:
                st.session_state.processing = True
                st.rerun()
```

---

## Phase 4: Architecture Improvements (Lower Priority)

### 4.1 Create Data Classes for Type Safety

**Create New File**: `models.py`

```python
"""
models.py - Data models for type safety and validation
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class GroupItem:
    """Represents an item in First or Second Group"""
    code: str
    name: str

    def to_compact(self) -> Dict[str, str]:
        """Convert to compact format for API"""
        return {"c": self.code, "n": self.name}

    def to_dict(self) -> Dict[str, str]:
        """Convert to standard dictionary"""
        return {"code": self.code, "name": self.name}


@dataclass
class MappingResult:
    """Represents a single mapping result"""
    first_code: str
    first_name: str
    second_code: Optional[str]
    second_name: Optional[str]
    similarity_score: int
    reasoning: str

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'MappingResult':
        """Create from API response (handles both compact and full format)"""
        return cls(
            first_code=data.get('fc', data.get('first_code', '')),
            first_name=data.get('fn', data.get('first_name', '')),
            second_code=data.get('sc', data.get('second_code')),
            second_name=data.get('sn', data.get('second_name')),
            similarity_score=data.get('ss', data.get('similarity_score', 0)),
            reasoning=data.get('r', data.get('reasoning', ''))
        )

    def to_dataframe_row(self) -> Dict[str, Any]:
        """Convert to DataFrame row format"""
        return {
            'First Group Code': self.first_code,
            'First Group Name': self.first_name,
            'Second Group Code': self.second_code,
            'Second Group Name': self.second_name,
            'Similarity Score': self.similarity_score,
            'Reasoning': self.reasoning
        }


@dataclass
class BatchResult:
    """Represents results from a single batch API call"""
    batch_number: int
    mappings: List[MappingResult]
    input_tokens: int
    output_tokens: int
    latency: float
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def mapping_count(self) -> int:
        return len(self.mappings)


@dataclass
class ProcessingStatistics:
    """Aggregate statistics for a processing run"""
    total_mappings: int = 0
    mapped_count: int = 0
    unmapped_count: int = 0
    avg_score: float = 0.0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_latency: float = 0.0
    batch_count: int = 0

    @property
    def total_tokens(self) -> int:
        return self.total_input_tokens + self.total_output_tokens

    def update_from_batch(self, batch: BatchResult):
        """Update statistics from a batch result"""
        self.batch_count += 1
        self.total_input_tokens += batch.input_tokens
        self.total_output_tokens += batch.output_tokens
        self.total_latency += batch.latency


@dataclass
class ProcessingConfig:
    """Configuration snapshot for a processing run"""
    model: str
    temperature: float
    top_p: float
    max_tokens: int
    threshold: int
    max_batch_size: int
    use_compact_json: bool
    abbreviate_keys: bool

    @classmethod
    def from_config(cls, config) -> 'ProcessingConfig':
        """Create from Config class"""
        return cls(
            model=config.model,
            temperature=config.temperature,
            top_p=config.top_p,
            max_tokens=config.max_tokens,
            threshold=config.threshold,
            max_batch_size=config.max_batch_size,
            use_compact_json=config.use_compact_json,
            abbreviate_keys=config.abbreviate_keys
        )
```

---

### 4.2 Add Retry Logic for API Calls

**Modify**: `api_mapping.py`

```python
"""
Add retry logic with exponential backoff for API calls
"""
import time
import logging
from functools import wraps
from openai import RateLimitError, APIConnectionError, APITimeoutError

logger = logging.getLogger(__name__)


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    retryable_exceptions: tuple = (RateLimitError, APIConnectionError, APITimeoutError)
):
    """
    Decorator for retry with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)
        exponential_base: Base for exponential backoff calculation
        retryable_exceptions: Tuple of exceptions to retry on
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except retryable_exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        logger.error(f"Max retries ({max_retries}) exceeded: {e}")
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        max_delay
                    )

                    logger.warning(
                        f"Retry {attempt + 1}/{max_retries} after {delay:.1f}s "
                        f"due to: {type(e).__name__}: {e}"
                    )
                    time.sleep(delay)

                except Exception as e:
                    # Non-retryable exception
                    logger.error(f"Non-retryable error: {type(e).__name__}: {e}")
                    raise

            # Should not reach here, but just in case
            raise last_exception

        return wrapper
    return decorator


# Usage in PerformMapping:
@retry_with_backoff(max_retries=3, base_delay=1.0)
def PerformMapping(first_group, second_group, prompt, verbose=True):
    """
    Perform mapping with automatic retry on transient failures.
    """
    # existing implementation
    pass
```

---

## Phase 5: Files to Delete

| Item | Location | Reason |
|------|----------|--------|
| Inline CSS | `streamlit_app.py` lines 30-202 | Move to `styles.py` |
| Duplicate config printing | `input_handler.py` ~80-95 | Use `Config.print_summary()` |
| Duplicate config printing | `batch_dispatcher.py` ~180-195 | Use `Config.print_summary()` |
| Duplicate config printing | `api_mapping.py` ~40-55 | Use `Config.print_summary()` |
| Redundant `group_type` branches | `optimization_utils.py` | Dead code |
| Redundant initialization | `config.py` lines 48-54 | Duplicate of class attributes |
| Bare `except:` blocks | Multiple files | Replace with specific handlers |

---

## Implementation Order

| Phase | Task | Effort | Risk | Dependencies |
|-------|------|--------|------|--------------|
| 1.3 | Add logging module | 2h | Low | None |
| 1.2 | Fix exception handling | 2h | Low | 1.3 |
| 2.1 | Fix config.py | 1h | Low | None |
| 2.2 | Fix optimization_utils.py | 30m | Low | None |
| 2.4 | Extract duplicate code | 2h | Low | 2.1 |
| 1.1 | Remove global state | 4h | Medium | 1.2, 1.3 |
| 2.3 | Fix pandas performance | 1h | Low | 1.1 |
| 4.1 | Create data classes | 2h | Low | None |
| 4.2 | Add retry logic | 2h | Low | 1.2 |
| 3.1 | Split streamlit_app.py | 6h | Medium | All above |

**Total Estimated Effort**: ~22 hours

---

## Summary

| Category | Count | Details |
|----------|-------|---------|
| **Files to Modify** | 8 | All core Python files |
| **New Files to Create** | 4 | `logger.py`, `models.py`, `styles.py`, `session_state.py` |
| **Code to Delete** | ~300 lines | Duplicates and dead code |
| **Files to Split** | 1 | `streamlit_app.py` → 10 files |

---

## Testing Checklist

After each phase, verify:

- [ ] Application starts without errors
- [ ] File upload works correctly
- [ ] All three prompt types load
- [ ] Processing completes successfully
- [ ] Results display correctly
- [ ] Excel export works
- [ ] Analytics charts render
- [ ] No console errors or warnings

---

## Notes

- Always create a backup before major changes
- Test each phase independently before moving to the next
- Keep the original files until new implementation is verified
- Update imports incrementally to avoid circular dependencies
