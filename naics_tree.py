import json
import dash
from dash import dcc, html, Input, Output, State, ALL, MATCH
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from database import (
    get_all_categories,
    get_subcategories,
    get_sub_subcategories,
    filter_taxonomy,
    get_distinct_values,
    get_companies_for_naics
)
import logging
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Color mappings for classifications
FUNCTION_COLORS = {
    'CF': 'primary',
    'E': 'success',
    'A': 'warning',
    'EU': 'danger'
}

TRL_COLORS = {
    '1': 'danger',
    '2': 'danger',
    '3': 'danger',
    '4': 'warning',
    '5': 'warning',
    '6': 'warning',
    '7': 'info',
    '8': 'info',
    '9': 'success'
}

SUPPLY_CHAIN_COLORS = {
    'RMC': 'primary',
    'MF': 'success',
    'CET': 'warning',
    'ASI': 'info',
    'EUP': 'danger'
}

def process_naics_data(data):
    """This function is deprecated - using database instead"""
    pass

def filter_naics_data(data, active_filters):
    """Filter NAICS data based on active filters"""
    if not active_filters:
        return data
    # ... rest of the function ...
    return filtered_data

# Remove JSON debug code and initialization
naics_data = None

def generate_naics_tree(filtered_data=None):
    """Generate the NAICS tree from database data"""
    tree_items = []
    
    try:
        # Get all categories
        if filtered_data is None:
            categories = [row['category'] for row in get_all_categories()]
        else:
            categories = set(row['category'] for row in filtered_data)
            
        for category in sorted(categories):
            # Get subcategories
            if filtered_data is None:
                subcategories = get_subcategories(category)
            else:
                subcategories = [row for row in filtered_data if row['category'] == category]
                
            # Create collapsible card for each category
            category_item = dbc.Card([
                dbc.CardHeader(
                    dbc.Button(
                        category,
                        id={"type": "category-collapse-button", "index": category},
                        color="link",
                        className="text-decoration-none d-flex justify-content-between align-items-center"
                    ),
                    className="p-0"
                ),
                dbc.Collapse(
                    dbc.CardBody([
                        dbc.ListGroup([
                            # Make each subcategory collapsible
                            dbc.Card([
                                dbc.CardHeader(
                                    html.Div([
                                        # Clickable subcategory content first
                                        html.Div([
                                            # Header row with subcategory name and NAICS code
                                            html.Div([
                                                html.Strong(f"{subcat['subcategory']} "),
                                                html.Small(f"({subcat['naics_code']})", className="text-muted"),
                                            ]),
                                            # Description row
                                            html.Div(subcat['naics_description'], 
                                                    className="text-muted small"),
                                            # Badges row
                                            html.Div([
                                                create_badge("Function", subcat['function']),
                                                create_badge("Supply Chain", subcat['supply_chain_position']),
                                                create_badge("TRL", subcat['trl']),
                                            ], className="mt-1"),
                                            # Applications row
                                            html.Div(subcat['potential_applications'], 
                                                    className="text-muted small")
                                        ],
                                        id={"type": "subcategory-item", "index": subcat['subcategory']},
                                        n_clicks=0,
                                        className="subcategory-content"
                                        ),
                                        # Collapse button below content
                                        html.Div([
                                            dbc.Button(
                                                html.I(className="fas fa-chevron-down"),
                                                id={"type": "subcategory-collapse-button", 
                                                    "index": f"{category}-{subcat['subcategory']}"},
                                                color="light",
                                                size="sm",
                                                className="collapse-button"
                                            )
                                        ], className="d-flex justify-content-center mt-2")
                                    ], className="flex-column"),
                                    className="p-2"
                                ),
                                dbc.Collapse(
                                    dbc.CardBody([
                                        # Only show sub-subcategories in the collapse
                                        dbc.ListGroup([
                                            dbc.ListGroupItem([
                                                html.Div([
                                                    html.Strong(f"{sub['sub_subcategory']} "),
                                                    html.Small(f"({sub['sub_naics_code']})", className="text-muted"),
                                                    html.Div(sub['sub_naics_description'], className="text-muted small"),
                                                    html.Div([
                                                        create_badge("Function", sub['function']),
                                                        create_badge("Supply Chain", sub['supply_chain_position']),
                                                        create_badge("TRL", sub['trl']),
                                                    ], className="mt-2"),
                                                    html.Div(sub['potential_applications'], 
                                                           className="text-muted small mt-2")
                                                ])
                                            ],
                                            id={"type": "sub-subcategory-item", "index": sub['sub_subcategory']},
                                            n_clicks=0,
                                            action=True,
                                            className="sub-subcategory-item"
                                            ) for sub in get_sub_subcategories(category, subcat['subcategory']) 
                                              if sub['sub_subcategory']
                                        ], flush=True) if get_sub_subcategories(category, subcat['subcategory']) 
                                        else html.Div("No 3rd layer", className="text-muted text-center p-3")
                                    ]),
                                    id={"type": "subcategory-collapse", 
                                        "index": f"{category}-{subcat['subcategory']}"},
                                    is_open=False
                                )
                            ], className="mb-2 subcategory-card")
                            for subcat in subcategories
                        ], flush=True)
                    ]),
                    id={"type": "category-collapse", "index": category},
                    is_open=False
                )
            ], className="mb-2")
            tree_items.append(category_item)
        
        return html.Div(tree_items)
        
    except Exception as e:
        logger.error(f"Error generating NAICS tree: {str(e)}")
        return html.Div(f"Error loading taxonomy data: {str(e)}")

