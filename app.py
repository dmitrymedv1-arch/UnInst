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
# UI COLOR PALETTES (DYNAMIC)
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

# Initialize or get UI palette from session
if 'ui_palette' not in st.session_state:
    st.session_state['ui_palette'] = random.choice(UI_COLOR_PALETTES)
if 'previous_palette' not in st.session_state:
    st.session_state['previous_palette'] = st.session_state['ui_palette']['name']

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
    
    /* Footer */
    .footer {{
        text-align: center;
        padding: 2rem;
        color: {colors['text']};
        opacity: 0.7;
        font-size: 0.9rem;
        border-top: 1px solid {colors['border']};
        margin-top: 3rem;
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

# Recent institutions storage
if 'recent_institutions' not in st.session_state:
    st.session_state['recent_institutions'] = []

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

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def normalize_institution_name(name: str) -> str:
    """Normalize institution name for search"""
    if not name:
        return ""
    # Remove extra spaces, convert to lowercase
    name = re.sub(r'\s+', ' ', name.strip().lower())
    # Remove common punctuation
    name = re.sub(r'[^\w\s-]', '', name)
    # Handle hyphenated variations
    name = name.replace('-', ' ')
    return name

def is_ror_id(text: str) -> bool:
    """Check if text is a valid ROR ID"""
    # ROR IDs are like: 0521rv456
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
    """Make synchronous batch request to Crossref API"""
    if not dois:
        return {}
    
    # Remove duplicates but preserve original case for return
    unique_dois = list(set(dois))
    results = {}
    
    # Process in batches
    for i in range(0, len(unique_dois), BATCH_SIZE):
        batch = unique_dois[i:i + BATCH_SIZE]
        
        # Prepare batch request
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
                
                # Parse results
                for item in data.get('items', []):
                    doi = item.get('DOI', '')
                    doi_lower = doi.lower()
                    
                    # Extract publication date with priority
                    pub_date = None
                    
                    # Priority 1: published-print
                    if 'published-print' in item:
                        date_parts = item['published-print'].get('date-parts', [[]])[0]
                        if date_parts:
                            pub_date = {
                                'year': date_parts[0],
                                'month': date_parts[1] if len(date_parts) > 1 else 1,
                                'day': date_parts[2] if len(date_parts) > 2 else 1,
                                'source': 'published-print'
                            }
                    
                    # Priority 2: published (main date)
                    elif 'published' in item:
                        date_parts = item['published'].get('date-parts', [[]])[0]
                        if date_parts:
                            pub_date = {
                                'year': date_parts[0],
                                'month': date_parts[1] if len(date_parts) > 1 else 1,
                                'day': date_parts[2] if len(date_parts) > 2 else 1,
                                'source': 'published'
                            }
                    
                    # Priority 3: published-online
                    elif 'published-online' in item:
                        date_parts = item['published-online'].get('date-parts', [[]])[0]
                        if date_parts:
                            pub_date = {
                                'year': date_parts[0],
                                'month': date_parts[1] if len(date_parts) > 1 else 1,
                                'day': date_parts[2] if len(date_parts) > 2 else 1,
                                'source': 'published-online'
                            }
                    
                    # Priority 4: issued
                    elif 'issued' in item:
                        date_parts = item['issued'].get('date-parts', [[]])[0]
                        if date_parts:
                            pub_date = {
                                'year': date_parts[0],
                                'month': date_parts[1] if len(date_parts) > 1 else 1,
                                'day': date_parts[2] if len(date_parts) > 2 else 1,
                                'source': 'issued'
                            }
                    
                    if pub_date:
                        # Store by lowercase DOI for lookup, but preserve original for display
                        results[doi_lower] = {
                            'doi': doi,  # Store original case
                            'doi_lower': doi_lower,
                            'year': pub_date['year'],
                            'month': pub_date['month'],
                            'day': pub_date['day'],
                            'source': pub_date['source'],
                            'title': item.get('title', [''])[0] if item.get('title') else '',
                            'container-title': item.get('container-title', [''])[0] if item.get('container-title') else '',
                            'publisher': item.get('publisher', ''),
                            'type': item.get('type', '')
                        }
            
            # Rate limiting
            time.sleep(0.1)  # 10 requests per second max
            
        except Exception as e:
            st.warning(f"Error validating batch {i//BATCH_SIZE + 1}: {str(e)}")
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
    
    # Split by commas
    parts = year_str.replace(' ', '').split(',')
    
    for part in parts:
        if '-' in part:
            # Range
            start, end = part.split('-')
            try:
                start_year = int(start)
                end_year = int(end)
                years.update(range(start_year, end_year + 1))
            except ValueError:
                st.error(f"Invalid year range: {part}")
                return []
        else:
            # Single year
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
            # Clean DOI (remove URL prefix if present) but preserve case
            doi = doi.replace('https://doi.org/', '').replace('http://doi.org/', '')
            dois.append(doi)
    return dois

def filter_papers_by_actual_years(papers: List[Dict], crossref_data: Dict[str, Dict], target_years: List[int]) -> Tuple[List[Dict], Dict]:
    """Filter papers by actual publication years from Crossref"""
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
        doi = paper.get('doi', '').replace('https://doi.org/', '').replace('http://doi.org/', '')
        
        if not doi:
            # No DOI - keep with OpenAlex year but mark as unvalidated
            validation_stats['no_doi'] += 1
            paper['_validation'] = {
                'source': 'openalex_only',
                'year': paper.get('publication_year'),
                'kept': paper.get('publication_year') in target_years
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
            crossref_year = crossref_data[doi_lower]['year']
            
            paper['_validation'] = {
                'source': 'crossref',
                'year': crossref_year,
                'original_year': paper.get('publication_year'),
                'kept': crossref_year in target_years,
                'crossref_doi': crossref_data[doi_lower]['doi']  # Store original case
            }
            
            # Update publication year with Crossref year
            paper['publication_year'] = crossref_year
            
            if crossref_year in target_years:
                filtered_papers.append(paper)
                validation_stats['kept'] += 1
            else:
                validation_stats['rejected'] += 1
                if crossref_year != paper.get('publication_year'):
                    validation_stats['year_mismatch'] += 1
        else:
            validation_stats['not_found'] += 1
            paper['_validation'] = {
                'source': 'openalex_only',
                'year': paper.get('publication_year'),
                'kept': paper.get('publication_year') in target_years
            }
            if paper.get('publication_year') in target_years:
                filtered_papers.append(paper)
                validation_stats['kept'] += 1
            else:
                validation_stats['rejected'] += 1
    
    return filtered_papers, validation_stats

def enrich_paper_data(paper: Dict) -> Dict:
    """Enrich paper data with additional fields"""
    enriched = {
        'id': paper.get('id', ''),
        'doi': paper.get('doi', '').replace('https://doi.org/', ''),
        'title': paper.get('title', 'No title'),
        'publication_year': paper.get('publication_year'),
        'publication_date': paper.get('publication_date', ''),
        'cited_by_count': paper.get('cited_by_count', 0),
        'referenced_works_count': paper.get('referenced_works_count', len(paper.get('referenced_works', []))),
        'type': paper.get('type', ''),
        'is_oa': paper.get('open_access', {}).get('is_oa', False),
        'validation': paper.get('_validation', {})
    }
    
    # Authors
    authorships = paper.get('authorships', [])
    authors = []
    author_affiliations = []
    author_countries = set()
    
    for authorship in authorships:
        if authorship.get('author'):
            author_name = authorship['author'].get('display_name', '')
            if author_name:
                authors.append(author_name)
                
                # Get affiliations for collaboration analysis
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
    
    # Journal and publisher - FIXED: Handle None source
    primary_location = paper.get('primary_location')
    if primary_location and isinstance(primary_location, dict):
        source = primary_location.get('source')
        if source and isinstance(source, dict):
            enriched['journal'] = source.get('display_name', 'Unknown')
            enriched['publisher'] = source.get('publisher', 'Unknown')
        else:
            enriched['journal'] = 'Unknown'
            enriched['publisher'] = 'Unknown'
    else:
        enriched['journal'] = 'Unknown'
        enriched['publisher'] = 'Unknown'
    
    # Determine collaboration type
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

def analyze_papers(papers: List[Dict]) -> Dict:
    """Perform comprehensive analysis on papers"""
    if not papers:
        # Return empty results if no papers
        return {
            'total_papers': 0,
            'total_citations': 0,
            'yearly_papers': {},
            'yearly_citations': {},
            'top_authors': [],
            'top_journals': [],
            'top_publishers': [],
            'citation_distribution': {k: 0 for k in ['0', '1-4', '5-10', '11-30', '31-50', '51-100', '100+']},
            'top_cited': [],
            'top_citations_per_year': [],
            'collaboration_types': {},
            'yearly_collaboration': {},
            'enriched_papers': []
        }
    
    enriched_papers = [enrich_paper_data(p) for p in papers if p]  # Filter out None papers
    
    # Basic stats
    total_papers = len(enriched_papers)
    total_citations = sum(p['cited_by_count'] for p in enriched_papers)
    
    # Yearly distribution
    yearly_papers = defaultdict(int)
    yearly_citations = defaultdict(int)
    for p in enriched_papers:
        year = p['publication_year']
        if year:  # Only process if year exists
            yearly_papers[year] += 1
            yearly_citations[year] += p['cited_by_count']
    
    # Authors analysis
    all_authors = []
    for p in enriched_papers:
        all_authors.extend(p.get('authors', []))
    
    author_counts = Counter(all_authors)
    top_authors = author_counts.most_common(20)
    
    # Journals analysis
    journal_counts = Counter(p.get('journal', 'Unknown') for p in enriched_papers)
    top_journals = journal_counts.most_common(20)
    
    # Publishers analysis
    publisher_counts = Counter(p.get('publisher', 'Unknown') for p in enriched_papers if p.get('publisher'))
    top_publishers = publisher_counts.most_common(20)
    
    # Citation distribution
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
    
    # Top cited papers
    top_cited = sorted(enriched_papers, key=lambda x: x.get('cited_by_count', 0), reverse=True)[:20]
    
    # Top papers by citations per year
    current_year = datetime.now().year
    for p in enriched_papers:
        if p.get('publication_year'):
            p['citations_per_year'] = calculate_citations_per_year(
                p.get('cited_by_count', 0), p['publication_year'], current_year
            )
        else:
            p['citations_per_year'] = 0
    
    top_cpy = sorted(enriched_papers, key=lambda x: x.get('citations_per_year', 0), reverse=True)[:20]
    
    # Collaboration analysis
    collab_types = Counter(p.get('collaboration_type', 'Unknown') for p in enriched_papers)
    
    # Yearly collaboration breakdown
    yearly_collab = defaultdict(lambda: defaultdict(int))
    for p in enriched_papers:
        year = p.get('publication_year')
        if year:
            yearly_collab[year][p.get('collaboration_type', 'Unknown')] += 1
    
    return {
        'total_papers': total_papers,
        'total_citations': total_citations,
        'yearly_papers': dict(yearly_papers),
        'yearly_citations': dict(yearly_citations),
        'top_authors': top_authors,
        'top_journals': top_journals,
        'top_publishers': top_publishers,
        'citation_distribution': citation_ranges,
        'top_cited': top_cited,
        'top_citations_per_year': top_cpy,
        'collaboration_types': dict(collab_types),
        'yearly_collaboration': {k: dict(v) for k, v in yearly_collab.items()},
        'enriched_papers': enriched_papers
    }

# ============================================================================
# PLOTTING FUNCTIONS (PLOTLY)
# ============================================================================

def plot_yearly_publications(yearly_data: Dict[int, int], colors: Dict):
    """Plot yearly publications"""
    years = sorted(yearly_data.keys())
    counts = [yearly_data[y] for y in years]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=years,
        y=counts,
        marker_color=colors['primary'],
        marker_line_color=colors['gradient_end'],
        marker_line_width=1,
        name='Publications'
    ))
    
    fig.update_layout(
        title='Publications by Year',
        xaxis_title='Year',
        yaxis_title='Number of Publications',
        template='plotly_white',
        hovermode='x',
        showlegend=False
    )
    
    fig.update_xaxes(tickangle=45)
    return fig

def plot_yearly_citations(yearly_citations: Dict[int, int], colors: Dict):
    """Plot yearly citations"""
    years = sorted(yearly_citations.keys())
    citations = [yearly_citations[y] for y in years]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=years,
        y=citations,
        marker_color=colors['secondary'],
        marker_line_color=colors['gradient_start'],
        marker_line_width=1,
        name='Citations'
    ))
    
    fig.update_layout(
        title='Citations by Year (Total)',
        xaxis_title='Year',
        yaxis_title='Total Citations',
        template='plotly_white',
        hovermode='x',
        showlegend=False
    )
    
    fig.update_xaxes(tickangle=45)
    return fig

