import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

app = dash.Dash(__name__)

# Dummy node information for testing
nodes_info = {
    'node01': {'CPUAlloc': '5', 'CPUErr': '0', 'CPUTot': '40', 'AllocMem': '40960', 'FreeMem': '106192', 'curr_r_jobs': 1},
    'node02': {'CPUAlloc': '10', 'CPUErr': '0', 'CPUTot': '32', 'AllocMem': '81920', 'FreeMem': '92160', 'curr_r_jobs': 2},
}

# Convert memory data to Gigabytes
for node in nodes_info:
    nodes_info[node]['AllocMem'] = int(nodes_info[node]['AllocMem']) / (1000)
    nodes_info[node]['FreeMem'] = int(nodes_info[node]['FreeMem']) / (1000)

# Layout of the dashboard
app.layout = html.Div([
    html.H1("Node Management Dashboard"),

    # Dropdown for selecting a node
    dcc.Dropdown(
        id='node-dropdown',
        options=[{'label': node, 'value': node} for node in nodes_info.keys()],
        placeholder="Select a node",
    ),

    # Flex layout for multiple charts
    html.Div(id='charts-container', style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-around'}),
])

# Callback to update the charts based on the selected node
@app.callback(
    Output('charts-container', 'children'),
    Input('node-dropdown', 'value')
)
def update_charts(selected_node):
    if selected_node is None:
        return []

    selected_node_info = nodes_info.get(selected_node, {})

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
        style={'width': '45%', 'margin': '10px'},
    )


    memory_pie_chart = dcc.Graph(
        figure=px.pie(labels=memory_labels, values=memory_values, title=f'Memory Usage (in GB) - {selected_node}', names=memory_labels).update_traces(textinfo='percent+value'),
        style={'width': '45%', 'margin': '10px'},
    )

    return [cpu_pie_chart, memory_pie_chart]

if __name__ == '__main__':
    app.run_server(debug=True)
