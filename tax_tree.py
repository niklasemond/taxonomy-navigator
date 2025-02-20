import json
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import pandas as pd

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

# Add Supply Chain Classification colors
SUPPLY_CHAIN_COLORS = {
    'RMC': 'primary',   # Raw Materials & Components - Blue
    'MF': 'success',    # Manufacturing Facilities - Green
    'CET': 'warning',   # Computing, Electronics & Telecommunications - Yellow
    'ASI': 'info',      # Applications, Systems & Integration - Light Blue
    'EUP': 'danger'     # End User Products - Red
}

# Add these constants near the top of the file, after the color mappings
CLASSIFICATION_DESCRIPTIONS = {
    'CF': """Core Foundational (CF): These technologies are the fundamental building blocks necessary for developing a broad range of applications. They often represent breakthroughs in scientific knowledge or novel engineering principles that serve as a basis for future advancements. CF technologies tend to have long-term impact and widespread applicability across multiple industries and domains.""",
    
    'E': """Enabling (E): These are key technologies that facilitate and accelerate the development of practical applications. They provide critical functionalities or infrastructure that allow applied and end-use solutions to function effectively. Enabling technologies often serve as intermediate components, bridging core foundational research and real-world applications.""",
    
    'A': """Application (A): These technologies represent integrated and developed solutions aimed at specific use cases or industry applications. Applied technologies are often built upon foundational and enabling technologies, bringing them into practical implementation in fields such as aerospace, cybersecurity, healthcare, energy, and defense""",
    
    'EU': """End Use (EU): These are finalized, market-ready solutions that are actively deployed and utilized across industries, defense, and society. End-use technologies are at the highest level of maturity, providing direct benefits to businesses, government agencies, and consumers. They often involve commercially available products, deployed defense systems, or large-scale industrial applications."""
}

TRL_DESCRIPTIONS = {
    'TRL 1-3': """Early Stage Research (TRL 1-3):
    • TRL 1: Basic principles observed and reported
    • TRL 2: Technology concept and/or application formulated
    • TRL 3: Analytical and experimental critical function proof-of-concept
    
    This stage represents fundamental research and early development, where basic principles are being discovered and initial concepts are being formulated.""",
    
    'TRL 4-6': """Technology Development & Demonstration (TRL 4-6):
    • TRL 4: Component and/or system validation in laboratory environment
    • TRL 5: Component and/or system validation in relevant environment
    • TRL 6: System/subsystem model or prototype demonstration in relevant environment
    
    This stage represents the development and testing of prototypes and demonstration of technology components in increasingly realistic environments.""",
    
    'TRL 7-8': """System Development & Qualification (TRL 7-8):
    • TRL 7: System prototype demonstration in operational environment
    • TRL 8: Actual system completed and qualified through test and demonstration
    
    This stage represents near-final technology development, where systems are being tested and qualified in operational environments.""",
    
    'TRL 9': """Operational Deployment (TRL 9):
    • TRL 9: Actual system proven through successful mission operations
    
    This represents fully mature technology that has been proven through successful operations in its intended environment."""
}