def plot_top_authors(authors_data: List[Tuple[str, int]], colors: Dict):
    """Plot top authors"""
    authors = [a[0][:30] + '...' if len(a[0]) > 30 else a[0] for a in authors_data[:15]]
    counts = [a[1] for a in authors_data[:15]]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=authors[::-1],
        x=counts[::-1],
        orientation='h',
        marker_color=colors['primary'],
        marker_line_color=colors['gradient_end'],
        marker_line_width=1
    ))
    
    fig.update_layout(
        title='Top Authors by Publication Count',
        xaxis_title='Number of Publications',
        yaxis_title='Author',
        template='plotly_white',
        height=500,
        showlegend=False
    )
    
    return fig

def plot_top_journals(journals_data: List[Tuple[str, int]], colors: Dict):
    """Plot top journals"""
    journals = [j[0][:40] + '...' if len(j[0]) > 40 else j[0] for j in journals_data[:15]]
    counts = [j[1] for j in journals_data[:15]]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=journals[::-1],
        x=counts[::-1],
        orientation='h',
        marker_color=colors['secondary'],
        marker_line_color=colors['gradient_start'],
        marker_line_width=1
    ))
    
    fig.update_layout(
        title='Top Journals by Publication Count',
        xaxis_title='Number of Publications',
        yaxis_title='Journal',
        template='plotly_white',
        height=500,
        showlegend=False
    )
    
    return fig

