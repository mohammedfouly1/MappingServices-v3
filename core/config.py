# config.py
import os
from pathlib import Path
import streamlit as st

class Config:
    """Configuration settings with Streamlit Cloud support"""

    # Provider options
    PROVIDERS = ["OpenAI", "OpenRouter"]

    # OpenAI Models with Tier 3 limits (max context, RPM, TPM, endpoints)
    # ALL models below have RPM = 5,000 for Tier 3
    OPENAI_MODELS = {
        # GPT-4 Turbo
        "gpt-4-turbo": {
            "max_context": 128000,
            "description": "GPT-4 Turbo with Vision",
            "rpm_limit": 5000,
            "tpm_limit": 600000,
            "endpoints": ["/v1/responses", "/v1/chat/completions"]
        },
        # GPT-4o series
        "gpt-4o-mini": {
            "max_context": 128000,
            "description": "GPT-4o Mini - Fast and affordable",
            "rpm_limit": 5000,
            "tpm_limit": 4000000,
            "endpoints": ["/v1/responses", "/v1/chat/completions"]
        },
        "gpt-4o": {
            "max_context": 128000,
            "description": "GPT-4o - Most capable multimodal model",
            "rpm_limit": 5000,
            "tpm_limit": 800000,
            "endpoints": ["/v1/responses", "/v1/chat/completions"]
        },
        "chatgpt-4o-latest": {
            "max_context": 128000,
            "description": "ChatGPT-4o - Latest ChatGPT model",
            "rpm_limit": 5000,
            "tpm_limit": 800000,
            "endpoints": ["/v1/responses", "/v1/chat/completions"]
        },
        # GPT-4 Base
        "gpt-4": {
            "max_context": 8192,
            "description": "GPT-4 Base model",
            "rpm_limit": 5000,
            "tpm_limit": 5000000,
            "endpoints": ["/v1/responses", "/v1/chat/completions"]
        },
        # GPT-5 series
        "gpt-5": {
            "max_context": 400000,
            "description": "GPT-5 - Next generation",
            "rpm_limit": 5000,
            "tpm_limit": 2000000,
            "endpoints": ["/v1/responses", "/v1/chat/completions"]
        },
        "gpt-5.2": {
            "max_context": 400000,
            "description": "GPT-5.2 - Advanced",
            "rpm_limit": 5000,
            "tpm_limit": 2000000,
            "endpoints": ["/v1/responses", "/v1/chat/completions"]
        },
        "gpt-5-mini": {
            "max_context": 400000,
            "description": "GPT-5 Mini - Fast",
            "rpm_limit": 5000,
            "tpm_limit": 4000000,
            "endpoints": ["/v1/responses", "/v1/chat/completions"]
        },
        "gpt-5.2-pro": {
            "max_context": 400000,
            "description": "GPT-5.2 Pro - Responses API only",
            "rpm_limit": 5000,
            "tpm_limit": 800000,
            "endpoints": ["/v1/responses"]
        },
    }

    # OpenRouter Models with their context window
    # NOTE: OpenAI models are available directly through OpenAI provider above
    OPENROUTER_MODELS = {
        # Anthropic Claude
        "anthropic/claude-3.5-sonnet": {"max_context": 200000, "description": "Claude 3.5 Sonnet"},
        "anthropic/claude-3.5-sonnet-20241022": {"max_context": 200000, "description": "Claude 3.5 Sonnet October 2024"},
        "anthropic/claude-3-opus": {"max_context": 200000, "description": "Claude 3 Opus - Most capable"},
        "anthropic/claude-3-sonnet": {"max_context": 200000, "description": "Claude 3 Sonnet"},
        "anthropic/claude-3-haiku": {"max_context": 200000, "description": "Claude 3 Haiku - Fast"},
        "anthropic/claude-3.5-haiku": {"max_context": 200000, "description": "Claude 3.5 Haiku"},
        # Google Gemini
        "google/gemini-pro-1.5": {"max_context": 1000000, "description": "Gemini Pro 1.5 - 1M context"},
        "google/gemini-flash-1.5": {"max_context": 1000000, "description": "Gemini Flash 1.5 - Fast"},
        "google/gemini-2.0-flash-exp": {"max_context": 1000000, "description": "Gemini 2.0 Flash Experimental"},
        "google/gemini-2.0-flash": {"max_context": 1000000, "description": "Gemini 2.0 Flash"},
        "google/gemini-2.0-flash-lite": {"max_context": 1000000, "description": "Gemini 2.0 Flash Lite - Lightweight"},
        "google/gemini-2.5-pro": {"max_context": 1000000, "description": "Gemini 2.5 Pro - Latest"},
        "google/gemini-2.5-flash": {"max_context": 1000000, "description": "Gemini 2.5 Flash - Fast"},
        "google/gemini-2.5-flash-lite": {"max_context": 1000000, "description": "Gemini 2.5 Flash Lite - Lightweight"},
        "google/gemini-3": {"max_context": 2000000, "description": "Gemini 3 - Next Gen (if available)"},
        "google/gemini-3-flash": {"max_context": 2000000, "description": "Gemini 3 Flash (if available)"},
        "google/gemini-exp-1206": {"max_context": 1000000, "description": "Gemini Experimental December 2024"},
        # Meta Llama
        "meta-llama/llama-3.3-70b-instruct": {"max_context": 131072, "description": "Llama 3.3 70B Instruct"},
        "meta-llama/llama-3.2-90b-vision-instruct": {"max_context": 131072, "description": "Llama 3.2 90B Vision"},
        "meta-llama/llama-3.1-405b-instruct": {"max_context": 131072, "description": "Llama 3.1 405B Instruct"},
        "meta-llama/llama-3.1-70b-instruct": {"max_context": 131072, "description": "Llama 3.1 70B Instruct"},
        "meta-llama/llama-3.1-8b-instruct": {"max_context": 131072, "description": "Llama 3.1 8B Instruct"},
        # Mistral
        "mistralai/mistral-large": {"max_context": 128000, "description": "Mistral Large"},
        "mistralai/mistral-medium": {"max_context": 32000, "description": "Mistral Medium"},
        "mistralai/mistral-small": {"max_context": 32000, "description": "Mistral Small"},
        "mistralai/mixtral-8x22b-instruct": {"max_context": 65536, "description": "Mixtral 8x22B Instruct"},
        "mistralai/mixtral-8x7b-instruct": {"max_context": 32768, "description": "Mixtral 8x7B Instruct"},
        "mistralai/codestral-latest": {"max_context": 32000, "description": "Codestral - Code model"},
        # DeepSeek
        "deepseek/deepseek-chat": {"max_context": 64000, "description": "DeepSeek Chat"},
        "deepseek/deepseek-r1": {"max_context": 64000, "description": "DeepSeek R1 - Reasoning"},
        "deepseek/deepseek-r1-zero": {"max_context": 64000, "description": "DeepSeek R1 Zero"},
        "deepseek/deepseek-v3": {"max_context": 128000, "description": "DeepSeek V3"},
        "deepseek/deepseek-v3.1": {"max_context": 128000, "description": "DeepSeek V3.1 - Enhanced"},
        "deepseek/deepseek-v3.2": {"max_context": 128000, "description": "DeepSeek V3.2 - Latest"},
        "deepseek/deepseek-coder": {"max_context": 64000, "description": "DeepSeek Coder"},
        "deepseek/deepseek-coder-v2": {"max_context": 128000, "description": "DeepSeek Coder V2"},
        # Qwen
        "qwen/qwen-2.5-72b-instruct": {"max_context": 131072, "description": "Qwen 2.5 72B Instruct"},
        "qwen/qwen-2.5-coder-32b-instruct": {"max_context": 131072, "description": "Qwen 2.5 Coder 32B"},
        "qwen/qwq-32b-preview": {"max_context": 32768, "description": "QwQ 32B Preview - Reasoning"},
        # Cohere
        "cohere/command-r-plus": {"max_context": 128000, "description": "Command R+ - Enterprise"},
        "cohere/command-r": {"max_context": 128000, "description": "Command R"},
        # Perplexity
        "perplexity/llama-3.1-sonar-large-128k-online": {"max_context": 128000, "description": "Sonar Large - Online search"},
        "perplexity/llama-3.1-sonar-small-128k-online": {"max_context": 128000, "description": "Sonar Small - Online search"},
    }

    # For Streamlit Cloud, use secrets management
    @staticmethod
    def get_api_key():
        # Try Streamlit secrets first (for cloud deployment)
        try:
            return st.secrets["OPENAI_API_KEY"]
        except:
            # Fall back to environment variable (for local)
            return os.getenv("OPENAI_API_KEY", "")

    @staticmethod
    def get_openrouter_api_key():
        # Try Streamlit secrets first (for cloud deployment)
        try:
            return st.secrets["OPENROUTER_API_KEY"]
        except:
            # Fall back to environment variable (for local)
            return os.getenv("OPENROUTER_API_KEY", "")

    # File paths - will be handled by file uploader in Streamlit
    excel_path = None
    prompt_path = None

    # API settings - can be overridden by Streamlit secrets
    @staticmethod
    def get_settings():
        try:
            # Try to load from Streamlit secrets
            return {
                "api_key": st.secrets.get("OPENAI_API_KEY", ""),
                "openrouter_api_key": st.secrets.get("OPENROUTER_API_KEY", ""),
                "provider": st.secrets.settings.get("provider", "OpenAI"),
                "model": st.secrets.settings.get("model", "gpt-4o"),
                "max_tokens": st.secrets.settings.get("max_tokens", 16000),
                "temperature": st.secrets.settings.get("temperature", 0.2),
                "top_p": st.secrets.settings.get("top_p", 0.9),
                "threshold": st.secrets.settings.get("threshold", 80)
            }
        except:
            # Default settings
            return {
                "api_key": os.getenv("OPENAI_API_KEY", ""),
                "openrouter_api_key": os.getenv("OPENROUTER_API_KEY", ""),
                "provider": "OpenAI",
                "model": "gpt-4o",
                "max_tokens": 16000,
                "temperature": 0.2,
                "top_p": 0.9,
                "threshold": 80
            }

    # Load settings
    settings = get_settings.__func__()
    api_key = get_api_key.__func__()
    openrouter_api_key = get_openrouter_api_key.__func__()
    provider = settings.get("provider", "OpenAI")
    model = settings.get("model", "gpt-4o")
    max_tokens = settings.get("max_tokens", 16000)
    temperature = settings.get("temperature", 0.2)
    top_p = settings.get("top_p", 0.9)
    threshold = settings.get("threshold", 80)

    # Optimization settings
    use_compact_json = True
    abbreviate_keys = True

    # Batch settings
    max_batch_size = 200
    wait_between_batches = 120
    max_concurrent_batches = 3  # Number of batches processed simultaneously with rate limiting

    @classmethod
    def log_configuration(cls):
        """Log current configuration settings"""
        from core.logger import get_logger
        logger = get_logger(__name__)
        logger.info(f"Configuration:")
        logger.info(f"  - Provider: {cls.provider}")
        logger.info(f"  - Model: {cls.model}")
        logger.info(f"  - Temperature: {cls.temperature}")
        logger.info(f"  - Top P: {cls.top_p}")
        logger.info(f"  - Max Tokens: {cls.max_tokens}")
        logger.info(f"  - Threshold: {cls.threshold}")
        logger.info(f"  - Max Batch Size: {cls.max_batch_size}")
        logger.info(f"  - Max Concurrent Batches: {cls.max_concurrent_batches}")
        logger.info(f"  - Use Compact JSON: {cls.use_compact_json}")

    @classmethod
    def get_models_for_provider(cls, provider: str) -> dict:
        """Get available models for the selected provider"""
        if provider == "OpenRouter":
            return cls.OPENROUTER_MODELS
        return cls.OPENAI_MODELS

    @classmethod
    def get_model_max_context(cls, model: str, provider: str = None) -> int:
        """Get the maximum context window for a model"""
        if provider is None:
            provider = cls.provider

        models = cls.get_models_for_provider(provider)
        if model in models:
            return models[model]["max_context"]
        # Default fallback
        return 8192

    @classmethod
    def validate_token_limit(cls, input_tokens: int, max_output_tokens: int, model: str = None, provider: str = None) -> tuple:
        """
        Validate that input_tokens + max_output_tokens doesn't exceed model capacity.

        Returns:
            tuple: (is_valid: bool, message: str, recommended_max_tokens: int)
        """
        if model is None:
            model = cls.model
        if provider is None:
            provider = cls.provider

        max_context = cls.get_model_max_context(model, provider)
        total_tokens = input_tokens + max_output_tokens

        if total_tokens > max_context:
            recommended = max(1000, max_context - input_tokens - 1000)  # Leave 1000 buffer
            return (
                False,
                f"Total tokens ({input_tokens:,} input + {max_output_tokens:,} output = {total_tokens:,}) "
                f"exceeds model capacity ({max_context:,}). Recommended max output: {recommended:,}",
                recommended
            )

        return (True, f"Token usage OK: {total_tokens:,} / {max_context:,}", max_output_tokens)