# Add Supply Chain Classification descriptions
SUPPLY_CHAIN_DESCRIPTIONS = {
    'RMC': "Raw Materials & Components: Basic materials and components manufacturing",
    'MF': "Manufacturing Facilities: Production and assembly facilities",
    'CET': "Computing, Electronics & Telecommunications: Digital and electronic systems",
    'ASI': "Applications, Systems & Integration: System integration and applications",
    'EUP': "End User Products: Final products for end users"
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
            supply_chain = subdetails['Supply Chain Classification']
            
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
                        ),
                        dbc.Badge(
                            supply_chain,
                            color=SUPPLY_CHAIN_COLORS.get(supply_chain, 'secondary'),
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

# Define the process_taxonomy_data function BEFORE loading the data
def process_taxonomy_data(data):
    """Convert flat list structure into hierarchical dictionary"""
    organized_data = {}
    
    print(f"Processing {len(data)} items")
    
    for item in data:
        category = item['Category']
        if not category:
            continue
            
        if category not in organized_data:
            organized_data[category] = {
                'Subcategories': {}
            }
        
        subcategory = item['Subcategory']
        if subcategory:
            organized_data[category]['Subcategories'][subcategory] = {
                'Classification': 'CF',
                'Supply Chain Classification': 'RMC',
                'TRL-Based Classification': 'TRL 1-3',
                'Description': item['NAICS Description'],
                'NAICS Code': item['NAICS Code'],
                'Potential Applications': item['Potential Applications']
            }
    
    return organized_data

# THEN load and process the data
with open('hierarchical_tax_with_descriptions.json', 'r') as file:
    raw_data = json.load(file)
    taxonomy_data = raw_data  # The data is already in the correct format

# Initialize Dash app without authentication
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# App Layout
layout = dbc.Container([
    html.H1("Technology Taxonomy Navigator", className="my-4"),
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

def register_callbacks(app):
    @app.callback(
        Output({'type': 'category-collapse', 'category': dash.MATCH}, 'is_open'),
        Input({'type': 'category-button', 'category': dash.MATCH}, 'n_clicks'),
        State({'type': 'category-collapse', 'category': dash.MATCH}, 'is_open'),
        prevent_initial_call=True
    )
    def toggle_category(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open

    @app.callback(
        [Output("taxonomy-tree", "children"),
         Output("active-filters-display", "children")],
        [Input({'type': 'filter-badge', 'filter_type': dash.ALL, 'value': dash.ALL}, 'n_clicks'),
         Input("clear-filters", "n_clicks")],
        [State({'type': 'filter-badge', 'filter_type': dash.ALL, 'value': dash.ALL}, 'id')],
        prevent_initial_call=True
    )
    def update_filters(badge_clicks, clear_clicks, badge_ids):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
            
        trigger_id = ctx.triggered[0]['prop_id']
        
        if trigger_id == 'clear-filters.n_clicks':
            return generate_tree(taxonomy_data), "No active filters"
        
        active_filters = {}
        for i, (clicks, badge_id) in enumerate(zip(badge_clicks, badge_ids)):
            if clicks and clicks % 2 == 1:  # Toggle on odd number of clicks
                active_filters[badge_id['filter_type']] = badge_id['value']
        
        if not active_filters:
            return generate_tree(taxonomy_data), "No active filters"
        
        filtered_data = filter_subcategories(taxonomy_data, active_filters)
        
        # Create active filters display
        filter_badges = [
            dbc.Badge(
                f"{filter_type}: {value}",
                color="primary",
                className="me-1 mb-1"
            )
            for filter_type, value in active_filters.items()
        ]
        
        return generate_tree(filtered_data), html.Div(filter_badges)

    @app.callback(
        Output('details-panel', 'children'),
        Input({'type': 'subcategory-item', 'category': dash.ALL, 'subcategory': dash.ALL}, 'n_clicks'),
        prevent_initial_call=True
    )
    def display_details(n_clicks):
        ctx = dash.callback_context
        if not ctx.triggered:
            return "Select a subcategory to view details"
        
        button_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
        category = button_id['category']
        subcategory = button_id['subcategory']
        
        details = taxonomy_data[category]['Subcategories'][subcategory]
        
        return html.Div([
            html.H3(subcategory),
            html.P(f"Classification: {details['Classification']}"),
            html.P(f"Supply Chain Classification: {details['Supply Chain Classification']}"),
            html.P(f"TRL Classification: {details['TRL-Based Classification']}"),
            html.P(f"Description: {details['Description']}"),
            html.P(f"NAICS Code: {details['NAICS Code']}"),
            html.P(f"Potential Applications: {details['Potential Applications']}")
        ])

# Only run this if the file is run directly
if __name__ == '__main__':
    app.layout = layout
    app.run_server(debug=True)

# At the very end of tax_tree.py, add this line:
__all__ = ['app', 'layout', 'register_callbacks']
