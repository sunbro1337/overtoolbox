import os.path
import io

from perfetto.trace_processor import TraceProcessor
from dash import Dash

from data_frames.prepare import prepare_pddf_battery, prepare_pddf_gpu, PhysicalDeivces
from layout import *
from callbacks import *

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)
# TODO
# https://dash.plotly.com/external-resources
# app.css.append_css({'external_url': 'static/background.css'})
# app.server.static_folder = 'static'

DEBUG_MODE = False
DARK_MODE = False
DEVICE = 'adreno'
if DARK_MODE:
    THEME = "plotly_dark"
else:
    THEME = "plotly_white"
NS = False
TIME_FORMAT = '%M:%S:%f' if NS else "%M:%S"
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
axs_labels = {
        'x': 'Duration',
        'y': 'Value'
    }

# Short mali trace for test
# TRACES = [
#     os.path.join("..", "..", "..", "build", "WOWSC_26131_Enable3DWavesAndDeformation", "com.lesta.legends.hybrid_20221202_1846.perfetto"),
#     os.path.join("..", "..", "..", "build", "WOWSC_26131_Enable3DWavesAndDeformation", "com.lesta.legends.hybrid_20221202_1846.perfetto"),
# ]

# Long adreno trace for test
TRACES = [
    os.path.join("..", "..", "..", "build", ".agi_traces", "com.lesta.legends.hybrid_20221227_1833.perfetto"),
    os.path.join("..", "..", "..", "build", ".agi_traces", "com.lesta.legends.hybrid_20221227_1849.perfetto"),
]

# Long adreno trace for test
# TRACES = [
#     os.path.join("..", "..", "..", "build", "WOWSC_26131_Enable3DWavesAndDeformation", "com.lesta.legends.hybrid_20221201_1808.perfetto"),
#     os.path.join("..", "..", "..", "build", "WOWSC_26131_Enable3DWavesAndDeformation", "com.lesta.legends.hybrid_20221201_1905.perfetto"),
# ]

NAMES = [
    "com.lesta.legends.hybrid_20221202_1846.perfetto",
    "com.lesta.legends.hybrid_20221202_1846.perfetto",
]

print("Loading traces")
TRACE_PROCESSORS = {}
for trace_i in range(0, len(TRACES)):
    TRACE_PROCESSORS[f"{NAMES[trace_i]}{trace_i}"] = TraceProcessor(trace=TRACES[trace_i])
print("Loading traces is complete")

battery_data = prepare_pddf_battery(TRACE_PROCESSORS)
gpu_data = prepare_pddf_gpu(TRACE_PROCESSORS, DEVICE)

layout_plots_all = [
        LayoutElements.create_plot_fig(
            battery_data['batt_current_ua'],
            'batt_current_ua'
        ),
        LayoutElements.create_plot_fig(
            battery_data['batt_charge_uah'],
            'batt_charge_uah'
        ),
        LayoutElements.create_plot_fig(
            battery_data['batt_capacity_pct'],
            'batt_capacity_pct'
        ),
        LayoutElements.create_plot_fig(
            gpu_data['gpu_utilization'],
            'gpu_utilization'
        ),
]

if DEVICE == PhysicalDeivces.ADRENO:
    layout_plots_all.append(
        LayoutElements.create_plot_fig(
            gpu_data['gpu_time_alus_working'],
            'gpu_time_alus_working'
        ),
    )

app.layout = html.Div(
    children=[
        html.A(
            html.Button("Collect as HTML"),
            id="collect_html_button",
        ),
        html.A(
            html.Button("Download as HTML"),
            id="download_html_button",
            href='',
            download="plotly_graph.html",
        ),
        html.Div(children=layout_plots_all),
    ]
)

callback_current_ua = Callback(
    name='batt_current_ua',
    app=app,
    data=battery_data['batt_current_ua'],
    axs_labels=axs_labels,
    theme=THEME
).update_fig_callback()
callback_charge_uah = Callback(
    name='batt_charge_uah',
    app=app,
    data=battery_data['batt_charge_uah'],
    axs_labels=axs_labels,
    theme=THEME
).update_fig_callback()
callback_capacity_pct = Callback(
    name='batt_capacity_pct',
    app=app,
    data=battery_data['batt_capacity_pct'],
    axs_labels=axs_labels,
    theme=THEME
).update_fig_callback()
callback_gpu_utilization = Callback(
    name='gpu_utilization',
    app=app,
    data=gpu_data['gpu_utilization'],
    axs_labels=axs_labels,
    theme=THEME
).update_fig_callback()

if DEVICE == PhysicalDeivces.ADRENO:
    callback_gpu_time_alus_working = Callback(
        name='gpu_time_alus_working',
        app=app,
        data=gpu_data['gpu_time_alus_working'],
        axs_labels=axs_labels,
        theme=THEME
    ).update_fig_callback()

Callback(
    name='gpu_utilization',
    app=app,
    data=gpu_data['gpu_utilization'],
    axs_labels=axs_labels,
    theme=THEME
).download_html_callback()

if __name__ == '__main__':
    app.run_server(debug=DEBUG_MODE)
#TODO Slices like in AGI
#TODO Save stats as HTMl
