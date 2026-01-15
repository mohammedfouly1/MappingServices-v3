# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Medical Services Mapping System - An AI-powered application that maps medical service items between two datasets using OpenAI/OpenRouter APIs. The system supports three specialized mapping types: Laboratory, Radiology, and Service.

**Key capabilities**: Intelligent batching, smart deduplication, token optimization (60-70% reduction), dual interface (CLI + Streamlit Web UI).

## Common Commands

### Setup and Installation
```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Set API keys (required)
set OPENAI_API_KEY=sk-...  # Windows
export OPENAI_API_KEY=sk-...  # macOS/Linux
```

### Running the Application
```bash
# Run CLI version
python main.py

# Run Streamlit web UI (primary interface)
streamlit run streamlit_app.py

# Access web UI at: http://localhost:8501
```

### Development
```bash
# No test suite currently exists
# Manual testing through Streamlit UI or CLI

# Check Python syntax
python -m py_compile <filename>.py
```

## Architecture

### Data Flow (High-Level)
```
User Input → Input Handler → Batch Dispatcher → API Mapping → Result Processor → Output
```

**Layered Architecture**:
1. **User Interface Layer**: `main.py` (CLI) and `streamlit_app.py` (Web UI)
2. **Orchestration Layer**: `input_handler.py` - coordinates the entire pipeline
3. **Processing Layer**: `batch_dispatcher.py` - intelligent batching and API call scheduling
4. **API Layer**: `api_mapping.py` - formats prompts, calls OpenAI/OpenRouter, parses responses
5. **Output Layer**: `result_processor.py` - deduplication and DataFrame creation
6. **Support Modules**: `config.py`, `prompts.py`, `optimization_utils.py`

### Key Architectural Patterns

**1. Multi-Provider API Support**
- Supports both OpenAI and OpenRouter providers
- Provider selection via `Config.provider` ("OpenAI" or "OpenRouter")
- Separate API keys: `Config.api_key` (OpenAI) and `Config.openrouter_api_key` (OpenRouter)
- OpenRouter uses OpenAI-compatible API with custom base URL

**2. Batch Processing Algorithm**
- Automatically calculates optimal batch splits to minimize API calls
- Algorithm: Find `(f, s)` where `f + s = max_batch_size` that minimizes `ceil(n1/f) × ceil(n2/s)`
- Implemented in `batch_dispatcher.py::calculate_optimal_batch_split()`
- Handles large datasets by splitting First Group and Second Group into optimal chunks

**3. Deduplication Strategy**
- Keeps ONE mapping per First Group Code (primary key)
- When duplicates exist, keeps highest similarity score
- Maintains original order of first occurrence
- Implemented in `result_processor.py::ProcessMappingResults()`

**4. Token Optimization**
- Uses compact JSON format with abbreviated keys to reduce tokens by 60-70%
- Standard: `{"first_code": "A001", "first_name": "Test"}` (~4 tokens)
- Compact: `{"fc": "A001", "fn": "Test"}` (~1.5 tokens)
- Controlled by `Config.use_compact_json` and `Config.abbreviate_keys`

**5. Prompt System**
- Unified prompt storage in `prompts.py` (replaced separate .txt files)
- Three specialized prompts: Lab, Radiology, Service
- Access via `Prompts.get(prompt_type)` or `Prompts.get_prompt_info(prompt_type)`
- Each prompt focuses on domain-specific matching criteria

## Critical Code Patterns

### Global State Warning (IMPORTANT)
`result_processor.py` uses **module-level global variables** for DataFrames:
- `df_api_call` - tracks API call metrics
- `df_api_mapping` - stores mapping results
- `seen_first_codes` - deduplication tracker

**Implications**:
- State persists across multiple runs in the same Python process (affects Streamlit auto-rerun)
- Must call `reset_dataframes()` before new processing runs
- Cannot run parallel processing with this design
- Makes unit testing difficult
- **Planned refactoring**: Convert to a `ResultProcessor` class (see REFACTORING_PLAN.md)

### Configuration Management
`config.py` has dual configuration support:
- **Streamlit Cloud**: Uses `st.secrets` for API keys and settings
- **Local Development**: Uses environment variables

All parameters can be overridden at runtime via Streamlit UI sidebar or function arguments.

### Exception Handling Issues
Multiple files use bare `except:` blocks which hide errors:
- `input_handler.py` lines 149, 200, 229
- `api_mapping.py` line 128
- `result_processor.py` line 101
- `streamlit_app.py` lines 739, 743

**When modifying**: Replace with specific exception types (JSONDecodeError, FileNotFoundError, etc.)

### Excel File Format Requirements
Expected structure:
- Sheet 1: "First Group" (no headers, columns: Code | Name)
- Sheet 2: "Second Group" (no headers, columns: Code | Name)
- Empty rows are automatically skipped

## Important Module Details

### config.py
- Extensive model definitions for both OpenAI and OpenRouter
- Includes future models (GPT-5, o3, Gemini 3, etc.) for forward compatibility
- `get_model_max_context()` - validates token limits for each model
- `validate_token_limit()` - prevents exceeding model context windows