def create_badge(label, value):
    """Helper function to create colored badges"""
    if not value:
        return None
        
    if label == "Function":
        color = FUNCTION_COLORS.get(value, 'secondary')
    elif label == "TRL":
        color = TRL_COLORS.get(value.replace('TRL ', ''), 'secondary')
    else:  # Supply Chain
        color = SUPPLY_CHAIN_COLORS.get(value, 'secondary')
        
    return dbc.Badge(
        f"{value}",
        color=color,
        className="me-1"
    )

def format_value(value, criteria):
    """Format value based on criteria type"""
    if value is None:
        return "N/A"
    
    try:
        if criteria in ["revenue", "market_cap"]:
            value = float(value) / 1e9  # Convert to billions
            return f"${value:,.1f}B"
        elif criteria in ["yoy_growth", "market_share", "r&d_spending"]:
            return f"{float(value):,.1f}%"
        else:
            return str(value)
    except (ValueError, TypeError):
        return "N/A"

def get_ranking_header(criteria):
    """Get the header text for the ranking table"""
    headers = {
        'revenue': 'Revenue ($B)',
        'market_cap': 'Market Cap ($B)',
        'yoy_growth': 'YoY Growth (%)',
        'market_share': 'Market Share (%)',
        'r&d_spending': 'R&D Spending (%)'
    }
    return headers.get(criteria, 'Revenue ($B)')

def create_filter_section():
    """Create filter buttons from database values"""
    function_values = get_distinct_values('function')
    trl_values = get_distinct_values('trl')
    supply_chain_values = get_distinct_values('supply_chain_position')
    
    # Create filter buttons
    # ... (rest of the filter creation code remains similar)

