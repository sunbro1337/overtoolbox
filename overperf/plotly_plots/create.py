import plotly.graph_objects as go
import pandas as pd


def create_scatter(data: list,  axs_labels: dict):
    fig = go.Figure()
    for plot in data:
        fig.add_trace(go.Scatter(
            x=plot['x'],
            y=plot['y'],
            mode='lines+markers',
            name=plot['label'],
        ))
    return fig
