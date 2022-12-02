# https://perfetto.dev/docs/data-sources/battery-counters

import os.path
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from perfetto.trace_processor import TraceProcessor
import pandas as pd
import numpy as np


def prepare_batt_df(query_data, rename=None):
    df = query_data.as_pandas_dataframe()[["ts", "value"]]
    if rename:
        df.rename(columns={"value": rename})
    df['duration_ts'] = df['ts'] - df['ts'][0]
    df['duration'] = pd.to_datetime(df['duration_ts'], unit='ns')#TODO .dt.strftime(TIME_FORMAT) Specify axis tick value for time
    return df

def create_plot(ax, data: list, title: str, axs_labels: dict):
    legend_labels = []
    for plot in data:
        label, = ax.plot(plot["x"], plot["y"], label=plot["label"])
        legend_labels.append(label)
    ax.legend(handles=legend_labels, loc='upper right')
    ax.set_title('current_ua')
    ax.set_xlabel(axs_labels['x'])
    ax.set_ylabel(axs_labels['y'])
    # x1 = np.arange(min(batt_current_ua_1['duration_ts'][1], batt_current_ua_2['duration_ts'][1]),
    #                               max(batt_current_ua_1['duration_ts'][len(batt_current_ua_1['duration_ts'])-1],
    #                                   batt_current_ua_2['duration_ts'][len(batt_current_ua_2['duration_ts'])-1]), 1000000000)
    ax.set_title(title)

def batt_query(tp):
    print("Querying to tp: battery")
    # batt_all = tp.query("""SELECT ts, value, name, ct.id, c.id FROM counter as c
    # left join counter_track as ct on c.track_id = ct.id
    # where SUBSTRING(ct.name, 1, 4)="batt"
    # order by ct.id and c.id""")

    batt_charge_uah = tp.query("""SELECT ts, value, name, ct.id, c.id FROM counter as c
    left join counter_track as ct on c.track_id = ct.id
    where ct.name="batt.charge_uah"
    order by ct.id and c.id""")

    batt_current_ua = tp.query("""SELECT ts, value, name, ct.id, c.id FROM counter as c
    left join counter_track as ct on c.track_id = ct.id
    where ct.name="batt.current_ua"
    order by ct.id and c.id""")

    batt_capacity_pct = tp.query("""SELECT ts, value, name, ct.id, c.id FROM counter as c
    left join counter_track as ct on c.track_id = ct.id
    where ct.name="batt.capacity_pct"
    order by ct.id and c.id""")
    print("Querying to tp is complete: battery")
    return (None, batt_charge_uah, batt_current_ua, batt_capacity_pct)

def gpu_query(tp):
    print("Querying to tp: GPU")
    GPU_utilization_data = tp.query("""SELECT ts, value FROM counter as c
    left join counter_track as ct on c.track_id = ct.id
    where ct.name="GPU utilization"
    order by ct.id and c.id""")
    GPU_utilization_details = tp.query("""SELECT name, description FROM counter as c
    left join counter_track as ct on c.track_id = ct.id
    where ct.name="GPU utilization"
    LIMIT 1""")
    print("Querying to tp is complete: GPU")
    return (GPU_utilization_data, GPU_utilization_details)


TRACE_1 = os.path.join("..", "..", "..", "build", "WOWSC_26131_Enable3DWavesAndDeformation", "com.lesta.legends.hybrid_20221123_1739.perfetto")
TRACE_2 = os.path.join("..", "..", "..", "build", "WOWSC_26131_Enable3DWavesAndDeformation", "com.lesta.legends.hybrid_20221123_1739.perfetto")
# TRACE_1 = os.path.join("..", "..", "..", "build", "WOWSC_26131_Enable3DWavesAndDeformation", "com.lesta.legends.hybrid_20221201_1829.perfetto")
# TRACE_1 = os.path.join("..", "..", "..", "build", "WOWSC_26131_Enable3DWavesAndDeformation", "com.lesta.legends.hybrid_20221201_1808.perfetto")
# TRACE_2 = os.path.join("..", "..", "..", "build", "WOWSC_26131_Enable3DWavesAndDeformation", "com.lesta.legends.hybrid_20221201_1905.perfetto")

DARK_MODE = False
NS = False
TIME_FORMAT = '%M:%S:%f' if NS else "%M:%S"
TIME_AXIS_TICK =1

print("Loading traces")
tp_1 = TraceProcessor(trace=TRACE_1)
tp_2 = TraceProcessor(trace=TRACE_2)
print("Loading traces is complete")

print("Preparing data frames: battery")
batt_qrdf_1 = batt_query(tp_1)
batt_qrdf_2 = batt_query(tp_2)
batt_charge_uah_1 = prepare_batt_df(batt_qrdf_1[1])
batt_charge_uah_2 = prepare_batt_df(batt_qrdf_2[1])
batt_current_ua_1 = prepare_batt_df(batt_qrdf_1[2])
batt_current_ua_2 = prepare_batt_df(batt_qrdf_2[2])
batt_capacity_pct_1 = prepare_batt_df(batt_qrdf_1[3])
batt_capacity_pct_2 = prepare_batt_df(batt_qrdf_2[3])
print(batt_charge_uah_1.head(), batt_charge_uah_2.head(), batt_current_ua_1.head(),
      batt_current_ua_2.head(), batt_capacity_pct_1.head(), batt_capacity_pct_2.head())
print("Preparing data frames is complete: battery")

print("Preparing plots")
if DARK_MODE:
    plt.style.use('dark_background')
else:
    plt.style.use('Solarize_Light2')

fig, (ax1, ax2, ax3) = plt.subplots(nrows=3, ncols=1, figsize=(16, 9), layout="constrained")

axs_labels = {
    'x': 'Duration',
    'y': 'Value'
}

data_current_ua = [
    {
        'x': batt_current_ua_1["duration"],
        'y': batt_current_ua_1["value"],
        'label': "current_ua_res1.0"
    },
    {
        'x': batt_current_ua_2["duration"],
        'y': batt_current_ua_2["value"],
        'label': "current_ua_res0.3"
    }
]
create_plot(ax1, data_current_ua, "current_ua", axs_labels)

data_charge_uah = [
    {
        'x': batt_charge_uah_1["duration"],
        'y': batt_charge_uah_1["value"],
        'label': "charge_uah_res1.0"
    },
    {
        'x': batt_charge_uah_2["duration"],
        'y': batt_charge_uah_2["value"],
        'label': "charge_uah_res0.3"
    }
]
create_plot(ax2, data_charge_uah, "charge_uah", axs_labels)

data_capacity_pct = [
    {
        'x': batt_capacity_pct_1["duration"],
        'y': batt_capacity_pct_1["value"],
        'label': "capacity_res1.0"
    },
    {
        'x': batt_capacity_pct_2["duration"],
        'y': batt_capacity_pct_2["value"],
        'label': "capacity_res0.3"
    }
]
create_plot(ax3, data_capacity_pct, "capacity_pct", axs_labels)

fig.suptitle("Battery usage")
print("Preparing plots is complete")
plt.show()

#TODO Slices like in AGI
