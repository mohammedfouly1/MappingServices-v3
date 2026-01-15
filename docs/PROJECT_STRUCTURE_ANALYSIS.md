# Project Structure Analysis & Reorganization Plan

**Date:** January 15, 2026
**Status:** Analysis Complete

---

## Current Structure Assessment

### Current Directory Layout

```
MappingServices-v2/
├── .git/
├── .gitignore
├── CLAUDE.md
├── REFACTORING_PLAN_V2.md
├── requirements.txt
│
├── components/           # UI components (9 files, organized ✓)
│   ├── __init__.py
│   ├── analytics_tab.py
│   ├── input_tab.py
│   ├── processing_tab.py
│   ├── rate_limiter_display.py
│   ├── results_tab.py
│   ├── sidebar.py
│   ├── styles.py
│   └── utils.py
│
├── session/              # Session management (2 files, organized ✓)
│   ├── __init__.py
│   └── state_manager.py
│
├── logs/                 # Log files (1 file)
│   └── mapping_service_20260115.log
│
└── Root Level (13 Python files) ❌ NEEDS ORGANIZATION
    ├── api_mapping.py         (438 lines)
    ├── api_utils.py           (258 lines)
    ├── batch_dispatcher.py    (535 lines)
    ├── config.py              (332 lines)
    ├── input_handler.py       (357 lines)
    ├── logger.py              (228 lines)
    ├── main.py                (55 lines)
    ├── models.py              (318 lines)
    ├── optimization_utils.py  (28 lines)
    ├── prompts.py             (213 lines)
    ├── rate_limiter.py        (318 lines)
    ├── result_processor.py    (357 lines)
    └── streamlit_app.py       (88 lines)
```

---

## Issues Identified

### 🔴 Critical Issues

1. **13 Python files in root directory**
   - Hard to navigate
   - Unclear module relationships
   - No logical grouping

2. **Missing proper package structure**
   - No `src/` or `app/` directory
   - Direct imports from root
   - Hard to package/distribute

3. **Mixed concerns in root**
   - API logic (api_mapping, api_utils)
   - Business logic (batch_dispatcher, input_handler)
   - Data models (models.py)
   - Configuration (config.py)
   - Utilities (logger, optimization_utils, rate_limiter)
   - Entry points (main.py, streamlit_app.py)

### 🟡 Medium Issues

4. **Inconsistent naming conventions**
   - Some files: snake_case (api_mapping.py, batch_dispatcher.py) ✓
   - Some modules: single word (config, models, logger) - could be clearer

5. **No tests directory**
   - Testing difficult
   - No clear place for test files

6. **No proper package metadata**
   - No setup.py or pyproject.toml
   - No version information
   - No package dependencies properly defined

### 🟢 Minor Issues

7. **Documentation scattered**
   - CLAUDE.md in root ✓
   - REFACTORING_PLAN_V2.md in root ✓
   - Could have docs/ folder for additional docs

8. **Logs in repository**
   - 11MB log file tracked
   - Should be in .gitignore (already is, but file committed before)

---

## Proposed Reorganization

### Option A: Simple Reorganization (Recommended)

**Minimal changes, maximum clarity**