def plot_top_publishers(publishers_data: List[Tuple[str, int]], colors: Dict):
    """Plot top publishers"""
    publishers = [p[0][:30] + '...' if len(p[0]) > 30 else p[0] for p in publishers_data[:15]]
    counts = [p[1] for p in publishers_data[:15]]
    
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=publishers,
        values=counts,
        marker_colors=[colors['primary'], colors['secondary'], colors['gradient_start'], 
                       colors['gradient_end'], colors['accent1'], colors['accent2']] * 3,
        textinfo='percent+label',
        insidetextorientation='radial'
    ))
    
    fig.update_layout(
        title='Top Publishers Distribution',
        template='plotly_white',
        height=500
    )
    
    return fig

def plot_citation_distribution(distribution: Dict[str, int], colors: Dict):
    """Plot citation distribution"""
    categories = list(distribution.keys())
    counts = list(distribution.values())
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=categories,
        y=counts,
        marker_color=colors['primary'],
        marker_line_color=colors['gradient_end'],
        marker_line_width=1
    ))
    
    fig.update_layout(
        title='Citation Distribution',
        xaxis_title='Citation Range',
        yaxis_title='Number of Papers',
        template='plotly_white',
        hovermode='x'
    )
    
    return fig

def plot_collaboration_types(collab_data: Dict[str, int], colors: Dict):
    """Plot collaboration types"""
    labels = list(collab_data.keys())
    values = list(collab_data.values())
    
    colors_map = {
        'Intra-institutional': colors['primary'],
        'Inter-institutional (domestic)': colors['secondary'],
        'International': colors['gradient_start']
    }
    
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=labels,
        values=values,
        marker_colors=[colors_map.get(l, colors['accent1']) for l in labels],
        textinfo='percent+label',
        insidetextorientation='radial'
    ))
    
    fig.update_layout(
        title='Collaboration Types',
        template='plotly_white',
        height=400
    )
    
    return fig

