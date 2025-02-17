import json
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import pandas as pd

# Load JSON taxonomy data
with open("hierarchical_tax_with_descriptions.json", 'r') as f:
    taxonomy_data = json.load(f)

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Color mappings for classifications
CLASSIFICATION_COLORS = {
    'CF': 'primary',   # Core Foundational - Blue
    'E': 'success',    # Enabling - Green
    'A': 'warning',    # Application - Yellow
    'EU': 'danger'     # End Use - Red
}

# Color mappings for TRL levels
TRL_COLORS = {
    'TRL 1-3': 'danger',     # Early stage - Red
    'TRL 4-6': 'warning',    # Mid stage - Yellow
    'TRL 7-8': 'info',       # Late stage - Light Blue
    'TRL 9': 'success'       # Deployed - Green
}

def generate_tree(taxonomy):
    """Generate the navigation tree from taxonomy data"""
    tree_elements = []
    
    for category, details in taxonomy.items():
        # Create list items for each subcategory
        subcategory_items = []
        for subcategory, subdetails in details.get('Subcategories', {}).items():
            # Create badges for classification and TRL
            classification = subdetails['Classification']
            trl = subdetails['TRL-Based Classification']
            
            subcategory_items.append(
                dbc.ListGroupItem([
                    html.Div([
                        html.Span(subcategory, className="me-2"),
                        dbc.Badge(
                            classification,
                            color=CLASSIFICATION_COLORS.get(classification, 'secondary'),
                            className="me-1"
                        ),
                        dbc.Badge(
                            trl,
                            color=TRL_COLORS.get(trl, 'secondary'),
                            className="me-1"
                        )
                    ], style={'display': 'flex', 'alignItems': 'center'})
                ],
                id={'type': 'subcategory-item', 'category': category, 'subcategory': subcategory},
                action=True,
                className="subcategory-item"
                )
            )
        
        # Create category card with collapsible subcategories
        tree_elements.append(
            dbc.Card([
                dbc.CardHeader(
                    dbc.Button(
                        category,
                        id={'type': 'category-button', 'category': category},
                        color="link",
                        className="text-left w-100"
                    )
                ),
                dbc.Collapse(
                    dbc.ListGroup(subcategory_items, flush=True),
                    id={'type': 'category-collapse', 'category': category},
                    is_open=False
                )
            ], className="mb-2")
        )
    
    return tree_elements

# Add a function to filter with multiple criteria
def filter_subcategories(taxonomy_data, active_filters=None):
    if not active_filters or len(active_filters) == 0:
        return taxonomy_data
    
    filtered_data = {}
    for category, cat_data in taxonomy_data.items():
        matching_subcats = {}
        for subcat_name, subcat_data in cat_data['Subcategories'].items():
            # Check if subcategory matches ALL active filters
            matches_all = all(
                subcat_data[filter_type] == filter_value 
                for filter_type, filter_value in active_filters.items()
            )
            if matches_all:
                matching_subcats[subcat_name] = subcat_data
        
        if matching_subcats:
            filtered_data[category] = {
                'Subcategories': matching_subcats,
                'Description': cat_data['Description']
            }
    
    return filtered_data

# App Layout
app.layout = dbc.Container([
    html.H1("Taxonomy Navigator", className="my-4"),
    # Enhanced legend with clickable badges
    dbc.Card([
        dbc.CardBody([
            html.H5("Legend (Click to Filter)", className="card-title"),
            dbc.Row([
                dbc.Col([
                    html.H6("Classification Types:", className="mb-2"),
                    dbc.Table([
                        html.Tbody([
                            html.Tr([
                                html.Td(dbc.Badge("CF", color="primary", className="me-1", id={'type': 'filter-badge', 'filter_type': 'Classification', 'value': 'CF'}, style={'cursor': 'pointer'})),
                                html.Td("Core Foundational"),
                                html.Td(dbc.Badge("E", color="success", className="me-1", id={'type': 'filter-badge', 'filter_type': 'Classification', 'value': 'E'}, style={'cursor': 'pointer'})),
                                html.Td("Enabling")
                            ]),
                            html.Tr([
                                html.Td(dbc.Badge("A", color="warning", className="me-1", id={'type': 'filter-badge', 'filter_type': 'Classification', 'value': 'A'}, style={'cursor': 'pointer'})),
                                html.Td("Application"),
                                html.Td(dbc.Badge("EU", color="danger", className="me-1", id={'type': 'filter-badge', 'filter_type': 'Classification', 'value': 'EU'}, style={'cursor': 'pointer'})),
                                html.Td("End Use")
                            ])
                        ])
                    ], bordered=False, size="sm")
                ], width=6),
                dbc.Col([
                    html.H6("TRL Levels:", className="mb-2"),
                    dbc.Table([
                        html.Tbody([
                            html.Tr([
                                html.Td(dbc.Badge("TRL 1-3", color="danger", className="me-1", id={'type': 'filter-badge', 'filter_type': 'TRL-Based Classification', 'value': 'TRL 1-3'}, style={'cursor': 'pointer'})),
                                html.Td("Early Stage"),
                                html.Td(dbc.Badge("TRL 4-6", color="warning", className="me-1", id={'type': 'filter-badge', 'filter_type': 'TRL-Based Classification', 'value': 'TRL 4-6'}, style={'cursor': 'pointer'})),
                                html.Td("Mid Stage")
                            ]),
                            html.Tr([
                                html.Td(dbc.Badge("TRL 7-8", color="info", className="me-1", id={'type': 'filter-badge', 'filter_type': 'TRL-Based Classification', 'value': 'TRL 7-8'}, style={'cursor': 'pointer'})),
                                html.Td("Late Stage"),
                                html.Td(dbc.Badge("TRL 9", color="success", className="me-1", id={'type': 'filter-badge', 'filter_type': 'TRL-Based Classification', 'value': 'TRL 9'}, style={'cursor': 'pointer'})),
                                html.Td("Deployed")
                            ])
                        ])
                    ], bordered=False, size="sm")
                ], width=6)
            ]),
            # Active Filters Display
            html.Div([
                html.H6("Active Filters:", className="mt-3 mb-2"),
                html.Div(id="active-filters-display", className="mb-2"),
                dbc.Button("Clear All Filters", id="clear-filters", color="secondary", size="sm", className="mt-2")
            ], className="text-center")
        ])
    ], className="mb-4"),
    dbc.Row([
        # Left column - Navigation Tree
        dbc.Col([
            html.Div(
                generate_tree(taxonomy_data),
                id="taxonomy-tree",
                className="border rounded p-3"
            )
        ], width=4),
        
        # Right column - Details Panel
        dbc.Col([
            html.Div(
                "Select a subcategory to view details",
                id="details-panel",
                className="border rounded p-3"
            )
        ], width=8)
    ])
], fluid=True)

