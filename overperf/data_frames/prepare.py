import pandas as pd

from .queries.battery import *
from .queries.gpu import *

class PhysicalDeivces:
    ADRENO = 'adreno'
    MALI = 'mali'
    POWERVR = 'povervr'

def prepare_pddf(query_data, name):
    print(query_data)
    df = query_data.as_pandas_dataframe()[["name", "ts", "value"]]
    df['name'] = df['name'] + name
    df['duration_ts'] = df['ts'] - df['ts'][0]
    df['duration'] = pd.to_datetime(df['duration_ts'], unit='ns')#TODO .dt.strftime(TIME_FORMAT) Specify axis tick value for time
    return df

def prepare_pddf_battery(trace_processors):
    print("Preparing pandas data frames: battery")
    prepared_pddfs = {
        "batt_current_ua": pd.DataFrame([]),
        "batt_charge_uah": pd.DataFrame([]),
        "batt_capacity_pct": pd.DataFrame([]),
    }
    for tp in trace_processors:
        batt_qrdf = batt_query_all(trace_processors[tp])
        prepared_pddfs['batt_current_ua'] = pd.concat([prepared_pddfs['batt_current_ua'], prepare_pddf(batt_qrdf['batt_current_ua'], tp)])
        prepared_pddfs['batt_charge_uah'] = pd.concat([prepared_pddfs['batt_charge_uah'], prepare_pddf(batt_qrdf['batt_charge_uah'], tp)])
        prepared_pddfs['batt_capacity_pct'] = pd.concat([prepared_pddfs['batt_capacity_pct'], prepare_pddf(batt_qrdf['batt_capacity_pct'], tp)])
    print("For more info about energy metrics see https://perfetto.dev/docs/data-sources/battery-counters")
    print(prepared_pddfs['batt_current_ua'].head(), '\n',
          prepared_pddfs['batt_charge_uah'].head(), '\n',
          prepared_pddfs['batt_capacity_pct'].head(), '\n')
    print("Preparing pandas data frames is complete: battery")
    return prepared_pddfs

def prepare_pddf_gpu(trace_processors, device):
    prepared_pddfs = {
        "gpu_utilization": pd.DataFrame([]),
    }
    if device == PhysicalDeivces.ADRENO:
        print(f"Preparing pandas data frames: GPU {device}")
        gpu_utilization_description = None
        gpu_time_alus_working_description = None
        for tp in trace_processors:
            gpu_qrdf = gpu_query_adreno(trace_processors[tp])
            prepared_pddfs["gpu_utilization"] = pd.concat([prepared_pddfs["gpu_utilization_data"], prepare_pddf(gpu_qrdf['gpu_utilization_data'], tp)])
            prepared_pddfs["gpu_time_alus_working"] = pd.concat([prepared_pddfs["gpu_time_alus_working"], prepare_pddf(gpu_qrdf['gpu_time_alus_working_data'], tp)])
            if not gpu_utilization_description and gpu_time_alus_working_description:
                gpu_utilization_description = gpu_qrdf["gpu_utilization_details"].as_pandas_dataframe()[
                    ['name', 'description']]
                gpu_time_alus_working_description = gpu_qrdf["gpu_time_alus_working_details"].as_pandas_dataframe()[
                    ['name', 'description']]
        print(f"{gpu_utilization_description['name'][0]}: {gpu_utilization_description['description'][0]}")
        print(prepared_pddfs['gpu_utilization_data'].head())
        print(f"{gpu_time_alus_working_description['name'][0]}: {gpu_time_alus_working_description['description'][0]}")
        print(prepared_pddfs['gpu_time_alus_working_data'].head())
    elif device == PhysicalDeivces.MALI:
        print(f"Preparing pandas data frames: GPU {device}")
        for tp in trace_processors:
            gpu_qrdf = gpu_query_mali(trace_processors[tp])
            prepared_pddfs["gpu_utilization"] = pd.concat(
                [prepared_pddfs["gpu_utilization"], prepare_pddf(gpu_qrdf['gpu_utilization_data'], tp)])
    elif device == PhysicalDeivces.POWERVR:
        pass
    else:
        raise RuntimeError(f'Device {device} is not suitable')
    print("Preparing pandas data frames is complete: GPU")
    return prepared_pddfs