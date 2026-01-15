"""
session/state_manager.py - Centralized session state management
"""

import streamlit as st
from typing import Optional, Any


class SessionState:
    """
    Centralized session state manager for the Streamlit app.

    This class provides a clean interface for managing all session state variables
    and ensures consistent initialization and reset behavior.
    """

    @staticmethod
    def initialize():
        """
        Initialize all session state variables with default values.

        This should be called once at the start of the main() function.
        """
        # Processing state
        if 'processing' not in st.session_state:
            st.session_state.processing = False

        # Results storage
        if 'results' not in st.session_state:
            st.session_state.results = None

        # Console output capture
        if 'console_output' not in st.session_state:
            st.session_state.console_output = []

        # User selections
        if 'selected_prompt_type' not in st.session_state:
            st.session_state.selected_prompt_type = None

        # File upload
        if 'uploaded_file_content' not in st.session_state:
            st.session_state.uploaded_file_content = None

        # Token estimation
        if 'estimated_input_tokens' not in st.session_state:
            st.session_state.estimated_input_tokens = 0

        # Note: result_processor uses global functions, no instance needed

    @staticmethod
    def reset():
        """
        Reset all session state to initial values.

        This clears all data and reinitializes with defaults.
        """
        st.session_state.clear()
        SessionState.initialize()

    @staticmethod
    def get_processor():
        """
        Get the result processor (uses global functions in result_processor module).

        Returns:
            None: result_processor uses global functions
        """
        # result_processor.py uses global functions, not a class instance
        return None

    @staticmethod
    def set_processing(value: bool):
        """
        Set the processing state.

        Args:
            value: True if processing is active, False otherwise
        """
        st.session_state.processing = value

    @staticmethod
    def is_processing() -> bool:
        """
        Check if processing is currently active.

        Returns:
            bool: True if processing, False otherwise
        """
        return st.session_state.get('processing', False)

    @staticmethod
    def set_results(results: Optional[dict]):
        """
        Store processing results in session state.

        Args:
            results: Dictionary containing processing results
        """
        st.session_state.results = results

    @staticmethod
    def get_results() -> Optional[dict]:
        """
        Get processing results from session state.

        Returns:
            Optional[dict]: Results dictionary or None
        """
        return st.session_state.get('results', None)

    @staticmethod
    def has_results() -> bool:
        """
        Check if results are available.

        Returns:
            bool: True if results exist, False otherwise
        """
        return st.session_state.get('results', None) is not None

    @staticmethod
    def set_prompt_type(prompt_type: str):
        """
        Set the selected prompt type.

        Args:
            prompt_type: One of "Lab", "Radiology", or "Service"
        """
        st.session_state.selected_prompt_type = prompt_type

    @staticmethod
    def get_prompt_type() -> Optional[str]:
        """
        Get the selected prompt type.

        Returns:
            Optional[str]: Prompt type or None
        """
        return st.session_state.get('selected_prompt_type', None)

    @staticmethod
    def set_uploaded_file_content(content: bytes):
        """
        Store uploaded file content.

        Args:
            content: File content as bytes
        """
        st.session_state.uploaded_file_content = content

    @staticmethod
    def get_uploaded_file_content() -> Optional[bytes]:
        """
        Get uploaded file content.

        Returns:
            Optional[bytes]: File content or None
        """
        return st.session_state.get('uploaded_file_content', None)

    @staticmethod
    def set_estimated_tokens(tokens: int):
        """
        Set estimated input tokens.

        Args:
            tokens: Estimated token count
        """
        st.session_state.estimated_input_tokens = tokens

    @staticmethod
    def get_estimated_tokens() -> int:
        """
        Get estimated input tokens.

        Returns:
            int: Estimated token count
        """
        return st.session_state.get('estimated_input_tokens', 0)

    @staticmethod
    def get_state(key: str, default: Any = None) -> Any:
        """
        Get any session state value by key.

        Args:
            key: Session state key
            default: Default value if key doesn't exist

        Returns:
            Any: Value from session state or default
        """
        return st.session_state.get(key, default)

    @staticmethod
    def set_state(key: str, value: Any):
        """
        Set any session state value.

        Args:
            key: Session state key
            value: Value to store
        """
        st.session_state[key] = value
