import os.path
import io
import argparse

from perfetto.trace_processor import TraceProcessor
from dash import Dash

from data_frames.prepare import prepare_pddf_battery, prepare_pddf_gpu, PhysicalDeivces
from layout import *
from callbacks import *

DARK_MODE = False
DEVICE = 'mali'
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

def load_traces(traces, names) -> dict:
    print("Loading traces")
    TRACE_PROCESSORS = {}
    for trace_i in range(0, len(traces)):
        TRACE_PROCESSORS[f"{names[trace_i]}{trace_i}"] = TraceProcessor(trace=traces[trace_i])
    print("Loading traces is complete")
    return TRACE_PROCESSORS


def prepare_data(trace_processors) -> dict:
    battery_data = prepare_pddf_battery(trace_processors)
    gpu_data = prepare_pddf_gpu(trace_processors, DEVICE)
    return {
        "battery_data": battery_data,
        "gpu_data": gpu_data,
    }


def prepare_layout(battery_data, gpu_data) -> list:
    layout_plots_all = [
        LayoutElements.create_plot_fig(
            'batt_current_ua'
        ),
        LayoutElements.create_table_overall(
            agg_data=battery_data['agg_overall'],
            name='batt_current_ua'
        ),
        LayoutElements.create_plot_fig(
            'batt_charge_uah'
        ),
        LayoutElements.create_table_overall(
            agg_data=battery_data['agg_overall'],
            name='batt_charge_uah'
        ),
        LayoutElements.create_plot_fig(
            'batt_capacity_pct'
        ),
        LayoutElements.create_table_overall(
            agg_data=battery_data['agg_overall'],
            name='batt_capacity_pct'
        ),
        LayoutElements.create_plot_fig(
            'gpu_utilization'
        ),
        LayoutElements.create_table_overall(
            agg_data=gpu_data['agg_overall'],
            name='gpu_utilization'
        ),
    ]

    if DEVICE == PhysicalDeivces.ADRENO:
        layout_plots_all.append(
            LayoutElements.create_plot_fig(
                'gpu_time_alus_working'
            ),
        )
        layout_plots_all.append(
            LayoutElements.create_table_overall(
                agg_data=gpu_data['agg_overall'],
                name='gpu_time_alus_working'
            ),
        )
    return layout_plots_all


def app_layout_update(layout_plots_all) -> None:
    app.layout = html.Div(
        children=[
            html.Div(children=[
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
                html.Em("Temporarily only for plots!"),
            ]),
            html.Div(children=layout_plots_all),
        ]
    )


def setup_callbacks(app, battery_data, gpu_data) -> None:
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

    Callback.download_html_callback(app)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="overperf")
    parser.add_argument("-t", "--trace",
                        help="traces files, nargs+",
                        nargs="+",
                        type=str)
    parser.add_argument("-n", "--name",
                        help="traces names, nargs+",
                        nargs="+",
                        type=str)
    parser.add_argument('--debug',
                        help='Enable debug mode for dash app',
                        action='store_true')
    args = parser.parse_args()

    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = Dash(__name__, external_stylesheets=external_stylesheets)
    # TODO
    # https://dash.plotly.com/external-resources
    # app.css.append_css({'external_url': 'static/background.css'})
    # app.server.static_folder = 'static'

    trace_processors = load_traces(args.trace, args.name)
    pddfs = prepare_data(trace_processors)
    layout_plots_all = prepare_layout(
        battery_data=pddfs['battery_data'],
        gpu_data=pddfs["battery_data"]
    )
    app_layout_update(layout_plots_all)
    setup_callbacks(
        battery_data=pddfs['battery_data'],
        gpu_data=pddfs["battery_data"]
    )

    app.run_server(debug=args.debug)
# TODO Slices like in AGI
# TODO Save stats as HTMl
