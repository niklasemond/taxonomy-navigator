import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from tax_tree import layout as tax_layout, register_callbacks as register_tax_callbacks
from naics_tree import naics_layout, register_callbacks as register_naics_callbacks

# Initialize the main app with callback suppression
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

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

# Callback to handle page routing
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
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

# Register both sets of callbacks
register_tax_callbacks(app)
register_naics_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True) 