```
MappingServices-v2/
├── .git/
├── .gitignore
├── README.md              # User-facing documentation
├── CLAUDE.md              # Developer documentation
├── requirements.txt
├── setup.py (NEW)         # Package metadata
│
├── docs/ (NEW)            # Documentation
│   └── REFACTORING_PLAN_V2.md
│
├── tests/ (NEW)           # Test files
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api/
│   ├── test_services/
│   └── test_models/
│
├── logs/                  # Runtime logs (gitignored)
│   └── .gitkeep
│
├── core/  (NEW)           # Core business logic
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── models.py          # Data models
│   ├── prompts.py         # Prompt templates
│   └── logger.py          # Logging setup
│
├── api/ (NEW)             # API clients and communication
│   ├── __init__.py
│   ├── client.py          # API client (from api_mapping.py)
│   ├── utils.py           # API utilities (from api_utils.py)
│   └── rate_limiter.py    # Rate limiting
│
├── services/ (NEW)        # Business logic services
│   ├── __init__.py
│   ├── batch_dispatcher.py   # Batch processing
│   ├── input_handler.py      # Input processing
│   ├── result_processor.py   # Result processing
│   └── optimization_utils.py # Optimization helpers
│
├── ui/ (RENAMED from components/)  # Streamlit UI
│   ├── __init__.py
│   ├── app.py             # Main Streamlit app (from streamlit_app.py)
│   ├── tabs/
│   │   ├── __init__.py
│   │   ├── analytics_tab.py
│   │   ├── input_tab.py
│   │   ├── processing_tab.py
│   │   └── results_tab.py
│   ├── components/
│   │   ├── __init__.py
│   │   ├── sidebar.py
│   │   └── rate_limiter_display.py
│   ├── styles.py          # CSS styles
│   └── utils.py           # UI utilities
│
├── session/               # Session state management
│   ├── __init__.py
│   └── state_manager.py
│
└── main.py                # CLI entry point
```

### Option B: Standard Python Package Structure

**Full package structure, production-ready**

```
MappingServices-v2/
├── .git/
├── .gitignore
├── README.md
├── LICENSE
├── setup.py
├── pyproject.toml
├── MANIFEST.in
│
├── docs/
│   ├── index.md
│   ├── installation.md
│   ├── usage.md
│   ├── api_reference.md
│   ├── architecture.md
│   └── REFACTORING_PLAN_V2.md
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── fixtures/
│   ├── unit/
│   │   ├── test_api/
│   │   ├── test_services/
│   │   ├── test_models/
│   │   └── test_config/
│   └── integration/
│       └── test_end_to_end.py
│
├── src/                   # Source code root
│   └── mapping_service/   # Main package
│       ├── __init__.py
│       ├── __version__.py
│       ├── core/
│       ├── api/
│       ├── services/
│       ├── ui/
│       └── session/
│
├── scripts/               # Utility scripts
│   ├── run_streamlit.sh
│   └── run_tests.sh
│
├── logs/
│   └── .gitkeep
│
└── data/ (OPTIONAL)       # Sample data
    └── examples/
```

---

## Recommended Approach: Option A (Simple Reorganization)

### Why Option A?

✅ **Pros:**
- Minimal disruption to existing code
- Clear logical grouping
- Easy to understand structure
- Maintains working imports with small changes
- Good balance of organization and simplicity

❌ **Cons of Option B:**
- Requires `src/` directory (more complex imports)
- Need to install package in development mode
- More setup overhead

---

## Implementation Plan

### Phase 1: Create New Directory Structure (No Breaking Changes)

```bash
# Create new directories
mkdir -p core api services ui/tabs ui/components tests/test_api tests/test_services docs

# Create __init__.py files
touch core/__init__.py api/__init__.py services/__init__.py
touch ui/__init__.py ui/tabs/__init__.py ui/components/__init__.py
touch tests/__init__.py
```

### Phase 2: Move Files to New Locations

**Core Module:**
```bash
mv config.py core/
mv models.py core/
mv prompts.py core/
mv logger.py core/
```

**API Module:**
```bash
mv api_mapping.py api/client.py     # Rename for clarity
mv api_utils.py api/utils.py
mv rate_limiter.py api/
```

**Services Module:**
```bash
mv batch_dispatcher.py services/
mv input_handler.py services/
mv result_processor.py services/
mv optimization_utils.py services/
```

**UI Module:**
```bash
# Rename components/ to ui/
mv components ui_temp
mkdir -p ui/tabs ui/components

# Move tab files
mv ui_temp/analytics_tab.py ui/tabs/
mv ui_temp/input_tab.py ui/tabs/
mv ui_temp/processing_tab.py ui/tabs/
mv ui_temp/results_tab.py ui/tabs/

# Move component files
mv ui_temp/sidebar.py ui/components/
mv ui_temp/rate_limiter_display.py ui/components/

# Move other files
mv ui_temp/styles.py ui/
mv ui_temp/utils.py ui/
mv streamlit_app.py ui/app.py

# Cleanup
rm -rf ui_temp
```