### prompts.py
- Contains three specialized mapping prompts
- `Prompts.LAB`, `Prompts.RADIOLOGY`, `Prompts.SERVICE` (class constants)
- Each prompt instructs the AI to return specific JSON format with similarity scores
- Focus areas differ by type (Lab: technique/substrate, Radiology: anatomy/contrast, Service: procedure type)

### batch_dispatcher.py
- `calculate_optimal_batch_split()` - core optimization algorithm
- `Dispatcher()` - decides whether batching is needed based on dataset size
- Manages wait times between batches to avoid rate limits (default: 120s)

### input_handler.py
- Main orchestrator: `SendInputParts()`
- Reads Excel → Validates → Creates JSON (full + compact) → Calls Dispatcher
- Supports runtime parameter overrides (temperature, model, batch settings)
- `SaveResults()` - exports to JSON and Excel

### streamlit_app.py
- **953 lines** (large, monolithic file - planned refactoring)
- Four tabs: Input, Processing, Results, Analytics
- Features terminal-style console output with macOS-inspired styling
- Uses session state extensively for maintaining state across reruns
- Custom CSS embedded in file (lines 30-202)

## Configuration Settings

### Key Settings (via Config class)
| Setting | Default | Description |
|---------|---------|-------------|
| `provider` | "OpenAI" | API provider: "OpenAI" or "OpenRouter" |
| `model` | "gpt-4o" | Model to use |
| `temperature` | 0.2 | Response randomness (0.0-1.0) |
| `top_p` | 0.9 | Nucleus sampling parameter |
| `max_tokens` | 16000 | Maximum response tokens |
| `threshold` | 80 | Minimum similarity score (0-100) |
| `max_batch_size` | 200 | Maximum items per batch |
| `wait_between_batches` | 120 | Seconds between API calls |
| `use_compact_json` | True | Enable token optimization |
| `abbreviate_keys` | True | Use short key names (c/n vs code/name) |

### Streamlit Secrets (for cloud deployment)
Create `.streamlit/secrets.toml`:
```toml
OPENAI_API_KEY = "sk-..."
OPENROUTER_API_KEY = "or-..."

[settings]
provider = "OpenAI"
model = "gpt-4o"
temperature = 0.2
threshold = 80
```

## Output Files

### Excel Export (4 sheets)
1. **API_Calls**: Performance metrics per batch (tokens, latency)
2. **Mappings**: Deduplicated mapping results
3. **Parameters**: Configuration snapshot
4. **Summary**: Aggregate statistics

### JSON Export
Complete results with metadata, all mappings, and statistics.

## Known Issues & Planned Improvements

See `REFACTORING_PLAN.md` for comprehensive refactoring plan. Key issues:

1. **Global state in result_processor.py** - Should be converted to class-based design
2. **Bare except blocks** - Replace with specific exception handling
3. **Large streamlit_app.py** - Should be split into modules (~10 files)
4. **Duplicate configuration printing** - Extract to `Config.print_summary()`
5. **Pandas performance** - Using concat in loop causes O(n²) performance
6. **No logging module** - Uses print() everywhere, should use Python logging
7. **No retry logic** - API calls don't retry on transient failures

## Development Notes

### Adding a New Mapping Type
1. Add prompt text to `prompts.py` as new class constant
2. Update `Prompts.get()` method to handle new type
3. Add type to `Prompts.get_all_types()` return list
4. Update Streamlit UI to add new button in Input tab
5. Prompt must instruct AI to return same JSON format

### Modifying Batch Algorithm
- Core logic in `batch_dispatcher.py::calculate_optimal_batch_split()`
- Algorithm optimizes for minimum total API calls
- Tie-breaking prefers: balanced splits → smaller remainders → larger second group
- Test with various dataset sizes (small: <100, medium: 100-500, large: >500)

### Working with Result DataFrames
```python
from result_processor import get_dataframes, reset_dataframes

# Always reset before new run
reset_dataframes()

# After processing, retrieve DataFrames
dfs = get_dataframes()
api_calls_df = dfs['ApiCall']
mappings_df = dfs['ApiMapping']
```

## Testing Recommendations

Since there's no automated test suite:

1. **Test with different dataset sizes**:
   - Small: <50 items each group (no batching)
   - Medium: 50-200 items (batching edge case)
   - Large: >200 items (multiple batches)

2. **Test all three mapping types**: Lab, Radiology, Service

3. **Test both providers**: OpenAI and OpenRouter

4. **Verify deduplication**: Include intentional duplicates in First Group

5. **Test error cases**:
   - Missing sheets in Excel
   - Empty datasets
   - Invalid API keys
   - Rate limiting scenarios

## Code Style Notes

- Uses `colorama` for colored console output
- F-strings preferred for string formatting
- Type hints used inconsistently (not enforced)
- 4-space indentation
- Global imports at file top
- Functions use snake_case, Classes use PascalCase
