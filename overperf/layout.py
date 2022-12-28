import pandas as pd
from dash import dcc, html
from datetime import datetime
import plotly.graph_objects as go


class LayoutElements:
    @staticmethod
    def create_scatter(data: list, axs_labels: dict):
        fig = go.Figure()
        for plot in data:
            fig.add_trace(go.Scatter(
                x=plot['x'],
                y=plot['y'],
                mode='lines+markers',
                name=plot['label'],
            ))
        return fig

    @staticmethod
    def create_plot_fig(data, name):
        min_dur = min(data[0]['duration_ts'].drop([0]).min(),
                                      data[1]['duration_ts'].drop([0]).min())
        max_dur = max(data[0]['duration_ts'].max(),
                                      data[1]['duration_ts'].max())
        cont_duration = pd.concat([data[0]['duration_ts'],
                                   data[1]['duration_ts']]).drop([0])
        marks = {
            str(time): str(datetime.fromtimestamp(time // 1000000000).strftime("%M:%S"))
            for time in cont_duration.unique()
        }
        layout = html.Div(
            # style={'backgroundColor': colors['background']},
            children=[

            dcc.Graph(
                id=f'{name}_graph',
            ),
            dcc.RadioItems(
                ['Linear', 'Log'],
                'Linear',
                id=f'{name}_yaxis_type',
                inline=True
            ),
            #TODO dcc.RangeSlider
            dcc.Slider(
                min=min_dur,
                max=max_dur,
                step=None,
                value=max_dur,
                marks=marks,
                id=f'{name}_duration_slider',
            ),
        ])
        return layout