### Phase 3: Update Import Statements

**Before:**
```python
from config import Config
from models import MappingItem
from api_mapping import PerformMapping
from batch_dispatcher import DispatchBatches
```

**After:**
```python
from core.config import Config
from core.models import MappingItem
from api.client import PerformMapping
from services.batch_dispatcher import DispatchBatches
```

**Tools to help:**
- Use `grep -r "from config import"` to find all imports
- Use search/replace in IDE
- Test after each module update

### Phase 4: Create Package Metadata

**Create setup.py:**
```python
from setuptools import setup, find_packages

setup(
    name="mapping-service",
    version="2.0.0",
    description="Medical Services Mapping with AI",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.30.0",
        "openai>=1.0.0",
        "pandas>=2.0.0",
        "openpyxl>=3.1.0",
        "colorama>=0.4.6",
    ],
    python_requires=">=3.9",
)
```

**Create pyproject.toml:**
```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_system"

[project]
name = "mapping-service"
version = "2.0.0"
description = "Medical Services Mapping with AI"
requires-python = ">=3.9"
dependencies = [
    "streamlit>=1.30.0",
    "openai>=1.0.0",
    "pandas>=2.0.0",
    "openpyxl>=3.1.0",
    "colorama>=0.4.6",
]
```

### Phase 5: Update Entry Points

**main.py (CLI entry):**
```python
#!/usr/bin/env python3
"""CLI entry point for mapping service"""

if __name__ == "__main__":
    from core.config import Config
    from services.input_handler import SendInputParts

    # CLI logic here
    pass
```

**ui/app.py (Streamlit entry):**
```python
"""Streamlit web application"""
import streamlit as st
from ui.components.sidebar import render_sidebar
from ui.tabs.input_tab import render_input_tab
# ... other imports

def main():
    st.set_page_config(...)
    # App logic here

if __name__ == "__main__":
    main()
```

### Phase 6: Update Documentation

**Update CLAUDE.md:**
```markdown
## Project Structure

```
MappingServices-v2/
├── core/          # Core configuration and models
├── api/           # API clients and rate limiting
├── services/      # Business logic
├── ui/            # Streamlit UI
├── session/       # Session management
└── tests/         # Test suite
```

## Running the Application

```bash
# Streamlit web UI
streamlit run ui/app.py

# CLI
python main.py --help
```
```

---

## Migration Checklist

### Pre-Migration
- [ ] Create backup branch: `git checkout -b backup-before-restructure`
- [ ] Commit all current changes
- [ ] Run all existing tests (if any)
- [ ] Document current working state

### Migration Steps
- [ ] **Phase 1:** Create new directory structure
- [ ] **Phase 2:** Move files to new locations
- [ ] **Phase 3:** Update all import statements
  - [ ] Update `core/` imports
  - [ ] Update `api/` imports
  - [ ] Update `services/` imports
  - [ ] Update `ui/` imports
  - [ ] Update `session/` imports
- [ ] **Phase 4:** Create package metadata
- [ ] **Phase 5:** Update entry points
- [ ] **Phase 6:** Update documentation

### Post-Migration Verification
- [ ] Run application: `streamlit run ui/app.py`
- [ ] Test file upload
- [ ] Test batch processing
- [ ] Test results export
- [ ] Check all imports work
- [ ] Verify no broken links
- [ ] Update .gitignore if needed
- [ ] Commit reorganization

---

## Import Update Script

Create a helper script to update imports automatically:

