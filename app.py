import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from user import User

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Layout for login page
login_layout = dbc.Container(
    dbc.Row(
        dbc.Col(
            html.Div([
                html.H1("Login Page", className="mb-4"),
                html.Div([
                    dbc.Label("Username", html_for="username-input", className="mr-2"),
                    dbc.Input(type="text", id="username-input", placeholder="Enter username"),
                ], className="mb-3"),
                html.Div([
                    dbc.Label("Password", html_for="password-input", className="mr-2"),
                    dbc.Input(type="password", id="password-input", placeholder="Enter password"),
                ], className="mb-3"),
                dbc.Button("Login", id="login-button", color="primary", className="mr-1"),
                html.Div(id="login-output", className="mt-3"),
                dcc.Location(id='url-redirect', refresh=False),
            ]),
            width=6,
            className="mt-5"
        ),
        justify="center"
    )
)
# Layout for dashboard page
dashboard_layout = html.Div([
    dbc.Row(dbc.Col(html.H1("Dashboard"), width=12), className="mb-4"),
    # Add your dashboard components here
])

# App layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Callback to switch between login and dashboard pages
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/dashboard':
        return dashboard_layout
    else:
        return login_layout

# Callback to handle login
@app.callback(
    Output("login-output", "children"),
    Output("url", "pathname"),
    Input("login-button", "n_clicks"),
    State("username-input", "value"),
    State("password-input", "value")
)

def login(n_clicks, username, password):
    if n_clicks is None:
        return "", dash.no_update

    # Attempt SSH login
    user_info = {
        'username': username,
        'hostname': 'simlab-cluster.um6p.ma',
        'password': password
    }
    user = User(**user_info)
    if user.connect_to_server():
        # If the connection is successful, return empty string for login-output and redirect to /dashboard
        return "", "/dashboard"
    else:
        # If authentication fails, return an error message
        return "Invalid credentials", dash.no_update
    
if __name__ == '__main__':
    app.run_server(debug=True)
