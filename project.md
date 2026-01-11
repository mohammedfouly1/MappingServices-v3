# Medical Services Mapping - Complete Project Documentation

> **Version**: 2.1.0
> **Last Updated**: January 2026
> **Status**: Production Ready

---

## Table of Contents

1. [Project Overview](#-project-overview)
2. [Key Features](#-key-features)
3. [Architecture](#-architecture)
4. [File Structure](#-file-structure)
5. [Module Documentation](#-module-documentation)
6. [Prompt System](#-prompt-system)
7. [Data Flow](#-data-flow)
8. [Configuration](#-configuration)
9. [Web Interface](#-web-interface-streamlit)
10. [API Integration](#-api-integration)
11. [Batch Processing](#-batch-processing)
12. [Token Optimization](#-token-optimization)
13. [Result Processing](#-result-processing)
14. [Deployment](#-deployment)
15. [Usage Guide](#-usage-guide)
16. [Best Practices](#-best-practices)
17. [Dependencies](#-dependencies)
18. [Troubleshooting](#-troubleshooting)

---

## Overview

The **Medical Services Mapping System** is an AI-powered application that intelligently maps medical service items between two different groups (datasets) using OpenAI's GPT models. It supports three specialized mapping types:

| Type | Icon | Description |
|------|------|-------------|
| **Laboratory** | Lab | Maps laboratory test items based on medical knowledge |
| **Radiology** | X-Ray | Maps radiological examinations based on imaging details |
| **Service** | Wrench | Maps general medical services |

### Core Capabilities

- **AI-Powered Mapping**: Uses GPT-4o/GPT-4 for intelligent semantic matching
- **Intelligent Batching**: Automatically optimizes batch sizes for large datasets
- **Smart Deduplication**: Keeps highest similarity scores, removes duplicates
- **Token Optimization**: Reduces API costs by 60-70% through compact JSON
- **Dual Interface**: CLI for automation, Streamlit Web UI for interactive use
- **Real-time Monitoring**: Live console output, progress tracking, analytics
- **Multi-format Export**: Excel, CSV, and JSON output formats

---

## Key Features

### 1. Three Specialized Mapping Types

```
Lab (Laboratory)
   - Focuses on: technique, approach, substrate, organism, anatomical site
   - Example: Maps "CBC" to "Complete Blood Count"

Radiology
   - Focuses on: anatomical site, contrast use, equipment, radiation dose
   - Example: Maps "Chest X-Ray" to "Thoracic Radiograph"

Service
   - Focuses on: procedure type, equipment, invasiveness, preparation
   - Example: Maps "ECG" to "Electrocardiogram"
```

### 2. Intelligent Batch Processing

- Automatically detects when batching is needed
- Calculates optimal batch sizes to minimize API calls
- Manages timing between batches to avoid rate limits
- Accumulates and deduplicates results across batches

### 3. Smart Deduplication

- Ensures one mapping per First Group Code
- Keeps highest similarity score when duplicates found
- Maintains original order of appearance
- Works seamlessly across multiple batches

### 4. Token Optimization

- Compact JSON format reduces tokens by 60-70%
- Abbreviated keys (`c`/`n` instead of `code`/`name`)
- Efficient prompt structuring
- Automatic format selection based on configuration

### 5. Real-time Monitoring

- Live console output with color-coded messages
- Processing stages with visual indicators
- Progress bars and status badges
- Token usage and performance metrics

---

## Architecture

```
                           User Interface Layer
    +----------------------------------------------------------+
    |                                                          |
    |   +------------------+         +---------------------+   |
    |   |    main.py       |         |  streamlit_app.py   |   |
    |   |   (CLI Entry)    |         |   (Web UI Entry)    |   |
    |   +--------+---------+         +---------+-----------+   |
    |            |                             |               |
    +------------|-----------------------------|--------------+
                 |                             |
                 v                             v
    +----------------------------------------------------------+
    |                   Orchestration Layer                     |
    |                                                          |
    |   +--------------------------------------------------+   |
    |   |              input_handler.py                     |   |
    |   |  - Reads Excel files (First/Second Group)        |   |
    |   |  - Validates data integrity                       |   |
    |   |  - Creates full and compact JSON formats          |   |
    |   |  - Coordinates processing pipeline                |   |
    |   +--------------------------------------------------+   |
    |                          |                               |
    +--------------------------|-------------------------------+
                               v
    +----------------------------------------------------------+
    |                   Processing Layer                        |
    |                                                          |
    |   +--------------------------------------------------+   |
    |   |            batch_dispatcher.py                    |   |
    |   |  - Calculates optimal batch strategy              |   |
    |   |  - Splits large datasets into chunks              |   |
    |   |  - Manages API call scheduling                    |   |
    |   |  - Handles wait times between batches             |   |
    |   +--------------------------------------------------+   |
    |                          |                               |
    +--------------------------|-------------------------------+
                               v
    +----------------------------------------------------------+
    |                      API Layer                            |
    |                                                          |
    |   +--------------------------------------------------+   |
    |   |              api_mapping.py                       |   |
    |   |  - Formats prompts (compact/standard)             |   |
    |   |  - Calls OpenAI API                               |   |
    |   |  - Parses responses with fallback strategies      |   |
    |   |  - Handles errors and retries                     |   |
    |   +--------------------------------------------------+   |
    |                          |                               |
    +--------------------------|-------------------------------+
                               v
    +----------------------------------------------------------+
    |                   Output Layer                            |
    |                                                          |
    |   +--------------------------------------------------+   |
    |   |            result_processor.py                    |   |
    |   |  - Deduplicates mappings by First Group Code     |   |
    |   |  - Creates pandas DataFrames                      |   |
    |   |  - Generates statistics and analytics             |   |
    |   |  - Exports to Excel/CSV/JSON                      |   |
    |   +--------------------------------------------------+   |
    |                                                          |
    +----------------------------------------------------------+

    +----------------------------------------------------------+
    |                   Support Modules                         |
    |                                                          |
    |   +----------------+  +----------------+  +-----------+  |
    |   |   config.py    |  |   prompts.py   |  | optim...  |  |
    |   | Configuration  |  | Prompt Storage |  | Token Opt |  |
    |   +----------------+  +----------------+  +-----------+  |
    |                                                          |
    +----------------------------------------------------------+
```

---

## File Structure

```
MappingServices/
│
├── Core Entry Points
│   ├── main.py                    # CLI entry point (54 lines)
│   └── streamlit_app.py           # Web UI entry point (800+ lines)
│
├── Processing Modules
│   ├── input_handler.py           # Input processing & validation (347 lines)
│   ├── batch_dispatcher.py        # Batch management & optimization (345 lines)
│   ├── api_mapping.py             # OpenAI API integration (242 lines)
│   └── result_processor.py        # Deduplication & DataFrames (352 lines)
│
├── Configuration & Utilities
│   ├── config.py                  # Configuration management (62 lines)
│   ├── prompts.py                 # Unified prompt storage (165 lines)
│   └── optimization_utils.py      # Token optimization utilities (30 lines)
│
├── Documentation
│   ├── project.md                 # This documentation file
│   └── REFACTORING_PLAN.md        # Future improvements plan
│
├── Configuration Files
│   └── requirements.txt           # Python dependencies (7 packages)
│
└── Runtime Directories (generated)
    ├── .venv/                     # Virtual environment
    ├── __pycache__/               # Python cache
    └── logs/                      # Log files (if enabled)
```

---

## Module Documentation

### 1. config.py - Configuration Management

**Purpose**: Centralized configuration with cloud/local dual support

**Key Features**:
- Streamlit Cloud integration using `st.secrets`
- Environment variable fallback for local development
- Dynamic configuration loading
- Support for both cloud and local deployments

**Configuration Options**:

| Setting | Default | Description |
|---------|---------|-------------|
| `api_key` | (from env) | OpenAI API key |
| `model` | `gpt-4o` | Model to use (gpt-4o, gpt-4o-mini, gpt-4) |
| `temperature` | `0.2` | Response randomness (0.0-1.0) |
| `top_p` | `0.9` | Nucleus sampling parameter |
| `max_tokens` | `16000` | Maximum response tokens |
| `threshold` | `80` | Minimum similarity score (0-100) |
| `max_batch_size` | `200` | Maximum items per batch |
| `wait_between_batches` | `120` | Seconds between API calls |
| `use_compact_json` | `True` | Enable token optimization |
| `abbreviate_keys` | `True` | Use short key names |

**Usage**:
```python
from config import Config

# Access settings
model = Config.model
api_key = Config.api_key

# Modify at runtime
Config.temperature = 0.3
Config.threshold = 70
```

---

### 2. prompts.py - Unified Prompt Management

**Purpose**: Centralized storage for all mapping prompts (replaces separate .txt files)

**Available Prompt Types**:

| Type | Class Constant | Focus Areas |
|------|----------------|-------------|
| Lab | `Prompts.LAB` | technique, approach, substrate, organism, anatomical site, test type |
| Radiology | `Prompts.RADIOLOGY` | anatomical site, contrast, equipment, radiation dose, positioning |
| Service | `Prompts.SERVICE` | procedure type, equipment, invasiveness, preparation |

**Key Methods**:

```python
from prompts import Prompts

# Get prompt text
lab_prompt = Prompts.get("Lab")
rad_prompt = Prompts.get("Radiology")
svc_prompt = Prompts.get("Service")

# Get all available types
types = Prompts.get_all_types()  # ["Lab", "Radiology", "Service"]

# Get prompt with metadata
info = Prompts.get_prompt_info("Lab")
# Returns: {
#     "name": "Laboratory Mapping",
#     "icon": "Lab",
#     "description": "Maps laboratory test items...",
#     "focus_areas": [...],
#     "text": "...",
#     "length": 1234
# }
```

**Prompt Structure** (All three prompts follow this format):
1. Receive two JSON arrays (First Group, Second Group)
2. Map every item from First Group to most similar in Second Group
3. Use medical knowledge for semantic matching
4. Output all First Group items (even without matches)
5. Provide similarity score (1-100) and reasoning

---

### 3. input_handler.py - Data Input Processing

**Purpose**: Excel file processing, validation, and workflow coordination

**Main Functions**:

#### `SendInputParts(excel_path, prompt_path, verbose=True, ...)`
Main orchestrator function that coordinates the entire processing pipeline.

**Steps**:
1. Load Excel file with pandas
2. Read "First Group" sheet (Code, Name columns)
3. Read "Second Group" sheet (Code, Name columns)
4. Read prompt text file
5. Validate all data is present
6. Create full and compact JSON formats
7. Send to Batch Dispatcher

**Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `excel_path` | str | Required | Path to Excel file |
| `prompt_path` | str | Required | Path to prompt text file |
| `verbose` | bool | True | Enable detailed output |
| `model` | str | None | Override Config.model |
| `temperature` | float | None | Override Config.temperature |
| `top_p` | float | None | Override Config.top_p |
| `max_tokens` | int | None | Override Config.max_tokens |

#### `SaveResults(results, output_path)`
Saves processing results to files.

**Outputs**:
- JSON file with mappings and statistics
- Excel file with multiple sheets (via result_processor)

---

### 4. batch_dispatcher.py - Intelligent Batching

**Purpose**: Optimize batch splitting to minimize API calls while maximizing efficiency

**Key Algorithm**: `calculate_optimal_batch_split(n1, n2, max_batch_size)`

Finds optimal split `(f, s)` where `f + s = max_batch_size` that minimizes:
```
total_batches = ceil(n1/f) × ceil(n2/s)
```

**Example**:
```
Input: n1=300, n2=400, max_batch=200

Naive approach:
  - Process all 300 × 400 = many combinations

Optimal calculation:
  - f=86, s=114 (where 86+114=200)
  - Results in 4×4=16 efficient batches
```

#### `Dispatcher(first_group_list, second_group_list, prompt, ...)`

Routes to appropriate processing based on dataset size:
- **Small datasets**: Direct processing (no batching)
- **Large datasets**: Calculate batch plan, process sequentially

**Batch Processing Flow**:
1. Calculate optimal split
2. Divide First Group into `ceil(n1/f)` parts
3. Divide Second Group into `ceil(n2/s)` parts
4. Process each combination
5. Wait between batches (rate limiting)
6. Accumulate results

---

### 5. api_mapping.py - OpenAI Integration

**Purpose**: Call OpenAI API with optimized prompts and handle responses

#### `PerformMapping(first_group, second_group, prompt, ...)`

**Features**:
- Dual format support (compact/standard JSON)
- Token optimization through abbreviated keys
- Response parsing with fallback strategies
- Error handling and reporting

**Compact Format Example**:
```json
// Standard format (~4 tokens per item)
{"First Group Code": "123", "First Group Name": "Blood Test"}

// Compact format (~1.5 tokens per item)
{"c": "123", "n": "Blood Test"}

// Result: ~60% token reduction
```

**Response Parsing**:
1. Attempt direct JSON parsing
2. If failed, use regex extraction
3. Handle both object wrapper and direct array formats
4. Expand compact keys if abbreviation was used

---

### 6. result_processor.py - Data Processing & Deduplication

**Purpose**: Process API results, deduplicate mappings, create DataFrames, generate statistics

**Global DataFrames** (managed by module):

#### ApiCall DataFrame
Tracks all API calls with performance metrics:

| Column | Description |
|--------|-------------|
| Batch | Batch number |
| First Group Count | Items in first group |
| Second Group Count | Items in second group |
| Input Tokens | Tokens sent to API |
| Output Tokens | Tokens received |
| Total Tokens | Sum of input + output |
| Latency | Response time (seconds) |

#### ApiMapping DataFrame
Deduplicated mapping results:

| Column | Description |
|--------|-------------|
| First Group Code | Code from first group |
| First Group Name | Name from first group |
| Second Group Code | Matched code (or null) |
| Second Group Name | Matched name (or null) |
| Similarity Score | AI confidence (0-100) |
| Reasoning | Explanation for match |

**Deduplication Algorithm**:
1. Track seen First Group Codes
2. For each new mapping:
   - If code not seen: Add to results
   - If code seen with lower score: Update with higher score
   - If code seen with higher score: Skip
3. Maintain original order of first occurrence

**Key Functions**:
```python
from result_processor import (
    reset_dataframes,       # Clear all DataFrames
    get_dataframes,         # Get current DataFrames
    ProcessMappingResults,  # Process new batch
    display_dataframe_summary,  # Print statistics
    save_dataframes_to_excel    # Export to Excel
)
```

---

### 7. optimization_utils.py - Token Optimization

**Purpose**: Reduce API token usage through efficient formatting

**Functions**:

```python
from optimization_utils import create_compact_item, expand_compact_result

# Create compact item for API call
item = create_compact_item("A001", "Blood Test")
# Result: {"c": "A001", "n": "Blood Test"}

# Expand compact result from API
expanded = expand_compact_result({
    "fc": "A001", "fn": "Blood Test",
    "sc": "B101", "sn": "CBC",
    "ss": 85, "r": "Similar tests"
})
# Result: {
#     "first_code": "A001",
#     "first_name": "Blood Test",
#     "second_code": "B101",
#     "second_name": "CBC",
#     "similarity_score": 85,
#     "reasoning": "Similar tests"
# }
```

**Token Savings**:
| Format | Tokens per Item | Savings |
|--------|-----------------|---------|
| Standard | ~4 tokens | Baseline |
| Compact | ~1.5 tokens | 60-70% |

---

## Prompt System

### Prompt Output Format

All three prompts expect the AI to return results in this JSON structure:

```json
{
  "mappings": [
    {
      "first_code": "A001",
      "first_name": "Blood Glucose Test",
      "second_code": "B101",
      "second_name": "Glucose Level Analysis",
      "similarity_score": 92,
      "reasoning": "Both tests measure blood glucose levels using similar methodologies"
    },
    {
      "first_code": "A002",
      "first_name": "Unknown Test",
      "second_code": null,
      "second_name": null,
      "similarity_score": 0,
      "reasoning": "No matching test found in second group"
    }
  ]
}
```

### Compact Output Format (when optimization enabled)

```json
{
  "mappings": [
    {
      "fc": "A001",
      "fn": "Blood Glucose Test",
      "sc": "B101",
      "sn": "Glucose Level Analysis",
      "ss": 92,
      "r": "Both tests measure blood glucose levels"
    }
  ]
}
```

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         INPUT                                    │
│                                                                 │
│   Excel File                          Prompt Selection          │
│   ┌──────────────────┐               ┌──────────────────┐      │
│   │ Sheet: First Group│               │  Lab            │      │
│   │ Code | Name       │               │  Radiology       │      │
│   ├──────────────────┤               │  Service         │      │
│   │ Sheet: Second Group               └──────────────────┘      │
│   │ Code | Name       │                                         │
│   └──────────────────┘                                         │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PROCESSING                                  │
│                                                                 │
│   1. Input Handler                                              │
│      └─→ Read Excel → Validate → Create JSON                   │
│                                                                 │
│   2. Batch Dispatcher                                           │
│      └─→ Calculate optimal batches → Schedule API calls        │
│                                                                 │
│   3. API Mapping (per batch)                                    │
│      └─→ Format prompt → Call OpenAI → Parse response          │
│                                                                 │
│   4. Result Processor                                           │
│      └─→ Deduplicate → Create DataFrames → Statistics          │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         OUTPUT                                   │
│                                                                 │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│   │   Excel     │  │    CSV      │  │    JSON     │            │
│   │  (4 sheets) │  │ (mappings)  │  │ (full data) │            │
│   └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
│   Excel Sheets:                                                 │
│   1. API_Calls - Performance metrics per batch                 │
│   2. Mappings - Deduplicated results                           │
│   3. Parameters - Configuration used                           │
│   4. Summary - Aggregate statistics                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...your-key-here...

# Optional (can also set in Streamlit UI)
MODEL=gpt-4o
TEMPERATURE=0.2
MAX_TOKENS=16000
```

### Streamlit Secrets (for cloud deployment)

Create `.streamlit/secrets.toml`:

```toml
OPENAI_API_KEY = "sk-...your-key-here..."

[settings]
model = "gpt-4o"
temperature = 0.2
top_p = 0.9
max_tokens = 16000
threshold = 80
```

### Configuration Priority

1. Streamlit UI settings (highest priority)
2. Streamlit secrets (`.streamlit/secrets.toml`)
3. Environment variables
4. Default values in `config.py` (lowest priority)

---

## Web Interface (Streamlit)

### Tab 1: Input

**Features**:
- Drag-and-drop Excel file upload
- Automatic sheet detection and preview
- Prompt type selection (Lab/Radiology/Service buttons)
- Data validation before processing
- Prompt preview and focus areas display

### Tab 2: Processing

**Features**:
- Styled gradient header with current task info
- Visual processing stages with status indicators:
  1. Initializing & Loading Data
  2. Preparing Batches
  3. Processing with AI
  4. Finalizing Results
- Configuration summary panel
- Progress bar with status badges
- Terminal-style console output with:
  - macOS-style window decorations
  - Color-coded log messages
  - Timestamps on each line
- Results summary with metrics

### Tab 3: Results

**Features**:
- Interactive DataFrame display
- Filter by mapped/unmapped status
- Filter by minimum similarity score
- Download buttons:
  - Excel (full export with all sheets)
  - CSV (mappings only)
  - JSON (complete results with metadata)

### Tab 4: Analytics

**Features**:
- Score distribution histogram (Plotly)
- Mapping status pie chart
- API call statistics:
  - Total calls
  - Average latency
  - Total tokens used
- Token usage over time chart

### Sidebar Configuration

All settings adjustable in real-time:
- API Key (password input)
- Model selection dropdown
- Temperature slider (0.0-1.0)
- Top P slider (0.1-1.0)
- Max tokens input
- Similarity threshold slider
- Batch size input
- Wait time between batches
- Optimization toggles

---

## API Integration

### Supported Models

| Model | Speed | Quality | Cost | Recommended For |
|-------|-------|---------|------|-----------------|
| gpt-4o | Fast | Excellent | Medium | Production use |
| gpt-4o-mini | Very Fast | Good | Low | Testing, high volume |
| gpt-4 | Slow | Excellent | High | Critical mappings |
| gpt-3.5-turbo | Fast | Moderate | Very Low | Development only |

### Rate Limiting

The system handles rate limiting through:
- Configurable wait time between batches (default: 120s)
- Automatic batch size optimization
- Token-aware request sizing

### Error Handling

| Error Type | Handling |
|------------|----------|
| Rate limit | Wait and retry |
| Invalid response | Fallback parsing |
| API timeout | Log and continue |
| Auth failure | Display error, stop |

---

## Batch Processing

### When Batching Occurs

Batching is triggered when:
```
first_group_count + second_group_count > max_batch_size
```

### Batch Optimization Algorithm

```python
def calculate_optimal_batch_split(n1, n2, max_batch_size):
    """
    Find (f, s) where f + s = max_batch_size
    that minimizes: ceil(n1/f) * ceil(n2/s)
    """
    best_split = None
    min_batches = float('inf')

    for f in range(1, max_batch_size):
        s = max_batch_size - f
        total = ceil(n1/f) * ceil(n2/s)
        if total < min_batches:
            min_batches = total
            best_split = (f, s)

    return best_split
```

### Example Batch Calculation

```
Input:
  - First Group: 300 items
  - Second Group: 400 items
  - Max Batch Size: 200

Calculation:
  - Optimal split: f=86, s=114
  - First Group batches: ceil(300/86) = 4
  - Second Group batches: ceil(400/114) = 4
  - Total batches: 4 × 4 = 16

Processing:
  Batch 1: First[0:86] × Second[0:114]
  Batch 2: First[0:86] × Second[114:228]
  ...
  Batch 16: First[258:300] × Second[342:400]
```

---

## Token Optimization

### Compact JSON Keys

| Full Key | Compact Key |
|----------|-------------|
| `first_code` | `fc` |
| `first_name` | `fn` |
| `second_code` | `sc` |
| `second_name` | `sn` |
| `similarity_score` | `ss` |
| `reasoning` | `r` |

### Token Savings Calculation

```
Standard item: {"code": "A001", "name": "Blood Test"}
  = ~15 characters = ~4 tokens

Compact item: {"c": "A001", "n": "Blood Test"}
  = ~10 characters = ~2.5 tokens

Savings: 37.5% per item

With full mapping result:
  Standard: ~60 tokens per mapping
  Compact: ~25 tokens per mapping
  Savings: ~60%
```

---

## Result Processing

### Deduplication Rules

1. **First occurrence wins** (for order)
2. **Highest score wins** (for duplicates)
3. **Threshold filtering** (scores below threshold marked as unmapped)

### Statistics Generated

| Metric | Description |
|--------|-------------|
| Total Mappings | Count of all mapping attempts |
| Mapped Items | Items with valid matches |
| Unmapped Items | Items without matches |
| Average Score | Mean similarity score |
| Total Tokens | API token consumption |
| Total Latency | Processing time |

### Excel Export Structure

**Sheet 1: API_Calls**
```
| Batch | First Count | Second Count | Input Tokens | Output Tokens | Latency |
|-------|-------------|--------------|--------------|---------------|---------|
| 1     | 86          | 114          | 2500         | 1800          | 3.2s    |
```

**Sheet 2: Mappings**
```
| First Code | First Name | Second Code | Second Name | Score | Reasoning |
|------------|------------|-------------|-------------|-------|-----------|
| A001       | Blood Test | B101        | CBC         | 85    | Similar   |
```

**Sheet 3: Parameters**
```
| Parameter   | Value     |
|-------------|-----------|
| Model       | gpt-4o    |
| Temperature | 0.2       |
| Threshold   | 80        |
```

**Sheet 4: Summary**
```
| Metric          | Value |
|-----------------|-------|
| Total Mappings  | 150   |
| Mapped Items    | 142   |
| Average Score   | 78.5  |
```

---

## Deployment

### Local Development

```bash
# 1. Clone/download project
cd MappingServices

# 2. Create virtual environment
python -m venv .venv

# 3. Activate environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set API key
# Windows:
set OPENAI_API_KEY=sk-...
# macOS/Linux:
export OPENAI_API_KEY=sk-...

# 6. Run CLI
python main.py

# 7. Or run Web UI
streamlit run streamlit_app.py
```

### Streamlit Cloud Deployment

1. Push code to GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Add secrets in Streamlit Cloud dashboard:
   ```toml
   OPENAI_API_KEY = "sk-..."
   ```
5. Deploy

### Docker Deployment (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501"]
```

---

## Usage Guide

### Input Excel Format

**Required Sheets**:

Sheet: `First Group`
```
| Column A (Code) | Column B (Name)      |
|-----------------|----------------------|
| A001            | Complete Blood Count |
| A002            | Urinalysis           |
| A003            | Liver Function Test  |
```

Sheet: `Second Group`
```
| Column A (Code) | Column B (Name)       |
|-----------------|-----------------------|
| B101            | CBC Analysis          |
| B102            | Urine Examination     |
| B103            | Hepatic Panel         |
```

**Notes**:
- No header row required (first row is data)
- Empty rows are automatically skipped
- Column order must be Code, then Name

### CLI Usage

```bash
# Basic usage
python main.py

# With custom paths (modify config.py first)
# Set Config.excel_path and Config.prompt_path

# Output:
# - Console progress and statistics
# - JSON results file
# - Excel results file
```

### Web UI Usage

1. **Start application**: `streamlit run streamlit_app.py`
2. **Configure settings** in sidebar (API key, model, etc.)
3. **Upload Excel file** in Input tab
4. **Select prompt type** (Lab, Radiology, or Service)
5. **Click "Start Mapping Process"**
6. **Monitor progress** in Processing tab
7. **View and download results** in Results tab
8. **Analyze performance** in Analytics tab

---

## Best Practices

### For Large Datasets (1000+ items)

```
Recommended Settings:
- Batch Size: 150-200
- Wait Time: 120-180 seconds
- Enable Compact JSON: Yes
- Enable Abbreviated Keys: Yes
- Model: gpt-4o-mini (for cost)
```

### For High Accuracy

```
Recommended Settings:
- Model: gpt-4o or gpt-4
- Temperature: 0.1-0.2
- Threshold: 70-80
- Review unmapped items manually
```

### For Cost Optimization

```
Recommended Settings:
- Enable all optimizations
- Use gpt-4o-mini for testing
- Monitor token usage in Analytics
- Batch similar requests together
```

### For Production

```
Recommended Settings:
- Validate input data before processing
- Use appropriate threshold (70-85)
- Export results to Excel for review
- Keep logs for audit trail
```

---

## Dependencies

### Required Packages

```
streamlit>=1.28.0     # Web framework
pandas>=1.3.0         # Data processing
openai>=1.0.0         # AI integration
colorama>=0.4.4       # Console colors
openpyxl>=3.0.0       # Excel handling
plotly>=5.17.0        # Visualizations
python-dotenv>=0.19.0 # Environment variables
```

### Python Version

- **Minimum**: Python 3.9
- **Recommended**: Python 3.11+

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "API key not set" | Missing OPENAI_API_KEY | Set in environment or sidebar |
| "Sheet not found" | Wrong sheet names | Use "First Group" and "Second Group" |
| "Rate limit exceeded" | Too many requests | Increase wait time between batches |
| "Invalid response" | API returned unexpected format | Check model and temperature |
| "Out of memory" | Dataset too large | Reduce batch size |

### Error Messages

```
"Failed to load prompt"
→ Check prompt type is one of: Lab, Radiology, Service

"No data in First Group"
→ Ensure Excel has data in First Group sheet

"API call failed"
→ Check API key is valid and has credits

"JSON parse error"
→ Model may need lower temperature for consistent output
```

### Getting Help

1. Check this documentation
2. Review console output for specific errors
3. Check Streamlit logs (terminal window)
4. Verify Excel file format matches requirements

---

## Status Indicators

```
Console Output Colors:
✓ Green   - Success
✗ Red     - Error
⚠ Yellow  - Warning
• White   - Information
═ Magenta - Section separator
→ Cyan    - Mapping result

Web UI Badges:
🟢 Running  - Processing in progress
🟢 Success  - Completed successfully
🔴 Error    - Failed with error
⏳ Pending  - Waiting to start
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.1.0 | Jan 2026 | Added styled Processing tab, terminal UI |
| 2.0.0 | Nov 2024 | Added prompts.py, unified prompt management |
| 1.5.0 | Oct 2024 | Added Streamlit web interface |
| 1.0.0 | Sep 2024 | Initial CLI release |

---

## License

MIT License - See LICENSE file for details.

---

## Contact

For issues and feature requests, please create an issue in the project repository.