# Callback for category collapse
@app.callback(
    Output({'type': 'category-collapse', 'category': dash.MATCH}, 'is_open'),
    Input({'type': 'category-button', 'category': dash.MATCH}, 'n_clicks'),
    State({'type': 'category-collapse', 'category': dash.MATCH}, 'is_open'),
    prevent_initial_call=True
)
def toggle_collapse(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

# Callback for subcategory details
@app.callback(
    Output('details-panel', 'children'),
    Input({'type': 'subcategory-item', 'category': dash.ALL, 'subcategory': dash.ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def update_details(n_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return "Select a subcategory to view details"
    
    # Get the triggered component's ID
    triggered_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
    category = triggered_id['category']
    subcategory = triggered_id['subcategory']
    
    # Get details from taxonomy data
    details = taxonomy_data[category]['Subcategories'][subcategory]
    
    # Return formatted details
    return html.Div([
        html.H3(subcategory, className="mb-3"),
        html.Div([
            html.Strong("Classification: "),
            html.Span(details['Classification'])
        ], className="mb-2"),
        html.Div([
            html.Strong("Supply Chain Classification: "),
            html.Span(details['Supply Chain Classification'])
        ], className="mb-2"),
        html.Div([
            html.Strong("TRL-Based Classification: "),
            html.Span(details['TRL-Based Classification'])
        ], className="mb-2"),
        html.Div([
            html.Strong("Description: "),
            html.Span(details['Description'])
        ], className="mt-3")
    ])

# Add callback for filter badges with state to maintain multiple filters
@app.callback(
    [Output("taxonomy-tree", "children"),
     Output("active-filters-display", "children"),
     Output({'type': 'filter-badge', 'filter_type': dash.ALL, 'value': dash.ALL}, 'n_clicks')],  # Reset clicks
    [Input({'type': 'filter-badge', 'filter_type': dash.ALL, 'value': dash.ALL}, 'n_clicks'),
     Input("clear-filters", "n_clicks")],
    [State({'type': 'filter-badge', 'filter_type': dash.ALL, 'value': dash.ALL}, 'id')],
    prevent_initial_call=True
)
def update_tree(badge_clicks, clear_clicks, badge_ids):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
        
    trigger_id = ctx.triggered[0]['prop_id']
    
    # Clear all filters if the clear button was clicked
    if trigger_id == 'clear-filters.n_clicks':
        # Return empty tree and reset all clicks to None
        return generate_tree(taxonomy_data), "No active filters", [None] * len(badge_clicks)
    
    # Initialize active filters
    active_filters = {}
    
    # Find which badges have been clicked
    active_badges = [
        badge_id for click, badge_id in zip(badge_clicks, badge_ids)
        if click is not None and click % 2 == 1  # Only odd number of clicks means filter is active
    ]
    
    # Update active filters
    for badge_id in active_badges:
        active_filters[badge_id['filter_type']] = badge_id['value']
    
    # Create active filters display
    if active_filters:
        filter_badges = [
            dbc.Badge(
                f"{filter_type}: {value}",
                color="primary",
                className="me-1 mb-1"
            )
            for filter_type, value in active_filters.items()
        ]
        active_filters_display = html.Div(filter_badges)
    else:
        active_filters_display = "No active filters"
    
    # Filter the data and regenerate the tree
    filtered_data = filter_subcategories(taxonomy_data, active_filters)
    return generate_tree(filtered_data), active_filters_display, badge_clicks

if __name__ == '__main__':
    app.run_server(debug=True)
