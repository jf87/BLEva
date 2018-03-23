from __future__ import division
import sys
import os
import util
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import itertools
patterns = ["*.json"]
SAVEPATH = './output/'


def get_df(path):
    scan_modes = ["balanced"]
    frames = []
    for mode in scan_modes:
        frame = util.process_folder(path, filter_scan_mode=mode,
                                    filter_benchmark="gatt")
        frames.append(frame)
    all_frames = pd.concat(frames)
    return all_frames


def save_fig(fig):
    fig.set_size_inches(6, 3)
    plt.tight_layout()
    fig.savefig(SAVEPATH + 'soc-write_latency.pdf', bbox_inches='tight')


def set_hatches_bar(ax):
    # hatches = ['//', '**', '++']
    hatches = itertools.cycle(['//', '////', '++', '--', 'xx', '\\\\', '**', 'oo', 'OO',
                               '.'])
    n = 4
    # hatch = next(hatches)
    for i, bar in enumerate(ax.patches):
            if i % n == 0:
                hatch = next(hatches)
            bar.set_hatch(hatch)


def get_socs(df):
    socs = []
    for k, v in enumerate(df["Phone Model"]):
        for va in util.PHONES:
            if util.PHONES[va]["pretty_name"] is v:
                socs.append(util.PHONES[va]["chip"])
    print socs
    print len(socs)
    return socs


def get_colors():
    return np.array([
        [0.1, 0.1, 0.1],          # black
        [0.4, 0.4, 0.4],          # very dark gray
        [0.7, 0.7, 0.7],          # dark gray
        [0.9, 0.9, 0.9],          # light gray
        [0.984375, 0.7265625, 0],  # dark yellow
        [1, 1, 0.9]               # light yellow
    ])

if __name__ == '__main__':
    args = sys.argv[1:]
    util.set_style()
    util.set_colors()
    if len(args) < 1:
        path = "../data/antenna_scheduling/all_phones/gatt/"
    else:
        path = args[0]
    df = get_df(path)
    df["Phone Model"] = df["Phone Model"].astype("category")
    df["SoC"] = df["SoC"].astype("category")
    df = df[df["Connection Interval (s)"] == 0.02]
    df = df[df["WiFi State"] == "on"]
    print df
    means = df.groupby(
        ["Phone Model", "SoC", "Operation", "Connection Interval (s)"],
        as_index=False).mean()
    means = df.dropna()
    # means = means[means["Operation"] != "Read"]
    print means

    fig, ax = plt.subplots()
    color_palette = sns.color_palette("RdBu_r", 7)
    # color_palette = sns.color_palette("colorblind", 3)
    # color_palette = sns.color_palette("cubehelix", 5)
    # colors =  get_colors()

    models = ['Samsung Galaxy S3', 'LG Nexus 5X', 'Motorola Nexus 6', 'HTC One M9',
              'Motorola MotoE2', 'Motorola Moto G', 'LG Nexus 4', 'Asus Nexus 7', 'LG Nexus 5', 'LG G3']
    models = models[::-1]
    # Plot 1 - background - "total" (top) series
    c = color_palette[6]
    # c = colors[1]
    sns.barplot(y="Phone Model", x="Time (s)", color=c, ax=ax, order=models,
                data=means[(means['Operation'] == "Write Sum")])
    topbar = plt.Rectangle((0, 0), 1, 1, fc=c, edgecolor='k')

    # Plot 2 - overlay - "bottom" series
    c = color_palette[3]
    # c = colors[2]
    sns.barplot(y="Phone Model", x="Time (s)", color=c, ax=ax, ci=None, order=models,
                data=means[(means['Operation'] == "Services Discovered Sum")])
    bottombar1 = plt.Rectangle((0, 0), 1, 1, fc=c, edgecolor='k')

    # Plot 3 - overlay - "bottom" series
    c = color_palette[1]
    # c = colors[3]
    sns.barplot(y="Phone Model", x="Time (s)", color=c, ax=ax, ci=None, order=models,
                data=means[(means['Operation'] == "Connected Sum")])
    bottombar2 = plt.Rectangle((0, 0), 1, 1, fc=c, edgecolor='k')

    # Plot 4 - foreground - "total" (top) series but pattern purpose
    grouped = df.groupby('Phone Model')
    socs = grouped['SoC'].agg(lambda x: x.value_counts().index[0])
    socs_set = socs.unique()
    socs_plot = [socs.loc[m] for m in models]
    hatches = ('/', '+', 'x', '\\', '|', 'o')
    ax2 = ax.twinx()
    ax2.get_yaxis().set_visible(False)
    bars = sns.barplot(y="Phone Model", x="Time (s)", color=c, ax=ax2,
                       order=models, data=means[(means['Operation'] == "Write Sum")])
    bars_legend = []
    socs_legend = []
    for i, bar in enumerate(bars.patches):
        soc_index = socs_set.tolist().index(socs_plot[i])
        print soc_index
        # Set a different hatch for each bar
        bar.set_facecolor((1, 1, 1, 0))
        bar.set_edgecolor('k')
        bar.set_hatch(3 * hatches[soc_index])
        if socs_plot[i] not in socs_legend:
            bars_legend.append(bar)
            socs_legend.append(socs_plot[i])
    socs_legend, bars_legend = zip(*sorted(zip(socs_legend, bars_legend)))
    ax2.legend(bars_legend, socs_legend, loc='center right', bbox_to_anchor=(1.35, 0.5))

    ax.set_ylabel("")
    ax.set_xlabel("Write Latency (s)")
    l = ax.legend([bottombar2, bottombar1, topbar],
                  ['Connected', 'Services Discovered', 'Write'], prop={'size': 12},
                  loc=9, ncol=3, bbox_to_anchor=(0.4, -0.25))
    l.draw_frame(False)
    fig.set_size_inches(6, 3)
    plt.tight_layout()
    if not os.path.exists(SAVEPATH):
        os.makedirs(SAVEPATH)
    fig.savefig("./output/write_latency_soc.pdf", bbox_inches='tight')
