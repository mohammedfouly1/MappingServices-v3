"""
components/styles.py - Custom CSS styles for Streamlit app
"""


def get_custom_css() -> str:
    """
    Returns custom CSS styles for the Streamlit app.

    Returns:
        str: CSS styles as HTML string
    """
    return """
<style>
    /* Global Styles */
    :root {
        --primary-color: #667eea;
        --secondary-color: #764ba2;
        --success-color: #27ca40;
        --warning-color: #ffcc00;
        --error-color: #ff6b6b;
        --info-color: #00bfff;
        --text-dark: #333;
        --text-light: #666;
        --bg-light: #f8f9fa;
        --border-color: #dee2e6;
        --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 6px 12px rgba(0, 0, 0, 0.15);
    }

    /* Typography */
    .stApp {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    }

    h1, h2, h3, h4, h5, h6 {
        font-weight: 600;
        line-height: 1.3;
        margin-bottom: 0.5rem;
    }

    /* Main Container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    /* Tab Styles */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: var(--bg-light);
        padding: 8px;
        border-radius: 10px;
        margin-bottom: 1rem;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 24px;
        background-color: white;
        border-radius: 8px;
        border: 1px solid var(--border-color);
        font-weight: 500;
        transition: all 0.3s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: #f0f0ff;
        border-color: var(--primary-color);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white !important;
        border: none;
    }

    /* Button Styles */
    .stButton>button {
        width: 100%;
        height: 50px;
        font-size: 16px;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-md);
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }

    .stButton>button:active {
        transform: translateY(0);
    }

    /* Download Button Styles */
    .stDownloadButton>button {
        width: 100%;
        height: 45px;
        font-size: 14px;
        font-weight: 500;
        border-radius: 8px;
        background-color: white;
        color: var(--primary-color);
        border: 2px solid var(--primary-color);
        transition: all 0.3s ease;
    }

    .stDownloadButton>button:hover {
        background-color: var(--primary-color);
        color: white;
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }

    /* Input Styles */
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input,
    .stSelectbox>div>div>div {
        border-radius: 8px;
        border: 2px solid var(--border-color);
        padding: 10px 14px;
        font-size: 14px;
        transition: border-color 0.3s ease;
    }

    .stTextInput>div>div>input:focus,
    .stNumberInput>div>div>input:focus,
    .stSelectbox>div>div>div:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }

    /* File Uploader */
    .stFileUploader {
        border: 2px dashed var(--border-color);
        border-radius: 10px;
        padding: 20px;
        background-color: var(--bg-light);
        transition: all 0.3s ease;
    }

    .stFileUploader:hover {
        border-color: var(--primary-color);
        background-color: #f0f0ff;
    }

    /* Alert Boxes */
    .success-box {
        padding: 16px 20px;
        border-radius: 10px;
        background-color: #d4edda;
        border-left: 4px solid var(--success-color);
        color: #155724;
        margin: 10px 0;
        box-shadow: var(--shadow-sm);
    }

    .error-box {
        padding: 16px 20px;
        border-radius: 10px;
        background-color: #f8d7da;
        border-left: 4px solid var(--error-color);
        color: #721c24;
        margin: 10px 0;
        box-shadow: var(--shadow-sm);
    }

    .info-box {
        padding: 16px 20px;
        border-radius: 10px;
        background-color: #d1ecf1;
        border-left: 4px solid var(--info-color);
        color: #0c5460;
        margin: 10px 0;
        box-shadow: var(--shadow-sm);
    }

    .warning-box {
        padding: 16px 20px;
        border-radius: 10px;
        background-color: #fff3cd;
        border-left: 4px solid var(--warning-color);
        color: #856404;
        margin: 10px 0;
        box-shadow: var(--shadow-sm);
    }

    /* Code and Pre Blocks */
    pre {
        background-color: var(--bg-light);
        padding: 16px;
        border-radius: 8px;
        border: 1px solid var(--border-color);
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        font-size: 13px;
        line-height: 1.6;
        overflow-x: auto;
    }

    /* DataFrame Styles */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: var(--shadow-md);
    }

    .stDataFrame table {
        font-size: 14px;
    }

    .stDataFrame thead tr th {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%) !important;
        color: white !important;
        font-weight: 600;
        padding: 12px !important;
        text-align: left;
    }

    .stDataFrame tbody tr:nth-child(even) {
        background-color: #f8f9fa;
    }

    .stDataFrame tbody tr:hover {
        background-color: #f0f0ff;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: var(--shadow-md);
        border-top: 3px solid var(--primary-color);
    }

    [data-testid="stMetricValue"] {
        font-size: 32px;
        font-weight: 700;
        color: var(--text-dark);
    }

    [data-testid="stMetricLabel"] {
        font-size: 14px;
        font-weight: 500;
        color: var(--text-light);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background-color: var(--bg-light);
        border-radius: 8px;
        padding: 12px 16px;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .streamlit-expanderHeader:hover {
        background-color: #f0f0ff;
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
        max-height: 350px;
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

    /* Card Containers */
    .card {
        background: white;
        border-radius: 12px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
    }

    .card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
    }

    .card-header {
        font-size: 18px;
        font-weight: 600;
        color: var(--text-dark);
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 2px solid var(--bg-light);
    }

    .card-body {
        color: var(--text-light);
        line-height: 1.6;
    }

    /* Section Spacing */
    .section {
        margin: 24px 0;
    }

    .section-title {
        font-size: 20px;
        font-weight: 600;
        color: var(--text-dark);
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .section-title::before {
        content: '';
        width: 4px;
        height: 24px;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        border-radius: 2px;
    }

    /* Grid Layout */
    .grid {
        display: grid;
        gap: 20px;
        margin: 20px 0;
    }

    .grid-2 {
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    }

    .grid-3 {
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    }

    .grid-4 {
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    }

    /* Sidebar Styles */
    .css-1d391kg {
        padding: 2rem 1rem;
    }

    section[data-testid="stSidebar"] {
        background-color: var(--bg-light);
        border-right: 2px solid var(--border-color);
    }

    section[data-testid="stSidebar"] .stButton>button {
        margin-top: 8px;
        margin-bottom: 8px;
    }

    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        border-radius: 10px;
    }

    /* Spinner */
    .stSpinner > div {
        border-top-color: var(--primary-color) !important;
    }

    /* Plotly Charts */
    .js-plotly-plot {
        border-radius: 10px;
        box-shadow: var(--shadow-md);
        overflow: hidden;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .grid-2, .grid-3, .grid-4 {
            grid-template-columns: 1fr;
        }

        .metrics-container {
            flex-direction: column;
        }

        .stButton>button {
            font-size: 14px;
            height: 45px;
        }

        [data-testid="stMetricValue"] {
            font-size: 24px;
        }
    }

    /* Scrollbar Styles */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: var(--bg-light);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary-color);
    }

    /* Tooltip Styles */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }

    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: var(--text-dark);
        color: white;
        text-align: center;
        border-radius: 6px;
        padding: 8px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 12px;
    }

    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }

    /* Loading Animation */
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }

    .loading {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }

    /* Fade In Animation */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }

    /* Badge Styles */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .badge-primary {
        background-color: var(--primary-color);
        color: white;
    }

    .badge-success {
        background-color: var(--success-color);
        color: white;
    }

    .badge-warning {
        background-color: var(--warning-color);
        color: var(--text-dark);
    }

    .badge-error {
        background-color: var(--error-color);
        color: white;
    }

    .badge-info {
        background-color: var(--info-color);
        color: white;
    }
</style>
"""
