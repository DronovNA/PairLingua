import plotly.graph_objects as go
import plotly.express as px
import json
import math

# Data from the provided JSON - adjusted for better balanced layout
data = {
    "nodes": [
        {"id": "nginx", "name": "Nginx<br>(Proxy)", "layer": 0, "x": 100, "y": 300},  # Top layer
        {"id": "frontend", "name": "Frontend<br>(React + TS)", "layer": 1, "x": 100, "y": 230},
        {"id": "backend", "name": "Backend<br>(FastAPI)", "layer": 2, "x": 100, "y": 160},
        {"id": "auth", "name": "Auth Service<br>(JWT)", "layer": 2, "x": 70, "y": 160},
        {"id": "study", "name": "Study Service<br>(SM-2)", "layer": 2, "x": 130, "y": 160},
        {"id": "postgres", "name": "PostgreSQL<br>(Database)", "layer": 3, "x": 100, "y": 90},
        {"id": "redis", "name": "Redis<br>(Cache)", "layer": 3, "x": 150, "y": 90}
    ],
    "connections": [
        {"from": "nginx", "to": "frontend", "type": "HTTP"},
        {"from": "nginx", "to": "backend", "type": "API"},
        {"from": "frontend", "to": "backend", "type": "REST"},
        {"from": "backend", "to": "postgres", "type": "SQL"},
        {"from": "backend", "to": "redis", "type": "Cache"},
        {"from": "auth", "to": "postgres", "type": "Users"},
        {"from": "study", "to": "postgres", "type": "Cards"}
    ]
}

# Create figure
fig = go.Figure()

# Define colors for different layers
layer_colors = {
    0: '#1FB8CD',  # Infrastructure - Strong cyan
    1: '#DB4545',  # Frontend - Bright red  
    2: '#2E8B57',  # Application - Sea green
    3: '#5D878F'   # Data - Cyan
}

layer_names = {
    0: 'Infrastructure',
    1: 'Frontend', 
    2: 'Application',
    3: 'Data Layer'
}

# Create node lookup for coordinates
node_lookup = {node['id']: node for node in data['nodes']}

# Add connection lines with better styling and arrows
for conn in data['connections']:
    from_node = node_lookup[conn['from']]
    to_node = node_lookup[conn['to']]
    
    # Calculate arrow position (80% along the line)
    arrow_x = from_node['x'] + 0.8 * (to_node['x'] - from_node['x'])
    arrow_y = from_node['y'] + 0.8 * (to_node['y'] - from_node['y'])
    
    # Calculate arrow direction
    dx = to_node['x'] - from_node['x']
    dy = to_node['y'] - from_node['y']
    length = math.sqrt(dx**2 + dy**2)
    
    if length > 0:
        # Normalize and scale for arrow
        arrow_dx = (dx / length) * 8
        arrow_dy = (dy / length) * 8
        
        # Add the connection line
        fig.add_trace(go.Scatter(
            x=[from_node['x'], to_node['x']],
            y=[from_node['y'], to_node['y']],
            mode='lines',
            line=dict(color='#333333', width=4),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Add arrow using annotation
        fig.add_annotation(
            x=arrow_x,
            y=arrow_y,
            ax=arrow_x - arrow_dx,
            ay=arrow_y - arrow_dy,
            xref='x',
            yref='y',
            axref='x',
            ayref='y',
            showarrow=True,
            arrowhead=2,
            arrowsize=1.5,
            arrowwidth=3,
            arrowcolor='#333333'
        )

# Add nodes grouped by layer for legend with larger size and better fonts
for layer in sorted(layer_colors.keys()):
    layer_nodes = [node for node in data['nodes'] if node['layer'] == layer]
    
    if layer_nodes:
        fig.add_trace(go.Scatter(
            x=[node['x'] for node in layer_nodes],
            y=[node['y'] for node in layer_nodes],
            mode='markers+text',
            marker=dict(
                size=70,
                color=layer_colors[layer],
                line=dict(width=4, color='white')
            ),
            text=[node['name'] for node in layer_nodes],
            textposition='middle center',
            textfont=dict(size=13, color='white', family='Arial Black'),
            name=layer_names[layer],
            hovertemplate='%{text}<br>Layer: ' + layer_names[layer] + '<extra></extra>'
        ))

# Update layout with better spacing and styling
fig.update_layout(
    title=dict(
        text='PairLingua App Architecture',
        font=dict(size=20, family='Arial Black'),
        x=0.5,
        y=0.95
    ),
    showlegend=True,
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=1.02,
        xanchor='center',
        x=0.5,
        font=dict(size=14),
        itemsizing='constant'
    ),
    xaxis=dict(
        showgrid=False, 
        zeroline=False, 
        showticklabels=False,
        range=[30, 190]
    ),
    yaxis=dict(
        showgrid=False, 
        zeroline=False, 
        showticklabels=False,
        range=[50, 340]
    ),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)'
)

fig.update_traces(cliponaxis=False)

# Save the chart
fig.write_image('network_diagram.png', width=800, height=750)