import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import re
import time
import json
from datetime import datetime
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Optional, Set, Any
import hashlib
import random
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import warnings
warnings.filterwarnings('ignore')
import io
import os
import networkx as nx
from itertools import combinations
import base64
import html

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="UnInst Analytics - OpenAlex",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# UI COLOR PALETTE (RANDOM ONLY, NOT USER SELECTABLE)
# ============================================================================

UI_COLOR_PALETTES = [
    {
        'name': 'Ocean Depth',
        'primary': '#006994',
        'secondary': '#00b4d8',
        'gradient_start': '#023e8a',
        'gradient_end': '#0077be',
        'accent1': '#03045e',
        'accent2': '#90e0ef',
        'background': '#f0f9ff',
        'card_bg': '#ffffff',
        'text': '#002b36',
        'border': '#caf0f8',
        'success': '#2ecc71',
        'warning': '#f39c12',
        'danger': '#e74c3c'
    },
    {
        'name': 'Forest Canopy',
        'primary': '#2e7d32',
        'secondary': '#81c784',
        'gradient_start': '#1b5e20',
        'gradient_end': '#4caf50',
        'accent1': '#0d3d0d',
        'accent2': '#a5d6a7',
        'background': '#f1f8e9',
        'card_bg': '#ffffff',
        'text': '#1b3b1b',
        'border': '#c8e6c9',
        'success': '#2ecc71',
        'warning': '#f39c12',
        'danger': '#e74c3c'
    },
    {
        'name': 'Sunset',
        'primary': '#e65100',
        'secondary': '#ffb74d',
        'gradient_start': '#bf360c',
        'gradient_end': '#ff9800',
        'accent1': '#8d2f00',
        'accent2': '#ffe082',
        'background': '#fff3e0',
        'card_bg': '#ffffff',
        'text': '#4a2c00',
        'border': '#ffe0b2',
        'success': '#27ae60',
        'warning': '#f39c12',
        'danger': '#e74c3c'
    },
    {
        'name': 'Royal Purple',
        'primary': '#6a1b9a',
        'secondary': '#ba68c8',
        'gradient_start': '#4a148c',
        'gradient_end': '#9c27b0',
        'accent1': '#311b92',
        'accent2': '#ce93d8',
        'background': '#f3e5f5',
        'card_bg': '#ffffff',
        'text': '#2a0f3a',
        'border': '#e1bee7',
        'success': '#2ecc71',
        'warning': '#f39c12',
        'danger': '#e74c3c'
    },
    {
        'name': 'Ruby',
        'primary': '#b71c1c',
        'secondary': '#ef5350',
        'gradient_start': '#8b0000',
        'gradient_end': '#d32f2f',
        'accent1': '#5a0000',
        'accent2': '#ffcdd2',
        'background': '#ffebee',
        'card_bg': '#ffffff',
        'text': '#3b0000',
        'border': '#ffcdd2',
        'success': '#27ae60',
        'warning': '#f39c12',
        'danger': '#e74c3c'
    },
    {
        'name': 'Teal',
        'primary': '#00796b',
        'secondary': '#4db6ac',
        'gradient_start': '#004d40',
        'gradient_end': '#009688',
        'accent1': '#00332e',
        'accent2': '#b2dfdb',
        'background': '#e0f2f1',
        'card_bg': '#ffffff',
        'text': '#00332e',
        'border': '#b2dfdb',
        'success': '#2ecc71',
        'warning': '#f39c12',
        'danger': '#e74c3c'
    },
    {
        'name': 'Midnight',
        'primary': '#2c3e50',
        'secondary': '#3498db',
        'gradient_start': '#1a2632',
        'gradient_end': '#34495e',
        'accent1': '#0a0f14',
        'accent2': '#7f8c8d',
        'background': '#ecf0f1',
        'card_bg': '#ffffff',
        'text': '#2c3e50',
        'border': '#bdc3c7',
        'success': '#27ae60',
        'warning': '#f39c12',
        'danger': '#e74c3c'
    },
    {
        'name': 'Lavender',
        'primary': '#8e44ad',
        'secondary': '#d6a2e8',
        'gradient_start': '#6c3483',
        'gradient_end': '#a569bd',
        'accent1': '#4a235a',
        'accent2': '#e8daef',
        'background': '#f5eef8',
        'card_bg': '#ffffff',
        'text': '#380b4a',
        'border': '#d7bde2',
        'success': '#2ecc71',
        'warning': '#f39c12',
        'danger': '#e74c3c'
    }
]

# ============================================================================
# PLOT COLOR PALETTES (15 OPTIONS FOR USER SELECTION)
# ============================================================================

PLOT_COLOR_PALETTES = [
    {
        'name': 'Viridis (Default)',
        'sequential': 'Viridis',
        'categorical': px.colors.sequential.Viridis,
        'diverging': px.colors.diverging.RdYlBu
    },
    {
        'name': 'Plasma',
        'sequential': 'Plasma',
        'categorical': px.colors.sequential.Plasma,
        'diverging': px.colors.diverging.Spectral
    },
    {
        'name': 'Inferno',
        'sequential': 'Inferno',
        'categorical': px.colors.sequential.Inferno,
        'diverging': px.colors.diverging.RdYlGn
    },
    {
        'name': 'Magma',
        'sequential': 'Magma',
        'categorical': px.colors.sequential.Magma,
        'diverging': px.colors.diverging.PiYG
    },
    {
        'name': 'Cividis',
        'sequential': 'Cividis',
        'categorical': px.colors.sequential.Cividis,
        'diverging': px.colors.diverging.PRGn
    },
    {
        'name': 'Turbo',
        'sequential': 'Turbo',
        'categorical': px.colors.sequential.Turbo,
        'diverging': px.colors.diverging.RdBu
    },
    {
        'name': 'Blues',
        'sequential': 'Blues',
        'categorical': px.colors.sequential.Blues,
        'diverging': px.colors.diverging.RdYlBu
    },
    {
        'name': 'Reds',
        'sequential': 'Reds',
        'categorical': px.colors.sequential.Reds,
        'diverging': px.colors.diverging.RdYlBu
    },
    {
        'name': 'Greens',
        'sequential': 'Greens',
        'categorical': px.colors.sequential.Greens,
        'diverging': px.colors.diverging.RdYlGn
    },
    {
        'name': 'Purples',
        'sequential': 'Purples',
        'categorical': px.colors.sequential.Purples,
        'diverging': px.colors.diverging.PuOr
    },
    {
        'name': 'Oranges',
        'sequential': 'Oranges',
        'categorical': px.colors.sequential.Oranges,
        'diverging': px.colors.diverging.RdBu
    },
    {
        'name': 'Spectral',
        'sequential': 'Spectral',
        'categorical': px.colors.diverging.Spectral,
        'diverging': px.colors.diverging.Spectral
    },
    {
        'name': 'Coolwarm',
        'sequential': 'RdBu',
        'categorical': px.colors.diverging.RdBu,
        'diverging': px.colors.diverging.RdBu
    },
    {
        'name': 'Viridis (Alternative)',
        'sequential': 'Viridis',
        'categorical': px.colors.sequential.Viridis,
        'diverging': px.colors.diverging.RdBu
    },
    {
        'name': 'Electric',
        'sequential': 'Electric',
        'categorical': px.colors.sequential.Electric,
        'diverging': px.colors.diverging.Spectral
    }
]

# Initialize UI palette (random only)
if 'ui_palette' not in st.session_state:
    st.session_state['ui_palette'] = random.choice(UI_COLOR_PALETTES)

# Initialize plot color palette (user selectable)
if 'plot_palette' not in st.session_state:
    st.session_state['plot_palette'] = PLOT_COLOR_PALETTES[0]  # Default to Viridis

# Get current colors
colors = st.session_state['ui_palette']

# ============================================================================
# CUSTOM CSS WITH DYNAMIC COLORS
# ============================================================================

