import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from tax_tree import layout as tax_layout, register_callbacks as register_tax_callbacks
from naics_tree import naics_layout, register_callbacks as register_naics_callbacks
import os
import sys
import logging
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
import secrets
from secret_key import generate_secret_key
from auth import User, users, init_login_manager
from werkzeug.security import check_password_hash
from database import init_database, import_json_to_db, import_companies_to_db

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock user database - In production, use a real database
VALID_USERNAME_PASSWORD_PAIRS = {
    'admin': 'admin123'
}

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, username):
        self.id = username

# Initialize database and import data at startup
try:
    # Initialize database first
    init_database()
    logger.info("Database initialized successfully")
    
    # Import taxonomy data
    import_json_to_db('data/taxonomy.json')
    logger.info("Taxonomy data imported successfully")
    
    # Import company data
    import_companies_to_db('top_global_firms.json')
    logger.info("Company data imported successfully")
except Exception as e:
    logger.error(f"Error during initialization: {e}")
    # Continue execution even if import fails
    pass

# Initialize the main app
try:
    app = dash.Dash(
        __name__, 
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=True
    )
    server = app.server  # Flask server
    
    # Set up secret key with fallback
    if os.environ.get('FLASK_SECRET_KEY'):
        server.secret_key = os.environ.get('FLASK_SECRET_KEY')
    else:
        # Generate a new secret key if none exists
        server.secret_key = generate_secret_key()
        logger.warning("Using generated secret key - for production, set FLASK_SECRET_KEY environment variable")
    
    # Setup the LoginManager
    login_manager = init_login_manager(server)
    
    @login_manager.user_loader
    def load_user(username):
        if username in VALID_USERNAME_PASSWORD_PAIRS:
            return User(username)
        return None
    
    logger.info("App initialized successfully")
except Exception as e:
    logger.error(f"Error initializing app: {str(e)}")
    raise

# Create login page layout
login_layout = dbc.Container([
    html.H1("Login", className="text-center my-4"),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Form([
                        dbc.Input(
                            id="username-input",
                            type="text",
                            placeholder="Username",
                            className="mb-3"
                        ),
                        dbc.Input(
                            id="password-input",
                            type="password",
                            placeholder="Password",
                            className="mb-3"
                        ),
                        dbc.Button(
                            "Login",
                            id="login-button",
                            color="primary",
                            n_clicks=0,
                            className="w-100"
                        ),
                        html.Div(id="login-error")
                    ])
                ])
            ])
        ], width=6)
    ], justify="center")
])

# Remove the static navbar definition and replace with a function
def create_navbar():
    return dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Technology Taxonomy", href="/tech", active="exact")),
            dbc.NavItem(dbc.NavLink("NAICS Taxonomy", href="/naics", active="exact")),
            dbc.NavItem(
                dbc.Button("Logout", id="logout-button", color="light", className="ms-2")
            ) if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated else None
        ],
        brand="Taxonomy Navigator",
        brand_href="/",
        color="primary",
        dark=True,
    )

# Main app layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    html.Div(id='navbar-container'),
    html.Div(id='page-content')
])

# Callbacks
@app.callback(
    [Output('url', 'pathname'),
     Output('login-error', 'children')],
    [Input('login-button', 'n_clicks')],
    [State('username-input', 'value'),
     State('password-input', 'value')],
    prevent_initial_call=True
)
def login_callback(n_clicks, username, password):
    print(f"Login attempt - clicks: {n_clicks}, username: {username}")
    
    if not n_clicks or not username or not password:
        return dash.no_update, dash.no_update
    
    if username in users and check_password_hash(users[username], password):
        print("Login successful")
        login_user(User(username))
        return '/tech', ''
    
    print("Login failed")
    return dash.no_update, html.Div('Invalid username or password', style={'color': 'red'})

@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    Input('logout-button', 'n_clicks'),
    prevent_initial_call=True
)
def logout_callback(n_clicks):
    if n_clicks:
        logout_user()
        return '/login'
    return dash.no_update

# Update the display_page callback to use the function
@app.callback(
    [Output('navbar-container', 'children'),
     Output('page-content', 'children')],
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/login' or not hasattr(current_user, 'is_authenticated') or not current_user.is_authenticated:
        return None, login_layout
    
    if pathname == '/tech':
        return create_navbar(), tax_layout
    elif pathname == '/naics':
        return create_navbar(), naics_layout
    else:
        return create_navbar(), dbc.Container([
            html.H1("Welcome to Taxonomy Navigator", className="text-center my-4"),
            html.P("Select a taxonomy view from the navigation bar above.", className="text-center")
        ])

# Register callbacks
register_tax_callbacks(app)
register_naics_callbacks(app)
logger.info("Callbacks registered successfully")

# Update server error handling
@server.errorhandler(404)
def not_found(e):
    return html.Div([
        dbc.Container([
            html.H1("404 - Page Not Found", className="text-center my-4"),
            html.P("The page you're looking for doesn't exist.", className="text-center"),
            dbc.Button("Go Home", href="/", color="primary", className="d-block mx-auto mt-3")
        ])
    ])

if __name__ == '__main__':
    try:
        # Get port from environment variable (for Render)
        port = int(os.environ.get("PORT", 10000))  # Changed default to 10000
        logger.info(f"Starting server on port {port}")
        app.run_server(
            debug=False,
            host='0.0.0.0',
            port=port
        )
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        raise