def register_callbacks(app):
    """Register callbacks for the NAICS tree"""
    @app.callback(
        Output("rankings-card", "style"),
        [Input("current-naics-code", "data")]
    )
    def toggle_rankings_card(naics_code):
        if naics_code:
            return {"display": "block"}
        return {"display": "none"}

    @app.callback(
        [Output("naics-tree", "children"),
         Output("naics-active-filters", "children")],
        [Input({'type': 'function-filter', 'value': ALL}, 'n_clicks'),
         Input({'type': 'trl-filter', 'value': ALL}, 'n_clicks'),
         Input({'type': 'supply-chain-filter', 'value': ALL}, 'n_clicks'),
         Input("naics-clear-filters", "n_clicks")],
        [State({'type': 'function-filter', 'value': ALL}, 'id'),
         State({'type': 'trl-filter', 'value': ALL}, 'id'),
         State({'type': 'supply-chain-filter', 'value': ALL}, 'id'),
         State("filter-mode-and", "active")]
    )
    def update_filters(func_clicks, trl_clicks, supply_clicks, clear_clicks,
                      func_ids, trl_ids, supply_ids, and_mode):
        if not dash.callback_context.triggered:
            raise PreventUpdate
            
        triggered = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
        
        # Handle clear filters
        if triggered == "naics-clear-filters" and clear_clicks:
            return generate_naics_tree(), "No active filters"
            
        # Get active filters
        active_filters = {
            'function': [],
            'trl': [],
            'supply_chain_position': []
        }
        
        # Check which filters are active based on clicks
        for clicks, ids, filter_type in [
            (func_clicks, func_ids, 'function'),
            (trl_clicks, trl_ids, 'trl'),
            (supply_clicks, supply_ids, 'supply_chain_position')
        ]:
            if clicks and ids:
                for n, id_dict in zip(clicks, ids):
                    if n and n % 2:  # Button is active (odd number of clicks)
                        value = id_dict['value']
                        if filter_type == 'trl':
                            value = f"TRL {value}"  # Add TRL prefix to match database
                        active_filters[filter_type].append(value)
        
        # If no filters are active, return full tree
        if not any(active_filters.values()):
            return generate_naics_tree(), "No active filters"
            
        # Apply filters to database query
        filtered_data = apply_filters(active_filters, and_mode)
        
        # Create active filters display
        active_filters_display = []
        for filter_type, values in active_filters.items():
            if values:
                if filter_type == 'function':
                    badges = [dbc.Badge(v, color=FUNCTION_COLORS.get(v, 'secondary'), className="me-1") for v in values]
                elif filter_type == 'trl':
                    badges = [dbc.Badge(v, color=TRL_COLORS.get(v.replace('TRL ', ''), 'secondary'), className="me-1") for v in values]
                else:  # supply_chain_position
                    badges = [dbc.Badge(v, color=SUPPLY_CHAIN_COLORS.get(v, 'secondary'), className="me-1") for v in values]
                active_filters_display.extend(badges)
        
        if not active_filters_display:
            active_filters_display = "No active filters"
            
        return generate_naics_tree(filtered_data), html.Div(active_filters_display)

    def apply_filters(active_filters, and_mode):
        """Apply filters to database query"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                where_clauses = []
                params = []
                
                # Build WHERE clause for each filter type
                for field, values in active_filters.items():
                    if values:
                        if and_mode:
                            # AND mode: each filter type must match one of its values
                            where_clauses.append(f"{field} IN ({','.join(['?'] * len(values))})")
                            params.extend(values)
                        else:
                            # OR mode: combine all conditions with OR
                            where_clauses.extend([f"{field} = ?" for _ in values])
                            params.extend(values)
                
                # Combine clauses based on filter mode
                if where_clauses:
                    where_sql = " AND " if and_mode else " OR "
                    where_sql = where_sql.join(where_clauses)
                    
                    query = f"""
                        SELECT *
                        FROM taxonomy
                        WHERE {where_sql}
                        ORDER BY category, subcategory, sub_subcategory
                    """
                    
                    cursor.execute(query, params)
                    return cursor.fetchall()
                
                return None
                
        except Exception as e:
            logger.error(f"Error applying filters: {str(e)}")
            return None

    @app.callback(
        [Output("naics-details-panel", "children"),
         Output("current-naics-code", "data")],
        [Input({"type": "subcategory-item", "index": ALL}, "n_clicks"),
         Input({"type": "sub-subcategory-item", "index": ALL}, "n_clicks")],
        prevent_initial_call=True
    )
    def update_details(subcategory_clicks, sub_subcategory_clicks):
        """Update the details panel when an item is clicked"""
        if not dash.callback_context.triggered:
            raise PreventUpdate
            
        # Get the clicked item's ID
        triggered = dash.callback_context.triggered[0]
        clicked_prop_id = triggered['prop_id']
        
        try:
            clicked_dict = json.loads(clicked_prop_id.split('.')[0])
            clicked_type = clicked_dict['type']
            clicked_id = clicked_dict['index']
            
            logger.info(f"Clicked item: type={clicked_type}, id={clicked_id}")
            
            # Get the selected item's data from the taxonomy data
            if clicked_type == "subcategory-item":
                logger.info(f"Getting data for subcategory: {clicked_id}")
                items = filter_taxonomy({'Subcategory': clicked_id})
                logger.info(f"Found {len(items)} items for subcategory")
                if not items:
                    return "No details available for this selection (no matching subcategory)", None
                
                item = items[0]
                # Extract NAICS code from the correct field
                code = str(item.get('NAICS Code', ''))
                logger.info(f"Using NAICS code from subcategory: {code}")
                
                # Create a properly structured item for the details panel
                formatted_item = {
                    'category': item.get('Category', ''),
                    'subcategory': item.get('Subcategory', ''),
                    'sub_subcategory': None,
                    'naics_code': code,
                    'naics_description': item.get('NAICS Description', ''),
                    'sub_naics_code': None,
                    'sub_naics_description': None,
                    'function': item.get('Function', ''),
                    'supply_chain_position': item.get('Supply Chain Position', ''),
                    'trl': item.get('TRL', ''),
                    'potential_applications': item.get('Potential Applications', '')
                }
                
            else:  # sub-subcategory-item
                logger.info(f"Getting data for sub-subcategory: {clicked_id}")
                items = filter_taxonomy({'Potential Sub-Subcategory': clicked_id})
                logger.info(f"Found {len(items)} items for sub-subcategory")
                if not items:
                    return "No details available for this selection (no matching sub-subcategory)", None
                
                item = items[0]
                # For sub-subcategories, use the Sub-Subcategory NAICS Code
                code = str(item.get('Sub-Subcategory NAICS Code', ''))
                if code == 'N/A':
                    code = str(item.get('NAICS Code', ''))
                logger.info(f"Using NAICS code from sub-subcategory: {code}")
                
                # Create a properly structured item for the details panel
                formatted_item = {
                    'category': item.get('Category', ''),
                    'subcategory': item.get('Subcategory', ''),
                    'sub_subcategory': item.get('Potential Sub-Subcategory', ''),
                    'naics_code': str(item.get('NAICS Code', '')),
                    'naics_description': item.get('NAICS Description', ''),
                    'sub_naics_code': code if code != 'N/A' else None,
                    'sub_naics_description': item.get('Sub-Subcategory NAICS Description', ''),
                    'function': item.get('Function', ''),
                    'supply_chain_position': item.get('Supply Chain Position', ''),
                    'trl': item.get('TRL', ''),
                    'potential_applications': item.get('Potential Applications', '')
                }
            
            logger.info(f"Using NAICS code for company search: {code}")
            # Get matching companies using the JSON-based function
            companies = get_companies_for_naics(code, "revenue")  # Default to revenue sorting
            logger.info(f"Found {len(companies)} matching companies")
            
            return create_details_panel(formatted_item, companies), code
                
        except Exception as e:
            logger.error(f"Error updating details: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return f"Error loading details: {str(e)}", None

    # Add callback for filter mode toggle
    @app.callback(
        [Output("filter-mode-and", "active"),
         Output("filter-mode-or", "active")],
        [Input("filter-mode-and", "n_clicks"),
         Input("filter-mode-or", "n_clicks")]
    )
    def toggle_filter_mode(and_clicks, or_clicks):
        triggered = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
        if triggered == "filter-mode-and":
            return True, False
        elif triggered == "filter-mode-or":
            return False, True
        return True, False  # Default to AND

    @app.callback(
        Output({"type": "category-collapse", "index": MATCH}, "is_open"),
        Input({"type": "category-collapse-button", "index": MATCH}, "n_clicks"),
        State({"type": "category-collapse", "index": MATCH}, "is_open"),
    )
    def toggle_category_collapse(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open

    @app.callback(
        Output({"type": "subcategory-collapse", "index": MATCH}, "is_open"),
        Input({"type": "subcategory-collapse-button", "index": MATCH}, "n_clicks"),
        State({"type": "subcategory-collapse", "index": MATCH}, "is_open"),
    )
    def toggle_subcategory_collapse(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open

    @app.callback(
        [Output("value-column", "children"),
         Output("rankings-table", "children")],
        [Input({"type": "ranking-criteria", "value": ALL}, "n_clicks"),
         Input("current-naics-code", "data")],
        prevent_initial_call=True
    )
    def update_rankings(n_clicks, current_naics_code):
        """Update company rankings based on selected criteria"""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
            
        # Get the criteria from the button that was clicked, or use the default
        criteria = 'revenue'  # default
        if ctx.triggered[0]['prop_id'].split('.')[0] != 'current-naics-code':
            try:
                button_id = ctx.triggered[0]['prop_id'].split('.')[0]
                criteria = json.loads(button_id)['value'].lower()
            except:
                pass
        
        if not current_naics_code:
            return "No NAICS code selected", []
            
        logger.info(f"Updating rankings for NAICS {current_naics_code} with criteria {criteria}")
        
        # Get header based on criteria
        header = get_ranking_header(criteria)
        
        try:
            # Get companies using the JSON-based function
            companies = get_companies_for_naics(current_naics_code, criteria)
            
            if not companies:
                return header, [html.Tr([html.Td("No companies found for this NAICS code", colSpan=4)])]
            
            # Check if any company has the selected criteria
            field_mapping = {
                'revenue': 'Revenue',
                'market_cap': 'Market_Cap',
                'yoy_growth': 'YoY_Growth',
                'market_share': 'Market_Share',
                'r&d_spending': 'R&D_Spending_Percentage'
            }
            json_field = field_mapping.get(criteria, 'Revenue')
            
            # Check if any company has data for the selected criteria
            has_data = any(company.get(json_field) is not None for company in companies)
            if not has_data:
                message = f"No {header} data available for these companies"
                return header, [html.Tr([html.Td(message, colSpan=4)])]
            
            # Generate table rows
            rows = []
            for idx, company in enumerate(companies, 1):
                value = company.get(json_field)
                formatted_value = format_value(value, criteria)
                
                # Skip companies with no data for the selected criteria
                if value is None:
                    continue
                    
                row = html.Tr([
                    html.Td(str(idx)),
                    html.Td(company.get('Company_Name', 'N/A')),
                    html.Td(company.get('Country', 'N/A')),
                    html.Td(formatted_value)
                ])
                rows.append(row)
            
            if not rows:
                return header, [html.Tr([html.Td(f"No {criteria} data available", colSpan=4)])]
            
            logger.info(f"Created {len(rows)} table rows")
            return header, rows
            
        except Exception as e:
            logger.error(f"Error updating rankings: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return header, [html.Tr([html.Td(f"Error loading company data: {str(e)}", colSpan=4)])]

    # Rest of the callbacks...

def create_details_panel(item, companies):
    """Create the details panel with taxonomy info and company rankings"""
    # Get title and description based on whether it's a subcategory or sub-subcategory
    title = item['sub_subcategory'] if item['sub_subcategory'] else item['subcategory']
    code = item['sub_naics_code'] if item['sub_subcategory'] else item['naics_code']
    description = item['sub_naics_description'] if item['sub_subcategory'] else item['naics_description']
    
    return html.Div([
        # Taxonomy Details Card
        dbc.Card([
            dbc.CardHeader(html.H4(title, className="details-title")),
            dbc.CardBody([
                html.Div([
                    html.H5("NAICS Information", className="details-section-title"),
                    html.P([
                        html.Strong("Code: "),
                        html.Span(code, className="text-primary"),
                    ]),
                    html.P([
                        html.Strong("Description: "),
                        html.Span(description),
                    ]),
                ], className="details-section"),
                html.Div([
                    html.H5("Classification", className="details-section-title"),
                    html.Div([
                        create_badge("Function", item['function']),
                        create_badge("Supply Chain", item['supply_chain_position']),
                        create_badge("TRL", item['trl']),
                    ]),
                ], className="details-section"),
                html.Div([
                    html.H5("Potential Applications", className="details-section-title"),
                    html.P(item['potential_applications']),
                ], className="details-section")
            ])
        ], className="mb-3")
    ])

# Create the layout
naics_layout = dbc.Container([
    # Add Font Awesome
    html.Link(
        rel="stylesheet",
        href="https://use.fontawesome.com/releases/v5.15.4/css/all.css"
    ),
    # Add custom CSS
    html.Link(
        rel='stylesheet',
        href='/assets/style.css'
    ),
    html.H1("NAICS Taxonomy Navigator", className="my-4"),
    # Add Filter Panel
    dbc.Card([
        dbc.CardBody([
            html.H5("Filters", className="filter-title"),
            # Updated filter mode selection
            html.Div([
                html.H6("Filter Mode:", className="filter-group-title"),
                dbc.ButtonGroup(
                    [
                        dbc.Button(
                            "AND",
                            id="filter-mode-and",
                            color="primary",
                            outline=True,
                            active=True,
                            className="me-1",
                            style={'width': '80px'}
                        ),
                        dbc.Button(
                            "OR",
                            id="filter-mode-or",
                            color="primary",
                            outline=True,
                            active=False,
                            style={'width': '80px'}
                        ),
                    ],
                    className="mb-3 d-flex justify-content-center"
                ),
                html.Small("AND: All filters must match • OR: Any filter can match", 
                          className="text-muted d-block text-center mb-3")
            ], className="text-center"),
            dbc.Row([
                # Function Filters
                dbc.Col([
                    html.H6("Function:", className="filter-group-title"),
                    dbc.ButtonGroup([
                        dbc.Button("CF", id={'type': 'function-filter', 'value': 'CF'}, 
                                   color="primary", outline=True, size="sm", className="me-1", n_clicks=0),
                        dbc.Button("E", id={'type': 'function-filter', 'value': 'E'}, 
                                   color="success", outline=True, size="sm", className="me-1", n_clicks=0),
                        dbc.Button("A", id={'type': 'function-filter', 'value': 'A'}, 
                                   color="warning", outline=True, size="sm", className="me-1", n_clicks=0),
                        dbc.Button("EU", id={'type': 'function-filter', 'value': 'EU'}, 
                                   color="danger", outline=True, size="sm", n_clicks=0)
                    ], className="mb-2")
                ], width=4),
                # TRL Filters
                dbc.Col([
                    html.H6("TRL:", className="filter-group-title"),
                    dbc.ButtonGroup([
                        dbc.Button("1", id={'type': 'trl-filter', 'value': '1'}, 
                                   color="danger", outline=True, size="sm", className="me-1", n_clicks=0),
                        dbc.Button("2", id={'type': 'trl-filter', 'value': '2'}, 
                                   color="danger", outline=True, size="sm", className="me-1", n_clicks=0),
                        dbc.Button("3", id={'type': 'trl-filter', 'value': '3'}, 
                                   color="danger", outline=True, size="sm", className="me-1", n_clicks=0),
                        dbc.Button("4", id={'type': 'trl-filter', 'value': '4'}, 
                                   color="warning", outline=True, size="sm", className="me-1", n_clicks=0),
                        dbc.Button("5", id={'type': 'trl-filter', 'value': '5'}, 
                                   color="warning", outline=True, size="sm", className="me-1", n_clicks=0),
                        dbc.Button("6", id={'type': 'trl-filter', 'value': '6'}, 
                                   color="warning", outline=True, size="sm", className="me-1", n_clicks=0),
                        dbc.Button("7", id={'type': 'trl-filter', 'value': '7'}, 
                                   color="info", outline=True, size="sm", className="me-1", n_clicks=0),
                        dbc.Button("8", id={'type': 'trl-filter', 'value': '8'}, 
                                   color="info", outline=True, size="sm", className="me-1", n_clicks=0),
                        dbc.Button("9", id={'type': 'trl-filter', 'value': '9'}, 
                                   color="success", outline=True, size="sm", n_clicks=0)
                    ], className="mb-2")
                ], width=4),
                # Supply Chain Filters
                dbc.Col([
                    html.H6("Supply Chain:", className="filter-group-title"),
                    dbc.ButtonGroup([
                        dbc.Button("RMC", id={'type': 'supply-chain-filter', 'value': 'RMC'}, 
                                   color="primary", outline=True, size="sm", className="me-1", n_clicks=0),
                        dbc.Button("MF", id={'type': 'supply-chain-filter', 'value': 'MF'}, 
                                   color="success", outline=True, size="sm", className="me-1", n_clicks=0),
                        dbc.Button("CET", id={'type': 'supply-chain-filter', 'value': 'CET'}, 
                                   color="warning", outline=True, size="sm", className="me-1", n_clicks=0),
                        dbc.Button("ASI", id={'type': 'supply-chain-filter', 'value': 'ASI'}, 
                                   color="info", outline=True, size="sm", className="me-1", n_clicks=0),
                        dbc.Button("EUP", id={'type': 'supply-chain-filter', 'value': 'EUP'}, 
                                   color="danger", outline=True, size="sm", n_clicks=0)
                    ], className="mb-2")
                ], width=4)
            ]),
            # Active Filters Display
            html.Div([
                html.H6("Active Filters:", className="filter-group-title"),
                html.Div(id="naics-active-filters", className="mb-2"),
                dbc.Button("Clear All Filters", id="naics-clear-filters", 
                          color="secondary", size="sm", className="mt-2")
            ], className="text-center")
        ])
    ], className="mb-4"),
    # Tree and Details
    dbc.Row([
        dbc.Col([
            html.Div(
                generate_naics_tree(),
                id="naics-tree",
                className="naics-tree border rounded p-3"
            )
        ], width=4),
        dbc.Col([
            html.Div([
                html.Div(
                    "Select a subcategory to view details",
                    id="naics-details-panel",
                    className="details-panel"
                ),
                # Rankings table
                dbc.Card([
                    dbc.CardHeader([
                        html.H4("Top Corporations", className="rankings-title d-inline"),
                        dbc.ButtonGroup([
                            dbc.Button(
                                "Revenue",
                                id={"type": "ranking-criteria", "value": "revenue"},
                                color="primary",
                                size="sm",
                                className="me-1 ranking-criteria-btn",
                                active=True
                            ),
                            dbc.Button(
                                "Market Cap",
                                id={"type": "ranking-criteria", "value": "market_cap"},
                                color="primary",
                                size="sm",
                                className="me-1 ranking-criteria-btn",
                                outline=True
                            ),
                            dbc.Button(
                                "YoY Growth",
                                id={"type": "ranking-criteria", "value": "yoy_growth"},
                                color="primary",
                                size="sm",
                                className="me-1 ranking-criteria-btn",
                                outline=True
                            ),
                            dbc.Button(
                                "Market Share",
                                id={"type": "ranking-criteria", "value": "market_share"},
                                color="primary",
                                size="sm",
                                className="me-1 ranking-criteria-btn",
                                outline=True
                            ),
                            dbc.Button(
                                "R&D Spending",
                                id={"type": "ranking-criteria", "value": "r&d_spending"},
                                color="primary",
                                size="sm",
                                className="ranking-criteria-btn",
                                outline=True
                            )
                        ], className="float-end")
                    ]),
                    dbc.CardBody([
                        dbc.Table([
                            html.Thead([
                                html.Tr([
                                    html.Th("Rank"),
                                    html.Th("Company"),
                                    html.Th("Country"),
                                    html.Th("Revenue ($B)", id="value-column")
                                ])
                            ]),
                            html.Tbody([
                                html.Tr([
                                    html.Td("Select a subcategory to view company rankings", colSpan=4)
                                ])
                            ], id="rankings-table")
                        ], bordered=True, hover=True, size="sm", className="mb-0")
                    ])
                ], className="rankings-card mt-3", style={"display": "none"}, id="rankings-card")
            ])
        ], width=8)
    ]),
    dcc.Store(id="current-naics-code", data=None),
])