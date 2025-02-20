import json
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

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
    """Convert flat list structure into hierarchical dictionary"""
    organized_data = {}
    
    # Debug: Print first item to see its structure
    if data:
        print("Sample data item:")
        print(json.dumps(data[0], indent=2))
    
    for item in data:
        category = item['Category']
        subcategory = item['Subcategory']
        sub_subcategory = item['Potential Sub-Subcategory']
        naics_code = item['NAICS Code']
        naics_desc = item['NAICS Description']
        sub_naics_code = item['Sub-Subcategory NAICS Code']
        sub_naics_desc = item['Sub-Subcategory NAICS Description']
        potential_apps = item['Potential Applications']
        
        # Debug: Print the classification fields
        print(f"Function: {item.get('Function', 'Not found')}")
        print(f"Supply Chain Position: {item.get('Supply Chain Position', 'Not found')}")
        print(f"TRL: {item.get('TRL', 'Not found')}")
        
        # Skip empty entries
        if not category:
            continue
            
        # Initialize category if it doesn't exist
        if category not in organized_data:
            organized_data[category] = {
                'children': {},
                'code': '',
                'description': ''
            }
        
        # Initialize subcategory if it doesn't exist
        if subcategory not in organized_data[category]['children']:
            organized_data[category]['children'][subcategory] = {
                'children': {},
                'code': naics_code,
                'description': naics_desc,
                'Potential Applications': potential_apps,
                'Function': item.get('Function', ''),
                'Supply Chain Position': item.get('Supply Chain Position', ''),
                'TRL': item.get('TRL', '')
            }
        
        # Add sub-subcategory if it exists and isn't "N/A"
        if sub_subcategory and sub_subcategory != "N/A":
            organized_data[category]['children'][subcategory]['children'][sub_subcategory] = {
                'code': sub_naics_code,
                'description': sub_naics_desc,
                'Potential Applications': potential_apps,
                'Function': item.get('Function', ''),
                'Supply Chain Position': item.get('Supply Chain Position', ''),
                'TRL': item.get('TRL', '')
            }
    
    # Debug: Print a sample of processed data
    if organized_data:
        first_category = next(iter(organized_data))
        print("\nProcessed data sample:")
        print(json.dumps({first_category: organized_data[first_category]}, indent=2))
    
    return organized_data

# Load and process NAICS JSON data
with open("tax_5-1.json", 'r') as f:  # Updated to use new file
    raw_data = json.load(f)
    naics_data = process_naics_data(raw_data)

# After loading the data
print("\nInitial data structure check:")
print("Top level categories:", list(naics_data.keys()))
if naics_data:
    first_cat = next(iter(naics_data))
    first_subcat = next(iter(naics_data[first_cat]['children']))
    print(f"\nSample subcategory data for {first_cat} -> {first_subcat}:")
    print(json.dumps(naics_data[first_cat]['children'][first_subcat], indent=2))

