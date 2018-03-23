from __future__ import division
import numpy as np
import sys
import os
import util
# import matplotlib.patches as mpatches
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

patterns = ["*.json"]
SAVEPATH = './output/'


def plot_prr(path):
    # scan_modes = ["low_power", "balanced","low_latency"]
    scan_modes = ["balanced"]
    frames = []
    for mode in scan_modes:
        frame = util.process_folder(path, filter_scan_mode=mode,
                                    filter_replicas=1, filter_benchmark="prr")
        frames.append(frame)
    all_frames = pd.concat(frames)
    all_frames["Advertising Interval (ms)"] = all_frames["Advertising Interval (ms)"].astype('category')
    all_frames["Phone Model"] = all_frames["Phone Model"].astype('category')
    all_frames["SoC"] = all_frames["SoC"].astype('category')
    # hard code models so same chips stay together
    models = ['Samsung Galaxy S3', 'LG Nexus 5X', 'Motorola Nexus 6', 'HTC One M9',
              'Motorola MotoE2', 'Motorola Moto G', 'LG Nexus 4', 'Asus Nexus 7',
              'LG Nexus 5', 'LG G3']
    pos = np.arange(len(models)) + .5
    grouped = all_frames.groupby('Phone Model')
    vals = grouped['PRR (%)'].agg([np.mean, np.std])
    socs = grouped['SoC'].agg(lambda x: x.value_counts().index[0])
    socs_set = socs.unique()
    print socs

    vals_plot = [vals.loc[m, 'mean'] for m in models]
    errs_plot = [vals.loc[m, 'std'] for m in models]
    socs_plot = [socs.loc[m] for m in models]
    print vals_plot
    print errs_plot

    # get palette
    colors = sns.color_palette("colorblind", len(socs_set))

    # get patterns
    patterns = ('-', '+', 'x', '\\', '|', 'o', 'O', '.')

    fig, ax = plt.subplots(1)
    fig.subplots_adjust(wspace=0, hspace=0)
    bars = plt.barh(pos, vals_plot, xerr=errs_plot, align='center', edgecolor='k')
    bars_legend = []
    socs_legend = []
    for i in range(len(bars)):
        soc_index = socs_set.tolist().index(socs_plot[i])
        pattern = 3 * patterns[soc_index]
        color = colors[soc_index]
        bars[i].set_hatch(pattern)
        bars[i].set_facecolor(color)
        if socs_plot[i] not in socs_legend:
            bars_legend.append(bars[i])
            socs_legend.append(socs_plot[i])
    plt.yticks(pos, models)
    socs_legend, bars_legend = zip(*sorted(zip(socs_legend, bars_legend)))
    plt.legend(bars_legend, socs_legend, loc="upper right", frameon=True,
               framealpha=1, edgecolor='0')  # bbox_to_anchor = (1.37, 0.8))
    # ax.set_title("Scan Mode = balanced", fontweight="bold")
    ax.set_ylabel('')
    ax.set_xlabel('Mean PRR (%)')
    ax.set_xlim(0, 100)
    return fig, ax


def save_fig(fig):
    # sns.set_context(font_scale=2)
    fig.set_size_inches(8, 4)
    plt.tight_layout()
    if not os.path.exists(SAVEPATH):
        os.makedirs(SAVEPATH)
    fig.savefig(SAVEPATH + 'prr_soc.pdf', bbox_inches='tight')

if __name__ == '__main__':
    args = sys.argv[1:]
    util.set_style(font_scale=1.3)
    util.set_colors()
    if len(args) < 1:
        path = "../benchmark-results/soc/adv-prr-latency/1280ms"
    else:
        path = args[0]
    fig, ax = plot_prr(path)
    save_fig(fig)