st.markdown(f"""
<style>
    /* Global styles */
    .stApp {{
        background-color: {colors['background']};
    }}
    
    /* Headers */
    .main-header {{
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, {colors['gradient_start']}, {colors['gradient_end']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        padding: 0.5rem 0;
    }}
    
    .sub-header {{
        font-size: 1.5rem;
        font-weight: 600;
        color: {colors['text']};
        margin-bottom: 1rem;
        border-bottom: 3px solid {colors['primary']};
        padding-bottom: 0.5rem;
    }}
    
    /* Cards */
    .card {{
        background: {colors['card_bg']};
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 8px 20px rgba(0,0,0,0.05);
        border: 1px solid {colors['border']};
        margin-bottom: 1rem;
        transition: transform 0.2s, box-shadow 0.2s;
    }}
    
    .card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 12px 25px rgba(0,0,0,0.1);
    }}
    
    .metric-card {{
        background: linear-gradient(135deg, {colors['gradient_start']}10, {colors['gradient_end']}10);
        border-radius: 12px;
        padding: 1rem;
        border-left: 4px solid {colors['primary']};
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }}
    
    .metric-card .value {{
        font-size: 2rem;
        font-weight: 700;
        color: {colors['primary']};
        line-height: 1.2;
    }}
    
    .metric-card .label {{
        font-size: 0.9rem;
        color: {colors['text']};
        opacity: 0.8;
        margin-top: 0.3rem;
    }}
    
    /* Steps */
    .step-container {{
        display: flex;
        justify-content: space-between;
        margin: 2rem 0;
        position: relative;
    }}
    
    .step {{
        flex: 1;
        text-align: center;
        padding: 1rem;
        background: {colors['card_bg']};
        border: 2px solid {colors['border']};
        border-radius: 10px;
        position: relative;
        transition: all 0.3s;
        margin: 0 5px;
    }}
    
    .step.active {{
        border-color: {colors['primary']};
        background: linear-gradient(135deg, {colors['gradient_start']}10, {colors['gradient_end']}10);
    }}
    
    .step.completed {{
        border-color: {colors['success']};
        background: {colors['success']}10;
    }}
    
    .step-number {{
        width: 30px;
        height: 30px;
        background: {colors['primary']};
        color: white;
        border-radius: 50%;
        display: inline-block;
        line-height: 30px;
        margin-bottom: 0.5rem;
    }}
    
    .step.completed .step-number {{
        background: {colors['success']};
    }}
    
    /* Buttons */
    .stButton > button {{
        background: linear-gradient(135deg, {colors['gradient_start']}, {colors['gradient_end']});
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s;
        box-shadow: 0 4px 10px {colors['primary']}30;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 15px {colors['primary']}50;
    }}
    
    .stButton > button:active {{
        transform: translateY(0);
    }}
    
    /* Secondary button */
    .stButton > button[kind="secondary"] {{
        background: white;
        color: {colors['primary']};
        border: 2px solid {colors['primary']};
        box-shadow: none;
    }}
    
    .stButton > button[kind="secondary"]:hover {{
        background: {colors['primary']}10;
    }}
    
    /* Info boxes */
    .info-box {{
        background: {colors['primary']}10;
        border-left: 4px solid {colors['primary']};
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }}
    
    .success-box {{
        background: {colors['success']}10;
        border-left: 4px solid {colors['success']};
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }}
    
    .warning-box {{
        background: {colors['warning']}10;
        border-left: 4px solid {colors['warning']};
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }}
    
    .error-box {{
        background: {colors['danger']}10;
        border-left: 4px solid {colors['danger']};
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }}
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: {colors['card_bg']};
        padding: 0.5rem;
        border-radius: 10px;
        border: 1px solid {colors['border']};
    }}
    
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px;
        padding: 0.5rem 1rem;
        color: {colors['text']};
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {colors['gradient_start']}, {colors['gradient_end']});
        color: white !important;
    }}
    
    /* Progress bar */
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, {colors['gradient_start']}, {colors['gradient_end']});
    }}
    
    /* Dataframe styling */
    .dataframe {{
        border: 1px solid {colors['border']};
        border-radius: 10px;
        overflow: hidden;
    }}
    
    .dataframe th {{
        background: linear-gradient(135deg, {colors['gradient_start']}, {colors['gradient_end']});
        color: white;
        padding: 0.75rem;
        font-weight: 600;
    }}
    
    .dataframe td {{
        padding: 0.5rem 0.75rem;
        border-bottom: 1px solid {colors['border']};
    }}
    
    .dataframe tr:hover {{
        background: {colors['primary']}05;
    }}
    
    /* Recent institutions */
    .recent-inst {{
        background: {colors['card_bg']};
        border: 1px solid {colors['border']};
        border-radius: 8px;
        padding: 0.5rem;
        margin: 0.2rem 0;
        cursor: pointer;
        transition: all 0.2s;
    }}
    
    .recent-inst:hover {{
        border-color: {colors['primary']};
        background: {colors['primary']}05;
    }}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SCIENTIFIC PLOT STYLE CONFIGURATION
# ============================================================================

plt.style.use('default')
plt.rcParams.update({
    'font.size': 10,
    'font.family': 'serif',
    'axes.labelsize': 11,
    'axes.labelweight': 'bold',
    'axes.titlesize': 12,
    'axes.titleweight': 'bold',
    'axes.facecolor': 'white',
    'axes.edgecolor': 'black',
    'axes.linewidth': 1.0,
    'axes.grid': False,
    'xtick.color': 'black',
    'ytick.color': 'black',
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'xtick.direction': 'out',
    'ytick.direction': 'out',
    'xtick.major.size': 4,
    'xtick.minor.size': 2,
    'ytick.major.size': 4,
    'ytick.minor.size': 2,
    'xtick.major.width': 0.8,
    'ytick.major.width': 0.8,
    'legend.fontsize': 10,
    'legend.frameon': True,
    'legend.framealpha': 0.9,
    'legend.edgecolor': 'black',
    'legend.fancybox': False,
    'figure.dpi': 600,
    'savefig.dpi': 600,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1,
    'figure.facecolor': 'white',
    'lines.linewidth': 1.5,
    'lines.markersize': 6,
    'errorbar.capsize': 3,
})

# ============================================================================
# CONFIGURATION
# ============================================================================

OPENALEX_BASE_URL = "https://api.openalex.org"
CROSSREF_BASE_URL = "https://api.crossref.org"
MAILTO = "your-email@example.com"  # Change to your email
HEADERS = {'User-Agent': f'Institution-Analytics (mailto:{MAILTO})'}

# Rate limits
OPENALEX_RATE_LIMIT = 10  # requests per second
CROSSREF_RATE_LIMIT = 50  # requests per second
MAX_RETRIES = 3
BATCH_SIZE = 100  # for Crossref batch queries

# Data limits
MAX_PAPERS_TO_ANALYZE = 10000  # Maximum papers to process
MAX_PAGES = 50  # Maximum pages to fetch (200 papers per page)
WARN_PAPERS_THRESHOLD = 5000  # Show warning above this

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'step' not in st.session_state:
    st.session_state['step'] = 1
if 'institution_id' not in st.session_state:
    st.session_state['institution_id'] = None
if 'institution_name' not in st.session_state:
    st.session_state['institution_name'] = ''
if 'institution_ror' not in st.session_state:
    st.session_state['institution_ror'] = ''
if 'institution_country' not in st.session_state:
    st.session_state['institution_country'] = ''
if 'total_papers' not in st.session_state:
    st.session_state['total_papers'] = 0
if 'papers_data' not in st.session_state:
    st.session_state['papers_data'] = None
if 'years_range' not in st.session_state:
    st.session_state['years_range'] = None
if 'analysis_complete' not in st.session_state:
    st.session_state['analysis_complete'] = False
if 'validation_stats' not in st.session_state:
    st.session_state['validation_stats'] = None
if 'search_results' not in st.session_state:
    st.session_state['search_results'] = None
if 'year_input_text' not in st.session_state:
    st.session_state['year_input_text'] = ''
if 'data_collection_started' not in st.session_state:
    st.session_state['data_collection_started'] = False
if 'issn_cache' not in st.session_state:
    st.session_state['issn_cache'] = {}
if 'crossref_data' not in st.session_state:
    st.session_state['crossref_data'] = None
if 'search_query' not in st.session_state:
    st.session_state['search_query'] = ''
if 'search_performed' not in st.session_state:
    st.session_state['search_performed'] = False
if 'recent_institutions' not in st.session_state:
    st.session_state['recent_institutions'] = []
if 'expanded_details' not in st.session_state:
    st.session_state['expanded_details'] = {}

# ============================================================================
# DATABASE LOADING AND CACHING
# ============================================================================

def normalize_issn(issn: Any) -> Optional[str]:
    """
    Normalize ISSN to 8-digit format without hyphens.
    Handles:
    - With hyphens: 0007-9235 -> 00079235
    - Without hyphens: 15299732 -> 15299732
    - With X at the end: 1234-567X -> 1234567X
    """
    if pd.isna(issn) or not issn:
        return None
    
    # Convert to string and remove any whitespace
    issn_str = str(issn).strip().upper()
    
    # Remove hyphens and spaces
    clean = re.sub(r'[\s-]', '', issn_str)
    
    # If it's all digits or digits with X at the end, pad to 8 digits
    if re.match(r'^\d{7}[\dX]?$', clean) or re.match(r'^\d{1,7}$', clean):
        if len(clean) < 8:
            clean = clean.zfill(8)
        if len(clean) == 8:
            return clean
    
    return None

def parse_crossref_date(date_parts: List) -> Optional[str]:
    """
    Парсит дату из Crossref в формат ГГГГ-ММ-ДД.
    Принимает date_parts в формате [год], [год, месяц] или [год, месяц, день].
    Если день отсутствует, устанавливается 01.
    Если месяц отсутствует, устанавливается 01.
    """
    if not date_parts or not isinstance(date_parts, list):
        return None
    
    # Очищаем от вложенных списков, если есть
    if date_parts and isinstance(date_parts[0], list):
        date_parts = date_parts[0]
    
    if len(date_parts) == 0:
        return None
    
    try:
        year = int(date_parts[0])
        month = int(date_parts[1]) if len(date_parts) > 1 else 1
        day = int(date_parts[2]) if len(date_parts) > 2 else 1
        
        # Валидация
        if year < 1000 or year > 2100:
            return None
        if month < 1 or month > 12:
            month = 1
        if day < 1 or day > 31:
            day = 1
        
        return f"{year:04d}-{month:02d}-{day:02d}"
    except (ValueError, TypeError, IndexError):
        return None

def debug_date_extraction(doi: str, item: Dict, results: Dict):
    """Отладочная функция для проверки извлечения дат"""
    print(f"\n=== DEBUG: Date extraction for DOI: {doi} ===")
    
    # Проверяем все возможные поля с датами
    date_fields = ['published-online', 'created', 'published-print', 'issued', 'journal-issue']
    
    for field in date_fields:
        if field in item:
            if field == 'journal-issue' and 'published' in item[field]:
                date_data = item[field]['published']
            else:
                date_data = item[field]
            
            if 'date-parts' in date_data:
                date_parts = date_data['date-parts']
                parsed = parse_crossref_date(date_parts)
                print(f"  {field}: {date_parts} -> {parsed}")
            else:
                print(f"  {field}: present but no date-parts")
    
    # Проверяем результат
    if doi.lower() in results:
        print(f"  RESULT in results: first_date={results[doi.lower()].get('first_date')}, final_date={results[doi.lower()].get('final_date')}")
    else:
        print(f"  WARNING: DOI not in results yet!")

def format_issn_with_hyphen(issn: str) -> Optional[str]:
    """
    Format ISSN to standard format with hyphen: XXXX-XXXX
    Handles:
    - 20734352 -> 2073-4352
    - 69358 -> 0006-9358 (pad with zeros)
    - 2073-4352 -> 2073-4352 (already formatted)
    """
    if pd.isna(issn) or not issn:
        return None
    
    # Convert to string and remove any whitespace
    issn_str = str(issn).strip().upper()
    
    # Remove existing hyphens first
    clean = re.sub(r'[\s-]', '', issn_str)
    
    # If it's all digits or digits with X, pad to 8 characters
    if re.match(r'^\d+$', clean) or re.match(r'^\d+X$', clean):
        if len(clean) < 8:
            clean = clean.zfill(8)
        if len(clean) == 8:
            # Insert hyphen after 4th character
            return f"{clean[:4]}-{clean[4:]}"
    
    return None

@st.cache_data(show_spinner="Loading WoS database...")
def load_wos_database() -> Tuple[Dict[str, Dict], Dict[str, Dict]]:
    """
    Load WoS database from IF.xlsx
    """
    # Look for file in current directory
    wos_file_path = 'IF.xlsx'
    
    if not os.path.exists(wos_file_path):
        return {}, {}
    
    try:
        df = pd.read_excel(wos_file_path)
        
        # Check for required columns
        required_cols = ['ISSN', 'IF', 'Quartile']
        if not all(col in df.columns for col in required_cols):
            return {}, {}
        
        issn_to_data = {}
        formatted_to_data = {}  # Store formatted ISSNs (with hyphen)
        normalized_to_data = {}  # Store normalized ISSNs (without hyphen)
        
        for _, row in df.iterrows():
            issn = str(row.get('ISSN', '')).strip()
            if pd.notna(issn) and issn and issn.lower() != 'nan':
                if_value = row.get('IF', 0)
                quartile = row.get('Quartile', '')
                journal_title = row.get('Journal title', row.get('Title', ''))  # Try different column names
                
                data = {
                    'if': if_value,
                    'quartile': quartile,
                    'database': 'WoS',
                    'title': journal_title
                }
                
                # Store original ISSN (as in file)
                issn_to_data[issn] = data
                
                # Format ISSN with hyphen
                formatted_issn = format_issn_with_hyphen(issn)
                if formatted_issn and formatted_issn != issn:
                    formatted_to_data[formatted_issn] = data
                
                # Normalize ISSN (remove hyphen)
                normalized_issn = normalize_issn(issn)
                if normalized_issn and normalized_issn != issn and normalized_issn != formatted_issn:
                    normalized_to_data[normalized_issn] = data
        
        # Merge all maps
        all_maps = {**issn_to_data, **formatted_to_data, **normalized_to_data}
        
        return issn_to_data, all_maps
        
    except Exception as e:
        print(f"Error loading WoS database: {e}")
        return {}, {}

@st.cache_data(show_spinner="Loading Scopus database...")
def load_scopus_database() -> Tuple[Dict[str, Dict], Dict[str, Dict]]:
    """
    Load Scopus database from CS.xlsx and normalize quartile values to Q1-Q4 format
    """
    # Look for file in current directory
    scopus_file_path = 'CS.xlsx'
    
    if not os.path.exists(scopus_file_path):
        return {}, {}
    
    try:
        df = pd.read_excel(scopus_file_path)
        
        # Check for required columns
        required_cols = ['Print ISSN', 'CiteScore', 'Quartile']
        if not all(col in df.columns for col in required_cols):
            return {}, {}
        
        issn_to_data = {}
        formatted_to_data = {}  # Store formatted ISSNs (with hyphen)
        normalized_to_data = {}  # Store normalized ISSNs (without hyphen)
        
        for _, row in df.iterrows():
            issn = str(row.get('Print ISSN', '')).strip()
            if pd.notna(issn) and issn and issn.lower() != 'nan':
                citescore = row.get('CiteScore', 0)
                quartile_raw = row.get('Quartile', '')
                
                # Normalize quartile to Q1-Q4 format
                quartile = ''
                if pd.notna(quartile_raw):
                    quartile_str = str(quartile_raw).strip()
                    # Extract the highest quartile (lowest number) if multiple
                    if ',' in quartile_str:
                        quartile_parts = [q.strip() for q in quartile_str.split(',')]
                        # Find the quartile with the smallest number
                        quartile_numbers = []
                        for q in quartile_parts:
                            # Extract number from Q1, Q2, etc. or just number
                            q_num = re.sub(r'[^0-9]', '', q)
                            if q_num:
                                quartile_numbers.append(int(q_num))
                        if quartile_numbers:
                            highest_quartile = min(quartile_numbers)
                            # Handle cases like 10, 20, 30, 40 -> 1, 2, 3, 4
                            if highest_quartile in [10, 20, 30, 40]:
                                quartile = f'Q{highest_quartile // 10}'
                            else:
                                quartile = f'Q{highest_quartile}'
                    else:
                        # Single quartile value
                        if 'Q' in quartile_str.upper():
                            quartile_raw = quartile_str.upper()
                            # Extract number after Q
                            q_num_match = re.search(r'Q(\d+)', quartile_raw)
                            if q_num_match:
                                q_num = int(q_num_match.group(1))
                                # Handle cases like Q10 -> Q1, Q20 -> Q2
                                if q_num in [10, 20, 30, 40]:
                                    quartile = f'Q{q_num // 10}'
                                else:
                                    quartile = quartile_raw
                            else:
                                quartile = quartile_raw
                        else:
                            # Try to extract just the number
                            q_num_match = re.search(r'(\d+)', quartile_str)
                            if q_num_match:
                                q_num = int(q_num_match.group(1))
                                if q_num in [10, 20, 30, 40]:
                                    quartile = f'Q{q_num // 10}'
                                elif 1 <= q_num <= 4:
                                    quartile = f'Q{q_num}'
                                else:
                                    # If number is >4, try to map to quartile
                                    # This is a fallback
                                    if q_num <= 25:
                                        quartile = 'Q1'
                                    elif q_num <= 50:
                                        quartile = 'Q2'
                                    elif q_num <= 75:
                                        quartile = 'Q3'
                                    else:
                                        quartile = 'Q4'
                            else:
                                quartile = ''
                
                source_title = row.get('Source title', row.get('Title', ''))  # Try different column names
                
                data = {
                    'citescore': citescore,
                    'quartile': quartile,
                    'database': 'Scopus',
                    'title': source_title
                }
                
                # Store original ISSN (as in file)
                issn_to_data[issn] = data
                
                # Format ISSN with hyphen
                formatted_issn = format_issn_with_hyphen(issn)
                if formatted_issn and formatted_issn != issn:
                    formatted_to_data[formatted_issn] = data
                
                # Normalize ISSN (remove hyphen)
                normalized_issn = normalize_issn(issn)
                if normalized_issn and normalized_issn != issn and normalized_issn != formatted_issn:
                    normalized_to_data[normalized_issn] = data
        
        # Merge all maps
        all_maps = {**issn_to_data, **formatted_to_data, **normalized_to_data}
        
        return issn_to_data, all_maps
        
    except Exception as e:
        print(f"Error loading Scopus database: {e}")
        return {}, {}

# Load databases at startup
if 'wos_data' not in st.session_state:
    wos_issn, wos_norm = load_wos_database()
    st.session_state['wos_data'] = {
        'issn_map': wos_issn,
        'normalized_map': wos_norm
    }

if 'scopus_data' not in st.session_state:
    scopus_issn, scopus_norm = load_scopus_database()
    st.session_state['scopus_data'] = {
        'issn_map': scopus_issn,
        'normalized_map': scopus_norm
    }

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def normalize_institution_name(name: str) -> str:
    """Normalize institution name for search"""
    if not name:
        return ""
    name = re.sub(r'\s+', ' ', name.strip().lower())
    name = re.sub(r'[^\w\s-]', '', name)
    name = name.replace('-', ' ')
    return name

def is_ror_id(text: str) -> bool:
    """Check if text is a valid ROR ID"""
    pattern = r'^[a-z0-9]{9,10}$'
    return bool(re.match(pattern, text.strip()))

def validate_year_range(years: List[int]) -> Tuple[bool, str]:
    """Validate year range for reasonableness"""
    current_year = datetime.now().year
    
    if not years:
        return False, "No years specified"
    
    if min(years) < 1900:
        return False, "Year cannot be before 1900"
    
    if max(years) > current_year + 1:
        return False, f"Year cannot be after {current_year + 1}"
    
    if len(years) > 30:
        return False, "Period cannot exceed 30 years (performance reasons)"
    
    return True, "Valid"

def check_issn_in_databases(issn_print: Optional[str], issn_electronic: Optional[str], 
                             issn_list: List[str]) -> Tuple[Dict, Dict]:
    """
    Check if any ISSN matches WoS or Scopus databases.
    Now aggressively searches all possible ISSN formats.
    Returns: (wos_info, scopus_info)
    """
    wos_info = {'indexed': False, 'if': None, 'quartile': None, 'title': None}
    scopus_info = {'indexed': False, 'citescore': None, 'quartile': None, 'title': None}
    
    # Collect all ISSNs in all possible formats
    all_issns = set()
    all_variants = set()
    
    # Helper function to add all variants of an ISSN
    def add_issn_variants(issn_val):
        if not issn_val or not isinstance(issn_val, str):
            return
        issn_val = issn_val.strip()
        if not issn_val:
            return
        
        # Add original
        all_issns.add(issn_val)
        
        # Add with hyphen (if not already)
        if '-' not in issn_val:
            formatted = format_issn_with_hyphen(issn_val)
            if formatted:
                all_variants.add(formatted)
        else:
            # Add without hyphen
            normalized = normalize_issn(issn_val)
            if normalized:
                all_variants.add(normalized)
    
    # Add all possible ISSN sources
    if issn_print:
        add_issn_variants(issn_print)
    
    if issn_electronic:
        add_issn_variants(issn_electronic)
    
    for issn in issn_list:
        if issn and isinstance(issn, str):
            add_issn_variants(issn)
    
    # Combine all variants
    all_to_check = all_issns.union(all_variants)
    
    # Check WoS database
    if st.session_state['wos_data']['normalized_map']:
        for issn in all_to_check:
            if issn in st.session_state['wos_data']['normalized_map']:
                data = st.session_state['wos_data']['normalized_map'][issn]
                wos_info = {
                    'indexed': True,
                    'if': data.get('if'),
                    'quartile': data.get('quartile'),
                    'title': data.get('title')
                }
                break
    
    # Check Scopus database
    if st.session_state['scopus_data']['normalized_map']:
        for issn in all_to_check:
            if issn in st.session_state['scopus_data']['normalized_map']:
                data = st.session_state['scopus_data']['normalized_map'][issn]
                scopus_info = {
                    'indexed': True,
                    'citescore': data.get('citescore'),
                    'quartile': data.get('quartile'),
                    'title': data.get('title')
                }
                break
    
    return wos_info, scopus_info

@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_exponential(multiplier=1, max=10)
)
def make_openalex_request(url: str, params: Optional[Dict] = None) -> Optional[Dict]:
    """Make request to OpenAlex API with retry logic"""
    if params is None:
        params = {}
    
    params['mailto'] = MAILTO
    
    try:
        response = requests.get(
            url,
            params=params,
            headers=HEADERS,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 5))
            time.sleep(retry_after)
            raise Exception("Rate limited")
        else:
            st.error(f"OpenAlex API error: {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"Request error: {str(e)}")
        raise

@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_exponential(multiplier=1, max=10)
)
def make_crossref_request_batch(dois: List[str]) -> Dict[str, Dict]:
    """Make synchronous batch request to Crossref API with correct date extraction logic.
    
    Date extraction priorities:
    - print_date: published-print -> issued -> journal-issue.published -> deposited
    - online_date: published-online -> created
    """
    if not dois:
        return {}
    
    unique_dois = list(set(dois))
    results = {}
    
    for i in range(0, len(unique_dois), BATCH_SIZE):
        batch = unique_dois[i:i + BATCH_SIZE]
        
        payload = {"ids": batch}
        
        try:
            response = requests.post(
                f"{CROSSREF_BASE_URL}/works",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                for item in data.get('items', []):
                    doi = item.get('DOI', '')
                    if doi:
                        doi_lower = doi.lower()
                        
                        # --- ИНИЦИАЛИЗАЦИЯ ПЕРЕМЕННЫХ ---
                        online_date = None  # published-online или created
                        print_date = None   # published-print или issued или journal-issue или deposited
                        
                        # --- ONLINE DATE (first/online version) ---
                        # Приоритет 1: published-online
                        if 'published-online' in item:
                            if 'date-parts' in item['published-online']:
                                online_date = parse_crossref_date(item['published-online']['date-parts'])
                        
                        # Приоритет 2: created (если нет published-online)
                        if not online_date and 'created' in item:
                            if 'date-parts' in item['created']:
                                online_date = parse_crossref_date(item['created']['date-parts'])
                        
                        # --- PRINT DATE (final published version) ---
                        # Приоритет 1: published-print
                        if 'published-print' in item:
                            if 'date-parts' in item['published-print']:
                                print_date = parse_crossref_date(item['published-print']['date-parts'])
                        
                        # Приоритет 2: issued (если нет published-print)
                        if not print_date and 'issued' in item:
                            if 'date-parts' in item['issued']:
                                print_date = parse_crossref_date(item['issued']['date-parts'])
                        
                        # Приоритет 3: journal-issue.published (если нет issued)
                        if not print_date and 'journal-issue' in item:
                            if 'published' in item['journal-issue']:
                                if 'date-parts' in item['journal-issue']['published']:
                                    print_date = parse_crossref_date(item['journal-issue']['published']['date-parts'])
                        
                        # Приоритет 4: deposited (если нет других дат публикации)
                        if not print_date and 'deposited' in item:
                            if 'date-parts' in item['deposited']:
                                print_date = parse_crossref_date(item['deposited']['date-parts'])
                        
                        # --- ИЗВЛЕЧЕНИЕ ГОДА ИЗ PRINT DATE ДЛЯ ФИЛЬТРАЦИИ ---
                        publication_year = None
                        if print_date:
                            try:
                                publication_year = int(print_date[:4])
                            except (ValueError, TypeError):
                                pass
                        
                        # Extract ISSN information from Crossref
                        issn_print = None
                        issn_electronic = None
                        issn_list = []
                        
                        # Method 1: Get from ISSN array
                        if 'ISSN' in item and item['ISSN']:
                            issn_list = item['ISSN']
                        
                        # Method 2: Get from issn-type
                        if 'issn-type' in item and isinstance(item['issn-type'], list):
                            for issn_type in item['issn-type']:
                                if isinstance(issn_type, dict):
                                    issn_value = issn_type.get('value', '')
                                    issn_type_name = issn_type.get('type', '').lower()
                                    
                                    if issn_type_name == 'print':
                                        issn_print = issn_value
                                    elif issn_type_name in ['electronic', 'e-issn']:
                                        issn_electronic = issn_value
                                    
                                    if issn_value and issn_value not in issn_list:
                                        issn_list.append(issn_value)
                        
                        # Method 3: If we have ISSN list but no type info
                        if not issn_print and not issn_electronic and issn_list:
                            if len(issn_list) == 1:
                                issn_electronic = issn_list[0]
                            elif len(issn_list) >= 2:
                                issn_print = issn_list[0]
                                issn_electronic = issn_list[1]
                        
                        # Get container title
                        container_title = None
                        if 'container-title' in item and item['container-title']:
                            if isinstance(item['container-title'], list) and item['container-title']:
                                container_title = item['container-title'][0]
                            else:
                                container_title = item['container-title']
                        
                        # Сохраняем результаты с правильными полями дат
                        results[doi_lower] = {
                            'doi': doi,
                            'doi_lower': doi_lower,
                            'year': publication_year,  # Год из print_date для фильтрации
                            'online_date': online_date,  # Дата онлайн-публикации
                            'print_date': print_date,    # Дата печатной публикации
                            'title': item.get('title', [''])[0] if item.get('title') else '',
                            'container-title': container_title or '',
                            'publisher': item.get('publisher', ''),
                            'type': item.get('type', ''),
                            'issn_print': issn_print,
                            'issn_electronic': issn_electronic,
                            'issn_list': issn_list,
                            'is_referenced_by_count': item.get('is-referenced-by-count', 0),
                            'references_count': len(item.get('reference', [])) if item.get('reference') else 0
                        }
            
            # Rate limiting
            time.sleep(0.1)
            
        except Exception as e:
            print(f"Error validating batch {i//BATCH_SIZE + 1}: {str(e)}")
            continue
    
    return results

def search_institution(query: str) -> List[Dict]:
    """Search for institutions in OpenAlex"""
    params = {
        'search': query,
        'per-page': 10
    }
    
    data = make_openalex_request(f"{OPENALEX_BASE_URL}/institutions", params)
    
    results = []
    if data and 'results' in data:
        for inst in data['results']:
            results.append({
                'id': inst.get('id', '').replace('https://openalex.org/', ''),
                'ror': inst.get('ror'),
                'display_name': inst.get('display_name'),
                'country': inst.get('country_code'),
                'type': inst.get('type'),
                'works_count': inst.get('works_count', 0)
            })
    
    return results

def get_institution_by_ror(ror_id: str) -> Optional[Dict]:
    """Get institution by ROR ID"""
    params = {
        'filter': f'ror:{ror_id}'
    }
    
    data = make_openalex_request(f"{OPENALEX_BASE_URL}/institutions", params)
    
    if data and 'results' in data and len(data['results']) > 0:
        inst = data['results'][0]
        return {
            'id': inst.get('id', '').replace('https://openalex.org/', ''),
            'ror': inst.get('ror'),
            'display_name': inst.get('display_name'),
            'country': inst.get('country_code'),
            'type': inst.get('type'),
            'works_count': inst.get('works_count', 0)
        }
    
    return None

def expand_year_range(years: List[int]) -> List[int]:
    """Expand user years to include ±1 for OpenAlex filter"""
    expanded = set()
    for year in years:
        expanded.add(year)
        expanded.add(year - 1)
        expanded.add(year + 1)
    return sorted(list(expanded))

def parse_year_input(year_str: str) -> List[int]:
    """Parse year input from user (e.g., '2023', '2023-2026', '2022-2024,2026')"""
    years = set()
    
    parts = year_str.replace(' ', '').split(',')
    
    for part in parts:
        if '-' in part:
            start, end = part.split('-')
            try:
                start_year = int(start)
                end_year = int(end)
                years.update(range(start_year, end_year + 1))
            except ValueError:
                st.error(f"Invalid year range: {part}")
                return []
        else:
            try:
                years.add(int(part))
            except ValueError:
                st.error(f"Invalid year: {part}")
                return []
    
    return sorted(list(years))

def get_total_papers_count(institution_id: str, years: List[int]) -> int:
    """Get total number of papers for institution in given years (expanded range)"""
    expanded_years = expand_year_range(years)
    year_filter = f"publication_year:{min(expanded_years)}-{max(expanded_years)}"
    
    params = {
        'filter': f'institutions.id:{institution_id},{year_filter}',
        'per-page': 1
    }
    
    data = make_openalex_request(f"{OPENALEX_BASE_URL}/works", params)
    
    if data and 'meta' in data:
        return data['meta'].get('count', 0)
    
    return 0

def fetch_papers_batch(institution_id: str, years: List[int], cursor: str = "*") -> Tuple[List[Dict], Optional[str], int]:
    """Fetch a batch of papers from OpenAlex, returns (papers, next_cursor, count_in_batch)"""
    expanded_years = expand_year_range(years)
    year_filter = f"publication_year:{min(expanded_years)}-{max(expanded_years)}"
    
    params = {
        'filter': f'institutions.id:{institution_id},{year_filter}',
        'per-page': 200,
        'cursor': cursor,
        'sort': 'publication_date:desc'
    }
    
    data = make_openalex_request(f"{OPENALEX_BASE_URL}/works", params)
    
    if data and 'results' in data:
        next_cursor = data.get('meta', {}).get('next_cursor')
        return data['results'], next_cursor, len(data['results'])
    
    return [], None, 0

def extract_dois_from_papers(papers: List[Dict]) -> List[str]:
    """Extract DOIs from papers, preserving original case"""
    dois = []
    for paper in papers:
        doi = paper.get('doi', '')
        if doi:
            # Safe replace - check if doi is string
            if isinstance(doi, str):
                doi = doi.replace('https://doi.org/', '').replace('http://doi.org/', '')
                dois.append(doi)
    return dois

def filter_papers_by_actual_years(papers: List[Dict], crossref_data: Dict[str, Dict], target_years: List[int]) -> Tuple[List[Dict], Dict]:
    """
    Filter papers by actual publication years from Crossref.
    Uses print_date (published-print -> issued -> journal-issue -> deposited) for filtering.
    """
    filtered_papers = []
    validation_stats = {
        'total': len(papers),
        'with_doi': 0,
        'validated': 0,
        'kept': 0,
        'rejected': 0,
        'no_doi': 0,
        'not_found': 0,
        'year_mismatch': 0
    }
    
    for paper in papers:
        doi = paper.get('doi', '')
        if doi and isinstance(doi, str):
            doi = doi.replace('https://doi.org/', '').replace('http://doi.org/', '')
        else:
            doi = ''
        
        if not doi:
            validation_stats['no_doi'] += 1
            # Для статей без DOI используем год из OpenAlex (с предупреждением)
            paper['_validation'] = {
                'source': 'openalex_only',
                'openalex_year': paper.get('publication_year'),
                'kept': paper.get('publication_year') in target_years,
                'note': 'No DOI, using OpenAlex year'
            }
            if paper.get('publication_year') in target_years:
                filtered_papers.append(paper)
                validation_stats['kept'] += 1
            else:
                validation_stats['rejected'] += 1
            continue
        
        validation_stats['with_doi'] += 1
        doi_lower = doi.lower()
        
        if doi_lower in crossref_data:
            validation_stats['validated'] += 1
            
            # Получаем год из print_date (опубликованная версия)
            filter_year = crossref_data[doi_lower].get('year')
            print_date = crossref_data[doi_lower].get('print_date')
            online_date = crossref_data[doi_lower].get('online_date')
            
            # Сохраняем всю информацию о валидации
            paper['_validation'] = {
                'source': 'crossref',
                'filter_year': filter_year,  # Год для фильтрации (из print_date)
                'openalex_year': paper.get('publication_year'),
                'print_date': print_date,
                'online_date': online_date,
                'kept': filter_year in target_years if filter_year else False,
                'crossref_doi': crossref_data[doi_lower]['doi'],
                'crossref_publisher': crossref_data[doi_lower].get('publisher', ''),
                'issn_print': crossref_data[doi_lower].get('issn_print', ''),
                'issn_electronic': crossref_data[doi_lower].get('issn_electronic', ''),
                'issn_list': crossref_data[doi_lower].get('issn_list', []),
                'is_referenced_by_count': crossref_data[doi_lower].get('is_referenced_by_count', 0),
                'references_count': crossref_data[doi_lower].get('references_count', 0)
            }
            
            # Фильтруем по году из print_date
            if filter_year and filter_year in target_years:
                filtered_papers.append(paper)
                validation_stats['kept'] += 1
            else:
                validation_stats['rejected'] += 1
                if filter_year and filter_year != paper.get('publication_year'):
                    validation_stats['year_mismatch'] += 1
        else:
            validation_stats['not_found'] += 1
            # DOI не найден в Crossref, используем OpenAlex год
            paper['_validation'] = {
                'source': 'openalex_only',
                'openalex_year': paper.get('publication_year'),
                'kept': paper.get('publication_year') in target_years,
                'note': 'DOI not found in Crossref'
            }
            if paper.get('publication_year') in target_years:
                filtered_papers.append(paper)
                validation_stats['kept'] += 1
            else:
                validation_stats['rejected'] += 1
    
    return filtered_papers, validation_stats

def enrich_paper_data(paper: Dict, crossref_data: Optional[Dict] = None) -> Dict:
    """Enrich paper data with additional fields including dates from Crossref."""
    doi = paper.get('doi', '')
    if doi and isinstance(doi, str):
        doi = doi.replace('https://doi.org/', '')
    else:
        doi = ''
    
    doi_lower = doi.lower() if doi else ''
    
    # Get publisher from OpenAlex
    publisher_oa = None
    primary_location = paper.get('primary_location')
    if primary_location and isinstance(primary_location, dict):
        source = primary_location.get('source')
        if source and isinstance(source, dict):
            publisher_oa = source.get('host_organization_name') or source.get('publisher')
    
    # Initialize date variables
    online_date = None  # published-online or created
    print_date = None   # published-print or issued or journal-issue or deposited
    publisher_crossref = None
    
    # Get dates from Crossref if available
    if crossref_data and doi_lower in crossref_data:
        publisher_crossref = crossref_data[doi_lower].get('publisher')
        online_date = crossref_data[doi_lower].get('online_date')
        print_date = crossref_data[doi_lower].get('print_date')
    
    # Get ISSN from multiple sources
    issn_print = None
    issn_electronic = None
    issn_list = []
    
    # Source 1: Data from Crossref
    if crossref_data and doi_lower in crossref_data:
        issn_print = crossref_data[doi_lower].get('issn_print')
        issn_electronic = crossref_data[doi_lower].get('issn_electronic')
        issn_list = crossref_data[doi_lower].get('issn_list', [])
    
    # Source 2: If Crossref didn't provide ISSN, try from OpenAlex
    if not issn_list and not issn_print and not issn_electronic:
        primary_location = paper.get('primary_location')
        if primary_location and isinstance(primary_location, dict):
            source = primary_location.get('source')
            if source and isinstance(source, dict):
                oa_issn_list = source.get('issn', [])
                if oa_issn_list and isinstance(oa_issn_list, list):
                    issn_list = oa_issn_list
                    if 'issn_l' in source and source['issn_l']:
                        if source['issn_l'] not in issn_list:
                            issn_list.append(source['issn_l'])
    
    # Clean ISSN list
    if issn_list:
        issn_list = [issn for issn in issn_list if issn and str(issn).strip()]
        issn_list = list(set(issn_list))
    
    # Check WoS and Scopus indexing
    wos_info, scopus_info = check_issn_in_databases(issn_print, issn_electronic, issn_list)
    
    validation = paper.get('_validation', {})
    
    # Determine which year to use for display
    display_year = None
    if print_date:
        try:
            display_year = int(print_date[:4])
        except (ValueError, TypeError):
            display_year = paper.get('publication_year')
    else:
        display_year = paper.get('publication_year')
    
    enriched = {
        'id': paper.get('id', ''),
        'doi': doi,
        # Date fields
        'online_date': online_date,  # Дата онлайн-публикации
        'print_date': print_date,    # Дата печатной публикации
        'publication_year': display_year,  # Год для отображения (из print_date)
        # Basic info
        'title': paper.get('title', 'No title'),
        'publication_date': paper.get('publication_date', ''),
        'cited_by_count': paper.get('cited_by_count', 0),
        'referenced_works_count': paper.get('referenced_works_count', len(paper.get('referenced_works', []))),
        'type': paper.get('type', ''),
        'is_oa': paper.get('open_access', {}).get('is_oa', False),
        'validation': validation,
        'publisher_oa': publisher_oa,
        'publisher_crossref': publisher_crossref,
        'publisher': publisher_crossref or publisher_oa or 'Unknown',
        # ISSN info
        'issn_print': issn_print,
        'issn_electronic': issn_electronic,
        'issn_list': issn_list,
        'is_referenced_by_count': validation.get('is_referenced_by_count', 0) if validation else 0,
        'references_count': validation.get('references_count', paper.get('referenced_works_count', 0)) if validation else paper.get('referenced_works_count', 0),
        # WoS indexing info
        'wos_indexed': wos_info['indexed'],
        'wos_if': wos_info.get('if'),
        'wos_quartile': wos_info.get('quartile'),
        'wos_journal': wos_info.get('title'),
        # Scopus indexing info
        'scopus_indexed': scopus_info['indexed'],
        'scopus_citescore': scopus_info.get('citescore'),
        'scopus_quartile': scopus_info.get('quartile'),
        'scopus_journal': scopus_info.get('title'),
        # Combined indexing
        'indexed_in': []
    }
    
    # Add to indexed_in list
    if wos_info['indexed']:
        enriched['indexed_in'].append('WoS')
    if scopus_info['indexed']:
        enriched['indexed_in'].append('Scopus')
    
    # Authors processing
    authorships = paper.get('authorships', [])
    authors = []
    author_affiliations = []
    author_countries = set()
    
    for authorship in authorships:
        if authorship.get('author'):
            author_name = authorship['author'].get('display_name', '')
            if author_name:
                authors.append(author_name)
                
                institutions = authorship.get('institutions', [])
                for inst in institutions:
                    if inst and inst.get('country_code'):
                        author_countries.add(inst['country_code'])
                    if inst and inst.get('display_name'):
                        author_affiliations.append(inst['display_name'])
    
    enriched['authors'] = authors
    enriched['author_count'] = len(authors)
    enriched['author_countries'] = list(author_countries)
    enriched['affiliations'] = list(set(author_affiliations))
    
    # Journal name
    primary_location = paper.get('primary_location')
    if primary_location and isinstance(primary_location, dict):
        source = primary_location.get('source')
        if source and isinstance(source, dict):
            enriched['journal'] = source.get('display_name', 'Unknown')
        else:
            enriched['journal'] = 'Unknown'
    else:
        enriched['journal'] = 'Unknown'
    
    # Collaboration type
    inst_count = len(set(author_affiliations))
    country_count = len(author_countries)
    
    if inst_count <= 1:
        enriched['collaboration_type'] = 'Intra-institutional'
    elif country_count <= 1:
        enriched['collaboration_type'] = 'Inter-institutional (domestic)'
    else:
        enriched['collaboration_type'] = 'International'
    
    return enriched

def calculate_citations_per_year(citations: int, pub_year: int, current_year: int = None) -> float:
    """Calculate average citations per year"""
    if current_year is None:
        current_year = datetime.now().year
    
    years_since = max(1, current_year - pub_year)
    return citations / years_since

def add_to_recent_institutions(inst: Dict):
    """Add institution to recent list"""
    recent = st.session_state['recent_institutions']
    
    # Check if already exists
    for i, existing in enumerate(recent):
        if existing['id'] == inst['id']:
            # Move to front
            recent.pop(i)
            recent.insert(0, inst)
            break
    else:
        # Add new
        recent.insert(0, inst)
    
    # Keep only last 5
    st.session_state['recent_institutions'] = recent[:5]

# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

def analyze_papers(papers: List[Dict], crossref_data: Optional[Dict] = None) -> Dict:
    """Perform comprehensive analysis on papers"""
    if not papers:
        return {
            'total_papers': 0,
            'total_citations': 0,
            'yearly_papers': {},
            'yearly_citations': {},
            'yearly_papers_wos': {},
            'yearly_papers_scopus': {},
            'yearly_papers_both': {},
            'top_authors': [],
            'top_journals': [],
            'top_publishers': [],
            'citation_distribution': {k: 0 for k in ['0', '1-4', '5-10', '11-30', '31-50', '51-100', '100+']},
            'top_cited': [],
            'top_citations_per_year': [],
            'collaboration_types': {},
            'yearly_collaboration': {},
            'country_collaborations': [],
            'enriched_papers': []
        }
    
    enriched_papers = [enrich_paper_data(p, crossref_data) for p in papers if p]
    
    total_papers = len(enriched_papers)
    total_citations = sum(p['cited_by_count'] for p in enriched_papers)
    
    # Count papers by database indexing
    wos_papers = [p for p in enriched_papers if p.get('wos_indexed')]
    scopus_papers = [p for p in enriched_papers if p.get('scopus_indexed')]
    both_papers = [p for p in enriched_papers if p.get('wos_indexed') and p.get('scopus_indexed')]
    
    yearly_papers = defaultdict(int)
    yearly_citations = defaultdict(int)
    yearly_papers_wos = defaultdict(int)
    yearly_papers_scopus = defaultdict(int)
    yearly_papers_both = defaultdict(int)
    
    for p in enriched_papers:
        year = p['publication_year']
        if year:
            yearly_papers[year] += 1
            yearly_citations[year] += p['cited_by_count']
            if p.get('wos_indexed'):
                yearly_papers_wos[year] += 1
            if p.get('scopus_indexed'):
                yearly_papers_scopus[year] += 1
            if p.get('wos_indexed') and p.get('scopus_indexed'):
                yearly_papers_both[year] += 1
    
    all_authors = []
    for p in enriched_papers:
        all_authors.extend(p.get('authors', []))
    
    author_counts = Counter(all_authors)
    top_authors = author_counts.most_common(20)
    
    journal_counts = Counter(p.get('journal', 'Unknown') for p in enriched_papers)
    top_journals = journal_counts.most_common(20)
    
    publisher_counts = Counter(p.get('publisher', 'Unknown') for p in enriched_papers if p.get('publisher'))
    top_publishers = publisher_counts.most_common(20)
    
    citations = [p['cited_by_count'] for p in enriched_papers]
    citation_ranges = {
        '0': sum(1 for c in citations if c == 0),
        '1-4': sum(1 for c in citations if 1 <= c <= 4),
        '5-10': sum(1 for c in citations if 5 <= c <= 10),
        '11-30': sum(1 for c in citations if 11 <= c <= 30),
        '31-50': sum(1 for c in citations if 31 <= c <= 50),
        '51-100': sum(1 for c in citations if 51 <= c <= 100),
        '100+': sum(1 for c in citations if c > 100)
    }
    
    top_cited = sorted(enriched_papers, key=lambda x: x.get('cited_by_count', 0), reverse=True)[:20]
    
    current_year = datetime.now().year
    for p in enriched_papers:
        if p.get('publication_year'):
            p['citations_per_year'] = calculate_citations_per_year(
                p.get('cited_by_count', 0), p['publication_year'], current_year
            )
        else:
            p['citations_per_year'] = 0
    
    top_cpy = sorted(enriched_papers, key=lambda x: x.get('citations_per_year', 0), reverse=True)[:20]
    
    collab_types = Counter(p.get('collaboration_type', 'Unknown') for p in enriched_papers)
    
    yearly_collab = defaultdict(lambda: defaultdict(int))
    for p in enriched_papers:
        year = p.get('publication_year')
        if year:
            yearly_collab[year][p.get('collaboration_type', 'Unknown')] += 1
    
    # Collect country collaborations for network graph
    country_collaborations = []
    for p in enriched_papers:
        countries = p.get('author_countries', [])
        if len(countries) >= 2:
            # Create all possible pairs of countries for this paper
            for pair in combinations(sorted(countries), 2):
                country_collaborations.append({
                    'source': pair[0],
                    'target': pair[1],
                    'weight': 1,
                    'year': p.get('publication_year')
                })
    
    return {
        'total_papers': total_papers,
        'total_citations': total_citations,
        'wos_papers': len(wos_papers),
        'scopus_papers': len(scopus_papers),
        'both_papers': len(both_papers),
        'yearly_papers': dict(yearly_papers),
        'yearly_citations': dict(yearly_citations),
        'yearly_papers_wos': dict(yearly_papers_wos),
        'yearly_papers_scopus': dict(yearly_papers_scopus),
        'yearly_papers_both': dict(yearly_papers_both),
        'top_authors': top_authors,
        'top_journals': top_journals,
        'top_publishers': top_publishers,
        'citation_distribution': citation_ranges,
        'top_cited': top_cited,
        'top_citations_per_year': top_cpy,
        'collaboration_types': dict(collab_types),
        'yearly_collaboration': {k: dict(v) for k, v in yearly_collab.items()},
        'country_collaborations': country_collaborations,
        'enriched_papers': enriched_papers
    }

def run_analysis_with_progress(institution_id: str, years: List[int], total_estimated: int, 
                                progress_container, status_container) -> bool:
    """Run complete analysis with progress tracking using correct date logic."""
    try:
        all_papers = []
        cursor = "*"
        page = 0
        total_pages_to_fetch = min(
            (total_estimated // 200) + 1,
            MAX_PAGES
        )
        
        status_container.text("Loading data from OpenAlex...")
        
        papers_to_fetch = min(total_estimated, MAX_PAPERS_TO_ANALYZE)
        status_container.text(f"Loading up to {papers_to_fetch:,} papers...")
        
        progress_bar = progress_container.progress(0)
        
        while cursor and len(all_papers) < MAX_PAPERS_TO_ANALYZE and page < MAX_PAGES:
            page += 1
            progress = min(0.1 + (page / total_pages_to_fetch) * 0.3, 0.4)
            progress_bar.progress(progress)
            
            papers, next_cursor, batch_count = fetch_papers_batch(
                institution_id,
                years,
                cursor
            )
            
            all_papers.extend(papers)
            cursor = next_cursor
            
            status_container.text(f"Loaded {len(all_papers)} papers (page {page}/{total_pages_to_fetch})...")
            time.sleep(0.1)
        
        status_container.text(f"✅ Loaded {len(all_papers)} papers from OpenAlex")
        progress_bar.progress(0.4)
        
        dois = extract_dois_from_papers(all_papers)
        status_container.text(f"Found {len(dois)} DOIs for validation")
        progress_bar.progress(0.45)
        
        # Check cache for existing data
        dois_to_fetch = [doi for doi in dois if doi.lower() not in st.session_state['issn_cache']]
        
        if dois_to_fetch:
            status_container.text(f"Fetching new data for {len(dois_to_fetch)} DOIs from Crossref...")
            new_crossref_data = make_crossref_request_batch(dois_to_fetch)
            
            # Update cache
            for doi_lower, data in new_crossref_data.items():
                st.session_state['issn_cache'][doi_lower] = data
        else:
            status_container.text("Using cached data for all DOIs")
            new_crossref_data = {}
        
        # Build complete crossref_data from cache
        crossref_data = {}
        for doi in dois:
            doi_lower = doi.lower()
            if doi_lower in st.session_state['issn_cache']:
                crossref_data[doi_lower] = st.session_state['issn_cache'][doi_lower]
        
        status_container.text(f"✅ Validated {len(crossref_data)} DOIs")
        progress_bar.progress(0.7)
        
        status_container.text("Filtering by actual publication years (using print_date)...")
        
        filtered_papers, validation_stats = filter_papers_by_actual_years(
            all_papers,
            crossref_data,
            years  # target_years = исходные годы пользователя [2008, 2023, 2024, 2025]
        )
        
        progress_bar.progress(0.8)
        
        status_container.text("Analyzing data and checking WoS/Scopus indexing...")
        
        analysis_results = analyze_papers(filtered_papers, crossref_data)
        
        st.session_state['papers_data'] = analysis_results
        st.session_state['validation_stats'] = validation_stats
        st.session_state['analysis_complete'] = True
        st.session_state['crossref_data'] = crossref_data
        
        progress_bar.progress(1.0)
        status_container.text("✅ Analysis complete!")

        # Debug output for first 5 papers
        print("\n=== DEBUG: First 5 enriched papers dates ===")
        for i, paper in enumerate(analysis_results['enriched_papers'][:5]):
            print(f"Paper {i+1}:")
            print(f"  DOI={paper.get('doi')}")
            print(f"  online_date={paper.get('online_date')}")
            print(f"  print_date={paper.get('print_date')}")
            print(f"  display_year={paper.get('publication_year')}")
            print(f"  kept_in_analysis={paper.get('publication_year') in years}")
        
        time.sleep(1)
        
        return True
        
    except Exception as e:
        status_container.text(f"❌ Error: {str(e)}")
        st.error(f"Analysis failed: {str(e)}")
        return False

# ============================================================================
# PLOTTING FUNCTIONS (PLOTLY) WITH SCIENTIFIC STYLE
# ============================================================================

def apply_scientific_style(fig: go.Figure) -> go.Figure:
    """Apply scientific style to plotly figures"""
    fig.update_layout(
        font=dict(
            family="serif",
            size=10,
        ),
        title_font=dict(
            family="serif",
            size=12,
            weight="bold"
        ),
        title=dict(
            x=0.5,  # Center title
            xanchor='center'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        hoverlabel=dict(
            font_family="serif",
            font_size=10
        ),
        margin=dict(l=60, r=30, t=60, b=60)
    )
    
    fig.update_xaxes(
        showline=True,
        linewidth=1,
        linecolor='black',
        mirror=True,
        ticks='outside',
        tickwidth=1,
        tickcolor='black',
        ticklen=4,
        gridcolor='lightgrey',
        griddash='dot',
        gridwidth=0.5,
        showgrid=False,  # No grid per scientific style
        title_font=dict(family="serif", size=11, weight="bold"),
        tickfont=dict(family="serif", size=10)
    )
    
    fig.update_yaxes(
        showline=True,
        linewidth=1,
        linecolor='black',
        mirror=True,
        ticks='outside',
        tickwidth=1,
        tickcolor='black',
        ticklen=4,
        gridcolor='lightgrey',
        griddash='dot',
        gridwidth=0.5,
        showgrid=False,  # No grid per scientific style
        title_font=dict(family="serif", size=11, weight="bold"),
        tickfont=dict(family="serif", size=10)
    )
    
    return fig

def plot_yearly_publications(yearly_data: Dict[int, int], plot_palette: Dict, colors: Dict):
    """Plot yearly publications"""
    years = sorted(yearly_data.keys())
    counts = [yearly_data[y] for y in years]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=years,
        y=counts,
        marker_color=plot_palette['categorical'][0] if plot_palette['categorical'] else colors['primary'],
        marker_line_color='black',
        marker_line_width=1,
        name='Publications'
    ))
    
    fig.update_layout(
        title='Publications by Year',
        xaxis_title='Year',
        yaxis_title='Number of Publications',
        hovermode='x',
        showlegend=False
    )
    
    fig = apply_scientific_style(fig)
    fig.update_xaxes(tickangle=45)
    return fig

def plot_comparative_publications(yearly_papers: Dict[int, int], 
                                   yearly_wos: Dict[int, int], 
                                   yearly_scopus: Dict[int, int],
                                   plot_palette: Dict, colors: Dict):
    """Plot comparative publications by year (OpenAlex vs WoS vs Scopus)"""
    years = sorted(set(list(yearly_papers.keys()) + list(yearly_wos.keys()) + list(yearly_scopus.keys())))
    
    all_counts = [yearly_papers.get(y, 0) for y in years]
    wos_counts = [yearly_wos.get(y, 0) for y in years]
    scopus_counts = [yearly_scopus.get(y, 0) for y in years]
    
    fig = go.Figure()
    
    categorical = plot_palette['categorical']
    if len(categorical) < 3:
        categorical = categorical * 3
    
    fig.add_trace(go.Bar(
        name='All OpenAlex',
        x=years,
        y=all_counts,
        marker_color=categorical[0],
        opacity=0.7
    ))
    
    fig.add_trace(go.Bar(
        name='WoS Indexed',
        x=years,
        y=wos_counts,
        marker_color=categorical[1],
        opacity=0.7
    ))
    
    fig.add_trace(go.Bar(
        name='Scopus Indexed',
        x=years,
        y=scopus_counts,
        marker_color=categorical[2],
        opacity=0.7
    ))
    
    fig.update_layout(
        title='Comparative Publications by Year: OpenAlex vs WoS vs Scopus',
        xaxis_title='Year',
        yaxis_title='Number of Publications',
        barmode='group',
        hovermode='x'
    )
    
    fig = apply_scientific_style(fig)
    fig.update_xaxes(tickangle=45)
    return fig

def plot_yearly_citations(yearly_citations: Dict[int, int], plot_palette: Dict, colors: Dict):
    """Plot yearly citations"""
    years = sorted(yearly_citations.keys())
    citations = [yearly_citations[y] for y in years]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=years,
        y=citations,
        marker_color=plot_palette['categorical'][1] if len(plot_palette['categorical']) > 1 else plot_palette['categorical'][0],
        marker_line_color='black',
        marker_line_width=1,
        name='Citations'
    ))
    
    fig.update_layout(
        title='Citations by Year (Total)',
        xaxis_title='Year',
        yaxis_title='Total Citations',
        hovermode='x',
        showlegend=False
    )
    
    fig = apply_scientific_style(fig)
    fig.update_xaxes(tickangle=45)
    return fig

def plot_top_authors(authors_data: List[Tuple[str, int]], plot_palette: Dict, colors: Dict):
    """Plot top authors"""
    authors = [a[0][:30] + '...' if len(a[0]) > 30 else a[0] for a in authors_data[:15]]
    counts = [a[1] for a in authors_data[:15]]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=authors[::-1],
        x=counts[::-1],
        orientation='h',
        marker_color=plot_palette['categorical'][0],
        marker_line_color='black',
        marker_line_width=1
    ))
    
    fig.update_layout(
        title='Top Authors by Publication Count',
        xaxis_title='Number of Publications',
        yaxis_title='Author',
        height=500,
        showlegend=False
    )
    
    fig = apply_scientific_style(fig)
    return fig

def plot_top_journals(journals_data: List[Tuple[str, int]], plot_palette: Dict, colors: Dict):
    """Plot top journals"""
    journals = [j[0][:40] + '...' if len(j[0]) > 40 else j[0] for j in journals_data[:15]]
    counts = [j[1] for j in journals_data[:15]]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=journals[::-1],
        x=counts[::-1],
        orientation='h',
        marker_color=plot_palette['categorical'][1] if len(plot_palette['categorical']) > 1 else plot_palette['categorical'][0],
        marker_line_color='black',
        marker_line_width=1
    ))
    
    fig.update_layout(
        title='Top Journals by Publication Count',
        xaxis_title='Number of Publications',
        yaxis_title='Journal',
        height=500,
        showlegend=False
    )
    
    fig = apply_scientific_style(fig)
    return fig

def plot_top_publishers(publishers_data: List[Tuple[str, int]], plot_palette: Dict, colors: Dict):
    """Plot top publishers with distinct colors"""
    publishers = [p[0][:30] + '...' if len(p[0]) > 30 else p[0] for p in publishers_data[:15]]
    counts = [p[1] for p in publishers_data[:15]]
    
    # Use categorical palette with enough distinct colors
    colors_list = plot_palette['categorical']
    if len(colors_list) < len(publishers):
        # Repeat colors if needed
        colors_list = colors_list * (len(publishers) // len(colors_list) + 1)
    
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=publishers,
        values=counts,
        marker_colors=colors_list[:len(publishers)],
        textinfo='percent+label',
        insidetextorientation='radial',
        textfont=dict(family="serif", size=10)
    ))
    
    fig.update_layout(
        title='Top Publishers Distribution',
        height=500,
        showlegend=False
    )
    
    fig = apply_scientific_style(fig)
    return fig

def plot_citation_distribution(distribution: Dict[str, int], plot_palette: Dict, colors: Dict):
    """Plot citation distribution"""
    categories = list(distribution.keys())
    counts = list(distribution.values())
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=categories,
        y=counts,
        marker_color=plot_palette['categorical'][2] if len(plot_palette['categorical']) > 2 else plot_palette['categorical'][0],
        marker_line_color='black',
        marker_line_width=1
    ))
    
    fig.update_layout(
        title='Citation Distribution',
        xaxis_title='Citation Range',
        yaxis_title='Number of Papers',
        hovermode='x'
    )
    
    fig = apply_scientific_style(fig)
    return fig

def plot_collaboration_types(collab_data: Dict[str, int], plot_palette: Dict, colors: Dict):
    """Plot collaboration types"""
    labels = list(collab_data.keys())
    values = list(collab_data.values())
    
    # Use first 3 colors from categorical palette
    colors_list = plot_palette['categorical'][:3]
    
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=labels,
        values=values,
        marker_colors=colors_list,
        textinfo='percent+label',
        insidetextorientation='radial',
        textfont=dict(family="serif", size=10)
    ))
    
    fig.update_layout(
        title='Collaboration Types',
        height=400
    )
    
    fig = apply_scientific_style(fig)
    return fig

def plot_yearly_collaboration(yearly_collab: Dict, plot_palette: Dict, colors: Dict):
    """Plot yearly collaboration breakdown"""
    years = sorted(yearly_collab.keys())
    
    intra = []
    inter = []
    international = []
    
    for year in years:
        data = yearly_collab[year]
        intra.append(data.get('Intra-institutional', 0))
        inter.append(data.get('Inter-institutional (domestic)', 0))
        international.append(data.get('International', 0))
    
    # Use first 3 colors from categorical palette
    colors_list = plot_palette['categorical'][:3]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Intra-institutional',
        x=years,
        y=intra,
        marker_color=colors_list[0]
    ))
    
    fig.add_trace(go.Bar(
        name='Inter-institutional (domestic)',
        x=years,
        y=inter,
        marker_color=colors_list[1]
    ))
    
    fig.add_trace(go.Bar(
        name='International',
        x=years,
        y=international,
        marker_color=colors_list[2]
    ))
    
    fig.update_layout(
        title='Collaboration Types by Year',
        xaxis_title='Year',
        yaxis_title='Number of Publications',
        barmode='stack',
        hovermode='x'
    )
    
    fig = apply_scientific_style(fig)
    fig.update_xaxes(tickangle=45)
    return fig

def plot_country_collaboration_network(country_collabs: List[Dict], plot_palette: Dict, colors: Dict):
    """Plot country collaboration network with domestic and international edges"""
    if len(country_collabs) < 2:
        return None
    
    # Create graph
    G = nx.Graph()
    
    # Add edges with weights
    for collab in country_collabs:
        source = collab['source']
        target = collab['target']
        if source and target and source != target:
            if G.has_edge(source, target):
                G[source][target]['weight'] += 1
            else:
                G.add_edge(source, target, weight=1)
    
    if len(G.nodes()) < 2:
        return None
    
    # Calculate layout
    pos = nx.spring_layout(G, k=2, iterations=50)
    
    # Prepare edge traces
    edge_x = []
    edge_y = []
    edge_colors = []
    
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        
        # Color edges: domestic (same country) vs international
        # For demo, we'll use different colors based on edge weight or node similarity
        # In real implementation, you'd need country information
        edge_colors.append(plot_palette['categorical'][1] if edge[2].get('weight', 1) > 1 else plot_palette['categorical'][0])
    
    # Node traces
    node_x = []
    node_y = []
    node_text = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
    
    fig = go.Figure()
    
    # Add edges
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color=plot_palette['categorical'][0]),
        hoverinfo='none',
        mode='lines'
    )
    fig.add_trace(edge_trace)
    
    # Add nodes
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="top center",
        hoverinfo='text',
        marker=dict(
            size=20,
            color=plot_palette['categorical'][2],
            line=dict(color='black', width=1)
        ),
        textfont=dict(family="serif", size=10)
    )
    fig.add_trace(node_trace)
    
    fig.update_layout(
        title='Country Collaboration Network',
        showlegend=False,
        hovermode='closest',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=500
    )
    
    fig = apply_scientific_style(fig)
    return fig

def plot_citations_vs_references(papers: List[Dict], plot_palette: Dict, colors: Dict):
    """Plot citations vs references scatter with real reference counts"""
    citations = [p['cited_by_count'] for p in papers]
    references = [p.get('references_count', 0) for p in papers]
    years = [p['publication_year'] for p in papers]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=references,
        y=citations,
        mode='markers',
        marker=dict(
            size=8,
            color=years,
            colorscale=plot_palette['sequential'],
            showscale=True,
            colorbar=dict(
                title='Year',
                title_font=dict(family='serif', size=10),
                tickfont=dict(family='serif', size=9)
            ),
            line=dict(width=1, color='white')
        ),
        text=[(p['title'][:50] + '...') if p.get('title') and isinstance(p['title'], str) else 'No title' for p in papers],
        hovertemplate='<b>%{text}</b><br>Citations: %{y}<br>References: %{x}<br>Year: %{marker.color}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Citations vs References (with Year Color Map)',
        xaxis_title='Number of References',
        yaxis_title='Number of Citations',
        height=500
    )
    
    fig = apply_scientific_style(fig)
    return fig

def plot_quartile_distribution(papers: List[Dict], database: str, plot_palette: Dict, colors: Dict):
    """Plot quartile distribution for WoS or Scopus (only Q1-Q4 format)"""
    if database == 'WoS':
        quartiles = [p.get('wos_quartile') for p in papers if p.get('wos_indexed') and p.get('wos_quartile')]
        title = 'WoS Quartile Distribution'
        color_idx = 0
    else:
        quartiles = [p.get('scopus_quartile') for p in papers if p.get('scopus_indexed') and p.get('scopus_quartile')]
        title = 'Scopus Quartile Distribution'
        color_idx = 1
    
    if not quartiles:
        return None
    
    # Filter to only include Q1-Q4 format and normalize
    filtered_quartiles = []
    for q in quartiles:
        if q and isinstance(q, str):
            # Extract just the Q1, Q2, etc. part
            match = re.search(r'(Q[1-4])', q.upper())
            if match:
                filtered_quartiles.append(match.group(1))
            elif q.strip() in ['1', '2', '3', '4']:
                filtered_quartiles.append(f'Q{q.strip()}')
    
    if not filtered_quartiles:
        return None
    
    quartile_counts = Counter(filtered_quartiles)
    # Ensure all Q1-Q4 are present
    for q in ['Q1', 'Q2', 'Q3', 'Q4']:
        if q not in quartile_counts:
            quartile_counts[q] = 0
    
    # Sort in order Q1, Q2, Q3, Q4
    sorted_items = sorted([(str(k), v) for k, v in quartile_counts.items()], key=lambda x: x[0])
    
    # Use colors from palette
    colors_list = plot_palette['categorical']
    bar_color = colors_list[color_idx % len(colors_list)]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[item[0] for item in sorted_items],
        y=[item[1] for item in sorted_items],
        marker_color=bar_color,
        marker_line_color='black',
        marker_line_width=1
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Quartile',
        yaxis_title='Number of Papers'
    )
    
    fig = apply_scientific_style(fig)
    return fig

def plot_top_cited_table(papers: List[Dict], title: str, colors: Dict):
    """Create a table for top cited papers"""
    if not papers:
        return None
    
    df = pd.DataFrame([
        {
            'Title': p['title'][:80] + '...' if len(p['title']) > 80 else p['title'],
            'Citations': p['cited_by_count'],
            'Year': p['publication_year'],
            'Authors': ', '.join(p['authors'][:3]) + (' et al.' if len(p['authors']) > 3 else ''),
            'Journal': p['journal'][:30] + '...' if len(p['journal']) > 30 else p['journal'],
            'WoS': '✓' if p.get('wos_indexed') else '',
            'Scopus': '✓' if p.get('scopus_indexed') else ''
        }
        for p in papers[:20]
    ])
    
    return df

# ============================================================================
# HTML REPORT GENERATION
# ============================================================================

def get_color_for_heatmap(value: float, max_value: float) -> str:
    """Generate color for heatmap cell based on value"""
    if max_value == 0:
        return '#ffffff'
    
    ratio = value / max_value
    # Blue to red gradient
    r = int(255 * ratio)
    g = int(255 * (1 - ratio) * 0.3)
    b = int(255 * (1 - ratio))
    return f'rgb({r}, {g}, {b})'

def generate_institution_html_report(data: Dict, validation: Dict, institution_name: str, 
                                      institution_ror: str, institution_country: str, 
                                      years_range: List[int], colors: Dict) -> str:
    """Generate comprehensive HTML report for institution analysis"""
    
    # Extract data
    total_papers = data['total_papers']
    total_citations = data['total_citations']
    wos_papers = data['wos_papers']
    scopus_papers = data['scopus_papers']
    both_papers = data['both_papers']
    yearly_papers = data['yearly_papers']
    yearly_citations = data['yearly_citations']
    top_authors = data['top_authors']
    top_journals = data['top_journals']
    top_publishers = data['top_publishers']
    citation_distribution = data['citation_distribution']
    top_cited = data['top_cited']
    top_citations_per_year = data['top_citations_per_year']
    collaboration_types = data['collaboration_types']
    yearly_collaboration = data['yearly_collaboration']
    enriched_papers = data['enriched_papers']
    
    # Calculate additional metrics
    avg_citations = total_citations / total_papers if total_papers > 0 else 0
    neither_papers = total_papers - (wos_papers + scopus_papers - both_papers)
    
    # Get years from data
    years = sorted(yearly_papers.keys())
    min_year = min(years) if years else None
    max_year = max(years) if years else None
    
    # Calculate active years
    active_years = len(years)
    
    # Count unique authors, affiliations, countries
    all_authors = set()
    all_affiliations = set()
    all_countries = set()
    
    for p in enriched_papers:
        all_authors.update(p.get('authors', []))
        all_affiliations.update(p.get('affiliations', []))
        all_countries.update(p.get('author_countries', []))
    
    unique_authors = len(all_authors)
    unique_affiliations = len(all_affiliations)
    unique_countries = len(all_countries)
    
    # Calculate citations per year for top papers
    current_year = datetime.now().year
    for p in top_cited:
        if 'citations_per_year' not in p:
            p['citations_per_year'] = calculate_citations_per_year(
                p.get('cited_by_count', 0), 
                p.get('publication_year', current_year), 
                current_year
            )
    
    # Build HTML
    primary = colors['primary']
    secondary = colors['secondary']
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Institution Analysis Report - {html.escape(institution_name)}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Times New Roman', 'DejaVu Serif', serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            color: #333;
        }}
        .report-wrapper {{
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            border-radius: 10px;
            overflow: hidden;
        }}
        
        /* ===== SIDEBAR NAVIGATION ===== */
        .sidebar {{
            position: fixed;
            left: 0;
            top: 0;
            width: 280px;
            height: 100vh;
            background: linear-gradient(135deg, {primary} 0%, {secondary} 100%);
            color: white;
            padding: 25px 18px;
            overflow-y: auto;
            z-index: 1000;
            box-shadow: 2px 0 20px rgba(0,0,0,0.15);
        }}
        .sidebar::-webkit-scrollbar {{ width: 4px; }}
        .sidebar::-webkit-scrollbar-thumb {{ background: rgba(255,255,255,0.3); border-radius: 4px; }}
        
        .sidebar h3 {{
            margin-bottom: 20px;
            font-size: 18px;
            font-weight: 700;
            color: white;
            border-bottom: 2px solid rgba(255,255,255,0.3);
            padding-bottom: 15px;
            letter-spacing: 0.5px;
            word-wrap: break-word;
        }}
        .sidebar .nav-section {{
            margin-top: 5px;
        }}
        .sidebar a {{
            color: white;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 14px;
            margin: 2px 0;
            border-radius: 8px;
            transition: all 0.3s;
            font-size: 13px;
        }}
        .sidebar a:hover {{
            background: rgba(255,255,255,0.2);
            transform: translateX(5px);
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .sidebar a .nav-icon {{
            font-size: 16px;
            width: 24px;
            text-align: center;
        }}
        
        /* ===== MAIN CONTENT ===== */
        .main-content {{
            margin-left: 280px;
            padding: 30px 40px;
        }}
        
        /* ===== HEADER ===== */
        .header {{
            background: linear-gradient(135deg, {primary} 0%, {secondary} 100%);
            color: white;
            padding: 30px 40px;
            border-radius: 15px;
            margin-bottom: 30px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .header-left {{
            display: flex;
            align-items: center;
            gap: 20px;
            flex: 1;
        }}
        .header h1 {{
            color: white;
            border-bottom: none;
            margin: 0;
            font-size: 28px;
            font-weight: 700;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
            word-wrap: break-word;
        }}
        .header .subtitle {{
            opacity: 0.9;
            margin-top: 5px;
            font-size: 14px;
            text-shadow: 0 1px 2px rgba(0,0,0,0.15);
        }}
        
        /* ===== SECTIONS ===== */
        .section {{
            background: white;
            border-radius: 15px;
            padding: 25px 30px;
            margin-bottom: 25px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            border: 1px solid #f0f0f0;
            transition: all 0.3s;
        }}
        .section:hover {{
            box-shadow: 0 4px 20px rgba(0,0,0,0.12);
        }}
        
        .section-header {{
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: space-between;
            user-select: none;
            padding: 5px 0;
        }}
        .section-header:hover .section-title {{
            color: {primary};
        }}
        .section-title {{
            font-size: 22px;
            font-weight: 700;
            margin-bottom: 0;
            padding-bottom: 0;
            border-bottom: none;
            display: flex;
            align-items: center;
            gap: 12px;
            color: #2C3E50;
            transition: color 0.3s;
        }}
        .section-title .icon {{
            font-size: 24px;
        }}
        .section-title .section-badge {{
            background: linear-gradient(135deg, {primary}, {secondary});
            color: white;
            padding: 2px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            margin-left: 8px;
        }}
        .section-divider {{
            height: 3px;
            background: linear-gradient(90deg, {primary}, {secondary}, transparent);
            margin: 15px 0 20px 0;
            border-radius: 3px;
        }}
        .toggle-indicator {{
            font-size: 18px;
            transition: transform 0.3s;
            color: {primary};
            font-weight: 300;
        }}
        .toggle-indicator.collapsed {{
            transform: rotate(-90deg);
        }}
        .section-content {{
            display: block;
            transition: all 0.4s ease;
        }}
        .section-content.collapsed {{
            display: none;
        }}
        
        /* ===== METRICS GRID ===== */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 12px;
            margin: 15px 0;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
            padding: 14px 18px;
            border-radius: 12px;
            border-left: 4px solid {primary};
            text-align: center;
            transition: all 0.3s;
            box-shadow: 0 2px 6px rgba(0,0,0,0.04);
            position: relative;
            overflow: hidden;
        }}
        .metric-card::after {{
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, transparent 50%, {primary}08 100%);
            border-radius: 0 12px 0 60px;
        }}
        .metric-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.1);
            border-left-color: {secondary};
        }}
        .metric-card .metric-icon {{
            font-size: 20px;
            display: block;
            margin-bottom: 4px;
        }}
        .metric-value {{
            font-size: 26px;
            font-weight: 700;
            color: #2C3E50;
            font-family: 'Times New Roman', serif;
            background: linear-gradient(135deg, {primary}, {secondary});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .metric-label {{
            font-size: 11px;
            color: #7F8C8D;
            margin-top: 4px;
            font-family: 'Times New Roman', serif;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }}
        
        /* ===== PROGRESS BARS ===== */
        .progress-bar-container {{
            width: 100%;
            background-color: #f0f0f0;
            border-radius: 8px;
            overflow: hidden;
            margin: 4px 0;
            height: 22px;
            position: relative;
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
        }}
        .progress-bar-fill {{
            height: 100%;
            border-radius: 8px;
            transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 11px;
            font-weight: 700;
            text-shadow: 0 1px 2px rgba(0,0,0,0.3);
            position: relative;
            overflow: hidden;
            min-width: 30px;
        }}
        .progress-bar-fill.animate {{
            animation: shimmer 2s infinite linear;
            background-size: 200% 100%;
        }}
        @keyframes shimmer {{
            0% {{ background-position: -200% 0; }}
            100% {{ background-position: 200% 0; }}
        }}
        
        .progress-bar-label {{
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            margin: 2px 0 1px 0;
            color: #555;
            font-weight: 500;
        }}
        .progress-bar-label .label-value {{
            font-weight: 700;
            color: #2C3E50;
        }}
        
        /* ===== TABLES ===== */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 12px 0;
            font-family: 'Times New Roman', serif;
            font-size: 13px;
        }}
        th {{
            background: linear-gradient(135deg, {primary} 0%, {secondary} 100%);
            color: white;
            padding: 10px 14px;
            text-align: left;
            font-weight: 600;
            position: sticky;
            top: 0;
            z-index: 10;
            white-space: nowrap;
        }}
        th.sortable {{
            cursor: pointer;
            user-select: none;
            position: relative;
        }}
        th.sortable:hover {{
            opacity: 0.9;
        }}
        th.sortable::after {{
            content: ' ↕';
            opacity: 0.5;
            font-size: 10px;
        }}
        td {{
            padding: 8px 14px;
            border-bottom: 1px solid #e9ecef;
            vertical-align: middle;
            transition: background 0.2s;
        }}
        tr:hover td {{
            background-color: #f8f9fa;
        }}
        .scrollable-table {{
            max-height: 500px;
            overflow-y: auto;
            border-radius: 8px;
            border: 1px solid #e9ecef;
        }}
        .scrollable-table thead {{
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        
        .citation-count {{
            background: linear-gradient(135deg, {primary}15, {secondary}15);
            padding: 2px 10px;
            border-radius: 12px;
            font-weight: 700;
            color: {primary};
        }}
        
        .doi-link {{
            color: #2980B9;
            text-decoration: none;
            font-size: 11px;
            word-break: break-all;
            transition: color 0.2s;
        }}
        .doi-link:hover {{
            color: {primary};
            text-decoration: underline;
        }}
        
        .badge {{
            display: inline-block;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            margin: 1px 2px;
        }}
        .badge-success {{ background: #2ECC71; color: white; }}
        .badge-warning {{ background: #F39C12; color: white; }}
        .badge-danger {{ background: #E74C3C; color: white; }}
        .badge-primary {{ background: {primary}; color: white; }}
        .badge-info {{ background: #3498DB; color: white; }}
        
        .color-scale-value {{
            display: inline-block;
            padding: 2px 10px;
            border-radius: 8px;
            font-weight: 600;
            text-align: center;
            min-width: 30px;
            transition: all 0.2s;
        }}
        .color-scale-value:hover {{
            transform: scale(1.05);
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .word-wrap {{
            word-wrap: break-word;
            max-width: 300px;
        }}
        
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e9ecef;
            text-align: center;
            color: #7F8C8D;
            font-size: 12px;
        }}
        .footer a {{
            color: {primary};
            text-decoration: none;
        }}
        .footer a:hover {{
            text-decoration: underline;
        }}
        
        .filter-section {{
            background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
            padding: 15px 20px;
            border-radius: 10px;
            margin-bottom: 15px;
            border: 1px solid #e9ecef;
        }}
        .filter-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            align-items: center;
        }}
        .filter-row .filter-group {{
            display: flex;
            align-items: center;
            gap: 6px;
            background: white;
            padding: 4px 10px 4px 12px;
            border-radius: 8px;
            border: 1px solid #e9ecef;
        }}
        .filter-row label {{
            font-size: 11px;
            font-weight: 600;
            color: #555;
            white-space: nowrap;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }}
        .filter-row select, .filter-row input {{
            padding: 4px 8px;
            border: none;
            border-radius: 4px;
            font-size: 12px;
            font-family: 'Times New Roman', serif;
            background: transparent;
            outline: none;
        }}
        .filter-row select:focus, .filter-row input:focus {{
            box-shadow: 0 0 0 2px {primary}40;
        }}
        .filter-row input[type="text"] {{
            width: 130px;
        }}
        .filter-row input[type="number"] {{
            width: 70px;
        }}
        .filter-stats {{
            margin-top: 10px;
            font-size: 13px;
            color: #555;
            padding: 6px 12px;
            background: white;
            border-radius: 8px;
            border: 1px solid #e9ecef;
            display: inline-block;
        }}
        .filter-stats strong {{
            color: #2C3E50;
        }}
        
        .geo-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 15px 0;
        }}
        .geo-card {{
            background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
            padding: 16px 20px;
            border-radius: 10px;
            border: 1px solid #e9ecef;
            transition: all 0.3s;
        }}
        .geo-card:hover {{
            box-shadow: 0 4px 16px rgba(0,0,0,0.06);
        }}
        .geo-card h4 {{
            color: {primary};
            margin-bottom: 8px;
            font-size: 14px;
        }}
        .geo-card .geo-value {{
            font-size: 18px;
            font-weight: 700;
            color: #2C3E50;
        }}
        .geo-card .geo-label {{
            font-size: 12px;
            color: #7F8C8D;
        }}
        
        .badge-wos {{ background: #2ECC71; color: white; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 600; }}
        .badge-scopus {{ background: #3498DB; color: white; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 600; }}
        .badge-both {{ background: #9B59B6; color: white; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 600; }}
        .badge-none {{ background: #95A5A6; color: white; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 600; }}
        
        @media print {{
            .sidebar {{ display: none; }}
            .main-content {{ margin-left: 0; }}
            .section {{ box-shadow: none; border: 1px solid #ddd; }}
            .metric-card {{ box-shadow: none; }}
        }}
        @media (max-width: 768px) {{
            .sidebar {{ display: none; }}
            .main-content {{ margin-left: 0; padding: 15px; }}
            .header {{ flex-direction: column; text-align: center; padding: 20px; }}
            .header-left {{ flex-direction: column; }}
            .geo-grid {{ grid-template-columns: 1fr; }}
            .filter-row {{ flex-direction: column; align-items: stretch; }}
            .filter-row .filter-group {{ flex-wrap: wrap; }}
            .metrics-grid {{ grid-template-columns: repeat(2, 1fr); }}
        }}
        
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .section {{
            animation: fadeInUp 0.6s ease forwards;
        }}
        .section:nth-child(2) {{ animation-delay: 0.1s; }}
        .section:nth-child(3) {{ animation-delay: 0.2s; }}
        .section:nth-child(4) {{ animation-delay: 0.3s; }}
        .section:nth-child(5) {{ animation-delay: 0.4s; }}
    </style>
</head>
<body>
    <div class="sidebar">
        <h3>{html.escape(institution_name[:40])}{'...' if len(institution_name) > 40 else ''}</h3>
        <div class="nav-section">
            <a href="#overview"><span class="nav-icon">📋</span> Overview</a>
            <a href="#publications"><span class="nav-icon">📄</span> Publications</a>
            <a href="#authors"><span class="nav-icon">👥</span> Authors</a>
            <a href="#journals"><span class="nav-icon">📚</span> Journals</a>
            <a href="#publishers"><span class="nav-icon">🏢</span> Publishers</a>
            <a href="#citations"><span class="nav-icon">📈</span> Citations</a>
            <a href="#collaborations"><span class="nav-icon">🌍</span> Collaborations</a>
            <a href="#indexing"><span class="nav-icon">🔬</span> Indexing</a>
            <a href="#all_publications"><span class="nav-icon">📚</span> All Publications</a>
        </div>
        <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.2); font-size: 11px; opacity: 0.8; line-height: 1.6;">
            <div>ROR: {html.escape(institution_ror)}</div>
            <div>Country: {html.escape(institution_country)}</div>
            <div>Period: {min_year} - {max_year}</div>
            <div style="margin-top: 4px; font-size: 10px; opacity: 0.6;">Generated: {datetime.now().strftime('%d.%m.%Y %H:%M')}</div>
        </div>
    </div>
    
    <div class="main-content">
        <!-- HEADER -->
        <div class="header">
            <div class="header-left">
                <div>
                    <h1>{html.escape(institution_name)}</h1>
                    <div class="subtitle">
                        ROR: {html.escape(institution_ror)} | Country: {html.escape(institution_country)} | Analysis Period: {min_year} - {max_year}
                    </div>
                    <div class="subtitle">
                        Total Publications: {total_papers:,} | Total Citations: {total_citations:,} | Average Citations: {avg_citations:.2f}
                    </div>
                </div>
            </div>
        </div>
        
        <!-- ============================================================ -->
        <!-- SECTION 1: OVERVIEW -->
        <!-- ============================================================ -->
        <div id="overview" class="section">
            <div class="section-header" onclick="toggleSection('overview_content')">
                <div class="section-title">
                    <span class="icon">📋</span> Overview
                    <span class="section-badge">{total_papers:,} Publications</span>
                </div>
                <span class="toggle-indicator" id="overview_indicator">▼</span>
            </div>
            <div class="section-divider"></div>
            <div id="overview_content" class="section-content">
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">{total_papers:,}</div>
                        <div class="metric-label">Total Publications</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{total_citations:,}</div>
                        <div class="metric-label">Total Citations</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{avg_citations:.2f}</div>
                        <div class="metric-label">Average Citations</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{active_years}</div>
                        <div class="metric-label">Active Years</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{unique_authors:,}</div>
                        <div class="metric-label">Unique Authors</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{unique_affiliations:,}</div>
                        <div class="metric-label">Unique Affiliations</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{unique_countries}</div>
                        <div class="metric-label">Unique Countries</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{wos_papers:,}</div>
                        <div class="metric-label">WoS Indexed</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{scopus_papers:,}</div>
                        <div class="metric-label">Scopus Indexed</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{both_papers:,}</div>
                        <div class="metric-label">Both Databases</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{neither_papers:,}</div>
                        <div class="metric-label">Not Indexed</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{validation.get('validated', 0):,}</div>
                        <div class="metric-label">Validated DOIs</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- ============================================================ -->
        <!-- SECTION 2: PUBLICATIONS -->
        <!-- ============================================================ -->
        <div id="publications" class="section">
            <div class="section-header" onclick="toggleSection('publications_content')">
                <div class="section-title">
                    <span class="icon">📄</span> Publications by Year
                    <span class="section-badge">{len(yearly_papers)} Years</span>
                </div>
                <span class="toggle-indicator" id="publications_indicator">▼</span>
            </div>
            <div class="section-divider"></div>
            <div id="publications_content" class="section-content">
                <div class="scrollable-table">
                    <table>
                        <thead>
                            <tr>
                                <th class="sortable" onclick="sortTable(this)">Year</th>
                                <th class="sortable" onclick="sortTable(this)">Publications</th>
                                <th class="sortable" onclick="sortTable(this)">Citations</th>
                                <th class="sortable" onclick="sortTable(this)">WoS Indexed</th>
                                <th class="sortable" onclick="sortTable(this)">Scopus Indexed</th>
                                <th class="sortable" onclick="sortTable(this)">Both</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f'''
                                <tr>
                                    <td><strong>{year}</strong></td>
                                    <td>{yearly_papers.get(year, 0)}</td>
                                    <td>{yearly_citations.get(year, 0):,}</td>
                                    <td>{data['yearly_papers_wos'].get(year, 0)}</td>
                                    <td>{data['yearly_papers_scopus'].get(year, 0)}</td>
                                    <td>{data['yearly_papers_both'].get(year, 0)}</td>
                                </tr>
                                '''
                                for year in sorted(yearly_papers.keys())
                            ])}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- ============================================================ -->
        <!-- SECTION 3: AUTHORS -->
        <!-- ============================================================ -->
        <div id="authors" class="section">
            <div class="section-header" onclick="toggleSection('authors_content')">
                <div class="section-title">
                    <span class="icon">👥</span> Authors
                    <span class="section-badge">{len(top_authors)} Authors</span>
                </div>
                <span class="toggle-indicator" id="authors_indicator">▼</span>
            </div>
            <div class="section-divider"></div>
            <div id="authors_content" class="section-content">
                <div class="scrollable-table">
                    <table>
                        <thead>
                            <tr>
                                <th class="sortable" onclick="sortTable(this)">Rank</th>
                                <th class="sortable" onclick="sortTable(this)">Author</th>
                                <th class="sortable" onclick="sortTable(this)">Publications</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f'''
                                <tr>
                                    <td>{i+1}</td>
                                    <td>{html.escape(author[0])}</td>
                                    <td>{author[1]}</td>
                                </tr>
                                '''
                                for i, author in enumerate(top_authors)
                            ])}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- ============================================================ -->
        <!-- SECTION 4: JOURNALS -->
        <!-- ============================================================ -->
        <div id="journals" class="section">
            <div class="section-header" onclick="toggleSection('journals_content')">
                <div class="section-title">
                    <span class="icon">📚</span> Journals
                    <span class="section-badge">{len(top_journals)} Journals</span>
                </div>
                <span class="toggle-indicator" id="journals_indicator">▼</span>
            </div>
            <div class="section-divider"></div>
            <div id="journals_content" class="section-content">
                <div class="scrollable-table">
                    <table>
                        <thead>
                            <tr>
                                <th class="sortable" onclick="sortTable(this)">Rank</th>
                                <th class="sortable" onclick="sortTable(this)">Journal</th>
                                <th class="sortable" onclick="sortTable(this)">Publications</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f'''
                                <tr>
                                    <td>{i+1}</td>
                                    <td>{html.escape(journal[0])}</td>
                                    <td>{journal[1]}</td>
                                </tr>
                                '''
                                for i, journal in enumerate(top_journals)
                            ])}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- ============================================================ -->
        <!-- SECTION 5: PUBLISHERS -->
        <!-- ============================================================ -->
        <div id="publishers" class="section">
            <div class="section-header" onclick="toggleSection('publishers_content')">
                <div class="section-title">
                    <span class="icon">🏢</span> Publishers
                    <span class="section-badge">{len(top_publishers)} Publishers</span>
                </div>
                <span class="toggle-indicator" id="publishers_indicator">▼</span>
            </div>
            <div class="section-divider"></div>
            <div id="publishers_content" class="section-content">
                <div class="scrollable-table">
                    <table>
                        <thead>
                            <tr>
                                <th class="sortable" onclick="sortTable(this)">Rank</th>
                                <th class="sortable" onclick="sortTable(this)">Publisher</th>
                                <th class="sortable" onclick="sortTable(this)">Publications</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f'''
                                <tr>
                                    <td>{i+1}</td>
                                    <td>{html.escape(publisher[0])}</td>
                                    <td>{publisher[1]}</td>
                                </tr>
                                '''
                                for i, publisher in enumerate(top_publishers)
                            ])}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- ============================================================ -->
        <!-- SECTION 6: CITATIONS -->
        <!-- ============================================================ -->
        <div id="citations" class="section">
            <div class="section-header" onclick="toggleSection('citations_content')">
                <div class="section-title">
                    <span class="icon">📈</span> Citation Analysis
                    <span class="section-badge">{total_citations:,} Citations</span>
                </div>
                <span class="toggle-indicator" id="citations_indicator">▼</span>
            </div>
            <div class="section-divider"></div>
            <div id="citations_content" class="section-content">
                <h3 style="color: {primary}; font-size: 16px;">Citation Distribution</h3>
                <div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));">
                    {''.join([
                        f'''
                        <div class="metric-card">
                            <div class="metric-value">{count}</div>
                            <div class="metric-label">{range_label}</div>
                        </div>
                        '''
                        for range_label, count in citation_distribution.items()
                    ])}
                </div>
                
                <h3 style="color: {primary}; font-size: 16px; margin-top: 20px;">Top 20 Most Cited Papers</h3>
                <div class="scrollable-table">
                    <table>
                        <thead>
                            <tr>
                                <th class="sortable" onclick="sortTable(this)">Rank</th>
                                <th class="sortable" onclick="sortTable(this)">Title</th>
                                <th class="sortable" onclick="sortTable(this)">Year</th>
                                <th class="sortable" onclick="sortTable(this)">Citations</th>
                                <th class="sortable" onclick="sortTable(this)">Citations/Year</th>
                                <th>Authors</th>
                                <th>DOI</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f'''
                                <tr>
                                    <td>{i+1}</td>
                                    <td class="word-wrap">{html.escape(paper.get('title', 'No title')[:120])}{'...' if len(paper.get('title', '')) > 120 else ''}</td>
                                    <td>{paper.get('publication_year', 'N/A')}</td>
                                    <td>{paper.get('cited_by_count', 0):,}</td>
                                    <td>{paper.get('citations_per_year', 0):.2f}</td>
                                    <td>{', '.join([html.escape(a) for a in paper.get('authors', [])[:3]])}{' +' + str(len(paper.get('authors', []))-3) if len(paper.get('authors', [])) > 3 else ''}</td>
                                    <td><a href="https://doi.org/{html.escape(paper.get('doi', ''))}" target="_blank" class="doi-link">{html.escape(paper.get('doi', 'N/A')[:30])}...</a></td>
                                </tr>
                                '''
                                for i, paper in enumerate(top_cited)
                            ])}
                        </tbody>
                    </table>
                </div>
                
                <h3 style="color: {primary}; font-size: 16px; margin-top: 20px;">Top 20 Papers by Annual Citation Rate</h3>
                <div class="scrollable-table">
                    <table>
                        <thead>
                            <tr>
                                <th class="sortable" onclick="sortTable(this)">Rank</th>
                                <th class="sortable" onclick="sortTable(this)">Title</th>
                                <th class="sortable" onclick="sortTable(this)">Year</th>
                                <th class="sortable" onclick="sortTable(this)">Citations</th>
                                <th class="sortable" onclick="sortTable(this)">Citations/Year</th>
                                <th>Authors</th>
                                <th>DOI</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f'''
                                <tr>
                                    <td>{i+1}</td>
                                    <td class="word-wrap">{html.escape(paper.get('title', 'No title')[:120])}{'...' if len(paper.get('title', '')) > 120 else ''}</td>
                                    <td>{paper.get('publication_year', 'N/A')}</td>
                                    <td>{paper.get('cited_by_count', 0):,}</td>
                                    <td>{paper.get('citations_per_year', 0):.2f}</td>
                                    <td>{', '.join([html.escape(a) for a in paper.get('authors', [])[:3]])}{' +' + str(len(paper.get('authors', []))-3) if len(paper.get('authors', [])) > 3 else ''}</td>
                                    <td><a href="https://doi.org/{html.escape(paper.get('doi', ''))}" target="_blank" class="doi-link">{html.escape(paper.get('doi', 'N/A')[:30])}...</a></td>
                                </tr>
                                '''
                                for i, paper in enumerate(top_citations_per_year)
                            ])}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- ============================================================ -->
        <!-- SECTION 7: COLLABORATIONS -->
        <!-- ============================================================ -->
        <div id="collaborations" class="section">
            <div class="section-header" onclick="toggleSection('collaborations_content')">
                <div class="section-title">
                    <span class="icon">🌍</span> Collaborations
                    <span class="section-badge">{sum(collaboration_types.values())} Papers</span>
                </div>
                <span class="toggle-indicator" id="collaborations_indicator">▼</span>
            </div>
            <div class="section-divider"></div>
            <div id="collaborations_content" class="section-content">
                <div class="geo-grid">
                    <div class="geo-card">
                        <h4>Collaboration Types</h4>
                        {''.join([
                            f'''
                            <div style="margin: 4px 0;">
                                <div class="progress-bar-label">
                                    <span>{html.escape(collab_type)}</span>
                                    <span class="label-value">{count} ({count/sum(collaboration_types.values())*100:.1f}%)</span>
                                </div>
                                <div class="progress-bar-container">
                                    <div class="progress-bar-fill animate" style="width: {count/sum(collaboration_types.values())*100:.1f}%; background: linear-gradient(90deg, {primary}, {secondary});">
                                        {count/sum(collaboration_types.values())*100:.1f}%
                                    </div>
                                </div>
                            </div>
                            '''
                            for collab_type, count in collaboration_types.items()
                        ])}
                    </div>
                    <div class="geo-card">
                        <h4>Collaboration by Year</h4>
                        {''.join([
                            f'''
                            <div style="margin: 2px 0; font-size: 12px;">
                                <strong>{year}:</strong> 
                                Intra: {yearly_collab.get(year, {}).get('Intra-institutional', 0)} | 
                                Inter: {yearly_collab.get(year, {}).get('Inter-institutional (domestic)', 0)} | 
                                Intl: {yearly_collab.get(year, {}).get('International', 0)}
                            </div>
                            '''
                            for year in sorted(yearly_collab.keys())
                        ])}
                    </div>
                </div>
            </div>
        </div>
        
        <!-- ============================================================ -->
        <!-- SECTION 8: INDEXING -->
        <!-- ============================================================ -->
        <div id="indexing" class="section">
            <div class="section-header" onclick="toggleSection('indexing_content')">
                <div class="section-title">
                    <span class="icon">🔬</span> WoS / Scopus Indexing
                    <span class="section-badge">{wos_papers + scopus_papers - both_papers} Indexed</span>
                </div>
                <span class="toggle-indicator" id="indexing_indicator">▼</span>
            </div>
            <div class="section-divider"></div>
            <div id="indexing_content" class="section-content">
                <div class="metrics-grid" style="grid-template-columns: repeat(4, 1fr);">
                    <div class="metric-card">
                        <div class="metric-value">{wos_papers:,}</div>
                        <div class="metric-label">WoS Indexed</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{scopus_papers:,}</div>
                        <div class="metric-label">Scopus Indexed</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{both_papers:,}</div>
                        <div class="metric-label">Both Databases</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{neither_papers:,}</div>
                        <div class="metric-label">Not Indexed</div>
                    </div>
                </div>
                
                <h3 style="color: {primary}; font-size: 16px; margin-top: 20px;">Indexing Status per Paper</h3>
                <div class="scrollable-table">
                    <table>
                        <thead>
                            <tr>
                                <th class="sortable" onclick="sortTable(this)">Title</th>
                                <th class="sortable" onclick="sortTable(this)">Year</th>
                                <th class="sortable" onclick="sortTable(this)">WoS</th>
                                <th class="sortable" onclick="sortTable(this)">WoS IF</th>
                                <th class="sortable" onclick="sortTable(this)">WoS Quartile</th>
                                <th class="sortable" onclick="sortTable(this)">Scopus</th>
                                <th class="sortable" onclick="sortTable(this)">Scopus CiteScore</th>
                                <th class="sortable" onclick="sortTable(this)">Scopus Quartile</th>
                                <th>DOI</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f'''
                                <tr>
                                    <td class="word-wrap">{html.escape(paper.get('title', 'No title')[:100])}{'...' if len(paper.get('title', '')) > 100 else ''}</td>
                                    <td>{paper.get('publication_year', 'N/A')}</td>
                                    <td>{'✅' if paper.get('wos_indexed') else '❌'}</td>
                                    <td>{paper.get('wos_if', '-')}</td>
                                    <td>{html.escape(paper.get('wos_quartile', '-'))}</td>
                                    <td>{'✅' if paper.get('scopus_indexed') else '❌'}</td>
                                    <td>{paper.get('scopus_citescore', '-')}</td>
                                    <td>{html.escape(paper.get('scopus_quartile', '-'))}</td>
                                    <td><a href="https://doi.org/{html.escape(paper.get('doi', ''))}" target="_blank" class="doi-link">{html.escape(paper.get('doi', 'N/A')[:20])}...</a></td>
                                </tr>
                                '''
                                for paper in enriched_papers
                            ])}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- ============================================================ -->
        <!-- SECTION 9: ALL PUBLICATIONS -->
        <!-- ============================================================ -->
        <div id="all_publications" class="section">
            <div class="section-header" onclick="toggleSection('all_content')">
                <div class="section-title">
                    <span class="icon">📚</span> All Publications
                    <span class="section-badge">{len(enriched_papers)} Articles</span>
                </div>
                <span class="toggle-indicator" id="all_indicator">▼</span>
            </div>
            <div class="section-divider"></div>
            <div id="all_content" class="section-content">
                <div class="filter-section">
                    <div class="filter-row">
                        <div class="filter-group">
                            <label>🔍</label>
                            <input type="text" id="titleFilter" placeholder="Filter by title..." onkeyup="filterPublications()">
                        </div>
                        <div class="filter-group">
                            <label>📅</label>
                            <select id="yearFilter" onchange="filterPublications()">
                                <option value="">All Years</option>
                                {''.join([
                                    f'<option value="{year}">{year}</option>'
                                    for year in sorted(set([p.get('publication_year') for p in enriched_papers if p.get('publication_year')]), reverse=True)
                                ])}
                            </select>
                        </div>
                        <div class="filter-group">
                            <label>👤</label>
                            <input type="text" id="authorFilter" placeholder="Filter by author..." onkeyup="filterPublications()">
                        </div>
                        <div class="filter-group">
                            <label>📊</label>
                            <input type="number" id="citationFilter" placeholder="Min citations..." min="0" onchange="filterPublications()">
                        </div>
                    </div>
                    <div class="filter-stats">
                        <span id="visibleCount">Showing {len(enriched_papers)} of {len(enriched_papers)} publications</span>
                    </div>
                </div>
                
                <div class="scrollable-table" style="max-height: 600px;">
                    <table id="publicationsTable">
                        <thead>
                            <tr>
                                <th class="sortable" onclick="sortTable(this)">#</th>
                                <th class="sortable" onclick="sortTable(this)">Title</th>
                                <th class="sortable" onclick="sortTable(this)">Year</th>
                                <th class="sortable" onclick="sortTable(this)">Authors</th>
                                <th class="sortable" onclick="sortTable(this)">Journal</th>
                                <th class="sortable" onclick="sortTable(this)">Citations</th>
                                <th class="sortable" onclick="sortTable(this)">WoS</th>
                                <th class="sortable" onclick="sortTable(this)">Scopus</th>
                                <th>DOI</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f'''
                                <tr 
                                    data-year="{p.get('publication_year', '')}" 
                                    data-authors="{','.join([html.escape(a) for a in p.get('authors', [])])}" 
                                    data-citations="{p.get('cited_by_count', 0)}" 
                                    data-title="{html.escape((p.get('title') or '').lower())}"
                                    data-doi="{html.escape((p.get('doi') or '').lower())}"
                                >
                                    <td>{i+1}</td>
                                    <td class="word-wrap">{html.escape((p.get('title') or 'No title')[:120])}{'...' if len(p.get('title') or '') > 120 else ''}</td>
                                    <td>{p.get('publication_year', 'N/A')}</td>
                                    <td>{', '.join([html.escape(a) for a in p.get('authors', [])[:3]])}{' +' + str(len(p.get('authors', []))-3) if len(p.get('authors', [])) > 3 else ''}</td>
                                    <td>{html.escape(p.get('journal', 'Unknown')[:40])}{'...' if len(p.get('journal', '')) > 40 else ''}</td>
                                    <td>{p.get('cited_by_count', 0)}</td>
                                    <td>{'✅' if p.get('wos_indexed') else ''}</td>
                                    <td>{'✅' if p.get('scopus_indexed') else ''}</td>
                                    <td><a href="https://doi.org/{html.escape(p.get('doi', ''))}" target="_blank" class="doi-link">{html.escape((p.get('doi') or 'N/A')[:20])}...</a></td>
                                </tr>
                                '''
                                for i, p in enumerate(enriched_papers)
                            ])}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- ============================================================ -->
        <!-- FOOTER -->
        <!-- ============================================================ -->
        <div class="footer">
            <p>Institution Analysis Report - {html.escape(institution_name)}</p>
            <p>Generated: {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
            <p>ROR: {html.escape(institution_ror)} | Analysis Period: {min_year} - {max_year}</p>
            <p>Total Publications: {total_papers:,} | Total Citations: {total_citations:,}</p>
        </div>
        
    </div>
</div>

<script>
    // ===== TOGGLE SECTIONS =====
    function toggleSection(sectionId) {{
        var content = document.getElementById(sectionId);
        var indicator = document.getElementById(sectionId.replace('_content', '_indicator'));
        if (content) {{
            if (content.style.display === 'none' || content.style.display === '') {{
                content.style.display = 'block';
                if (indicator) indicator.textContent = '▼';
                content.style.animation = 'fadeInUp 0.4s ease forwards';
            }} else {{
                content.style.display = 'none';
                if (indicator) indicator.textContent = '▶';
            }}
        }}
    }}
    
    // ===== FILTER PUBLICATIONS =====
    function filterPublications() {{
        var titleFilter = document.getElementById('titleFilter').value.toLowerCase();
        var yearFilter = document.getElementById('yearFilter').value;
        var authorFilter = document.getElementById('authorFilter').value.toLowerCase();
        var citationFilter = parseInt(document.getElementById('citationFilter').value) || 0;
        
        var rows = document.querySelectorAll('#publicationsTable tbody tr');
        var visible = 0;
        
        rows.forEach(function(row) {{
            var title = row.getAttribute('data-title') || '';
            var year = row.getAttribute('data-year') || '';
            var authors = row.getAttribute('data-authors') || '';
            var citations = parseInt(row.getAttribute('data-citations')) || 0;
            
            var show = true;
            
            if (titleFilter && !title.includes(titleFilter)) show = false;
            if (yearFilter && year !== yearFilter) show = false;
            if (authorFilter && !authors.toLowerCase().includes(authorFilter)) show = false;
            if (citationFilter > 0 && citations < citationFilter) show = false;
            
            row.style.display = show ? '' : 'none';
            if (show) visible++;
        }});
        
        document.getElementById('visibleCount').textContent = 
            'Showing ' + visible + ' of ' + rows.length + ' publications';
    }}
    
    // ===== UNIVERSAL SORT FUNCTION =====
    function sortTable(header) {{
        var table = header.closest('table');
        if (!table) return;
        var tbody = table.querySelector('tbody');
        if (!tbody) return;
        var rows = Array.from(tbody.querySelectorAll('tr'));
        var colIndex = Array.from(header.parentElement.children).indexOf(header);
        
        var key = table.id + '_col_' + colIndex;
        if (!window.sortState) window.sortState = {{}};
        if (!window.sortState[key]) window.sortState[key] = 1;
        else window.sortState[key] *= -1;
        var direction = window.sortState[key];
        
        var headers = table.querySelectorAll('thead th');
        headers.forEach(function(th, idx) {{
            th.classList.remove('asc', 'desc');
            if (idx === colIndex) {{
                th.classList.add(direction > 0 ? 'asc' : 'desc');
            }}
        }});
        
        rows.sort(function(a, b) {{
            var valA = a.cells[colIndex] ? a.cells[colIndex].textContent.trim() : '';
            var valB = b.cells[colIndex] ? b.cells[colIndex].textContent.trim() : '';
            
            var numA = parseFloat(valA.replace(/,/g, ''));
            var numB = parseFloat(valB.replace(/,/g, ''));
            if (!isNaN(numA) && !isNaN(numB)) {{
                return (numA - numB) * direction;
            }}
            
            return valA.localeCompare(valB) * direction;
        }});
        
        rows.forEach(function(row) {{
            tbody.appendChild(row);
        }});
    }}
    
    document.addEventListener('DOMContentLoaded', function() {{
        var sections = ['publications_content', 'authors_content', 'journals_content', 
                       'publishers_content', 'citations_content', 'collaborations_content', 
                       'indexing_content', 'all_content'];
        sections.forEach(function(id) {{
            var el = document.getElementById(id);
            if (el) {{
                el.style.display = 'none';
            }}
        }});
        var indicators = ['publications_indicator', 'authors_indicator', 'journals_indicator',
                         'publishers_indicator', 'citations_indicator', 'collaborations_indicator',
                         'indexing_indicator', 'all_indicator'];
        indicators.forEach(function(id) {{
            var el = document.getElementById(id);
            if (el) {{
                el.textContent = '▶';
            }}
        }});
    }});
</script>

</body>
</html>
"""
    
    return html_content

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    with st.sidebar:
        st.markdown(f"<h2 style='color: {colors['primary']};'>⚙️ Settings</h2>", unsafe_allow_html=True)
        
        st.markdown("**Plot Color Palette:**")
        palette_names = [p['name'] for p in PLOT_COLOR_PALETTES]
        selected_palette_idx = palette_names.index(st.session_state['plot_palette']['name']) if st.session_state['plot_palette']['name'] in palette_names else 0
        
        selected_palette_name = st.selectbox(
            "Select color scheme for plots",
            options=palette_names,
            index=selected_palette_idx
        )
        
        # Update selected palette
        for p in PLOT_COLOR_PALETTES:
            if p['name'] == selected_palette_name:
                st.session_state['plot_palette'] = p
                break
        
        st.markdown("---")
        
        if st.session_state['recent_institutions']:
            st.markdown("**Recent Institutions:**")
            for inst in st.session_state['recent_institutions']:
                if st.button(
                    f"🏛️ {inst['name'][:30]}...",
                    key=f"recent_{inst['id']}",
                    help=f"ROR: {inst['ror']}",
                    use_container_width=True
                ):
                    st.session_state['institution_id'] = inst['id']
                    st.session_state['institution_name'] = inst['name']
                    st.session_state['institution_ror'] = inst['ror']
                    st.session_state['institution_country'] = inst['country']
                    st.session_state['step'] = 2
                    st.rerun()
            st.markdown("---")
        
        # Database status indicators
        st.markdown(f"**📚 Database Status:**")
        
        wos_status = "✅" if st.session_state['wos_data']['normalized_map'] else "❌"
        scopus_status = "✅" if st.session_state['scopus_data']['normalized_map'] else "❌"
        
        st.markdown(f"{wos_status} WoS (IF.xlsx)")
        st.markdown(f"{scopus_status} Scopus (CS.xlsx)")
        
        if not st.session_state['wos_data']['normalized_map']:
            st.markdown("⚠️ WoS file not found or invalid")
        if not st.session_state['scopus_data']['normalized_map']:
            st.markdown("⚠️ Scopus file not found or invalid")
        
        st.markdown("---")
        
        st.markdown("**About:**")
        st.markdown("""
        University & Institute publication analysis using OpenAlex with:
        - Date validation via Crossref
        - WoS indexing check (IF.xlsx)
        - Scopus indexing check (CS.xlsx)
        - Quartile analysis
        """)
    
    st.markdown(f'<div class="main-header" style="text-align: center;">', unsafe_allow_html=True)
    st.image('logo.png', width=200)
    st.markdown('</div>', unsafe_allow_html=True)
    
    steps = ["Institution Search", "Period Selection", "Results"]
    current_step = st.session_state['step'] - 1
    if current_step >= 2:
        current_step = 2 if st.session_state['step'] == 3 else st.session_state['step'] - 1
    
    step_html = '<div class="step-container">'
    for i, step_name in enumerate(steps):
        if i < current_step:
            status = "completed"
        elif i == current_step:
            status = "active"
        else:
            status = ""
        
        step_html += f'<div class="step {status}"><div class="step-number">{i+1}</div><div>{step_name}</div></div>'
    step_html += '</div>'
    
    st.markdown(step_html, unsafe_allow_html=True)

    if st.session_state['step'] == 1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🔍 Step 1: Institution Search")
        
        st.markdown("""
        Enter institution name or ROR ID.
        
        **Examples:**
        - Name: `Institute of High-Temperature Electrochemistry`
        - ROR ID: `0521rv456`
        """)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Use value from session_state for display
            query = st.text_input(
                "Institution or ROR ID",
                value=st.session_state['search_query'],
                placeholder="Enter name or ROR ID...",
                key="inst_query_input"
            )
            # Update session_state on change
            if query != st.session_state['search_query']:
                st.session_state['search_query'] = query
                # Reset results when query changes
                st.session_state['search_performed'] = False
                st.session_state['search_results'] = None
        
        with col2:
            search_clicked = st.button("🔍 Search", type="primary", key="search_btn", use_container_width=True)
        
        # Perform search ONLY when Search button is clicked
        if search_clicked and query:
            with st.spinner("Searching for institution..."):
                if is_ror_id(query):
                    # Search by ROR
                    inst = get_institution_by_ror(query)
                    if inst:
                        # Single result found (ROR search always returns 0 or 1)
                        st.session_state['institution_id'] = inst['id']
                        st.session_state['institution_name'] = inst['display_name']
                        st.session_state['institution_ror'] = inst['ror']
                        st.session_state['institution_country'] = inst.get('country', 'N/A')
                        
                        add_to_recent_institutions({
                            'id': inst['id'],
                            'name': inst['display_name'],
                            'ror': inst['ror'],
                            'country': inst.get('country', 'N/A')
                        })
                        
                        st.session_state['step'] = 2
                        st.rerun()
                    else:
                        st.session_state['search_results'] = []
                        st.session_state['search_performed'] = True
                        st.markdown(f"""
                        <div class="error-box">
                            ❌ Institution with ROR ID {query} not found
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    # Search by name
                    results = search_institution(query)
                    
                    # Check if exactly one result found
                    if len(results) == 1:
                        inst = results[0]
                        st.session_state['institution_id'] = inst['id']
                        st.session_state['institution_name'] = inst['display_name']
                        st.session_state['institution_ror'] = inst['ror']
                        st.session_state['institution_country'] = inst.get('country', 'N/A')
                        
                        add_to_recent_institutions({
                            'id': inst['id'],
                            'name': inst['display_name'],
                            'ror': inst['ror'],
                            'country': inst.get('country', 'N/A')
                        })
                        
                        st.session_state['step'] = 2
                        st.rerun()
                    else:
                        # Multiple or zero results - show selection interface
                        st.session_state['search_results'] = results
                        st.session_state['search_performed'] = True
        
        # Display results from session_state (if they exist)
        if st.session_state['search_performed'] and st.session_state['search_results'] is not None:
            results = st.session_state['search_results']
            
            if results:
                st.markdown("**Found institutions:**")
                
                # Initialize expanded details state if not exists
                if 'expanded_details' not in st.session_state:
                    st.session_state['expanded_details'] = {}
                
                for i, inst in enumerate(results):
                    # Create a unique key for this institution
                    inst_key = f"{inst['id']}_{i}"
                    
                    # Create a container for each institution
                    inst_container = st.container()
                    
                    with inst_container:
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            st.markdown(f"**{inst['display_name']}**")
                            st.markdown(f"ROR: {inst['ror']} | Country: {inst.get('country', 'N/A')} | Works: {inst['works_count']:,}")
                        
                        with col2:
                            # Select button - sets institution and moves to step 2
                            if st.button("Select", key=f"select_{inst_key}", use_container_width=True):
                                st.session_state['institution_id'] = inst['id']
                                st.session_state['institution_name'] = inst['display_name']
                                st.session_state['institution_ror'] = inst['ror']
                                st.session_state['institution_country'] = inst.get('country', 'N/A')
                                
                                add_to_recent_institutions({
                                    'id': inst['id'],
                                    'name': inst['display_name'],
                                    'ror': inst['ror'],
                                    'country': inst.get('country', 'N/A')
                                })
                                
                                st.session_state['step'] = 2
                                st.rerun()
                        
                        with col3:
                            # Details button - toggles details without rerun
                            if st.button("Details", key=f"details_{inst_key}", use_container_width=True):
                                # Toggle details for this institution
                                if inst_key in st.session_state['expanded_details']:
                                    st.session_state['expanded_details'][inst_key] = not st.session_state['expanded_details'][inst_key]
                                else:
                                    st.session_state['expanded_details'][inst_key] = True
                        
                        # Show details if expanded (use unique key)
                        if st.session_state['expanded_details'].get(inst_key, False):
                            st.markdown(f"""
                            <div style="background-color: {colors['background']}; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;">
                                <h4>📋 Detailed Information</h4>
                                <p><strong>Full Name:</strong> {inst['display_name']}</p>
                                <p><strong>ROR ID:</strong> {inst['ror']}</p>
                                <p><strong>OpenAlex ID:</strong> {inst['id']}</p>
                                <p><strong>Country:</strong> {inst.get('country', 'N/A')}</p>
                                <p><strong>Type:</strong> {inst.get('type', 'N/A')}</p>
                                <p><strong>Total Works:</strong> {inst['works_count']:,}</p>
                                <p><em>Click 'Select' to analyze this institution.</em></p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("---")
            else:
                st.markdown(f"""
                <div class="warning-box">
                    ⚠️ No institutions found. Try:
                    - Using a more general name
                    - Checking spelling
                    - Using ROR ID
                </div>
                """, unsafe_allow_html=True)
        
        # Navigation buttons (only if institution is selected)
        if st.session_state['institution_id']:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Back", key="back_to_search", use_container_width=True):
                    st.session_state['step'] = 1
                    st.session_state['institution_id'] = None
                    st.session_state['institution_name'] = ''
                    st.session_state['institution_ror'] = ''
                    st.session_state['institution_country'] = ''
                    st.rerun()
            with col2:
                if st.button("Next →", key="next_to_period", type="primary", use_container_width=True):
                    st.session_state['step'] = 2
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state['step'] == 2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📅 Step 2: Analysis Period")
        
        st.markdown(f"""
        <div class="info-box">
            <strong>Institution:</strong> {st.session_state['institution_name']}<br>
            <strong>ROR:</strong> {st.session_state['institution_ror']}<br>
            <strong>Country:</strong> {st.session_state['institution_country']}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        **Select analysis period:**
        
        **Input formats:**
        - Single year: `2023`
        - Range: `2020-2024`
        - Multiple periods: `2020-2022,2024,2023-2025`
        
        *Note: Period limited to 30 years for performance*
        """)
        
        def on_year_input_change():
            st.session_state['year_input_text'] = st.session_state['year_input_widget']
        
        year_input = st.text_input(
            "Analysis Period",
            value=st.session_state['year_input_text'],
            placeholder="e.g., 2020-2024 or 2023,2025-2026",
            key="year_input_widget",
            on_change=on_year_input_change
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("← Back", use_container_width=True):
                st.session_state['step'] = 1
                st.rerun()
        
        with col2:
            if st.button("Start Analysis →", type="primary", use_container_width=True):
                if year_input:
                    years = parse_year_input(year_input)
                    if years:
                        is_valid, message = validate_year_range(years)
                        if not is_valid:
                            st.markdown(f"""
                            <div class="error-box">
                                ❌ {message}
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.session_state['year_input_text'] = year_input
                            
                            with st.spinner("Checking data availability..."):
                                total = get_total_papers_count(st.session_state['institution_id'], years)
                                
                                st.session_state['years_range'] = years
                                st.session_state['total_papers'] = total
                                
                                if total > 0:
                                    st.rerun()
                    else:
                        st.markdown("""
                        <div class="error-box">
                            ❌ Invalid period format
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="error-box">
                        ❌ Please enter analysis period
                    </div>
                    """, unsafe_allow_html=True)
        
        if st.session_state['years_range'] and st.session_state['total_papers'] > 0:
            expanded = expand_year_range(st.session_state['years_range'])
            
            if st.session_state['total_papers'] > WARN_PAPERS_THRESHOLD:
                st.markdown(f"""
                <div class="warning-box">
                    <strong>⚠️ Large Dataset Warning</strong><br>
                    Found {st.session_state['total_papers']:,} papers. Analysis will be limited to {MAX_PAPERS_TO_ANALYZE:,} papers for performance.
                    This may take several minutes.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="success-box">
                    <strong>✅ Data found</strong><br>
                    Total papers (with expanded filter): {st.session_state['total_papers']:,}<br>
                    OpenAlex search period: {min(expanded)}-{max(expanded)}
                </div>
                """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 1, 2])
            with col2:
                if st.button("▶️ Start Analysis", type="primary", use_container_width=True, key="start_analysis_main"):
                    with st.spinner("Starting analysis..."):
                        progress_container = st.empty()
                        status_container = st.empty()
                        
                        success = run_analysis_with_progress(
                            st.session_state['institution_id'],
                            st.session_state['years_range'],
                            st.session_state['total_papers'],
                            progress_container,
                            status_container
                        )
                        
                        if success:
                            st.session_state['step'] = 4
                            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif st.session_state['step'] == 4 and st.session_state['analysis_complete']:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📊 Step 4: Analysis Results")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("← New Search", use_container_width=True):
                palette = st.session_state['ui_palette']
                plot_palette = st.session_state['plot_palette']
                recent = st.session_state['recent_institutions']
                for key in list(st.session_state.keys()):
                    if key not in ['ui_palette', 'plot_palette', 'previous_palette', 'recent_institutions', 'wos_data', 'scopus_data']:
                        del st.session_state[key]
                st.session_state['ui_palette'] = palette
                st.session_state['plot_palette'] = plot_palette
                st.session_state['recent_institutions'] = recent
                st.session_state['step'] = 1
                st.rerun()
        
        with col2:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        
        data = st.session_state['papers_data']
        validation = st.session_state['validation_stats']
        crossref_data = st.session_state.get('crossref_data', {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="value">{data['total_papers']:,}</div>
                <div class="label">Total Papers</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="value">{data['total_citations']:,}</div>
                <div class="label">Total Citations</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            avg_citations = data['total_citations'] / data['total_papers'] if data['total_papers'] > 0 else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="value">{avg_citations:.1f}</div>
                <div class="label">Avg. Citations</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="value">{validation['validated']:,}</div>
                <div class="label">Validated DOIs</div>
            </div>
            """, unsafe_allow_html=True)
        
        # New metrics for WoS and Scopus
        st.markdown("### 📚 Database Indexing Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            wos_percent = (data['wos_papers'] / data['total_papers'] * 100) if data['total_papers'] > 0 else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="value">{data['wos_papers']:,}</div>
                <div class="label">WoS Indexed ({wos_percent:.1f}%)</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            scopus_percent = (data['scopus_papers'] / data['total_papers'] * 100) if data['total_papers'] > 0 else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="value">{data['scopus_papers']:,}</div>
                <div class="label">Scopus Indexed ({scopus_percent:.1f}%)</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            both_percent = (data['both_papers'] / data['total_papers'] * 100) if data['total_papers'] > 0 else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="value">{data['both_papers']:,}</div>
                <div class="label">Both Databases ({both_percent:.1f}%)</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            neither = data['total_papers'] - (data['wos_papers'] + data['scopus_papers'] - data['both_papers'])
            neither_percent = (neither / data['total_papers'] * 100) if data['total_papers'] > 0 else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="value">{neither:,}</div>
                <div class="label">Not Indexed ({neither_percent:.1f}%)</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown(f"""
        **📊 Date Validation Statistics (Crossref):**
        - Total papers: {validation['total']:,}
        - Papers with DOI: {validation['with_doi']:,} ({validation['with_doi']/validation['total']*100:.1f}%)
        - Successfully validated: {validation['validated']:,} ({validation['validated']/validation['with_doi']*100:.1f}% of papers with DOI)
        - Rejected (year mismatch): {validation['rejected']:,} ({validation['rejected']/validation['total']*100:.1f}%)
        - Kept for analysis: {data['total_papers']:,}
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "📈 Years", "👥 Authors", "📚 Journals", "🏢 Publishers", "📊 Citations", "🌍 Collaborations", "🔬 WoS/Scopus"
        ])
        
        with tab1:
            st.markdown("### Publications by Year")
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_yearly = plot_yearly_publications(data['yearly_papers'], st.session_state['plot_palette'], colors)
                st.plotly_chart(fig_yearly, use_container_width=True)
            
            with col2:
                fig_cit_year = plot_yearly_citations(data['yearly_citations'], st.session_state['plot_palette'], colors)
                st.plotly_chart(fig_cit_year, use_container_width=True)
            
            # Comparative plot
            fig_comp = plot_comparative_publications(
                data['yearly_papers'], 
                data['yearly_papers_wos'], 
                data['yearly_papers_scopus'],
                st.session_state['plot_palette'], 
                colors
            )
            st.plotly_chart(fig_comp, use_container_width=True)
            
            fig_scatter = plot_citations_vs_references(data['enriched_papers'], st.session_state['plot_palette'], colors)
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        with tab2:
            st.markdown("### Top 20 Authors")
            
            if data['top_authors']:
                fig_authors = plot_top_authors(data['top_authors'], st.session_state['plot_palette'], colors)
                st.plotly_chart(fig_authors, use_container_width=True)
                
                df_authors = pd.DataFrame(data['top_authors'], columns=['Author', 'Publications'])
                st.dataframe(df_authors, use_container_width=True)
            else:
                st.info("No author data available")
        
        with tab3:
            st.markdown("### Top 20 Journals")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if data['top_journals']:
                    fig_journals = plot_top_journals(data['top_journals'], st.session_state['plot_palette'], colors)
                    st.plotly_chart(fig_journals, use_container_width=True)
            
            with col2:
                if data['top_journals']:
                    df_journals = pd.DataFrame(data['top_journals'], columns=['Journal', 'Publications'])
                    st.dataframe(df_journals, use_container_width=True)
        
        with tab4:
            st.markdown("### Top 20 Publishers")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if data['top_publishers']:
                    fig_publishers = plot_top_publishers(data['top_publishers'], st.session_state['plot_palette'], colors)
                    st.plotly_chart(fig_publishers, use_container_width=True)
            
            with col2:
                if data['top_publishers']:
                    df_publishers = pd.DataFrame(data['top_publishers'], columns=['Publisher', 'Publications'])
                    st.dataframe(df_publishers, use_container_width=True)
        
        with tab5:
            st.markdown("### Citation Analysis")
            
            fig_cit_dist = plot_citation_distribution(data['citation_distribution'], st.session_state['plot_palette'], colors)
            st.plotly_chart(fig_cit_dist, use_container_width=True)
            
            st.markdown("### Top 20 Most Cited Papers")
            df_top_cited = plot_top_cited_table(data['top_cited'], "Top by Citations", colors)
            if df_top_cited is not None:
                st.dataframe(df_top_cited, use_container_width=True)
            
            st.markdown("### Top 20 Papers by Annual Citation Rate")
            df_top_cpy = plot_top_cited_table(data['top_citations_per_year'], "Top by Annual Citations", colors)
            if df_top_cpy is not None:
                st.dataframe(df_top_cpy, use_container_width=True)
        
        with tab6:
            st.markdown("### Collaboration Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_collab = plot_collaboration_types(data['collaboration_types'], st.session_state['plot_palette'], colors)
                st.plotly_chart(fig_collab, use_container_width=True)
            
            with col2:
                df_collab = pd.DataFrame(
                    list(data['collaboration_types'].items()),
                    columns=['Collaboration Type', 'Count']
                )
                st.dataframe(df_collab, use_container_width=True)
            
            fig_yearly_collab = plot_yearly_collaboration(data['yearly_collaboration'], st.session_state['plot_palette'], colors)
            st.plotly_chart(fig_yearly_collab, use_container_width=True)
            
            # Country collaboration network
            if data.get('country_collaborations'):
                fig_country_network = plot_country_collaboration_network(data['country_collaborations'], st.session_state['plot_palette'], colors)
                if fig_country_network:
                    st.plotly_chart(fig_country_network, use_container_width=True)
        
        with tab7:
            st.markdown("### WoS and Scopus Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_wos_quartile = plot_quartile_distribution(data['enriched_papers'], 'WoS', st.session_state['plot_palette'], colors)
                if fig_wos_quartile:
                    st.plotly_chart(fig_wos_quartile, use_container_width=True)
                else:
                    st.info("No WoS-indexed papers with quartile information")
            
            with col2:
                fig_scopus_quartile = plot_quartile_distribution(data['enriched_papers'], 'Scopus', st.session_state['plot_palette'], colors)
                if fig_scopus_quartile:
                    st.plotly_chart(fig_scopus_quartile, use_container_width=True)
                else:
                    st.info("No Scopus-indexed papers with quartile information")
            
            # Top WoS journals by IF
            wos_papers = [p for p in data['enriched_papers'] if p.get('wos_indexed') and p.get('wos_if')]
            if wos_papers:
                st.markdown("### Top WoS Journals by Impact Factor")
                wos_journals = defaultdict(list)
                for p in wos_papers:
                    if p.get('wos_journal'):
                        wos_journals[p['wos_journal']].append({
                            'if': p.get('wos_if', 0),
                            'title': p['title']
                        })
                
                journal_avg_if = []
                for journal, papers_list in wos_journals.items():
                    # Filter None values
                    if_values = [p['if'] for p in papers_list if p['if'] is not None]
                    if if_values:
                        avg_if = np.mean(if_values)
                    else:
                        avg_if = 0
                    
                    journal_avg_if.append({
                        'Journal': journal,
                        'Papers': len(papers_list),
                        'Average IF': avg_if
                    })
                
                if journal_avg_if:
                    df_wos = pd.DataFrame(journal_avg_if)
                    # Check column existence before sorting
                    if 'Average IF' in df_wos.columns:
                        df_wos = df_wos.sort_values('Average IF', ascending=False).head(15)
                        st.dataframe(df_wos, use_container_width=True)
                    else:
                        st.warning("Could not create Average IF column")
            
            # Top Scopus journals by CiteScore
            scopus_papers = [p for p in data['enriched_papers'] if p.get('scopus_indexed') and p.get('scopus_citescore')]
            if scopus_papers:
                st.markdown("### Top Scopus Journals by CiteScore")
                scopus_journals = defaultdict(list)
                for p in scopus_papers:
                    if p.get('scopus_journal'):
                        scopus_journals[p['scopus_journal']].append({
                            'citescore': p.get('scopus_citescore', 0),
                            'title': p['title']
                        })
                
                journal_avg_citescore = []
                for journal, papers_list in scopus_journals.items():
                    # Filter None values
                    citescore_values = [p['citescore'] for p in papers_list if p['citescore'] is not None]
                    if citescore_values:
                        avg_citescore = np.mean(citescore_values)
                    else:
                        avg_citescore = 0
                    
                    journal_avg_citescore.append({
                        'Journal': journal,
                        'Papers': len(papers_list),
                        'Average CiteScore': avg_citescore
                    })
                
                if journal_avg_citescore:
                    df_scopus = pd.DataFrame(journal_avg_citescore)
                    # Check column existence before sorting
                    if 'Average CiteScore' in df_scopus.columns:
                        df_scopus = df_scopus.sort_values('Average CiteScore', ascending=False).head(15)
                        st.dataframe(df_scopus, use_container_width=True)
                    else:
                        st.warning("Could not create Average CiteScore column")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📥 Export Data")
        
        export_df = pd.DataFrame([
            {
                'DOI': p['doi'],
                'Online Date': p.get('online_date', ''),
                'Print Date': p.get('print_date', ''),
                'Publication Year (used for filtering)': p.get('publication_year', ''),
                'Authors': '; '.join(p['authors']),
                'Title': p['title'],
                'Journal': p['journal'],
                'ISSN (Print)': p.get('issn_print', ''),
                'ISSN (Electronic)': p.get('issn_electronic', ''),
                'ISSN List': ', '.join(p.get('issn_list', [])) if p.get('issn_list') else '',
                'Publisher': p.get('publisher', 'Unknown'),
                'References': p.get('references_count', 0),
                'Citations (CR)': p.get('is_referenced_by_count', 0),
                'Citations (OA)': p.get('cited_by_count', 0),
                'Collaboration Type': p.get('collaboration_type', 'Unknown'),
                'WoS Indexed': p.get('wos_indexed', False),
                'WoS IF': p.get('wos_if', ''),
                'WoS Quartile': p.get('wos_quartile', ''),
                'Scopus Indexed': p.get('scopus_indexed', False),
                'Scopus CiteScore': p.get('scopus_citescore', ''),
                'Scopus Quartile': p.get('scopus_quartile', ''),
                'Indexed In': ', '.join(p.get('indexed_in', []))
            }
            for p in data['enriched_papers']
        ])
        
        col1, col2 = st.columns(2)
        
        with col1:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                export_df.to_excel(writer, sheet_name='All Papers', index=False)
                
                summary_data = {
                    'Metric': ['Institution', 'ROR', 'Country', 'Total Papers', 'Total Citations', 
                              'Average Citations', 'Validated DOIs', 'WoS Indexed', 'Scopus Indexed',
                              'Both Databases', 'Analysis Date'],
                    'Value': [
                        st.session_state['institution_name'],
                        st.session_state['institution_ror'],
                        st.session_state['institution_country'],
                        data['total_papers'],
                        data['total_citations'],
                        f"{data['total_citations']/data['total_papers']:.2f}" if data['total_papers'] > 0 else 0,
                        validation['validated'],
                        data['wos_papers'],
                        data['scopus_papers'],
                        data['both_papers'],
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ]
                }
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                
                pd.DataFrame([validation]).to_excel(writer, sheet_name='Validation', index=False)
                
                collab_df = pd.DataFrame(
                    list(data['collaboration_types'].items()),
                    columns=['Collaboration Type', 'Count']
                )
                collab_df.to_excel(writer, sheet_name='Collaborations', index=False)
            
            st.download_button(
                label="📈 Download Excel",
                data=output.getvalue(),
                file_name=f"uninst_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col2:
            # Generate HTML Report
            html_report = generate_institution_html_report(
                data=data,
                validation=validation,
                institution_name=st.session_state['institution_name'],
                institution_ror=st.session_state['institution_ror'],
                institution_country=st.session_state['institution_country'],
                years_range=st.session_state['years_range'],
                colors=colors
            )
            
            st.download_button(
                label="📄 Generate HTML Report",
                data=html_report.encode('utf-8'),
                file_name=f"institution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html",
                use_container_width=True,
                help="Download comprehensive HTML report with all data and visualizations"
            )
            
            # Show preview option
            if st.button("👁️ Preview HTML Report", use_container_width=True):
                st.markdown("### HTML Report Preview")
                st.components.v1.html(html_report, height=800, scrolling=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
