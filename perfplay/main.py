import os

import pandas as pd
import numpy as np
import math
import yaml


_space = "-" * 100


def parce_yaml(yaml_file):
    with open(yaml_file, "r") as tree_file:
        tree = yaml.safe_load(tree_file)
    return tree


def collect_df(log_root, name_substring):
    pddfs = []
    corrupted_paths = []
    for path in os.listdir(log_root):
        if "events.log" in path:
            continue
        if name_substring in path:
            try:
                # dropna(axis=1, how="all") - drop nan column only https://saturncloud.io/blog/how-to-drop-columns-with-all-nans-in-pandas-a-data-scientists-guide/#:~:text=To%20drop%20columns%20with%20all%20NaN's%20in%20Pandas%2C%20we%20can,to%200%2C%20it%20drops%20rows.
                pddfs.append(pd.read_csv(os.path.join(log_root, path)).dropna(axis=1, how="all"))
            except:
                corrupted_paths.append(path)
                print(f"{path} are not loaded")
                continue
    result_df = pd.concat(pddfs) #TODO need to customize contact call
    result_df.fillna(0)
    return result_df, corrupted_paths


def collect_metric(pddf, metric_key):
    metric = pddf[metric_key].dropna()
    aggr = {
            'describe': metric.describe(),
            # 'min': metrics[metric_key].min(),
            # 'mean': metrics[metric_key].mean(),
            # 'max': metrics[metric_key].max(),
        }
    return metric, aggr


def walk_metrics_tree(tree, pddf):
    metrics = {}
    aggrs = {}
    def walk(node, pddf):
        for key, item in node.items():
            if type(item) is dict:
                metric_data = collect_metric(pddf, key)
                metrics[key] = metric_data[0]
                aggrs[key] = metric_data[1]
                walk(item, pddf)
    walk(tree, pddf)
    return metrics, aggrs


def compare_stat_delta(left, right): # **args?s
    delta_for_metrics = {}
    for metric in left:
        print(_space)
        print(metric)
        delta_for_metrics[metric] = {}
        for stat in left[metric]:
            print(stat)
            delta_for_metrics[metric][stat] = {}
            for i in left[metric][stat].index:
                delta_for_metrics[metric][stat][i] = {}
                try:
                    delta_for_metrics[metric][stat][i] = {
                        'left': left[metric][stat][i],
                        'right': right[metric][stat][i],
                        'delta': abs(left[metric][stat][i] - right[metric][stat][i])
                    }
                    print(f"{i}:\n\t{delta_for_metrics[metric][stat][i]}")
                except:
                    delta_for_metrics[metric][stat] = None
                    print(f"{i}: not enough data")
        print(_space)
    return delta_for_metrics


def research_compared_stat(compare_stat, metric_tree, metrics_inaccuracy):
    def walk(node):
        for key, item in node.items():
            if type(item) is dict:
                #TODO fix cycle walking thought all stats
                affected = False
                for stat in compare_stat[key]['describe']:
                    try:
                        if metrics_inaccuracy[key][stat]:
                            affected = compare_stat[key]['describe'][stat]['delta'] > metrics_inaccuracy[key][stat]
                    except:
                        print(f"{key}.{stat} Not enough data")
                        continue
                if not affected:
                    print(f"{key} are not affected")
                    continue
                print(f"{key} has been affected")
                print(f"\tdelta: {compare_stat[key]['describe']}, inaccuracy {metrics_inaccuracy[key]}")
                walk(item)
    walk(metric_tree)


if __name__ == '__main__':
    log_root1 = "logs"
    log_root2 = "logs1"
    name_substring = "_thread_"
    metrics_tree_file = 'metrics_tree.yaml'
    metrics_inaccuracy_file = 'metrics_inaccuracy.yaml'
    metrics_tree = parce_yaml(metrics_tree_file)
    metrics_inaccuracy = parce_yaml(metrics_inaccuracy_file)

    pddf1 = collect_df(log_root1, name_substring)[0]
    pddf2 = collect_df(log_root2, name_substring)[0]

    resul1 = walk_metrics_tree(metrics_tree, pddf1)
    resul2 = walk_metrics_tree(metrics_tree, pd.concat([pddf1, pddf2]))

    delta = compare_stat_delta(resul1[1], resul2[1])
    research_compared_stat(delta, metrics_tree, metrics_inaccuracy)
