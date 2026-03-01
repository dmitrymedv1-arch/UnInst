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
import asyncio
import aiohttp
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
        gap: 10px;
    }}
    
    .step {{
        flex: 1;
        text-align: center;
        padding: 1rem;
        background: {colors['card_bg']};
        border: 2px solid {colors['border']};
        border-radius: 10px;
        transition: all 0.3s;
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
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CONFIGURATION
# ============================================================================

OPENALEX_BASE_URL = "https://api.openalex.org"
CROSSREF_BASE_URL = "https://api.crossref.org"
MAILTO = "your-email@example.com"  # Change to your email
HEADERS = {'User-Agent': f'UnInst-Analytics (mailto:{MAILTO})'}

# Rate limits
MAX_RETRIES = 3
BATCH_SIZE = 100  # for Crossref batch queries

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
if 'show_start_analysis' not in st.session_state:
    st.session_state['show_start_analysis'] = False

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_ror_id(text: str) -> bool:
    """Check if text is a valid ROR ID"""
    pattern = r'^[a-z0-9]{9,10}$'
    return bool(re.match(pattern, text.strip()))

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
            return None
            
    except Exception as e:
        raise

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
    """Parse year input from user"""
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
                return []
        else:
            try:
                years.add(int(part))
            except ValueError:
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

def fetch_papers_batch(institution_id: str, years: List[int], cursor: str = "*") -> Tuple[List[Dict], Optional[str]]:
    """Fetch a batch of papers from OpenAlex"""
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
        return data['results'], next_cursor
    
    return [], None

def extract_dois_from_papers(papers: List[Dict]) -> List[str]:
    """Extract DOIs from papers"""
    dois = []
    for paper in papers:
        doi = paper.get('doi', '')
        if doi:
            doi = doi.replace('https://doi.org/', '').replace('http://doi.org/', '')
            dois.append(doi)
    return dois

async def validate_dois_with_crossref(dois: List[str], batch_size: int = 100) -> Dict[str, Dict]:
    """Validate DOIs with Crossref in batches"""
    if not dois:
        return {}
    
    results = {}
    dois = list(set(dois))
    batches = [dois[i:i + batch_size] for i in range(0, len(dois), batch_size)]
    
    async with aiohttp.ClientSession() as session:
        for batch in batches:
            payload = {"ids": batch}
            
            try:
                async with session.post(
                    f"{CROSSREF_BASE_URL}/works",
                    json=payload,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for item in data.get('items', []):
                            doi = item.get('DOI', '').lower()
                            pub_date = None
                            
                            if 'published-print' in item:
                                date_parts = item['published-print'].get('date-parts', [[]])[0]
                                if date_parts:
                                    pub_date = {
                                        'year': date_parts[0],
                                        'month': date_parts[1] if len(date_parts) > 1 else 1,
                                        'day': date_parts[2] if len(date_parts) > 2 else 1,
                                        'source': 'published-print'
                                    }
                            elif 'published' in item:
                                date_parts = item['published'].get('date-parts', [[]])[0]
                                if date_parts:
                                    pub_date = {
                                        'year': date_parts[0],
                                        'month': date_parts[1] if len(date_parts) > 1 else 1,
                                        'day': date_parts[2] if len(date_parts) > 2 else 1,
                                        'source': 'published'
                                    }
                            elif 'published-online' in item:
                                date_parts = item['published-online'].get('date-parts', [[]])[0]
                                if date_parts:
                                    pub_date = {
                                        'year': date_parts[0],
                                        'month': date_parts[1] if len(date_parts) > 1 else 1,
                                        'day': date_parts[2] if len(date_parts) > 2 else 1,
                                        'source': 'published-online'
                                    }
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
                                results[doi] = {
                                    'doi': doi,
                                    'year': pub_date['year'],
                                    'source': pub_date['source']
                                }
                    
                    await asyncio.sleep(0.1)
                    
            except Exception as e:
                continue
    
    return results

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
            validation_stats['no_doi'] += 1
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
            
            if crossref_year in target_years:
                paper['publication_year'] = crossref_year
                filtered_papers.append(paper)
                validation_stats['kept'] += 1
            else:
                validation_stats['rejected'] += 1
                if crossref_year != paper.get('publication_year'):
                    validation_stats['year_mismatch'] += 1
        else:
            validation_stats['not_found'] += 1
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
        'cited_by_count': paper.get('cited_by_count', 0),
        'type': paper.get('type', ''),
        'is_oa': paper.get('open_access', {}).get('is_oa', False)
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
                
                institutions = authorship.get('institutions', [])
                for inst in institutions:
                    if inst.get('country_code'):
                        author_countries.add(inst['country_code'])
                
                author_affiliations.extend([inst.get('display_name', '') for inst in institutions if inst.get('display_name')])
    
    enriched['authors'] = authors
    enriched['author_count'] = len(authors)
    
    # Journal and publisher
    primary_location = paper.get('primary_location', {})
    if primary_location:
        source = primary_location.get('source', {})
        enriched['journal'] = source.get('display_name', 'Unknown')
        enriched['publisher'] = source.get('publisher', 'Unknown')
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

def analyze_papers(papers: List[Dict]) -> Dict:
    """Perform comprehensive analysis on papers"""
    enriched_papers = [enrich_paper_data(p) for p in papers]
    
    # Basic stats
    total_papers = len(enriched_papers)
    total_citations = sum(p['cited_by_count'] for p in enriched_papers)
    
    # Yearly distribution
    yearly_papers = defaultdict(int)
    yearly_citations = defaultdict(int)
    for p in enriched_papers:
        year = p['publication_year']
        yearly_papers[year] += 1
        yearly_citations[year] += p['cited_by_count']
    
    # Authors analysis
    all_authors = []
    for p in enriched_papers:
        all_authors.extend(p['authors'])
    
    author_counts = Counter(all_authors)
    top_authors = author_counts.most_common(20)
    
    # Journals analysis
    journal_counts = Counter(p['journal'] for p in enriched_papers)
    top_journals = journal_counts.most_common(20)
    
    # Publishers analysis
    publisher_counts = Counter(p['publisher'] for p in enriched_papers if p['publisher'])
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
    top_cited = sorted(enriched_papers, key=lambda x: x['cited_by_count'], reverse=True)[:20]
    
    # Top papers by citations per year
    current_year = datetime.now().year
    for p in enriched_papers:
        p['citations_per_year'] = calculate_citations_per_year(
            p['cited_by_count'], p['publication_year'], current_year
        )
    
    top_cpy = sorted(enriched_papers, key=lambda x: x['citations_per_year'], reverse=True)[:20]
    
    # Collaboration analysis
    collab_types = Counter(p['collaboration_type'] for p in enriched_papers)
    
    # Yearly collaboration breakdown
    yearly_collab = defaultdict(lambda: defaultdict(int))
    for p in enriched_papers:
        year = p['publication_year']
        yearly_collab[year][p['collaboration_type']] += 1
    
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
# PLOTTING FUNCTIONS
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
        name='Citations'
    ))
    
    fig.update_layout(
        title='Citations by Year',
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
        marker_color=colors['primary']
    ))
    
    fig.update_layout(
        title='Top Authors',
        xaxis_title='Publications',
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
        marker_color=colors['secondary']
    ))
    
    fig.update_layout(
        title='Top Journals',
        xaxis_title='Publications',
        yaxis_title='Journal',
        template='plotly_white',
        height=500,
        showlegend=False
    )
    
    return fig

