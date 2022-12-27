from dash import Input, Output
from layout import LayoutElements
import pandas as pd

class Callback:
    def __init__(self, name, app, data, axs_labels, theme):
        self.name = name
        self.app = app
        self.data = data
        self.axs_labels = axs_labels,
        self.theme = theme

    def update_fig_callback(self):
        @self.app.callback(
            Output(f"{self.name}_graph", 'figure'),
            Input(f"{self.name}_duration_slider", 'value'),
            Input(f"{self.name}_yaxis_type", 'value'),
        )
        def update_plot_fig(selected_duration, current_ua_yaxis_type):
            filtered_data = []
            for data_i in range(0, len(self.data)):
                filtered_data.append(
                    {
                        'x': self.data[data_i]["x"][(self.data[data_i]["x"]
                                                                      <= pd.to_datetime(selected_duration))
                                                                     & (self.data[data_i]["x"] >= pd.to_datetime(0))],
                        'y': self.data[data_i]["y"],
                        'label': self.data[data_i]['label'],
                        'duration_ts': self.data[data_i]['duration_ts']
                    }
                )
            fig = LayoutElements.create_scatter(filtered_data, self.axs_labels)
            fig.update_yaxes(type=current_ua_yaxis_type.lower())
            fig.update_layout(
                transition_duration=500,
                title=self.name,
                template=self.theme
            )
            return fig