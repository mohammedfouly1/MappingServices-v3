#!/usr/bin/env python3
"""
Update imports after project reorganization.

This script automatically updates import statements to reflect the new project structure.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Mapping of old imports to new imports
IMPORT_MAPPINGS = {
    # Core module imports
    r'\bfrom config import\b': 'from core.config import',
    r'\bimport config\b': 'from core import config',
    r'\bfrom models import\b': 'from core.models import',
    r'\bimport models\b': 'from core import models',
    r'\bfrom prompts import\b': 'from core.prompts import',
    r'\bimport prompts\b': 'from core import prompts',
    r'\bfrom logger import\b': 'from core.logger import',
    r'\bimport logger\b': 'from core import logger',

    # API module imports
    r'\bfrom api_mapping import\b': 'from api.client import',
    r'\bimport api_mapping\b': 'from api import client',
    r'\bfrom api_utils import\b': 'from api.utils import',
    r'\bimport api_utils\b': 'from api import utils',
    r'\bfrom rate_limiter import\b': 'from api.rate_limiter import',
    r'\bimport rate_limiter\b': 'from api import rate_limiter',

    # Services module imports
    r'\bfrom batch_dispatcher import\b': 'from services.batch_dispatcher import',
    r'\bimport batch_dispatcher\b': 'from services import batch_dispatcher',
    r'\bfrom input_handler import\b': 'from services.input_handler import',
    r'\bimport input_handler\b': 'from services import input_handler',
    r'\bfrom result_processor import\b': 'from services.result_processor import',
    r'\bimport result_processor\b': 'from services import result_processor',
    r'\bfrom optimization_utils import\b': 'from services.optimization_utils import',
    r'\bimport optimization_utils\b': 'from services import optimization_utils',

    # UI module imports (for internal UI files)
    r'\bfrom components\.([a-z_]+) import\b': r'from ui.tabs.\1 import',
    r'\bimport components\.([a-z_]+)\b': r'from ui.tabs import \1',

    # Session imports
    r'\bfrom session\.state_manager import\b': 'from ui.session.state_manager import',
    r'\bfrom session import\b': 'from ui.session import',
}

# Specific component renames
COMPONENT_RENAMES = {
    'components.analytics_tab': 'ui.tabs.analytics_tab',
    'components.input_tab': 'ui.tabs.input_tab',
    'components.processing_tab': 'ui.tabs.processing_tab',
    'components.results_tab': 'ui.tabs.results_tab',
    'components.sidebar': 'ui.components.sidebar',
    'components.rate_limiter_display': 'ui.components.rate_limiter_display',
    'components.styles': 'ui.styles',
    'components.utils': 'ui.utils',
}


def update_imports_in_file(filepath: str) -> Tuple[bool, List[str]]:
    """
    Update imports in a single file.

    Args:
        filepath: Path to the file to update

    Returns:
        Tuple of (was_modified, list_of_changes)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return False, [f"Error reading {filepath}: {e}"]

    original_content = content
    changes = []

    # Apply general mappings
    for old_pattern, new_pattern in IMPORT_MAPPINGS.items():
        matches = re.findall(old_pattern, content)
        if matches:
            content = re.sub(old_pattern, new_pattern, content)
            changes.append(f"  {old_pattern} -> {new_pattern}")

    # Apply component-specific renames
    for old_name, new_name in COMPONENT_RENAMES.items():
        if old_name in content:
            content = content.replace(old_name, new_name)
            changes.append(f"  {old_name} -> {new_name}")

    # Only write if changed
    if content != original_content:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, changes
        except Exception as e:
            return False, [f"Error writing {filepath}: {e}"]

    return False, []


def find_python_files(root_dir: str) -> List[str]:
    """Find all Python files in the project."""
    python_files = []

    # Directories to search
    search_dirs = ['core', 'api', 'services', 'ui', 'ui/tabs', 'ui/components', 'ui/session']

    # Also check root-level files
    root_files = ['main.py']

    for filename in root_files:
        filepath = os.path.join(root_dir, filename)
        if os.path.exists(filepath):
            python_files.append(filepath)

    # Search in directories
    for directory in search_dirs:
        dir_path = os.path.join(root_dir, directory)
        if os.path.exists(dir_path):
            for root, dirs, files in os.walk(dir_path):
                # Skip __pycache__ and .git
                dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', '.claude']]

                for file in files:
                    if file.endswith('.py') and not file.startswith('__'):
                        filepath = os.path.join(root, file)
                        python_files.append(filepath)

    return python_files


def main():
    """Main function to update all imports."""
    print("=" * 70)
    print("  IMPORT UPDATE SCRIPT - Project Reorganization")
    print("=" * 70)
    print()

    # Get project root (script location)
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)

    print(f"[*] Project root: {project_root}")
    print()

    # Find all Python files
    print("[*] Finding Python files...")
    python_files = find_python_files('.')
    print(f"   Found {len(python_files)} Python files")
    print()

    # Update imports in each file
    print("[*] Updating imports...")
    print()

    updated_files = []
    unchanged_files = []
    errors = []

    for filepath in python_files:
        rel_path = os.path.relpath(filepath, project_root)
        modified, changes = update_imports_in_file(filepath)

        if modified:
            updated_files.append(rel_path)
            print(f"[+] Updated: {rel_path}")
            for change in changes:
                print(change)
            print()
        else:
            unchanged_files.append(rel_path)

    # Summary
    print("=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print()
    print(f"[+] Updated files:   {len(updated_files)}")
    print(f"[-] Unchanged files: {len(unchanged_files)}")
    print(f"[!] Errors:          {len(errors)}")
    print()

    if updated_files:
        print("[*] Updated files:")
        for filepath in updated_files:
            print(f"   - {filepath}")
        print()

    if errors:
        print("[!] Errors:")
        for error in errors:
            print(f"   - {error}")
        print()

    print("[*] Import update complete!")
    print()
    print("[*] Next steps:")
    print("   1. Review changes: git diff")
    print("   2. Test application: streamlit run ui/app.py")
    print("   3. Delete old files after testing")
    print()


if __name__ == "__main__":
    main()
