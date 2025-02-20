import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from tax_tree import layout as tax_layout, register_callbacks as register_tax_callbacks
from naics_tree import naics_layout, register_callbacks as register_naics_callbacks
import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the main app
try:
    app = dash.Dash(
        __name__, 
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=True
    )
    logger.info("App initialized successfully")
except Exception as e:
    logger.error(f"Error initializing app: {str(e)}")
    raise

# Create the server variable for gunicorn
server = app.server

try:
    # Create the navigation bar
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Technology Taxonomy", href="/tech", active="exact")),
            dbc.NavItem(dbc.NavLink("NAICS Taxonomy", href="/naics", active="exact")),
        ],
        brand="Taxonomy Navigator",
        brand_href="/",
        color="primary",
        dark=True,
    )

    # Main app layout
    app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        navbar,
        html.Div(id='page-content')
    ])

    logger.info("Layout created successfully")
except Exception as e:
    logger.error(f"Error creating layout: {str(e)}")
    raise

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    try:
        if pathname == '/tech':
            return tax_layout
        elif pathname == '/naics':
            return naics_layout
        else:
            # Home page
            return dbc.Container([
                html.H1("Welcome to Taxonomy Navigator", className="text-center my-4"),
                html.P("Select a taxonomy view from the navigation bar above.", className="text-center")
            ])
    except Exception as e:
        logger.error(f"Error in display_page: {str(e)}")
        return html.Div(f"An error occurred: {str(e)}")

try:
    # Register callbacks
    register_tax_callbacks(app)
    register_naics_callbacks(app)
    logger.info("Callbacks registered successfully")
except Exception as e:
    logger.error(f"Error registering callbacks: {str(e)}")
    raise

if __name__ == '__main__':
    try:
        # Get port from environment variable (for Render)
        port = int(os.environ.get("PORT", 8080))
        logger.info(f"Starting server on port {port}")
        app.run_server(debug=False, host='0.0.0.0', port=port)
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        raise 