import matplotlib.ticker as ticker
import numpy as np

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