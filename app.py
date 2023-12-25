import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
from user import User
from flask import session
import secrets

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

app.server.secret_key = secrets.token_hex(16)

def convertMemToGB(nodes_info):
    # Convert memory data to Gigabytes
    new_nodes_info = nodes_info.copy()

    for node in new_nodes_info:
        new_nodes_info[node]['AllocMem'] = int(new_nodes_info[node]['AllocMem']) / (1000)
        new_nodes_info[node]['FreeMem'] = int(new_nodes_info[node]['FreeMem']) / (1000)

    return new_nodes_info


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
    isLoggedIn = session.get("username") is not None

    if isLoggedIn:
        if pathname == "/dashboard" or pathname == "/":
            return dashboard_layout
        elif pathname == "/login":
            return "You're already logged in."
        else:
            return "404"
        
    else:
        if pathname == "/login" or pathname == "/":
            return login_layout
        elif pathname == "/dashboard":
            return "You're not logged in."
        else:
            return "404"
        


# Callback to handle login
@app.callback(
    Output("login-output", "children"),
    Output("url", "pathname", allow_duplicate=True),
    Input("login-button", "n_clicks"),
    State("username-input", "value"),
    State("password-input", "value"),
    prevent_initial_call=True
)
def login(n_clicks, username, password):
    if n_clicks is None:
        return "", dash.no_update

    # Attempt SSH login
    user_info = {
        'username': username,
        'hostname': 'simlab-cluster.um6p.ma'
    }
    user = User(**user_info)
    if user.connect_to_server(password):
        # If the connection is successful, return empty string for login-output and redirect to /dashboard
        global nodes, nodes_info, dashboard_layout
        nodes = user.get_nodes()
        nodes_info = convertMemToGB(user.get_nodes_info())

        global dashboard_layout
        dashboard_layout = html.Div([
            html.Div([
                dbc.Button("Logout", id="logout-button", color="danger", className="mt-3"),
            ], style={'position': 'absolute', 'top': -14, 'right': 48, 'zIndex': 1000}),
            
            html.H1("Node Management Dashboard"),

            # Dropdown for selecting a node
            dcc.Dropdown(
                id='node-dropdown',
                options=[{'label': node, 'value': node} for node in nodes],
                placeholder="Select a node",
            ),

            # Flex layout for multiple charts
            html.Div(id='charts-container', style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-around'}),
            html.Div(id="other-info"),

        ], style={'margin': "1em", 'padding-left': '2em', 'padding-right': '2em', 'margin-top': '-3px'})

        session["username"] = username
        return "", "/dashboard"
    else:
        # If authentication fails, return an error message
        return "Invalid credentials", dash.no_update
    

shadow_style = "0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)"


# Callback to handle logout
@app.callback(
    Output("url", "pathname"),
    Input("logout-button", "n_clicks"),
)
def logout(n_clicks):
    if n_clicks is None:
        return dash.no_update

    # Clear the session and redirect to the login page
    session.clear()
    return "/login"


@app.callback(
    Output('charts-container', 'children'),
    Output("other-info", "children"),
    Input('node-dropdown', 'value')
)
def update_charts(selected_node):
    if selected_node is None:
        return [], ""

    selected_node_info = nodes_info.get(selected_node, {})

    curr_r_jobs = selected_node_info["curr_r_jobs"]
    cpu_err = selected_node_info["CPUErr"]
    features = selected_node_info["AvailableFeatures"]

    other_info = [
        html.P([
            html.Strong("Number of currently running jobs on this node: "),
            str(curr_r_jobs)
        ]),
        html.P([
            html.Strong("Number of CPUs that have problems: "),
            str(cpu_err)
        ]),
        html.P([
            html.Strong("Features: "),
            str(features)
        ]),
    ]


    # Extract relevant information for the CPU pie chart
    allocated_cpu = int(selected_node_info.get('CPUAlloc', 0))
    total_cpu = int(selected_node_info.get('CPUTot', 1))
    cpu_labels = ['Allocated CPU', 'Free CPU']
    cpu_values = [allocated_cpu, total_cpu - allocated_cpu]

    # Extract relevant information for the Memory pie chart
    allocated_memory = selected_node_info.get('AllocMem', 0)
    free_memory = selected_node_info.get('FreeMem', 1)
    memory_labels = ["Allocated Memory", "Free Memory"]
    memory_values = [allocated_memory, free_memory]

    # Create CPU pie chart
    cpu_pie_chart = dcc.Graph(
        figure=px.pie(labels=cpu_labels, values=cpu_values, title=f'CPU Information - {selected_node}',
                      names=cpu_labels).update_traces(textinfo='value+percent+label'),
        style={'width': '45%', 'margin': '10px', "border-radius": "8px", "box-shadow": shadow_style, "padding": "13px"},
    )


    memory_pie_chart = dcc.Graph(
        figure=px.pie(labels=memory_labels, values=memory_values, title=f'Memory Usage (in GB) - {selected_node}', names=memory_labels).update_traces(textinfo='percent+value'),
        style={'width': '45%', 'margin': '10px', "border-radius": "8px", "box-shadow": shadow_style, "padding": "13px"},
    )

    return [cpu_pie_chart, memory_pie_chart], other_info
    
if __name__ == '__main__':
    app.run_server(debug=True)
