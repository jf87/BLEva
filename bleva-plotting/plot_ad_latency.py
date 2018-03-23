from __future__ import division
import sys
import os
import util
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
SAVEPATH = './output/'


# plot HL plot for 1285ms adv. frequency (default estimote ibeacon) and for
# balanced scanning mode (default/recommendation by Android)
def plot_hl_latency(path):
    fig, ax1 = plt.subplots()
    scan_modes = ["balanced"]
    frames = []
    for mode in scan_modes:
        frame = util.process_folder(path, filter_scan_mode=mode,
                                    filter_replicas=None,
                                    filter_benchmark='first')
        frames.append(frame)
    all_frames = pd.concat(frames)
    # TODO this does not work dependent on pandas version..
    all_frames["Advertising Interval (ms)"] = all_frames["Advertising Interval (ms)"].astype('category')
    all_frames["Phone Model"] = all_frames["Phone Model"].astype("category")
    all_frames = all_frames.rename(columns={'OS Timestamp (ms)': 'OS Timestamp (s)'})
    all_frames["OS Timestamp (s)"] = all_frames["OS Timestamp (s)"] / 1000.0
    all_frames = all_frames[(all_frames['Advertising Interval (ms)'] == 1280)]

    sns.barplot(y="Phone Model", x="OS Timestamp (s)", data=all_frames, ax=ax1)
    ax1.set_ylabel("")
    ax1.set_xlabel('Mean Time (s)')
    return fig, ax1


def save_fig(fig):
    fig.set_size_inches(6, 3)
    plt.tight_layout()
    if not os.path.exists(SAVEPATH):
        os.makedirs(SAVEPATH)
    fig.savefig(SAVEPATH + 'ad_latency.pdf', bbox_inches='tight')


if __name__ == '__main__':
    args = sys.argv[1:]
    util.set_style(font_scale=1.0)
    util.set_colors()
    if len(args) < 1:
        path = "../benchmark-results/soc/adv-prr-latency/1280ms"
    else:
        path = args[0]
    fig, ax = plot_hl_latency(path)
    # util.set_hatches_box(ax)
    save_fig(fig)