def plot_yearly_collaboration(yearly_collab: Dict, colors: Dict):
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
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Intra-institutional',
        x=years,
        y=intra,
        marker_color=colors['primary']
    ))
    
    fig.add_trace(go.Bar(
        name='Inter-institutional (domestic)',
        x=years,
        y=inter,
        marker_color=colors['secondary']
    ))
    
    fig.add_trace(go.Bar(
        name='International',
        x=years,
        y=international,
        marker_color=colors['gradient_start']
    ))
    
    fig.update_layout(
        title='Collaboration Types by Year',
        xaxis_title='Year',
        yaxis_title='Number of Publications',
        barmode='stack',
        template='plotly_white',
        hovermode='x'
    )
    
    fig.update_xaxes(tickangle=45)
    return fig

def plot_citations_vs_references(papers: List[Dict], colors: Dict):
    """Plot citations vs references scatter with real reference counts"""
    citations = [p['cited_by_count'] for p in papers]
    references = [p.get('referenced_works_count', 0) for p in papers]
    years = [p['publication_year'] for p in papers]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=references,
        y=citations,
        mode='markers',
        marker=dict(
            size=8,
            color=years,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title='Year'),
            line=dict(width=1, color='white')
        ),
        text=[p['title'][:50] + '...' for p in papers],
        hovertemplate='<b>%{text}</b><br>Citations: %{y}<br>References: %{x}<br>Year: %{marker.color}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Citations vs References (with Year Color Map)',
        xaxis_title='Number of References',
        yaxis_title='Number of Citations',
        template='plotly_white',
        height=500
    )
    
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
            'Journal': p['journal'][:30] + '...' if len(p['journal']) > 30 else p['journal']
        }
        for p in papers[:20]
    ])
    
    return df

