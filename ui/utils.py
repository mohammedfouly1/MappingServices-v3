"""
components/utils.py - Utility functions for Streamlit app
"""

import sys
import re
import streamlit as st
from datetime import datetime
from typing import List
from core.prompts import Prompts


class StreamlitConsoleCapture:
    """Capture console output for Streamlit display with terminal styling"""

    def __init__(self, text_element, metrics_placeholder=None):
        self.text_element = text_element
        self.metrics_placeholder = metrics_placeholder
        self.output: List[str] = []
        self.old_stdout = sys.stdout

        # Batch tracking for metrics
        self.batches_completed = 0
        self.batches_failed = 0
        self.total_batches = 0
        self.start_time = datetime.now()
        self.last_batch_time = datetime.now()

    def write(self, text: str):
        """
        Write text to console and capture for Streamlit display.

        Args:
            text: Text to write
        """
        # Write to original stdout
        self.old_stdout.write(text)

        # Remove ANSI color codes for display
        clean_text = re.sub(r'\x1b\[[0-9;]*m', '', text)

        # Capture for Streamlit
        if clean_text.strip():
            # Filter out verbose log messages (token usage, parameters, mapping statistics, configuration)
            filtered_patterns = [
                # Configuration details
                r'Current Configuration',
                r'Provider: OpenAI',
                r'Model: gpt',
                r'Temperature:',
                r'Top P:',
                r'Max Tokens:',
                r'Threshold: \d+%',
                r'Batch Size:',
                r'Wait Between Batches:',
                r'Use Compact JSON:',
                r'Abbreviate Keys:',
                r'^={10,}$',  # Lines with only equals signs
                r'Calling OpenAI API\.\.\.',

                # Deduplication details
                r'Processing Mapping Results with Deduplication',
                r'Using Parameters:',
                r'Deduplication Summary:',
                r'• Total mappings received:',
                r'• New mappings added:',
                r'• Mappings updated \(better score\):',
                r'• Duplicates ignored:',
                r'• Total unique mappings:',
                r'• Threshold:',

                # Old patterns (kept for backward compatibility)
                r'Token Usage:',
                r'• Input tokens:',
                r'• Output tokens:',
                r'• Total tokens:',
                r'Parameters Used:',
                r'Mapping Statistics:',
                r'• Mapped items:',
                r'• Unmapped items:',
                r'• Average similarity score:',
                r'• Above threshold',
                r'• Below threshold'
            ]

            # Skip this line if it matches any filtered pattern
            if any(re.search(pattern, clean_text) for pattern in filtered_patterns):
                return

            # Track batch completions for metrics
            self._update_batch_metrics(clean_text)

            # Add timestamp
            timestamp = datetime.now().strftime("%H:%M:%S")

            # Determine log type for styling
            log_class = "log-info"
            if "error" in clean_text.lower() or "failed" in clean_text.lower() or "[X]" in clean_text:
                log_class = "log-error"
            elif "success" in clean_text.lower() or "completed" in clean_text.lower() or "[+]" in clean_text:
                log_class = "log-success"
            elif "warning" in clean_text.lower() or "[!]" in clean_text:
                log_class = "log-warning"

            # Highlight batch numbers more prominently
            if "Batch" in clean_text and ("completed" in clean_text.lower() or "processing" in clean_text.lower()):
                log_class = "log-success"

            formatted_line = f'<span class="log-time">[{timestamp}]</span> <span class="{log_class}">{clean_text}</span>'
            self.output.append(formatted_line)

            # Build terminal HTML
            terminal_html = self._build_terminal_html()

            # Try to update UI, but handle NoSessionContext from worker threads
            try:
                self.text_element.markdown(terminal_html, unsafe_allow_html=True)
            except Exception as e:
                # Silently ignore NoSessionContext errors from async threads
                if 'NoSessionContext' not in str(type(e).__name__):
                    raise  # Re-raise if it's a different error

    def _build_terminal_html(self) -> str:
        """
        Build styled terminal HTML output.

        Returns:
            str: HTML string for terminal display
        """
        lines = self.output[-100:]  # Last 100 lines (increased for better visibility)
        content = "<br>".join(lines)

        return f'''
        <div class="terminal-container">
            <div class="terminal-header">
                <span class="terminal-dot red"></span>
                <span class="terminal-dot yellow"></span>
                <span class="terminal-dot green"></span>
                <span class="terminal-title">Processing Output - Live Console</span>
            </div>
            <div class="terminal-body">
                {content}
            </div>
        </div>
        '''

    def flush(self):
        """Flush stdout"""
        self.old_stdout.flush()

    def get_final_html(self) -> str:
        """
        Get final terminal output for display after processing.

        Returns:
            str: HTML string for final terminal display
        """
        return self._build_terminal_html()

    def _update_batch_metrics(self, text: str):
        """
        Parse log messages to update batch processing metrics.

        Args:
            text: Log message text to parse
        """
        # Look for "Batch X of Y completed successfully"
        batch_complete_match = re.search(r'Batch (\d+) of (\d+) completed successfully', text)
        if batch_complete_match:
            current_batch = int(batch_complete_match.group(1))
            total_batches = int(batch_complete_match.group(2))

            self.batches_completed = current_batch
            self.total_batches = total_batches
            self.last_batch_time = datetime.now()

            # Update metrics display
            self._update_metrics_display()

        # Look for batch failures
        elif 'failed' in text.lower() and 'batch' in text.lower():
            self.batches_failed += 1
            self._update_metrics_display()

    def _update_metrics_display(self):
        """
        Update the metrics dashboard display.
        """
        if not self.metrics_placeholder or self.total_batches == 0:
            return

        # Calculate metrics
        batches_remaining = self.total_batches - self.batches_completed
        progress_pct = (self.batches_completed / self.total_batches * 100) if self.total_batches > 0 else 0
        success_rate = ((self.batches_completed - self.batches_failed) / self.batches_completed * 100) if self.batches_completed > 0 else 100

        # Calculate ETA
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        if self.batches_completed > 0:
            avg_time_per_batch = elapsed_time / self.batches_completed
            eta_seconds = avg_time_per_batch * batches_remaining
            eta_minutes = int(eta_seconds / 60)
            eta_display = f"~{eta_minutes} min" if eta_minutes > 0 else "<1 min"
        else:
            eta_display = "Calculating..."

        # Build metrics HTML
        metrics_html = f'''
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            margin-bottom: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        ">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px;">
                    <div style="font-size: 12px; opacity: 0.9; margin-bottom: 5px;">PROGRESS</div>
                    <div style="font-size: 24px; font-weight: bold;">{self.batches_completed}/{self.total_batches}</div>
                    <div style="font-size: 14px; opacity: 0.8;">{progress_pct:.1f}% Complete</div>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px;">
                    <div style="font-size: 12px; opacity: 0.9; margin-bottom: 5px;">REMAINING</div>
                    <div style="font-size: 24px; font-weight: bold;">{batches_remaining}</div>
                    <div style="font-size: 14px; opacity: 0.8;">Batches Left</div>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px;">
                    <div style="font-size: 12px; opacity: 0.9; margin-bottom: 5px;">SUCCESS RATE</div>
                    <div style="font-size: 24px; font-weight: bold;">{success_rate:.1f}%</div>
                    <div style="font-size: 14px; opacity: 0.8;">{self.batches_failed} Failures</div>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px;">
                    <div style="font-size: 12px; opacity: 0.9; margin-bottom: 5px;">EST. TIME</div>
                    <div style="font-size: 24px; font-weight: bold;">{eta_display}</div>
                    <div style="font-size: 14px; opacity: 0.8;">To Completion</div>
                </div>
            </div>
        </div>
        '''

        # Update the placeholder
        try:
            self.metrics_placeholder.markdown(metrics_html, unsafe_allow_html=True)
        except Exception:
            pass  # Silently ignore if placeholder is not available


def load_prompt_from_file(prompt_type: str) -> str:
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
