import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Global variables to store data in memory
_taxonomy_data = None
_company_data = None

def load_taxonomy_data():
    """Load taxonomy data from JSON file"""
    global _taxonomy_data
    try:
        with open('tax_5-1.json', 'r') as f:
            _taxonomy_data = json.load(f)
        logger.info("Taxonomy data loaded successfully")
    except Exception as e:
        logger.error(f"Error loading taxonomy data: {e}")
        _taxonomy_data = []

def load_company_data():
    """Load company data from JSON file"""
    global _company_data
    try:
        with open('company_rankings.json', 'r') as f:
            data = json.load(f)
            if isinstance(data, list) and len(data) > 0 and 'companies' in data[0]:
                _company_data = data[0]['companies']
            else:
                _company_data = []
        logger.info("Company data loaded successfully")
    except Exception as e:
        logger.error(f"Error loading company data: {e}")
        _company_data = []

def ensure_data_loaded():
    """Ensure data is loaded before operations"""
    if _taxonomy_data is None:
        load_taxonomy_data()
    if _company_data is None:
        load_company_data()

def get_all_categories() -> List[Dict[str, Any]]:
    """Get all top-level categories"""
    ensure_data_loaded()
    categories = set(item['Category'] for item in _taxonomy_data if item['Category'])
    return [{'category': cat} for cat in sorted(categories)]

def get_subcategories(category: str) -> List[Dict[str, Any]]:
    """Get subcategories for a given category"""
    ensure_data_loaded()
    subcategories = []
    for item in _taxonomy_data:
        if item['Category'] == category and item['Subcategory']:
            subcategories.append({
                'category': category,
                'subcategory': item['Subcategory'],
                'naics_code': str(item['NAICS Code']),
                'naics_description': item['NAICS Description'],
                'function': item['Function'],
                'supply_chain_position': item['Supply Chain Position'],
                'trl': item['TRL'],
                'potential_applications': item['Potential Applications']
            })
    
    # Remove duplicates while preserving order
    seen = set()
    unique_subcategories = []
    for subcat in subcategories:
        key = subcat['subcategory']
        if key not in seen:
            seen.add(key)
            unique_subcategories.append(subcat)
    
    return sorted(unique_subcategories, key=lambda x: x['subcategory'])

def get_sub_subcategories(category: str, subcategory: str) -> List[Dict[str, Any]]:
    """Get sub-subcategories for a given subcategory"""
    ensure_data_loaded()
    return [
        {
            'category': item['Category'],
            'subcategory': item['Subcategory'],
            'sub_subcategory': item['Potential Sub-Subcategory'],
            'sub_naics_code': item['Sub-Subcategory NAICS Code'],
            'sub_naics_description': item['Sub-Subcategory NAICS Description'],
            'naics_code': str(item['NAICS Code']),
            'naics_description': item['NAICS Description'],
            'function': item['Function'],
            'supply_chain_position': item['Supply Chain Position'],
            'trl': item['TRL'],
            'potential_applications': item['Potential Applications']
        }
        for item in _taxonomy_data
        if item['Category'] == category 
        and item['Subcategory'] == subcategory
        and item['Potential Sub-Subcategory'] != 'N/A'
    ]

def filter_taxonomy(filters: Dict[str, str], filter_mode: str = "AND") -> List[Dict[str, Any]]:
    """Filter taxonomy data based on provided filters"""
    ensure_data_loaded()
    
    def matches_filters(item: Dict[str, Any]) -> bool:
        if filter_mode == "AND":
            return all(
                str(item.get(field, '')).lower() == str(value).lower()
                for field, value in filters.items()
            )
        else:  # OR mode
            return any(
                str(item.get(field, '')).lower() == str(value).lower()
                for field, value in filters.items()
            )
    
    # Log the filtering process
    logger.info(f"Filtering taxonomy with filters: {filters}, mode: {filter_mode}")
    filtered_items = [item for item in _taxonomy_data if matches_filters(item)]
    logger.info(f"Found {len(filtered_items)} matching items")
    
    return filtered_items

def get_distinct_values(field: str) -> List[str]:
    """Get distinct values for a given field"""
    ensure_data_loaded()
    field_mapping = {
        'function': 'Function',
        'supply_chain_position': 'Supply Chain Position',
        'trl': 'TRL'
    }
    json_field = field_mapping.get(field, field)
    values = set(
        str(item.get(json_field, ''))
        for item in _taxonomy_data
        if item.get(json_field) and item.get(json_field) != 'N/A'
    )
    return sorted(values)

def get_companies_for_naics(naics_code: str, sort_by: str = "revenue") -> List[Dict[str, Any]]:
    """Get companies matching a NAICS code"""
    ensure_data_loaded()
    
    # Convert sort_by to match JSON structure
    sort_by_mapping = {
        'revenue': 'Revenue',
        'market_cap': 'Market_Cap',
        'yoy_growth': 'YoY_Growth',
        'market_share': 'Market_Share',
        'r&d_spending': 'R&D_Spending_Percentage'
    }
    sort_field = sort_by_mapping.get(sort_by, 'Revenue')
    
    logger.info(f"Searching for companies with NAICS code: {naics_code}")
    
    # Try exact match first
    companies = []
    for company in _company_data:
        company_naics = str(company.get('NAICS_Codes', ''))
        if company_naics:
            codes = [code.strip() for code in company_naics.split(',')]
            if str(naics_code) in codes:
                companies.append(company)
    
    logger.info(f"Found {len(companies)} companies with exact NAICS match")
    
    # If no results and code is long enough, try broader match
    if not companies and len(str(naics_code)) > 3:
        prefix = str(naics_code)[:3]
        logger.info(f"Trying broader match with prefix: {prefix}")
        for company in _company_data:
            company_naics = str(company.get('NAICS_Codes', ''))
            if company_naics:
                codes = [code.strip() for code in company_naics.split(',')]
                if any(code.startswith(prefix) for code in codes):
                    companies.append(company)
        logger.info(f"Found {len(companies)} companies with broader NAICS match")
    
    # Sort companies by the specified criteria
    def safe_sort_key(x):
        value = x.get(sort_field)
        if value is None:
            return float('-inf')
        try:
            return float(value)
        except (ValueError, TypeError):
            return float('-inf')
    
    companies.sort(key=safe_sort_key, reverse=True)
    result = companies[:10]  # Return top 10
    
    # Log the results
    logger.info(f"Returning {len(result)} companies sorted by {sort_field}")
    for company in result:
        logger.info(f"Company: {company.get('Company_Name')}, {sort_field}: {company.get(sort_field)}")
    
    return result

# Initialize data when module is imported
load_taxonomy_data()
load_company_data() 