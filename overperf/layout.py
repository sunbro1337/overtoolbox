from dash import dcc, html
from callbacks import Callback
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
    def create_table_overall(agg_data, name):
        df_indexes = None
        agg_data = agg_data[name]
        for data_key in agg_data:
            if not df_indexes:
                df_indexes = list(agg_data[data_key].index)
                df_indexes.insert(0, 'name')
                break
        t_head = html.Tr([html.Th(col) for col in df_indexes])
        t_body = []
        for data_key in agg_data:
            t_ds = []
            for index in agg_data[data_key].index:
                t_ds.append(html.Td(agg_data[data_key].loc[index]))
            t_ds.insert(0, html.Td(data_key))
            t_body.append(html.Tr(t_ds))


        layout = html.Div(
            children=[
                html.Thead(t_head),
                html.Tbody(t_body),
            ]
        )

        #TODO Save dash layout as html
        # Callback.save_html_dict['name'] = layout
        return layout

    @staticmethod
    def create_table_percentile(agg_data):
        layout = html.Div(
            children=[

            ]
        )
        return layout
