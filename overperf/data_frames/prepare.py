import pandas as pd

from .queries.battery import *
from .queries.gpu import *

class PhysicalDeivces:
    ADRENO = 'adreno'
    MALI = 'mali'
    POWERVR = 'povervr'

def prepare_pddf(query_data, rename=None):
    df = query_data.as_pandas_dataframe()[["ts", "value"]]
    if rename:
        df.rename(columns={"value": rename})
    df['duration_ts'] = df['ts'] - df['ts'][0]
    df['duration'] = pd.to_datetime(df['duration_ts'], unit='ns')#TODO .dt.strftime(TIME_FORMAT) Specify axis tick value for time
    return df

def prepare_pddf_battery(tp_1, tp_2):
    print("Preparing pandas data frames: battery")
    batt_qrdf_1 = batt_query_all(tp_1)
    batt_qrdf_2 = batt_query_all(tp_2)
    batt_charge_uah_1 = prepare_pddf(batt_qrdf_1["batt_charge_uah"])
    batt_charge_uah_2 = prepare_pddf(batt_qrdf_2["batt_charge_uah"])
    batt_current_ua_1 = prepare_pddf(batt_qrdf_1["batt_current_ua"])
    batt_current_ua_2 = prepare_pddf(batt_qrdf_2["batt_current_ua"])
    batt_capacity_pct_1 = prepare_pddf(batt_qrdf_1["batt_capacity_pct"])
    batt_capacity_pct_2 = prepare_pddf(batt_qrdf_2["batt_capacity_pct"])
    print("For more info about energy metrics see https://perfetto.dev/docs/data-sources/battery-counters")
    print(batt_charge_uah_1.head(), '\n', batt_charge_uah_2.head(), '\n', batt_current_ua_1.head(), '\n',
          batt_current_ua_2.head(), '\n', batt_capacity_pct_1.head(), '\n', batt_capacity_pct_2.head())
    print("Preparing pandas data frames is complete: battery")
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
            'label': "charge_uah_res1.0",
            'duration_ts': batt_current_ua_1['duration_ts']
        },
        {
            'x': batt_charge_uah_2["duration"],
            'y': batt_charge_uah_2["value"],
            'label': "charge_uah_res0.3",
            'duration_ts': batt_current_ua_2['duration_ts']
        }
    ]

    data_capacity_pct = [
        {
            'x': batt_capacity_pct_1["duration"],
            'y': batt_capacity_pct_1["value"],
            'label': "capacity_res1.0",
            'duration_ts': batt_capacity_pct_1['duration_ts']
        },
        {
            'x': batt_capacity_pct_2["duration"],
            'y': batt_capacity_pct_2["value"],
            'label': "capacity_res0.3",
            'duration_ts': batt_capacity_pct_2['duration_ts']
        }
    ]
    return {
        "current_ua": data_current_ua,
        "charge_uah": data_charge_uah,
        "capacity_pct": data_capacity_pct,
    }

def prepare_pddf_gpu(tp_1, tp_2, device):
    if device == PhysicalDeivces.ADRENO:
        print(f"Preparing pandas data frames: GPU {device}")
        gpu_qrdf_1 = gpu_query_adreno(tp_1)
        gpu_qrdf_2 = gpu_query_adreno(tp_2)
    elif device == PhysicalDeivces.MALI:
        print(f"Preparing pandas data frames: GPU {device}")
        gpu_qrdf_1 = gpu_query_mali(tp_1)
        gpu_qrdf_2 = gpu_query_mali(tp_2)
    elif device == PhysicalDeivces.POWERVR:
        pass
    else:
        raise RuntimeError(f'Device {device} is not suitable')
    gpu_utilization_1 = prepare_pddf(gpu_qrdf_1["GPU_utilization_data"])
    gpu_utilization_2 = prepare_pddf(gpu_qrdf_2["GPU_utilization_data"])
    gpu_utilization_description = gpu_qrdf_1["GPU_utilization_details"].as_pandas_dataframe()[['name', 'description']]
    print(f"{gpu_utilization_description['name'][0]}: {gpu_utilization_description['description'][0]}")
    print(gpu_utilization_1.head(), '\n', gpu_utilization_2.head())
    # gpu_time_alus_working_1 = prepare_pddf(gpu_qrdf_1["GPU_time_alus_working_data"])
    # gpu_time_alus_working_2 = prepare_pddf(gpu_qrdf_2["GPU_time_alus_working_data"])
    # gpu_time_alus_description = gpu_qrdf_1["GPU_time_alus_working_details"].as_pandas_dataframe()[['name', 'description']]
    # print(f"{gpu_time_alus_description['name'][0]}: {gpu_time_alus_description['description'][0]}")
    # print(gpu_time_alus_working_1.head(), '\n', gpu_time_alus_working_2.head())
    print("Preparing pandas data frames is complete: GPU")
    gpu_utilization = [
        {
            'x': gpu_utilization_1["duration"],
            'y': gpu_utilization_1["value"],
            'label': "gpu_utilization_1",
            'duration_ts': gpu_utilization_1['duration_ts']
        },
        {
            'x': gpu_utilization_2["duration"],
            'y': gpu_utilization_2["value"],
            'label': "gpu_utilization_2",
            'duration_ts': gpu_utilization_2['duration_ts']
        }
    ]
    # gpu_time_alus_working = [
    #     {
    #         'x': gpu_time_alus_working_1["duration"],
    #         'y': gpu_time_alus_working_1["value"],
    #         'label': "gpu_time_alus_working_1",
    #         'duration_ts': gpu_time_alus_working_1['duration_ts']
    #     },
    #     {
    #         'x': gpu_time_alus_working_2["duration"],
    #         'y': gpu_time_alus_working_2["value"],
    #         'label': "gpu_time_alus_working_2",
    #         'duration_ts': gpu_time_alus_working_2['duration_ts']
    #     }
    # ]
    return {
        'gpu_utilization': gpu_utilization,
        # 'gpu_time_alus_working': gpu_time_alus_working,
    }