def generate_naics_tree(taxonomy):
    """Generate the navigation tree from NAICS taxonomy data"""
    tree_elements = []
    
    for level1, level1_details in taxonomy.items():
        level2_items = []
        
        for level2, level2_details in level1_details.get('children', {}).items():
            level3_items = []
            
            # Create level 3 items (sub-subcategories)
            for level3, level3_details in level2_details.get('children', {}).items():
                if level3 != "N/A":
                    level3_items.append(
                        dbc.ListGroupItem([
                            html.Div([
                                html.Span(f"{level3_details.get('code', '')} - {level3}", className="me-2"),
                                dbc.Badge(
                                    level3_details.get('Function', ''),
                                    color=FUNCTION_COLORS.get(level3_details.get('Function', ''), 'secondary'),
                                    className="me-1"
                                ),
                                dbc.Badge(
                                    level3_details.get('TRL', ''),
                                    color=TRL_COLORS.get(level3_details.get('TRL', ''), 'secondary'),
                                    className="me-1"
                                ),
                                dbc.Badge(
                                    level3_details.get('Supply Chain Position', ''),
                                    color=SUPPLY_CHAIN_COLORS.get(level3_details.get('Supply Chain Position', ''), 'secondary'),
                                    className="me-1"
                                )
                            ], style={'display': 'flex', 'alignItems': 'center', 'flexWrap': 'wrap'})
                        ],
                        id={'type': 'level3-item', 'level1': level1, 'level2': level2, 'level3': level3},
                        action=True,
                        className="ms-4"
                        )
                    )
            
            # Create level 2 items (subcategories)
            level2_items.append(
                html.Div([
                    dbc.ListGroupItem([
                        html.Div([
                            html.Span(f"{level2_details.get('code', '')} - {level2}", className="me-2"),
                            dbc.Badge(
                                level2_details.get('Function', ''),
                                color=FUNCTION_COLORS.get(level2_details.get('Function', ''), 'secondary'),
                                className="me-1"
                            ),
                            dbc.Badge(
                                level2_details.get('TRL', ''),
                                color=TRL_COLORS.get(level2_details.get('TRL', ''), 'secondary'),
                                className="me-1"
                            ),
                            dbc.Badge(
                                level2_details.get('Supply Chain Position', ''),
                                color=SUPPLY_CHAIN_COLORS.get(level2_details.get('Supply Chain Position', ''), 'secondary'),
                                className="me-1"
                            )
                        ], style={'display': 'flex', 'alignItems': 'center', 'flexWrap': 'wrap'})
                    ],
                    id={'type': 'level2-item', 'level1': level1, 'level2': level2},
                    action=True
                    ),
                    *level3_items
                ])
            )
        
        tree_elements.append(
            dbc.Card([
                dbc.CardHeader(
                    dbc.Button(
                        level1,
                        id={'type': 'level1-button', 'level1': level1},
                        color="link",
                        className="text-left w-100"
                    )
                ),
                dbc.Collapse(
                    dbc.ListGroup(level2_items, flush=True),
                    id={'type': 'level1-collapse', 'level1': level1},
                    is_open=False
                )
            ], className="mb-2")
        )
    
    return tree_elements

