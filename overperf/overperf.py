import datetime
import os.path

import pandas as pd
from perfetto.trace_processor import TraceProcessor
from dash import Dash, Input, Output

# from _old_matplotlib_plots.create_plots import *
from plotly_plots.create import create_scatter
from data_frames.prepare import prepare_pddf_battery, prepare_pddf_gpu
from app_layout import *


# TRACE_1 = os.path.join("..", "..", "..", "build", "WOWSC_26131_Enable3DWavesAndDeformation", "com.lesta.legends.hybrid_20221202_1846.perfetto")
# TRACE_2 = os.path.join("..", "..", "..", "build", "WOWSC_26131_Enable3DWavesAndDeformation", "com.lesta.legends.hybrid_20221202_1846.perfetto")
# TRACE_1 = os.path.join("..", "..", "..", "build", "WOWSC_26131_Enable3DWavesAndDeformation", "com.lesta.legends.hybrid_20221201_1829.perfetto")
# TRACE_1 = os.path.join("..", "..", "..", "build", "WOWSC_26131_Enable3DWavesAndDeformation", "com.lesta.legends.hybrid_20221201_1808.perfetto")
# TRACE_2 = os.path.join("..", "..", "..", "build", "WOWSC_26131_Enable3DWavesAndDeformation", "com.lesta.legends.hybrid_20221201_1905.perfetto")
TRACE_1 = os.path.join("..", "..", "com.lesta.legends.hybrid_20221202_1846.perfetto")
TRACE_2 = os.path.join("..", "..", "com.lesta.legends.hybrid_20221202_1846.perfetto")


DARK_MODE = True
if DARK_MODE:
    THEME = "plotly_dark"
else:
    THEME = "plotly_white"
NS = False
TIME_FORMAT = '%M:%S:%f' if NS else "%M:%S"
TIME_AXIS_TICK =1

print("Loading traces")
tp_1 = TraceProcessor(trace=TRACE_1)
tp_2 = TraceProcessor(trace=TRACE_2)
print("Loading traces is complete")

battery_data = prepare_pddf_battery(tp_1, tp_2)
gpu_data = prepare_pddf_gpu(tp_1, tp_2)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

theme = {
    'dark': True,
    'detail': '#007439',
    'primary': '#00EA64',
    'secondary': '#6E6E6E',
}

app = Dash(__name__)
# TODO
# https://dash.plotly.com/external-resources
# app.css.append_css({'external_url': 'static/background.css'})
# app.server.static_folder = 'static'

app.layout = AppLayout.scatter_plots(
    colors=colors,
    theme=THEME,
    battery_data=battery_data,
    gpu_data=gpu_data,
)

@app.callback(
    Output('data_current_ua-graph', 'figure'),
    Input('data_current_ua-duration-slider', 'value')
)
def update_figure(selected_duration):
    filtered_data_current_ua = [
        {
            'x': battery_data['data_current_ua'][0]["x"][(battery_data['data_current_ua'][0]["x"]
                                                          <= pd.to_datetime(selected_duration))
                                                         & (battery_data['data_current_ua'][0]["x"] >= pd.to_datetime(0))],
            'y': battery_data['data_current_ua'][0]["y"],
            'label': "current_ua_res1.0",
            'duration_ts': battery_data['data_current_ua'][0]['duration_ts']
        },
        {
            'x': battery_data['data_current_ua'][1]["x"][(battery_data['data_current_ua'][1]["x"]
                                                          <= pd.to_datetime(selected_duration))
                                                         & (battery_data['data_current_ua'][1]["x"] >= pd.to_datetime(0))],
            'y': battery_data['data_current_ua'][1]["y"],
            'label': "current_ua_res1.0",
            'duration_ts': battery_data['data_current_ua'][1]['duration_ts']
        }
    ]
    data_current_ua_fig = create_scatter(filtered_data_current_ua, battery_data['axs_labels'])
    data_current_ua_fig.update_layout(
        transition_duration=500,
        title='data_current_ua',
        template=THEME
    )
    return data_current_ua_fig

if __name__ == '__main__':
    app.run_server(debug=True)
#TODO Slices like in AGI