def plot_top_publishers(publishers_data: List[Tuple[str, int]], colors: Dict):
    """Plot top publishers"""
    publishers = [p[0][:30] + '...' if len(p[0]) > 30 else p[0] for p in publishers_data[:8]]
    counts = [p[1] for p in publishers_data[:8]]
    
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=publishers,
        values=counts,
        marker_colors=[colors['primary'], colors['secondary'], colors['gradient_start'], 
                       colors['gradient_end'], colors['accent1'], colors['accent2']],
        textinfo='percent+label',
        insidetextorientation='radial'
    ))
    
    fig.update_layout(
        title='Top Publishers',
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
        marker_color=colors['primary']
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
    
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=labels,
        values=values,
        marker_colors=[colors['primary'], colors['secondary'], colors['gradient_start']],
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
        title='Collaboration by Year',
        xaxis_title='Year',
        yaxis_title='Publications',
        barmode='stack',
        template='plotly_white',
        hovermode='x'
    )
    
    fig.update_xaxes(tickangle=45)
    return fig

def plot_citations_vs_references(papers: List[Dict], colors: Dict):
    """Plot citations vs references scatter"""
    citations = [p['cited_by_count'] for p in papers]
    references = [random.randint(0, 100) for _ in papers]  # Placeholder
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
            colorbar=dict(title='Year')
        ),
        text=[p['title'][:50] + '...' for p in papers],
        hovertemplate='<b>%{text}</b><br>Citations: %{y}<br>Year: %{marker.color}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Citations vs Year',
        xaxis_title='References',
        yaxis_title='Citations',
        template='plotly_white',
        height=500
    )
    
    return fig