```python
#!/usr/bin/env python3
"""Update imports after reorganization"""

import os
import re
from pathlib import Path

# Mapping of old imports to new imports
IMPORT_MAPPINGS = {
    r'from config import': 'from core.config import',
    r'from models import': 'from core.models import',
    r'from prompts import': 'from core.prompts import',
    r'from logger import': 'from core.logger import',
    r'from api_mapping import': 'from api.client import',
    r'from api_utils import': 'from api.utils import',
    r'from rate_limiter import': 'from api.rate_limiter import',
    r'from batch_dispatcher import': 'from services.batch_dispatcher import',
    r'from input_handler import': 'from services.input_handler import',
    r'from result_processor import': 'from services.result_processor import',
    r'from optimization_utils import': 'from services.optimization_utils import',
    r'import config': 'from core import config',
    r'import models': 'from core import models',
}

def update_imports_in_file(filepath):
    """Update imports in a single file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Apply all mappings
    for old_pattern, new_pattern in IMPORT_MAPPINGS.items():
        content = re.sub(old_pattern, new_pattern, content)

    # Only write if changed
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Updated: {filepath}")
        return True
    return False

def main():
    """Update all Python files"""
    updated_count = 0

    # Find all .py files
    for root, dirs, files in os.walk('.'):
        # Skip .git, __pycache__, etc.
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if update_imports_in_file(filepath):
                    updated_count += 1

    print(f"\n✓ Updated {updated_count} files")

if __name__ == "__main__":
    main()
```

---

## Risk Assessment

### Low Risk
- Creating new directories (doesn't break anything)
- Moving documentation files
- Creating __init__.py files

### Medium Risk
- Moving Python files (breaks imports temporarily)
- Renaming api_mapping.py → api/client.py

### High Risk
- Updating all imports (must be done correctly)
- Changing entry points (main.py, streamlit_app.py)

### Mitigation
1. **Work in a branch**: `git checkout -b restructure-project`
2. **Incremental approach**: Move one module at a time, test
3. **Automated import updates**: Use script above
4. **Testing after each step**: Verify application still runs
5. **Easy rollback**: Keep backup branch

---

## Expected Benefits

### Immediate Benefits
✅ **Clearer structure** - Easier to navigate
✅ **Logical grouping** - Related files together
✅ **Better imports** - Clear module hierarchy
✅ **Professional layout** - Standard Python project

### Long-term Benefits
✅ **Easier onboarding** - New developers understand structure
✅ **Better testability** - Clear where tests go
✅ **Easier refactoring** - Modules well-defined
✅ **Package distribution** - Can publish as package
✅ **IDE support** - Better autocomplete and navigation

---

## Timeline Estimate

- **Phase 1 (Directory Creation)**: 15 minutes
- **Phase 2 (File Moving)**: 30 minutes
- **Phase 3 (Import Updates)**: 1-2 hours (manual) or 30 minutes (scripted)
- **Phase 4 (Package Metadata)**: 30 minutes
- **Phase 5 (Entry Points)**: 30 minutes
- **Phase 6 (Documentation)**: 30 minutes
- **Testing & Verification**: 1 hour

**Total: 4-5 hours**

---

## Decision Required

**Which option should we implement?**

1. **Option A (Simple)** - Recommended
   - 4-5 hours work
   - Clear structure
   - Minimal disruption

2. **Option B (Full Package)** - For production
   - 6-8 hours work
   - Complete package structure
   - Ready for PyPI distribution

3. **No Change** - Keep current structure
   - 0 hours work
   - Status quo
   - Technical debt remains

**Recommendation: Option A** - Best balance of clarity and effort

---

## Next Steps

1. **Review this analysis** - Agree on approach
2. **Create backup branch** - Safety first
3. **Execute Phase 1-6** - Incremental migration
4. **Test thoroughly** - Verify functionality
5. **Update CLAUDE.md** - Document new structure
6. **Commit changes** - One commit per phase

---

**Document Status:** Ready for Review
**Recommended Action:** Proceed with Option A
**Estimated Effort:** 4-5 hours
**Risk Level:** Medium (with mitigation: Low)