# Create the layout first
naics_layout = dbc.Container([
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
                generate_naics_tree(naics_data),
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

def filter_naics_data(data, active_filters, filter_mode="AND"):
    """Filter NAICS data based on active filters"""
    print(f"\nFiltering with mode: {filter_mode}")
    print(f"Active filters: {active_filters}")
    
    if not active_filters:
        return data
        
    filtered_data = {}
    for level1, level1_details in data.items():
        filtered_level2 = {}
        
        # Process level2 items
        for level2, level2_details in level1_details.get('children', {}).items():
            # Check level2 against filters
            level2_matches = []
            for filter_type, filter_value in active_filters.items():
                actual_value = level2_details.get(filter_type)
                
                if actual_value is None:
                    level2_matches.append(False)
                    continue
                
                if filter_type == 'TRL':
                    # Strip 'TRL ' from both values for comparison
                    actual_trl = actual_value.replace('TRL ', '')
                    filter_trl = filter_value.replace('TRL ', '')
                    level2_matches.append(actual_trl == filter_trl)
                else:
                    level2_matches.append(actual_value == filter_value)
            
            # Process level3 items
            filtered_level3 = {}
            for level3, level3_details in level2_details.get('children', {}).items():
                level3_matches = []
                for filter_type, filter_value in active_filters.items():
                    actual_value = level3_details.get(filter_type)
                    
                    if actual_value is None:
                        level3_matches.append(False)
                        continue
                    
                    if filter_type == 'TRL':
                        actual_trl = actual_value.replace('TRL ', '')
                        filter_trl = filter_value.replace('TRL ', '')
                        level3_matches.append(actual_trl == filter_trl)
                    else:
                        level3_matches.append(actual_value == filter_value)
                
                # Include level3 item if it matches the filter criteria
                if filter_mode == "AND":
                    if all(level3_matches):
                        filtered_level3[level3] = level3_details
                else:  # OR mode
                    if any(level3_matches):
                        filtered_level3[level3] = level3_details
            
            # Include level2 if either:
            # 1. It matches the filters directly
            # 2. It has matching children (level3 items)
            level2_should_include = False
            if filter_mode == "AND":
                if all(level2_matches):
                    level2_should_include = True
            else:  # OR mode
                if any(level2_matches):
                    level2_should_include = True
            
            if level2_should_include or filtered_level3:
                filtered_level2[level2] = level2_details.copy()
                if filtered_level3:
                    filtered_level2[level2]['children'] = filtered_level3
                else:
                    filtered_level2[level2]['children'] = {}
        
        # Include level1 if it has any matching children
        if filtered_level2:
            filtered_data[level1] = {
                'children': filtered_level2,
                'code': level1_details.get('code', ''),
                'description': level1_details.get('description', '')
            }
    
    print(f"Filtered data contains {len(filtered_data)} top-level categories")
    return filtered_data

def register_callbacks(app):
    @app.callback(
        Output('naics-details-panel', 'children'),
        [Input({'type': 'level2-item', 'level1': dash.ALL, 'level2': dash.ALL}, 'n_clicks'),
        Input({'type': 'level3-item', 'level1': dash.ALL, 'level2': dash.ALL, 'level3': dash.ALL}, 'n_clicks')],
        prevent_initial_call=True
    )
    def display_details(level2_clicks, level3_clicks):
        ctx = dash.callback_context
        if not ctx.triggered:
            return "Select a subcategory to view details"
        
        triggered_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
        level1 = triggered_id['level1']
        level2 = triggered_id['level2']
        
        if 'level3' in triggered_id:
            level3 = triggered_id['level3']
            details = naics_data[level1]['children'][level2]['children'][level3]
            title = f"{details.get('code', '')} - {level3}"
        else:
            details = naics_data[level1]['children'][level2]
            title = f"{details.get('code', '')} - {level2}"
        
        return html.Div([
            html.H3(title, className="mb-3"),
            html.Div([
                html.Strong("Description: "),
                html.Span(details.get('description', ''))
            ], className="mb-3"),
            html.Div([
                html.Strong("Function: "),
                dbc.Badge(
                    details.get('Function', ''),
                    color=FUNCTION_COLORS.get(details.get('Function', ''), 'secondary'),
                    className="ms-2"
                )
            ], className="mb-2"),
            html.Div([
                html.Strong("TRL: "),
                dbc.Badge(
                    details.get('TRL', ''),
                    color=TRL_COLORS.get(details.get('TRL', ''), 'secondary'),
                    className="ms-2"
                )
            ], className="mb-2"),
            html.Div([
                html.Strong("Supply Chain Position: "),
                dbc.Badge(
                    details.get('Supply Chain Position', ''),
                    color=SUPPLY_CHAIN_COLORS.get(details.get('Supply Chain Position', ''), 'secondary'),
                    className="ms-2"
                )
            ], className="mb-3"),
            html.Div([
                html.Strong("Potential Applications:"),
                html.Ul([
                    html.Li(app.strip()) 
                    for app in details.get('Potential Applications', '').split(', ')
                    if app.strip()
                ], className="mb-0")
            ], className="mb-3")
        ])

    @app.callback(
        Output({'type': 'level1-collapse', 'level1': dash.MATCH}, 'is_open'),
        Input({'type': 'level1-button', 'level1': dash.MATCH}, 'n_clicks'),
        State({'type': 'level1-collapse', 'level1': dash.MATCH}, 'is_open'),
        prevent_initial_call=True
    )
    def toggle_level1(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open

    @app.callback(
        [Output("filter-mode-and", "active"),
         Output("filter-mode-or", "active"),
         Output("filter-mode-and", "outline"),
         Output("filter-mode-or", "outline")],
        [Input("filter-mode-and", "n_clicks"),
         Input("filter-mode-or", "n_clicks")],
        [State("filter-mode-and", "active"),
         State("filter-mode-or", "active")],
        prevent_initial_call=True
    )
    def toggle_filter_mode(and_clicks, or_clicks, and_active, or_active):
        ctx = dash.callback_context
        if not ctx.triggered:
            return True, False, False, True  # Default to AND
            
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if button_id == "filter-mode-and":
            return True, False, False, True  # AND active, OR inactive
        elif button_id == "filter-mode-or":
            return False, True, True, False  # OR active, AND inactive
        
        return and_active, or_active, not and_active, not or_active

    @app.callback(
        [Output("naics-tree", "children"),
         Output("naics-active-filters", "children"),
         Output({'type': 'function-filter', 'value': dash.ALL}, 'n_clicks'),
         Output({'type': 'trl-filter', 'value': dash.ALL}, 'n_clicks'),
         Output({'type': 'supply-chain-filter', 'value': dash.ALL}, 'n_clicks')],
        [Input({'type': 'function-filter', 'value': dash.ALL}, 'n_clicks'),
         Input({'type': 'trl-filter', 'value': dash.ALL}, 'n_clicks'),
         Input({'type': 'supply-chain-filter', 'value': dash.ALL}, 'n_clicks'),
         Input("naics-clear-filters", "n_clicks")],
        [State({'type': 'function-filter', 'value': dash.ALL}, 'id'),
         State({'type': 'trl-filter', 'value': dash.ALL}, 'id'),
         State({'type': 'supply-chain-filter', 'value': dash.ALL}, 'id'),
         State("filter-mode-and", "active")],
        prevent_initial_call=True
    )
    def update_filters(func_clicks, trl_clicks, supply_clicks, clear_clicks,
                      func_ids, trl_ids, supply_ids, and_mode):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate

        # Initialize click counts
        func_clicks = [0 if n is None else n for n in (func_clicks or [])]
        trl_clicks = [0 if n is None else n for n in (trl_clicks or [])]
        supply_clicks = [0 if n is None else n for n in (supply_clicks or [])]

        # Handle clear filters
        if ctx.triggered[0]['prop_id'] == 'naics-clear-filters.n_clicks':
            return (
                generate_naics_tree(naics_data),
                "No active filters",
                [0] * len(func_ids),
                [0] * len(trl_ids),
                [0] * len(supply_ids)
            )

        # Build active filters
        active_filters = {}
        
        # Process function filters
        for clicks, id_obj in zip(func_clicks, func_ids):
            if clicks and clicks % 2 == 1:  # Button is active
                active_filters['Function'] = id_obj['value']
        
        # Process TRL filters
        for clicks, id_obj in zip(trl_clicks, trl_ids):
            if clicks and clicks % 2 == 1:  # Button is active
                active_filters['TRL'] = f"TRL {id_obj['value']}"
        
        # Process supply chain filters
        for clicks, id_obj in zip(supply_clicks, supply_ids):
            if clicks and clicks % 2 == 1:  # Button is active
                active_filters['Supply Chain Position'] = id_obj['value']

        # If no filters are active, return unfiltered data
        if not active_filters:
            return (
                generate_naics_tree(naics_data),
                "No active filters",
                func_clicks,
                trl_clicks,
                supply_clicks
            )

        # Apply filters
        filtered_data = filter_naics_data(naics_data, active_filters, 
                                        filter_mode="AND" if and_mode else "OR")

        # Create filter badges
        filter_badges = []
        for key, value in active_filters.items():
            if key == 'Function':
                color = FUNCTION_COLORS.get(value, 'secondary')
            elif key == 'TRL':
                color = TRL_COLORS.get(value.replace('TRL ', ''), 'secondary')
            else:  # Supply Chain Position
                color = SUPPLY_CHAIN_COLORS.get(value, 'secondary')
            
            filter_badges.append(
                dbc.Badge(
                    f"{key}: {value}",
                    color=color,
                    className="me-1 mb-1"
                )
            )

        return (
            generate_naics_tree(filtered_data),
            html.Div(filter_badges),
            func_clicks,
            trl_clicks,
            supply_clicks
        )