def create_validation_summary(validation_stats: Dict, colors: Dict):
    """Create validation summary visualization"""
    if not validation_stats:
        return None
    
    # Create pie chart for validation results
    labels = ['Validated & Kept', 'Kept (No DOI/Not Found)', 'Rejected (Year Mismatch)']
    values = [
        validation_stats.get('validated', 0),
        validation_stats.get('no_doi', 0) + validation_stats.get('not_found', 0),
        validation_stats.get('rejected', 0)
    ]
    
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=labels,
        values=values,
        marker_colors=[colors['success'], colors['warning'], colors['danger']],
        textinfo='percent+label',
        insidetextorientation='radial'
    ))
    
    fig.update_layout(
        title='DOI Validation Summary',
        template='plotly_white',
        height=400
    )
    
    return fig

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    # Sidebar for settings
    with st.sidebar:
        st.markdown(f"<h2 style='color: {colors['primary']};'>🎨 Settings</h2>", unsafe_allow_html=True)
        
        # Theme selector
        st.markdown("**Color Theme:**")
        
        # Display color palette options in a grid
        cols = st.columns(4)
        for i, palette in enumerate(UI_COLOR_PALETTES[:8]):  # Show first 8
            with cols[i % 4]:
                if st.button(
                    "●", 
                    key=f"palette_{i}",
                    help=palette['name'],
                    use_container_width=True
                ):
                    st.session_state['ui_palette'] = palette
                    st.rerun()
                
                # Show color indicator
                st.markdown(
                    f'<div style="width:100%; height:5px; background: linear-gradient(90deg, {palette["gradient_start"]}, {palette["gradient_end"]}); border-radius:3px; margin-bottom:5px;"></div>',
                    unsafe_allow_html=True
                )
        
        st.markdown("---")
        
        # Recent institutions
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
        
        # API Status
        st.markdown(f"**API Status:**")
        st.markdown(f"✅ OpenAlex")
        st.markdown(f"✅ Crossref")
        st.markdown("---")
        
        # About
        st.markdown("**About:**")
        st.markdown("""
        University & Institute publication analysis using OpenAlex with date validation via Crossref.
        
        **Data Sources:**
        - OpenAlex: Primary search
        - Crossref: Date validation
        """)
        
        # Rate limits info
        with st.expander("ℹ️ Rate Limits & Limits"):
            st.markdown("""
            - OpenAlex: 10 requests/sec
            - Crossref: 50 requests/sec (no key)
            - Max papers analyzed: 10,000
            - Max period: 30 years
            
            Analysis may take time for large datasets.
            """)
    
    # Main content
    st.markdown(f'<h1 class="main-header">🏛️ UnInst Analytics</h1>', unsafe_allow_html=True)
    
    # Step indicator - ALWAYS SHOWN
    steps = ["Institution Search", "Period Selection", "Data Collection", "Results"]
    current_step = st.session_state['step'] - 1
    
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
    
    # ========================================================================
    # STEP 1: INSTITUTION SEARCH
    # ========================================================================
    
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
            query = st.text_input(
                "Institution or ROR ID",
                placeholder="Enter name or ROR ID...",
                key="inst_query"
            )
        
        with col2:
            search_clicked = st.button("🔍 Search", type="primary", use_container_width=True)
        
        if search_clicked and query:
            with st.spinner("Searching for institution..."):
                if is_ror_id(query):
                    # Search by ROR
                    inst = get_institution_by_ror(query)
                    if inst:
                        st.session_state['institution_id'] = inst['id']
                        st.session_state['institution_name'] = inst['display_name']
                        st.session_state['institution_ror'] = inst['ror']
                        st.session_state['institution_country'] = inst.get('country', 'N/A')
                        
                        # Add to recent
                        add_to_recent_institutions({
                            'id': inst['id'],
                            'name': inst['display_name'],
                            'ror': inst['ror'],
                            'country': inst.get('country', 'N/A')
                        })
                        
                        st.markdown(f"""
                        <div class="success-box">
                            <strong>✅ Institution Found:</strong><br>
                            {inst['display_name']}<br>
                            ROR: {inst['ror']}<br>
                            Country: {inst.get('country', 'N/A')}<br>
                            Total works in OpenAlex: {inst['works_count']:,}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Store in session for next step
                        st.session_state['search_results'] = [inst]
                    else:
                        st.markdown(f"""
                        <div class="error-box">
                            ❌ Institution with ROR ID {query} not found
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    # Search by name
                    results = search_institution(query)
                    st.session_state['search_results'] = results
                    
                    if results:
                        st.markdown("**Found institutions:**")
                        
                        for i, inst in enumerate(results):
                            col1, col2, col3 = st.columns([3, 1, 1])
                            with col1:
                                st.markdown(f"**{inst['display_name']}**")
                                st.markdown(f"ROR: {inst['ror']} | Country: {inst.get('country', 'N/A')} | Works: {inst['works_count']:,}")
                            with col2:
                                if st.button("Select", key=f"select_{i}"):
                                    st.session_state['institution_id'] = inst['id']
                                    st.session_state['institution_name'] = inst['display_name']
                                    st.session_state['institution_ror'] = inst['ror']
                                    st.session_state['institution_country'] = inst.get('country', 'N/A')
                                    
                                    # Add to recent
                                    add_to_recent_institutions({
                                        'id': inst['id'],
                                        'name': inst['display_name'],
                                        'ror': inst['ror'],
                                        'country': inst.get('country', 'N/A')
                                    })
                                    
                                    st.session_state['step'] = 2
                                    st.rerun()
                            with col3:
                                st.button("Details", key=f"details_{i}", disabled=True)
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
        
        # Navigation buttons
        if st.session_state['institution_id']:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Back", use_container_width=True):
                    st.session_state['step'] = 1
                    st.rerun()
            with col2:
                if st.button("Next →", type="primary", use_container_width=True):
                    st.session_state['step'] = 2
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
     
    # ========================================================================
    # STEP 2: YEAR SELECTION (ИСПРАВЛЕННАЯ ВЕРСИЯ)
    # ========================================================================
    
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
        
        # Use on_change to update session state
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
            if st.button("Check Availability →", type="primary", use_container_width=True):
                if year_input:
                    years = parse_year_input(year_input)
                    if years:
                        # Validate years
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
                                # Get total count with expanded range
                                total = get_total_papers_count(st.session_state['institution_id'], years)
                                
                                st.session_state['years_range'] = years
                                st.session_state['total_papers'] = total
                                
                                if total > 0:
                                    expanded = expand_year_range(years)
                                    
                                    # Clear any previous error/success messages by rerunning
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
        
        # Show results and Start Analysis button if we have data
        if st.session_state['years_range'] and st.session_state['total_papers'] > 0:
            expanded = expand_year_range(st.session_state['years_range'])
            
            # Show warning for large datasets
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
            
            # Add Start Analysis button
            col1, col2, col3 = st.columns([1, 1, 2])
            with col2:
                if st.button("▶️ Start Analysis", type="primary", use_container_width=True):
                    st.session_state['step'] = 3
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # STEP 3: DATA COLLECTION
    # ========================================================================
    
    elif st.session_state['step'] == 3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📥 Step 3: Data Collection & Validation")
        
        st.markdown(f"""
        <div class="info-box">
            <strong>Analysis Parameters:</strong><br>
            Institution: {st.session_state['institution_name']}<br>
            Requested period: {min(st.session_state['years_range'])}-{max(st.session_state['years_range'])}<br>
            Total papers (OpenAlex with expansion): {st.session_state['total_papers']:,}
        </div>
        """, unsafe_allow_html=True)
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("← Back", use_container_width=True):
                st.session_state['step'] = 2
                st.rerun()
        
        with col2:
            if st.button("Start Data Collection", type="primary", use_container_width=True):
                all_papers = []
                cursor = "*"
                page = 0
                total_pages_to_fetch = min(
                    (st.session_state['total_papers'] // 200) + 1,
                    MAX_PAGES
                )
                
                # Step 1: Fetch from OpenAlex with limits
                status_text.text("Loading data from OpenAlex...")
                
                papers_to_fetch = min(st.session_state['total_papers'], MAX_PAPERS_TO_ANALYZE)
                status_text.text(f"Loading up to {papers_to_fetch:,} papers...")
                
                while cursor and len(all_papers) < MAX_PAPERS_TO_ANALYZE and page < MAX_PAGES:
                    page += 1
                    progress = min(0.1 + (page / total_pages_to_fetch) * 0.3, 0.4)
                    progress_bar.progress(progress)
                    
                    papers, next_cursor, batch_count = fetch_papers_batch(
                        st.session_state['institution_id'],
                        st.session_state['years_range'],
                        cursor
                    )
                    
                    all_papers.extend(papers)
                    cursor = next_cursor
                    
                    status_text.text(f"Loaded {len(all_papers)} papers (page {page}/{total_pages_to_fetch})...")
                    time.sleep(0.1)  # Rate limiting
                
                status_text.text(f"✅ Loaded {len(all_papers)} papers from OpenAlex")
                progress_bar.progress(0.4)
                
                # Step 2: Extract DOIs
                dois = extract_dois_from_papers(all_papers)
                status_text.text(f"Found {len(dois)} DOIs for validation")
                progress_bar.progress(0.45)
                
                # Step 3: Validate with Crossref (synchronous)
                status_text.text("Validating dates with Crossref...")
                
                crossref_data = make_crossref_request_batch(dois)
                
                status_text.text(f"✅ Validated {len(crossref_data)} DOIs")
                progress_bar.progress(0.7)
                
                # Step 4: Filter by actual years
                status_text.text("Filtering by actual publication years...")
                
                filtered_papers, validation_stats = filter_papers_by_actual_years(
                    all_papers,
                    crossref_data,
                    st.session_state['years_range']
                )
                
                progress_bar.progress(0.8)
                
                # Step 5: Analyze
                status_text.text("Analyzing data...")
                
                analysis_results = analyze_papers(filtered_papers)
                
                st.session_state['papers_data'] = analysis_results
                st.session_state['validation_stats'] = validation_stats
                st.session_state['analysis_complete'] = True
                
                progress_bar.progress(1.0)
                status_text.text("✅ Analysis complete!")
                
                time.sleep(0.5)
                
                st.session_state['step'] = 4
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # STEP 4: RESULTS
    # ========================================================================
    
    elif st.session_state['step'] == 4 and st.session_state['analysis_complete']:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📊 Step 4: Analysis Results")
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("← New Search", use_container_width=True):
                # Clear session but keep theme and recent
                palette = st.session_state['ui_palette']
                recent = st.session_state['recent_institutions']
                for key in list(st.session_state.keys()):
                    if key not in ['ui_palette', 'previous_palette', 'recent_institutions']:
                        del st.session_state[key]
                st.session_state['ui_palette'] = palette
                st.session_state['recent_institutions'] = recent
                st.session_state['step'] = 1
                st.rerun()
        
        with col2:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        
        # Summary metrics
        data = st.session_state['papers_data']
        validation = st.session_state['validation_stats']
        
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
        
        # Validation summary
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
        
        # Validation visualization
        if validation:
            fig_val = create_validation_summary(validation, colors)
            if fig_val:
                st.plotly_chart(fig_val, use_container_width=True)
        
        st.markdown("---")
        
        # Tabs for different analyses
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📈 Years", "👥 Authors", "📚 Journals", "🏢 Publishers", "📊 Citations", "🌍 Collaborations"
        ])
        
        with tab1:
            st.markdown("### Publications by Year")
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_yearly = plot_yearly_publications(data['yearly_papers'], colors)
                st.plotly_chart(fig_yearly, use_container_width=True)
            
            with col2:
                fig_cit_year = plot_yearly_citations(data['yearly_citations'], colors)
                st.plotly_chart(fig_cit_year, use_container_width=True)
            
            # Citations vs References
            fig_scatter = plot_citations_vs_references(data['enriched_papers'], colors)
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        with tab2:
            st.markdown("### Top 20 Authors")
            
            if data['top_authors']:
                fig_authors = plot_top_authors(data['top_authors'], colors)
                st.plotly_chart(fig_authors, use_container_width=True)
                
                # Table
                df_authors = pd.DataFrame(data['top_authors'], columns=['Author', 'Publications'])
                st.dataframe(df_authors, use_container_width=True)
            else:
                st.info("No author data available")
        
        with tab3:
            st.markdown("### Top 20 Journals")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if data['top_journals']:
                    fig_journals = plot_top_journals(data['top_journals'], colors)
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
                    fig_publishers = plot_top_publishers(data['top_publishers'], colors)
                    st.plotly_chart(fig_publishers, use_container_width=True)
            
            with col2:
                if data['top_publishers']:
                    df_publishers = pd.DataFrame(data['top_publishers'], columns=['Publisher', 'Publications'])
                    st.dataframe(df_publishers, use_container_width=True)
        
        with tab5:
            st.markdown("### Citation Analysis")
            
            # Citation distribution
            fig_cit_dist = plot_citation_distribution(data['citation_distribution'], colors)
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
                fig_collab = plot_collaboration_types(data['collaboration_types'], colors)
                st.plotly_chart(fig_collab, use_container_width=True)
            
            with col2:
                df_collab = pd.DataFrame(
                    list(data['collaboration_types'].items()),
                    columns=['Collaboration Type', 'Count']
                )
                st.dataframe(df_collab, use_container_width=True)
            
            # Yearly collaboration
            fig_yearly_collab = plot_yearly_collaboration(data['yearly_collaboration'], colors)
            st.plotly_chart(fig_yearly_collab, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Export section
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📥 Export Data")
        
        col1, col2, col3 = st.columns(3)
        
        # Prepare export data
        export_df = pd.DataFrame([
            {
                'Title': p['title'],
                'Authors': ', '.join(p['authors']),
                'Year': p['publication_year'],
                'Journal': p['journal'],
                'Publisher': p['publisher'],
                'Citations': p['cited_by_count'],
                'References': p.get('referenced_works_count', 0),
                'Citations per Year': p.get('citations_per_year', 0),
                'Type': p['type'],
                'DOI': p['doi'],
                'Collaboration Type': p['collaboration_type'],
                'Validation Source': p['validation'].get('source', 'N/A'),
                'Validation Year': p['validation'].get('year', 'N/A')
            }
            for p in data['enriched_papers']
        ])
        
        with col1:
            csv = export_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📊 Download CSV",
                data=csv,
                file_name=f"uninst_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # Excel export
            import io
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                export_df.to_excel(writer, sheet_name='All Papers', index=False)
                
                # Add summary sheet
                summary_data = {
                    'Metric': ['Institution', 'ROR', 'Country', 'Total Papers', 'Total Citations', 
                              'Average Citations', 'Validated DOIs', 'Analysis Date'],
                    'Value': [
                        st.session_state['institution_name'],
                        st.session_state['institution_ror'],
                        st.session_state['institution_country'],
                        data['total_papers'],
                        data['total_citations'],
                        f"{data['total_citations']/data['total_papers']:.2f}" if data['total_papers'] > 0 else 0,
                        validation['validated'],
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ]
                }
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                
                # Add validation stats
                pd.DataFrame([validation]).to_excel(writer, sheet_name='Validation', index=False)
                
                # Add collaboration stats
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
        
        with col3:
            # JSON export
            json_data = json.dumps({
                'institution': {
                    'name': st.session_state['institution_name'],
                    'ror': st.session_state['institution_ror'],
                    'country': st.session_state['institution_country']
                },
                'years': st.session_state['years_range'],
                'analysis_date': datetime.now().isoformat(),
                'summary': {
                    'total_papers': data['total_papers'],
                    'total_citations': data['total_citations'],
                    'validation_stats': validation,
                    'collaboration_types': data['collaboration_types']
                },
                'papers': [
                    {
                        'title': p['title'],
                        'authors': p['authors'],
                        'year': p['publication_year'],
                        'citations': p['cited_by_count'],
                        'references': p.get('referenced_works_count', 0),
                        'doi': p['doi']
                    }
                    for p in data['enriched_papers'][:100]  # Limit for JSON
                ]
            }, indent=2, ensure_ascii=False).encode('utf-8')
            
            st.download_button(
                label="📋 Download JSON",
                data=json_data,
                file_name=f"uninst_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown(f"""
    <div class="footer">
        <p>🏛️ UnInst Analytics | Data: OpenAlex, Crossref | Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()




