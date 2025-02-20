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
    get_db_connection
)
import logging

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
        Output("naics-details-panel", "children"),
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
            
            # Get the selected item's data from the database
            with get_db_connection() as conn:
                cursor = conn.cursor()
                if clicked_type == "subcategory-item":
                    cursor.execute("""
                        SELECT * FROM taxonomy 
                        WHERE subcategory = ? 
                        AND (sub_subcategory IS NULL OR sub_subcategory = '')
                        LIMIT 1
                    """, (clicked_id,))
                else:  # sub-subcategory-item
                    cursor.execute("""
                        SELECT * FROM taxonomy 
                        WHERE sub_subcategory = ?
                        LIMIT 1
                    """, (clicked_id,))
                
                item = cursor.fetchone()
                
                if not item:
                    logger.warning(f"No data found for {clicked_type} with id {clicked_id}")
                    return "No details available for this selection"
                
                logger.info(f"Found item data: {dict(item)}")
                
                # Create detailed view
                title = item['sub_subcategory'] if clicked_type == "sub-subcategory-item" else item['subcategory']
                code = item['sub_naics_code'] if clicked_type == "sub-subcategory-item" else item['naics_code']
                description = item['sub_naics_description'] if clicked_type == "sub-subcategory-item" else item['naics_description']
                
                return dbc.Card([
                    dbc.CardHeader(html.H4(title)),
                    dbc.CardBody([
                        html.H5("NAICS Information"),
                        html.P([
                            html.Strong("Code: "),
                            html.Span(code),
                        ]),
                        html.P([
                            html.Strong("Description: "),
                            html.Span(description),
                        ]),
                        html.H5("Classification", className="mt-3"),
                        html.Div([
                            create_badge("Function", item['function']),
                            create_badge("Supply Chain", item['supply_chain_position']),
                            create_badge("TRL", item['trl']),
                        ]),
                        html.H5("Potential Applications", className="mt-3"),
                        html.P(item['potential_applications']),
                    ])
                ])
                
        except Exception as e:
            logger.error(f"Error updating details: {str(e)}")
            return f"Error loading details: {str(e)}"

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

# Create the layout - fix indentation by moving it to module level
naics_layout = dbc.Container([
    # Add Font Awesome
    html.Link(
        rel="stylesheet",
        href="https://use.fontawesome.com/releases/v5.15.4/css/all.css"
    ),
    # Replace html.Style with dbc.Container for CSS
    dbc.Container([
        html.Link(
            rel='stylesheet',
            href='/assets/style.css'
        )
    ]),
    html.H1("NAICS Taxonomy Navigator", className="my-4"),
    # Add Filter Panel
    dbc.Card([
        dbc.CardBody([
            html.H5("Filters", className="card-title"),
            # Updated filter mode selection
            html.Div([
                html.H6("Filter Mode:", className="mb-2"),
                dbc.ButtonGroup(
                    [
                        dbc.Button(
                            "AND",
                            id="filter-mode-and",
                            color="primary",
                            outline=True,  # Add outline style
                            active=True,
                            className="me-1",
                            style={'width': '80px'}  # Fixed width for better appearance
                        ),
                        dbc.Button(
                            "OR",
                            id="filter-mode-or",
                            color="primary",
                            outline=True,  # Add outline style
                            active=False,
                            style={'width': '80px'}  # Fixed width for better appearance
                        ),
                    ],
                    className="mb-3 d-flex justify-content-center"  # Center the buttons
                ),
                html.Small("AND: All filters must match • OR: Any filter can match", 
                          className="text-muted d-block text-center mb-3")  # Add explanation
            ], className="text-center"),  # Center the entire filter mode section
            dbc.Row([
                # Function Filters
                dbc.Col([
                    html.H6("Function:", className="mb-2"),
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
                # Updated TRL Filters
                dbc.Col([
                    html.H6("TRL:", className="mb-2"),
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
                    html.H6("Supply Chain:", className="mb-2"),
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
                html.H6("Active Filters:", className="mt-3 mb-2"),
                html.Div(id="naics-active-filters", className="mb-2"),
                dbc.Button("Clear All Filters", id="naics-clear-filters", 
                          color="secondary", size="sm", className="mt-2")
            ], className="text-center")
        ])
    ], className="mb-4"),
    # Existing Row with Tree and Details
    dbc.Row([
        dbc.Col([
            html.Div(
                generate_naics_tree(),  # No argument needed, will load from database
                id="naics-tree",
                className="border rounded p-3"
            )
        ], width=4),
        dbc.Col([
            html.Div(
                "Select a subcategory to view details",
                id="naics-details-panel",
                className="border rounded p-3"
            )
        ], width=8)
    ])
], fluid=True)