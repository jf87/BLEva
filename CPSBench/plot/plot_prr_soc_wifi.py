from __future__ import division
import sys
import os
import util
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

patterns = ["*.json"]
SAVEPATH = './output/'


def plot_prr(path):
    frames = []
    for path in paths:
        frame = util.process_folder(path,
                                    filter_replicas=1, filter_benchmark="prr")
        frames.append(frame)
    all_frames = pd.concat(frames)
    print all_frames
    all_frames["Advertising Interval (ms)"] = \
        all_frames["Advertising Interval (ms)"].astype('category')
    all_frames["Phone Model"] = all_frames["Phone Model"].astype('category')
    all_frames["SoC"] = all_frames["SoC"].astype('category')
    all_frames["WiFi State"] = all_frames["WiFi State"].astype('category')

    all_frames = all_frames[(all_frames["Advertising Interval (ms)"] == 160)]
    all_frames = all_frames[(all_frames["Scan Mode"] == "balanced")]

    wifion = all_frames[(all_frames["WiFi State"] == "on")]
    print wifion
    wifiactive = all_frames[(all_frames["WiFi State"] == "active")]
    print wifiactive
    fig, axarr = plt.subplots(1, 2, sharey='row', figsize=(10, 4))

    # fig.subplots_adjust(wspace=0, hspace=0)
    models = ['Samsung Galaxy S3', 'LG Nexus 5X', 'Motorola Nexus 6', 'HTC One M9',
              'Motorola MotoE2', 'Motorola Moto G', 'LG Nexus 4', 'Asus Nexus 7', 'LG Nexus 5', 'LG G3']
    models = models[::-1]
    bars = sns.barplot(x='PRR (%)', y="Phone Model", data=wifion, order=models,
                       ax=axarr[0])
#    axarr[0].legend_.remove() #(frameon=True, framealpha=1, edgecolor='0')
    axarr[0].set_title("WiFi Idle", fontweight="bold")
    axarr[0].set_ylabel('')
    axarr[0].set_xlabel('Mean PRR (%)')
    axarr[0].set_xlim(0, 100)

    grouped = wifion.groupby('Phone Model')
    socs = grouped['SoC'].agg(lambda x: x.value_counts().index[0])
    socs_set = socs.unique()
    socs_plot = [socs.loc[m] for m in models]
    hatches = ('/', '+', 'x', '\\', '|', 'o')
    colors = sns.color_palette("colorblind", len(socs_set))

    bars_legend = []
    socs_legend = []
    for i, bar in enumerate(bars.patches):
        soc_index = socs_set.tolist().index(socs_plot[i])
        # Set a different hatch for each bar
        bar.set_edgecolor('k')
        bar.set_hatch(3 * hatches[soc_index])
        bar.set_facecolor(colors[soc_index])
        if socs_plot[i] not in socs_legend:
            bars_legend.append(bar)
            socs_legend.append(socs_plot[i])
    # socs_legend, bars_legend = zip(*sorted(zip(socs_legend, bars_legend)))
    # axarr[0].legend(bars_legend, socs_legend, loc='center right', frameon=True, framealpha=1, edgecolor='0')

    bars = sns.barplot(x='PRR (%)', y="Phone Model", data=wifiactive, order=models,
                       ax=axarr[1])
    axarr[1].set_title("WiFi Active", fontweight="bold")
    axarr[1].set_ylabel('')
    axarr[1].set_xlabel('Mean PRR (%)')
    axarr[1].set_xlim(0, 100)

    bars_legend = []
    socs_legend = []
    for i, bar in enumerate(bars.patches):
        soc_index = socs_set.tolist().index(socs_plot[i])
        # Set a different hatch for each bar
        bar.set_edgecolor('k')
        bar.set_hatch(3 * hatches[soc_index])
        bar.set_facecolor(colors[soc_index])
        if socs_plot[i] not in socs_legend:
            bars_legend.append(bar)
            socs_legend.append(socs_plot[i])
    socs_legend, bars_legend = zip(*sorted(zip(socs_legend, bars_legend)))
    axarr[1].legend(bars_legend, socs_legend, loc='center right', frameon=True, framealpha=1, edgecolor='0')

    return fig, axarr


def save_fig(fig):
    # sns.set_context(font_scale=2)
    fig.set_size_inches(12, 5.5)
    plt.tight_layout()
    if not os.path.exists(SAVEPATH):
        os.makedirs(SAVEPATH)
    fig.savefig(SAVEPATH + 'prr_soc_wifi.pdf', bbox_inches='tight')


if __name__ == '__main__':
    args = sys.argv[1:]
    util.set_style(font_scale=1.4)
    util.set_colors()
    wifi_active = "../data/antenna_scheduling/all_phones"
    wifi_on = "../data/soc/gatt"
    paths = [wifi_active]
    fig, axarr = plot_prr(paths)
    save_fig(fig)
