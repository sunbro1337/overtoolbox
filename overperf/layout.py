from dash import dcc, html
from datetime import datetime
import plotly.graph_objects as go


class LayoutElements:

    @staticmethod
    def create_plot_fig(name):
        layout = html.Div(
            # style={'backgroundColor': colors['background']},
            children=[
            dcc.RadioItems(
                ['Linear', 'Log'],
                'Linear',
                id=f'{name}_yaxis_type',
                inline=True
            ),
            dcc.Graph(
                id=f'{name}_graph',
            ),
        ])
        return layout

    @staticmethod
    def create_table_overall(agg_data):
        layout = html.Div(
            children=[

            ]
        )
        return layout

    @staticmethod
    def create_table_percentile(agg_data):
        layout = html.Div(
            children=[

            ]
        )
        return layout
