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
        marks = {
            str(time): str(datetime.fromtimestamp(time // 1000000000).strftime("%M:%S"))
            for time in data['duration_ts'].drop([0]).unique()
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
            #TODO dcc.RangeSlider https: // plotly.com / python / line - and -scatter /
            #dcc.RangeSlider(
            #    id='range-slider',
            #    min=0, max=2.5, step=0.1,
            #    marks={0: '0', 2.5: '2.5'},
            #    value=[0.5, 2]
            #),
            dcc.Slider(
                min=data['duration_ts'].min(),
                max=data['duration_ts'].max(),
                step=None,
                value=data['duration_ts'].max(),
                marks=marks,
                id=f'{name}_duration_slider',
            ),
        ])
        return layout