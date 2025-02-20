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
    login_manager = LoginManager()
    login_manager.init_app(server)
    login_manager.login_view = '/login'
    
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
    html.Div([
        html.H1("Login", className="text-center mb-4"),
        dbc.Card([
            dbc.CardBody([
                dbc.Form([
                    dbc.Input(
                        type="text",
                        id="username-input",
                        placeholder="Username",
                        className="mb-3"
                    ),
                    dbc.Input(
                        type="password",
                        id="password-input",
                        placeholder="Password",
                        className="mb-3"
                    ),
                    dbc.Button(
                        "Login",
                        id="login-button",
                        color="primary",
                        className="w-100"
                    ),
                    html.Div(id="login-error-message", className="text-danger mt-3")
                ])
            ])
        ], className="shadow-sm")
    ], style={'max-width': '400px', 'margin': '100px auto'})
])

# Add 404 page layout
not_found_layout = dbc.Container([
    html.H1("404 - Page Not Found", className="text-center my-4"),
    html.P("The page you're looking for doesn't exist.", className="text-center"),
    dbc.Button("Go Home", href="/", color="primary", className="d-block mx-auto mt-3")
])

# Update app layout to handle initial state
try:
    app.layout = html.Div([
        dcc.Location(id='url', refresh=True),
        dcc.Store(id='login-status', storage_type='session', data=False),  # Initialize as False
        html.Div(id='page-content', children=login_layout),  # Set initial content
        html.Div(id='login-error-div'),
        # Add loading component
        dcc.Loading(
            id="loading",
            type="default",
            children=html.Div(id="loading-output")
        )
    ])
    logger.info("Layout created successfully")
except Exception as e:
    logger.error(f"Error creating layout: {str(e)}")
    raise

# Update the display_page callback to handle initial state
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname'),
     Input('login-status', 'data')],
    prevent_initial_call=False  # Allow initial call
)
def display_page(pathname, logged_in):
    try:
        logger.info(f"Page request - Path: {pathname}, Logged in: {logged_in}")
        
        # Handle initial state
        if pathname is None:
            pathname = '/'
            
        if logged_in is None:
            logged_in = False
        
        if not logged_in:
            logger.info("User not logged in, showing login page")
            return login_layout
            
        # Navigation bar for authenticated users
        navbar = dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Technology Taxonomy", href="/tech", active="exact")),
                dbc.NavItem(dbc.NavLink("NAICS Taxonomy", href="/naics", active="exact")),
                dbc.NavItem(dbc.Button("Logout", id="logout-button", color="light", className="ms-3")),
            ],
            brand="Taxonomy Navigator",
            brand_href="/",
            color="primary",
            dark=True,
        )
        
        # Content based on pathname
        if pathname == '/tech':
            content = tax_layout
        elif pathname == '/naics':
            content = naics_layout
        else:
            content = dbc.Container([
                html.H1("Welcome to Taxonomy Navigator", className="text-center my-4"),
                html.P("Select a taxonomy view from the navigation bar above.", className="text-center")
            ])
            
        return html.Div([navbar, content])
        
    except Exception as e:
        logger.error(f"Error in display_page: {str(e)}")
        return dbc.Alert(
            f"An error occurred: {str(e)}",
            color="danger",
            className="m-3"
        )

# Logout callback
@app.callback(
    [Output('login-status', 'clear_data'),
     Output('url', 'pathname')],
    Input('logout-button', 'n_clicks'),
    prevent_initial_call=True
)
def logout_callback(n_clicks):
    if n_clicks:
        logout_user()
        return True, '/login'
    raise dash.exceptions.PreventUpdate

# Add error handling to login callback
@app.callback(
    [Output('login-status', 'data'),
     Output('login-error-message', 'children'),
     Output('url', 'pathname'),
     Output('loading-output', 'children')],  # Add loading output
    [Input('login-button', 'n_clicks'),
     Input('username-input', 'n_submit'),
     Input('password-input', 'n_submit')],
    [State('username-input', 'value'),
     State('password-input', 'value')],
    prevent_initial_call=True
)
def login_callback(n_clicks, username_submit, password_submit, username, password):
    try:
        triggered = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
        if not any([n_clicks, username_submit, password_submit]):
            raise dash.exceptions.PreventUpdate
        
        logger.info(f"Login attempt for user: {username}")
        
        if not username or not password:
            logger.warning("Login attempt with empty credentials")
            return False, 'Please enter both username and password', '/login', ''
            
        if username in VALID_USERNAME_PASSWORD_PAIRS and VALID_USERNAME_PASSWORD_PAIRS[username] == password:
            try:
                login_user(User(username))
                logger.info(f"Successful login for user: {username}")
                return True, '', '/', ''
            except Exception as e:
                logger.error(f"Error during login: {str(e)}")
                return False, f'Login error: {str(e)}', '/login', ''
        
        logger.warning(f"Failed login attempt for user: {username}")
        return False, 'Invalid username or password', '/login', ''
        
    except Exception as e:
        logger.error(f"Error in login callback: {str(e)}")
        return False, f'An error occurred: {str(e)}', '/login', ''

try:
    # Register callbacks
    register_tax_callbacks(app)
    register_naics_callbacks(app)
    logger.info("Callbacks registered successfully")
except Exception as e:
    logger.error(f"Error registering callbacks: {str(e)}")
    raise

# Update server error handling
@server.errorhandler(404)
def not_found(e):
    return html.Div([
        not_found_layout
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