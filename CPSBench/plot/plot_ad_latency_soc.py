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
def plot_latency(path):
    fig, ax1 = plt.subplots()
    scan_modes = ["low_latency"]
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
    all_frames["SoC"] = all_frames["SoC"].astype('category')
    all_frames = all_frames.rename(columns={'OS Timestamp (ms)': 'OS Timestamp (s)'})
    all_frames["OS Timestamp (s)"] = all_frames["OS Timestamp (s)"] / 1000.0
    all_frames = all_frames[(all_frames['Advertising Interval (ms)'] == 1280)]

    df = all_frames
    soc_list = df["SoC"].unique()
    colors = sns.color_palette("colorblind", len(soc_list))
    color_dict = dict(zip(soc_list, colors))
    tmp = df.drop_duplicates("Phone Model")
    tmp["color"] = tmp["SoC"].map(color_dict)
    soc_palette = dict(zip(tmp["Phone Model"], tmp["color"]))

    models = ['Samsung Galaxy S3', 'LG Nexus 5X', 'Motorola Nexus 6',
              'HTC One M9', 'Motorola MotoE2', 'Motorola Moto G', 'LG Nexus 4',
              'Asus Nexus 7', 'LG Nexus 5', 'LG G3']
    models = models[::-1]
    ax = sns.boxplot(y="Phone Model", x="OS Timestamp (s)", palette=soc_palette, order=models,
                       data=all_frames, ax=ax1)
    ax1.set_ylabel('')

    boxes = ax.artists

    grouped = all_frames.groupby('Phone Model')
    socs = grouped['SoC'].agg(lambda x: x.value_counts().index[0])
    socs_set = socs.unique()
    socs_plot = [socs.loc[m] for m in models]
    hatches = ('/', '+', 'x', '\\', '|', 'o')
    boxs_legend = []
    socs_legend = []
    for i, box in enumerate(boxes):
        soc_index = socs_set.tolist().index(socs_plot[i])
        print soc_index
        # Set a different hatch for each box
        box.set_edgecolor('k')
        box.set_hatch(3 * hatches[soc_index])
        box.set_facecolor(colors[soc_index])
        if socs_plot[i] not in socs_legend:
            boxs_legend.append(box)
            socs_legend.append(socs_plot[i])
    socs_legend, boxs_legend = zip(*sorted(zip(socs_legend, boxs_legend)))
    ax.legend(boxs_legend, socs_legend, loc='center right', bbox_to_anchor=(1.35, 0.5))
    return fig, ax1


def save_fig(fig):
    fig.set_size_inches(9, 5)
    plt.tight_layout()
    if not os.path.exists(SAVEPATH):
        os.makedirs(SAVEPATH)
    fig.savefig(SAVEPATH + 'ad_latency_soc.pdf', bbox_inches='tight')

if __name__ == '__main__':
    args = sys.argv[1:]
    util.set_style(font_scale=1.6)
    util.set_colors()
    if len(args) < 1:
        path = "../data/soc/adv-prr-latency/1280ms"
    else:
        path = args[0]
    fig, ax = plot_latency(path)
    save_fig(fig)
