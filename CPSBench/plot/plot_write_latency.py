#! /usr/bin/env python2
from __future__ import division
import sys
import os
import util
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

patterns = ["*.json"]
SAVEPATH = './output/'


def plot_hl_write(path):
    scan_modes = ["balanced"]
    frames = []
    for mode in scan_modes:
        frame = util.process_folder(
            path, filter_scan_mode=mode, filter_benchmark="gatt")
        frames.append(frame)
    all_frames = pd.concat(frames)
    # util.print_full(all_frames.groupby(['Operation', 'Connection Interval
    # (s)', 'Phone Model']).mean())
    # util.print_full(all_frames.groupby(['Operation', 'Connection Interval
    # (s)', 'Phone Model']).median())
    all_frames["Phone Model"] = all_frames["Phone Model"].astype("category")
    # all_frames = all_frames[all_frames["Connection Interval (s)"] == 0.32]
    print all_frames
    means = all_frames.groupby(
        ["Phone Model", "Operation", "Connection Interval (s)"],
        as_index=False).mean()
    means = means[means["Operation"] != "Read"]
    print means
    sums = means.groupby(["Phone Model"], as_index=False).sum()
    print sums
    fig, ax1 = plt.subplots()
    wifion_20ms_write = all_frames[(all_frames['Operation'] == 'Write Sum') & (
        all_frames['Connection Interval (s)'] == 0.02) &
                                   (all_frames['WiFi State'] == 'on')]
    print wifion_20ms_write

    sns.barplot(x="Time (s)", y="Phone Model", data=wifion_20ms_write, ax=ax1)
    ax1.set_ylabel('')
    ax1.set_xlabel('Mean Time (s)')
    return fig, ax1


def save_fig(fig):
    fig.set_size_inches(6, 3)
    plt.tight_layout()
    if not os.path.exists(SAVEPATH):
        os.makedirs(SAVEPATH)
    fig.savefig(SAVEPATH + 'write_latency.pdf', bbox_inches='tight')


if __name__ == '__main__':
    args = sys.argv[1:]
    util.set_style()
    util.set_colors()
    if len(args) < 1:
        path = "../data/antenna_scheduling/all_phones/gatt/"
    else:
        path = args[0]
    fig, ax = plot_hl_write(path)
    save_fig(fig)