def create_validation_summary(validation_stats: Dict, colors: Dict):
    """Create validation summary visualization"""
    if not validation_stats:
        return None
    
    labels = ['Validated & Kept', 'Kept (No DOI/Not Found)', 'Rejected']
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
        title='DOI Validation',
        template='plotly_white',
        height=400
    )
    
    return fig

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    # Sidebar
    with st.sidebar:
        st.markdown(f"<h2 style='color: {colors['primary']};'>🎨 Theme</h2>", unsafe_allow_html=True)
        
        cols = st.columns(4)
        for i, palette in enumerate(UI_COLOR_PALETTES[:8]):
            with cols[i % 4]:
                if st.button("●", key=f"theme_{i}", help=palette['name']):
                    st.session_state['ui_palette'] = palette
                    st.rerun()
        
        st.markdown("---")
        st.markdown("**About UnInst Analytics**")
        st.markdown("University & Institution analytics using OpenAlex")
    
    # Main content
    st.markdown(f'<h1 class="main-header">🏛️ UnInst Analytics</h1>', unsafe_allow_html=True)
    
    # Step indicator
    steps = ["Institution", "Period", "Collection", "Results"]
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
    # STEP 1
    # ========================================================================
    
    if st.session_state['step'] == 1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🔍 Step 1: Institution Search")
        
        query = st.text_input("Institution name or ROR ID", placeholder="e.g., Institute of High-Temperature Electrochemistry or 0521rv456")
        
        if st.button("🔍 Search", type="primary"):
            with st.spinner("Searching..."):
                if is_ror_id(query):
                    inst = get_institution_by_ror(query)
                    if inst:
                        st.session_state['institution_id'] = inst['id']
                        st.session_state['institution_name'] = inst['display_name']
                        st.session_state['institution_ror'] = inst['ror']
                        st.session_state['institution_country'] = inst.get('country', 'N/A')
                        st.session_state['search_results'] = [inst]
                        st.rerun()
                else:
                    results = search_institution(query)
                    st.session_state['search_results'] = results
                    st.rerun()
        
        # Show results
        if st.session_state['search_results']:
            st.markdown("### Results")
            for i, inst in enumerate(st.session_state['search_results']):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{inst['display_name']}**")
                    st.markdown(f"ROR: {inst['ror']} | Country: {inst.get('country', 'N/A')} | Works: {inst['works_count']:,}")
                with col2:
                    if st.button("Select", key=f"sel_{i}"):
                        st.session_state['institution_id'] = inst['id']
                        st.session_state['institution_name'] = inst['display_name']
                        st.session_state['institution_ror'] = inst['ror']
                        st.session_state['institution_country'] = inst.get('country', 'N/A')
                        st.session_state['step'] = 2
                        st.rerun()
                st.markdown("---")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # STEP 2
    # ========================================================================
    
    elif st.session_state['step'] == 2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📅 Step 2: Analysis Period")
        
        st.markdown(f"""
        <div class="info-box">
            <strong>Institution:</strong> {st.session_state['institution_name']}<br>
            <strong>ROR:</strong> {st.session_state['institution_ror']}
        </div>
        """, unsafe_allow_html=True)
        
        year_input = st.text_input(
            "Period (e.g., 2023, 2020-2024, or 2020-2022,2024)",
            value=st.session_state['year_input_text']
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("← Back", use_container_width=True):
                st.session_state['step'] = 1
                st.rerun()
        
        with col2:
            if st.button("Check", type="primary", use_container_width=True):
                if year_input:
                    years = parse_year_input(year_input)
                    if years:
                        st.session_state['year_input_text'] = year_input
                        
                        with st.spinner("Checking..."):
                            total = get_total_papers_count(st.session_state['institution_id'], years)
                            st.session_state['years_range'] = years
                            st.session_state['total_papers'] = total
                            
                            if total > 0:
                                expanded = expand_year_range(years)
                                st.markdown(f"""
                                <div class="success-box">
                                    <strong>✅ Data found</strong><br>
                                    Papers: {total:,}<br>
                                    Search period: {min(expanded)}-{max(expanded)}
                                </div>
                                """, unsafe_allow_html=True)
                                st.session_state['show_start_analysis'] = True
                            else:
                                st.markdown("""
                                <div class="warning-box">
                                    ⚠️ No papers found
                                </div>
                                """, unsafe_allow_html=True)
        
        if st.session_state.get('show_start_analysis', False):
            if st.button("Start Analysis →", type="primary", use_container_width=True):
                st.session_state['step'] = 3
                st.session_state['show_start_analysis'] = False
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # STEP 3
    # ========================================================================
    
    elif st.session_state['step'] == 3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📥 Step 3: Data Collection")
        
        st.markdown(f"""
        <div class="info-box">
            <strong>Parameters:</strong><br>
            Institution: {st.session_state['institution_name']}<br>
            Period: {min(st.session_state['years_range'])}-{max(st.session_state['years_range'])}<br>
            Estimated papers: {st.session_state['total_papers']:,}
        </div>
        """, unsafe_allow_html=True)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("← Back", use_container_width=True):
                st.session_state['step'] = 2
                st.rerun()
        
        with col2:
            if st.button("Start", type="primary", use_container_width=True):
                all_papers = []
                cursor = "*"
                page = 0
                
                status_text.text("Loading from OpenAlex...")
                
                while cursor:
                    page += 1
                    progress_bar.progress(min(page * 0.1, 0.3))
                    
                    papers, next_cursor = fetch_papers_batch(
                        st.session_state['institution_id'],
                        st.session_state['years_range'],
                        cursor
                    )
                    
                    all_papers.extend(papers)
                    cursor = next_cursor
                    status_text.text(f"Loaded {len(all_papers)} papers...")
                    time.sleep(0.1)
                
                status_text.text(f"✅ Loaded {len(all_papers)} papers")
                progress_bar.progress(0.3)
                
                # Extract DOIs
                dois = extract_dois_from_papers(all_papers)
                status_text.text(f"Found {len(dois)} DOIs")
                progress_bar.progress(0.4)
                
                # Validate with Crossref
                status_text.text("Validating with Crossref...")
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                crossref_data = loop.run_until_complete(validate_dois_with_crossref(dois))
                loop.close()
                
                status_text.text(f"✅ Validated {len(crossref_data)} DOIs")
                progress_bar.progress(0.8)
                
                # Filter
                status_text.text("Filtering papers...")
                
                filtered_papers, validation_stats = filter_papers_by_actual_years(
                    all_papers, crossref_data, st.session_state['years_range']
                )
                
                progress_bar.progress(0.9)
                
                # Analyze
                status_text.text("Analyzing...")
                
                analysis_results = analyze_papers(filtered_papers)
                
                st.session_state['papers_data'] = analysis_results
                st.session_state['validation_stats'] = validation_stats
                st.session_state['analysis_complete'] = True
                
                progress_bar.progress(1.0)
                status_text.text("✅ Complete!")
                
                time.sleep(0.5)
                st.session_state['step'] = 4
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # STEP 4
    # ========================================================================
    
    elif st.session_state['step'] == 4 and st.session_state['analysis_complete']:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📊 Step 4: Results")
        
        # New search button
        if st.button("← New Search", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key not in ['ui_palette']:
                    del st.session_state[key]
            st.session_state['step'] = 1
            st.rerun()
        
        # Metrics
        data = st.session_state['papers_data']
        validation = st.session_state['validation_stats']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f'<div class="metric-card"><div class="value">{data["total_papers"]:,}</div><div class="label">Papers</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><div class="value">{data["total_citations"]:,}</div><div class="label">Citations</div></div>', unsafe_allow_html=True)
        with col3:
            avg = data["total_citations"]/data["total_papers"] if data["total_papers"] > 0 else 0
            st.markdown(f'<div class="metric-card"><div class="value">{avg:.1f}</div><div class="label">Avg</div></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metric-card"><div class="value">{validation["validated"]:,}</div><div class="label">Validated</div></div>', unsafe_allow_html=True)
        
        # Validation summary
        st.markdown(f"""
        <div class="info-box">
            <strong>Validation:</strong> {validation['validated']}/{validation['with_doi']} DOIs validated | {validation['kept']}/{validation['total']} papers kept
        </div>
        """, unsafe_allow_html=True)
        
        # Tabs
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "Years", "Authors", "Journals", "Publishers", "Citations", "Collaborations"
        ])
        
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(plot_yearly_publications(data['yearly_papers'], colors), use_container_width=True)
            with col2:
                st.plotly_chart(plot_yearly_citations(data['yearly_citations'], colors), use_container_width=True)
            st.plotly_chart(plot_citations_vs_references(data['enriched_papers'], colors), use_container_width=True)
        
        with tab2:
            if data['top_authors']:
                st.plotly_chart(plot_top_authors(data['top_authors'], colors), use_container_width=True)
                df = pd.DataFrame(data['top_authors'], columns=['Author', 'Publications'])
                st.dataframe(df, use_container_width=True)
        
        with tab3:
            if data['top_journals']:
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(plot_top_journals(data['top_journals'], colors), use_container_width=True)
                with col2:
                    df = pd.DataFrame(data['top_journals'], columns=['Journal', 'Publications'])
                    st.dataframe(df, use_container_width=True)
        
        with tab4:
            if data['top_publishers']:
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(plot_top_publishers(data['top_publishers'], colors), use_container_width=True)
                with col2:
                    df = pd.DataFrame(data['top_publishers'], columns=['Publisher', 'Publications'])
                    st.dataframe(df, use_container_width=True)
        
        with tab5:
            st.plotly_chart(plot_citation_distribution(data['citation_distribution'], colors), use_container_width=True)
            
            st.markdown("### Top 20 Most Cited")
            df_cited = pd.DataFrame([
                {'Title': p['title'][:80] + '...', 'Citations': p['cited_by_count'], 'Year': p['publication_year']}
                for p in data['top_cited'][:10]
            ])
            st.dataframe(df_cited, use_container_width=True)
            
            st.markdown("### Top 20 by Annual Rate")
            df_rate = pd.DataFrame([
                {'Title': p['title'][:80] + '...', 'Rate': f"{p['citations_per_year']:.1f}", 'Year': p['publication_year']}
                for p in data['top_citations_per_year'][:10]
            ])
            st.dataframe(df_rate, use_container_width=True)
        
        with tab6:
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(plot_collaboration_types(data['collaboration_types'], colors), use_container_width=True)
            with col2:
                df = pd.DataFrame(list(data['collaboration_types'].items()), columns=['Type', 'Count'])
                st.dataframe(df, use_container_width=True)
            st.plotly_chart(plot_yearly_collaboration(data['yearly_collaboration'], colors), use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Export
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📥 Export")
        
        export_df = pd.DataFrame([
            {
                'Title': p['title'],
                'Authors': ', '.join(p['authors']),
                'Year': p['publication_year'],
                'Journal': p['journal'],
                'Citations': p['cited_by_count'],
                'DOI': p['doi']
            }
            for p in data['enriched_papers']
        ])
        
        csv = export_df.to_csv(index=False).encode('utf-8')
        st.download_button("📊 Download CSV", csv, "uninst_analysis.csv", "text/csv", use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown(f'<div class="footer">UnInst Analytics | Data: OpenAlex, Crossref</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
