import dash
from dash import html
import dash_bootstrap_components as dbc
from naics_tree import naics_layout, register_callbacks
from database import load_taxonomy_data, load_company_data
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Load data
load_taxonomy_data()
load_company_data()

# Set the layout
app.layout = naics_layout

# Register callbacks
register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)