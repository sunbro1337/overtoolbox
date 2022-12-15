import pandas as pd

from .queries.battery import *
from .queries.gpu import *

def prepare_pddf(query_data, rename=None):
    df = query_data.as_pandas_dataframe()[["ts", "value"]]
    if rename:
        df.rename(columns={"value": rename})
    df['duration_ts'] = df['ts'] - df['ts'][0]
    df['duration'] = pd.to_datetime(df['duration_ts'], unit='ns')#TODO .dt.strftime(TIME_FORMAT) Specify axis tick value for time
    return df

def prepare_pddf_battery(tp_1, tp_2):
    print("Preparing pandas data frames: battery")
    batt_qrdf_1 = batt_query(tp_1)
    batt_qrdf_2 = batt_query(tp_2)
    batt_charge_uah_1 = prepare_pddf(batt_qrdf_1[1])
    batt_charge_uah_2 = prepare_pddf(batt_qrdf_2[1])
    batt_current_ua_1 = prepare_pddf(batt_qrdf_1[2])
    batt_current_ua_2 = prepare_pddf(batt_qrdf_2[2])
    batt_capacity_pct_1 = prepare_pddf(batt_qrdf_1[3])
    batt_capacity_pct_2 = prepare_pddf(batt_qrdf_2[3])
    print("For more info about energy metrics see https://perfetto.dev/docs/data-sources/battery-counters")
    print(batt_charge_uah_1.head(), batt_charge_uah_2.head(), batt_current_ua_1.head(),
          batt_current_ua_2.head(), batt_capacity_pct_1.head(), batt_capacity_pct_2.head())
    print("Preparing pandas data frames is complete: battery")
    axs_labels = {
        'x': 'Duration',
        'y': 'Value'
    }
    data_current_ua = [
        {
            'x': batt_current_ua_1["duration"],
            'y': batt_current_ua_1["value"],
            'label': "current_ua_res1.0",
            'duration_ts': batt_current_ua_1['duration_ts']
        },
        {
            'x': batt_current_ua_2["duration"],
            'y': batt_current_ua_2["value"],
            'label': "current_ua_res0.3",
            'duration_ts': batt_current_ua_2['duration_ts']
        }
    ]

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
    return {
        "axs_labels": axs_labels,
        "data_current_ua": data_current_ua,
        "data_charge_uah": data_charge_uah,
        "data_capacity_pct": data_capacity_pct,
    }

def prepare_pddf_gpu(tp_1, tp_2):
    print("Preparing pandas data frames: GPU")
    gpu_qrdf_1 = gpu_query(tp_1)
    gpu_qrdf_2 = gpu_query(tp_2)
    gpu_utilization_1 = prepare_pddf(gpu_qrdf_1[0])
    gpu_utilization_2 = prepare_pddf(gpu_qrdf_2[0])
    gpu_description = gpu_qrdf_1[1].as_pandas_dataframe()[['name', 'description']]
    print(f"{gpu_description['name'][0]}: {gpu_description['description'][0]}")
    print(gpu_utilization_1.head(), gpu_utilization_2.head())
    print("Preparing pandas data frames is complete: GPU")
    axs_labels = {
        'x': 'Duration',
        'y': 'Value'
    }
    gpu_utilization = [
        {
            'x': gpu_utilization_1["duration"],
            'y': gpu_utilization_1["value"],
            'label': "current_ua_res1.0"
        },
        {
            'x': gpu_utilization_2["duration"],
            'y': gpu_utilization_2["value"],
            'label': "current_ua_res0.3"
        }
    ]
    return {
        'axs_labels': axs_labels,
        'gpu_utilization': gpu_utilization,
    }