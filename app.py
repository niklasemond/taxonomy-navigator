import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from tax_tree import layout as tax_layout, register_callbacks as register_tax_callbacks
from naics_tree import naics_layout, register_callbacks as register_naics_callbacks
import os
import sys
import logging
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

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
                        id="username",
                        placeholder="Username",
                        className="mb-3"
                    ),
                    dbc.Input(
                        type="password",
                        id="password",
                        placeholder="Password",
                        className="mb-3"
                    ),
                    dbc.Button(
                        "Login",
                        id="login-button",
                        color="primary",
                        className="w-100"
                    ),
                    html.Div(id="login-error", className="text-danger mt-3")
                ])
            ])
        ], className="shadow-sm")
    ], style={'max-width': '400px', 'margin': '100px auto'})
])

# Update app layout to include login state
try:
    app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        dcc.Store(id='login-status', storage_type='session'),
        html.Div(id='page-layout')
    ])
    logger.info("Layout created successfully")
except Exception as e:
    logger.error(f"Error creating layout: {str(e)}")
    raise

# Callbacks for login system
@app.callback(
    [Output('login-status', 'data'),
     Output('login-error', 'children')],
    [Input('login-button', 'n_clicks')],
    [State('username', 'value'),
     State('password', 'value')],
    prevent_initial_call=True
)
def login_callback(n_clicks, username, password):
    if not n_clicks:
        raise dash.exceptions.PreventUpdate
        
    if username in VALID_USERNAME_PASSWORD_PAIRS and VALID_USERNAME_PASSWORD_PAIRS[username] == password:
        login_user(User(username))
        return True, ''
    return False, 'Invalid username or password'

# Update page routing to include authentication
@app.callback(
    Output('page-layout', 'children'),
    [Input('url', 'pathname'),
     Input('login-status', 'data')]
)
def display_page(pathname, logged_in):
    try:
        if not logged_in and pathname != '/login':
            return login_layout
            
        if pathname == '/login':
            if logged_in:
                return dcc.Location(pathname='/', id='redirect-home')
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
        return html.Div(f"An error occurred: {str(e)}")

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