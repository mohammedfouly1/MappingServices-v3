"""
components/sidebar.py - Configuration sidebar for Streamlit app
"""

import streamlit as st
from core.config import Config


def render_sidebar():
    """
    Render the configuration sidebar.

    This includes:
    - Provider selection (OpenAI/OpenRouter)
    - API key inputs
    - Model settings (temperature, top_p, max tokens, threshold)
    - Batch settings
    - Optimization settings
    """
    with st.sidebar:
        st.header("⚙️ Configuration")

        # ===== Provider Selection =====
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

        # ===== Model Settings =====
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
                st.success(f"✓ {msg}")

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

        # ===== Batch Settings =====
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
            value=getattr(Config, 'max_concurrent_batches', 3),
            step=1,
            help="Maximum number of batches processed simultaneously (with rate limiting)"
        )
        Config.max_concurrent_batches = max_concurrent_batches

        st.caption("💡 Async processing with automatic rate limiting (RPM/TPM)")

        st.divider()

        # ===== Optimization Settings =====
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
