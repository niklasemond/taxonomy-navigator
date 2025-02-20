import json
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

def process_naics_data(data):
    """Convert flat list structure into hierarchical dictionary"""
    organized_data = {}
    
    for item in data:
        category = item['Category']
        subcategory = item['Subcategory']
        sub_subcategory = item['Potential Sub-Subcategory']
        naics_code = item['NAICS Code']
        naics_desc = item['NAICS Description']
        sub_naics_code = item['Sub-Subcategory NAICS Code']
        sub_naics_desc = item['Sub-Subcategory NAICS Description']
        potential_apps = item['Potential Applications']
        
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
                'Potential Applications': potential_apps
            }
        
        # Add sub-subcategory if it exists and isn't "N/A"
        if sub_subcategory and sub_subcategory != "N/A":
            organized_data[category]['children'][subcategory]['children'][sub_subcategory] = {
                'code': sub_naics_code,
                'description': sub_naics_desc,
                'Potential Applications': potential_apps  # Include applications at sub-subcategory level
            }
    
    return organized_data

# Load and process NAICS JSON data
with open("tax_5-0.json", 'r') as f:
    raw_data = json.load(f)
    naics_data = process_naics_data(raw_data)

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
                                html.Small(level3_details.get('description', ''), className="text-muted")
                            ], style={'display': 'flex', 'alignItems': 'center', 'flexWrap': 'wrap'})
                        ],
                        id={'type': 'level3-item', 'level1': level1, 'level2': level2, 'level3': level3},
                        action=True,
                        className="ms-4"  # Add indent for level 3
                        )
                    )
            
            # Create level 2 items (subcategories)
            level2_items.append(
                html.Div([
                    dbc.ListGroupItem([
                        html.Div([
                            html.Span(f"{level2_details.get('code', '')} - {level2}", className="me-2"),
                            html.Small(level2_details.get('description', ''), className="text-muted")
                        ], style={'display': 'flex', 'alignItems': 'center', 'flexWrap': 'wrap'})
                    ],
                    id={'type': 'level2-item', 'level1': level1, 'level2': level2},
                    action=True
                    ),
                    # Add level 3 items if they exist
                    *level3_items
                ])
            )
        
        # Create level 1 card with collapsible level 2 and 3 items
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
    dbc.Row([
        # Left column - Navigation Tree
        dbc.Col([
            html.Div(
                generate_naics_tree(naics_data),
                id="naics-tree",
                className="border rounded p-3"
            )
        ], width=4),
        
        # Right column - Details Panel
        dbc.Col([
            html.Div(
                "Select a subcategory to view details",
                id="naics-details-panel",  # This ID needs to exist in the layout
                className="border rounded p-3"
            )
        ], width=8)
    ])
], fluid=True)

# Then define the callback registration function
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
        
        # Create details panel content
        details_content = [
            html.H3(title, className="mb-3"),
            html.Div([
                html.Strong("Description: "),
                html.Span(details.get('description', ''))
            ], className="mb-3"),
        ]
        
        # Add Potential Applications if they exist
        if 'Potential Applications' in details and details['Potential Applications'] != "N/A":
            # Split applications into a list if they're comma-separated
            applications = details['Potential Applications'].split(', ')
            details_content.extend([
                html.Div([
                    html.Strong("Potential Applications:"),
                    html.Ul([
                        html.Li(app.strip()) for app in applications
                    ], className="mb-0")
                ], className="mb-3")
            ])
        
        return html.Div(details_content)

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