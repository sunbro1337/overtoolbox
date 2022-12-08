from dash import dcc, html

from plotly_plots.create import *

class AppLayout:
    @staticmethod
    def scatter_plots(colors, theme, gpu_data, battery_data):
        data_current_ua_fig = create_scatter(battery_data['data_current_ua'], battery_data['axs_labels'])
        data_charge_uah_fig = create_scatter(battery_data['data_charge_uah'], battery_data['axs_labels'])
        data_capacity_pct_fig = create_scatter(battery_data['data_capacity_pct'], battery_data['axs_labels'])
        gpu_fig = create_scatter(gpu_data['gpu_utilization'], gpu_data['axs_labels'])
        data_current_ua_fig.update_layout(
            template=theme,
            title='data_current_ua'
            # plot_bgcolor=colors['background'],
            # paper_bgcolor=colors['background'],
            # font_color=colors['text']
        )
        data_charge_uah_fig.update_layout(
            template=theme,
            title='data_charge_uah'
        )
        data_capacity_pct_fig.update_layout(
            template=theme,
            title='data_capacity_pct'
        )
        gpu_fig.update_layout(
            template=theme,
            title='gpu_utilization'
        )

        app_layout = html.Div(
            # style={'backgroundColor': colors['background']},
            children=[

            dcc.Graph(
                id='data_current_ua',
                figure=data_current_ua_fig
            ),

            dcc.Graph(
                id='data_charge_uah',
                figure=data_charge_uah_fig
            ),

                dcc.Graph(
                    id='data_capacity_pct',
                    figure=data_capacity_pct_fig
                ),

            dcc.Graph(
                id='gpu_utilization',
                figure=gpu_fig
            )
        ])
        return app_layout