import io
from base64 import b64encode

from dash import Input, Output
import plotly.express as px
# import pandas as pd
import plotly.io as pio


class Callback:
    save_html_dict = {}

    def __init__(self, name, app, data, axs_labels, theme=None):
        self.name = name
        self.app = app
        self.data = data
        self.axs_labels = axs_labels,
        if not theme:
            self.theme = pio.templates.default
        else:
            self.theme = theme

    def update_fig_callback(self):
        @self.app.callback(
            Output(f"{self.name}_graph", 'figure'),
            # Input(f"{self.name}_duration_slider", 'value'),
            Input(f"{self.name}_yaxis_type", 'value'),
        )
        def update_plot_fig(
                # selected_duration,
                current_ua_yaxis_type,
        ):
            # filtered_data = self.data[self.data.duration <= pd.to_datetime(selected_duration)]
            filtered_data = self.data
            fig = px.line(filtered_data, x="duration", y="value", color='name')
            fig.update_yaxes(type=current_ua_yaxis_type.lower())
            fig.update_layout(
                transition_duration=500,
                title=self.name,
                template=self.theme,
                # plot_bgcolor=colors['background'],
                # paper_bgcolor=colors['background'],
                # font_color=colors['text']
            )
            fig.update_xaxes(
                rangeslider_visible=True,
                tickformatstops=[
                    dict(dtickrange=[None, 1000], value="%H:%M:%S.%L ms"),
                    dict(dtickrange=[1000, 60000], value="%H:%M:%S s"),
                    dict(dtickrange=[60000, 3600000], value="%H:%M m"),
                    dict(dtickrange=[3600000, 86400000], value="%H:%M h"),
                    dict(dtickrange=[86400000, 604800000], value="%e. %b d"),
                    dict(dtickrange=[604800000, "M1"], value="%e. %b w"),
                    dict(dtickrange=["M1", "M12"], value="%b '%y M"),
                    dict(dtickrange=["M12", None], value="%Y Y")
                ]
            )
            Callback.save_html_dict[self.name] = io.StringIO()
            fig.write_html(Callback.save_html_dict[self.name], full_html=False)
            return fig

    @staticmethod
    def download_html_callback(app):
        @app.callback(
            Output('download_html_button', 'href'),
            Input('collect_html_button', 'n_clicks'),

        )
        def download_html(n_clicks):
            if not n_clicks:
                return ""
            print('Start collecting html')
            save_html_buffer = ''
            for string_io in Callback.save_html_dict.values():
                save_html_buffer += string_io.getvalue()
            html_bytes = save_html_buffer.encode()
            encoded = b64encode(html_bytes).decode()
            href = "data:text/html;base64," + encoded
            print('HTML is collected')
            return href
