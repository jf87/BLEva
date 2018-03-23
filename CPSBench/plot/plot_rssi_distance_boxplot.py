from __future__ import division
import os
import util
import matplotlib.pyplot as plt
import seaborn as sns
SAVEPATH = './output/'


def plot_rssi():
    path = "../data/rssi"
    df = util.process_folder(path, filter_benchmark='rssi')
    # df = df[(df["Phone Model"] == "Motorola MotoE2")]
    # sns.set_context("paper")
    df = df[(df['RSSI (dBm)'] < 0)]
    # sns.set_context("paper")
    # sns.set_style("whitegrid")
    df["Phone Model"] = df["Phone Model"].astype("category")
    # sns.set(style="whitegrid", font_scale=1)
    util.set_style(font_scale=1.7)
    util.set_colors()

    # figure 2b
    fig, axarr = plt.subplots(1, 2, sharey='row', figsize=(12, 5.5))
    # fig.subplots_adjust(wspace=0, hspace=0)

    models = ['Samsung Galaxy S3', 'LG Nexus 5X', 'Motorola Nexus 6', 'HTC One M9',
              'Motorola MotoE2', 'Motorola Moto G', 'LG Nexus 4', 'Asus Nexus 7', 'LG Nexus 5', 'LG G3']
    models = models[::-1]
    grouped = df.groupby('Phone Model')
    socs = grouped['SoC'].agg(lambda x: x.value_counts().index[0])
    socs_set = socs.unique()
    socs_plot = [socs.loc[m] for m in models]
    hatches = ('/', '+', 'x', '\\', '|', 'o')
    colors = sns.color_palette("colorblind", len(socs_set))

    ax = sns.boxplot(x="RSSI (dBm)", y="Phone Model", data=df[(df['Distance (m)'] == 1.0)],
                     order=models, ax=axarr[0])  # , size=10, aspect=2.0, legend=False)
    # Now add the legend with some customizations.
    # axarr[0].legend(frameon=True, framealpha=1, edgecolor='0')
    axarr[0].set_title("Distance = 1 m", fontweight="bold")
    axarr[0].set_ylabel('')
    axarr[0].set_xlabel('RSSI (dBm)')
    axarr[0].set_xlim(-110, -50)

    for i, box in enumerate(ax.artists):
        soc_index = socs_set.tolist().index(socs_plot[i])
        # Set a different hatch for each box
        box.set_edgecolor('k')
        box.set_hatch(3 * hatches[soc_index])
        box.set_facecolor(colors[soc_index])

    ax = sns.boxplot(x="RSSI (dBm)", y="Phone Model", data=df[(df['Distance (m)'] == 10.0)],
                     order=models, ax=axarr[1])  # , size=10, aspect=2.0, legend=False)
    # Now add the legend with some customizations.
    # axarr[1].legend(frameon=True, framealpha=1, edgecolor='0')
    axarr[1].set_title("Distance = 10 m", fontweight="bold")
    axarr[1].set_ylabel('')
    axarr[1].set_xlabel('RSSI (dBm)')
    axarr[1].set_xlim(-110, -50)

    boxs_legend = []
    socs_legend = []
    for i, box in enumerate(ax.artists):
        soc_index = socs_set.tolist().index(socs_plot[i])
        # Set a different hatch for each box
        box.set_edgecolor('k')
        box.set_hatch(3 * hatches[soc_index])
        box.set_facecolor(colors[soc_index])
        if socs_plot[i] not in socs_legend:
            boxs_legend.append(box)
            socs_legend.append(socs_plot[i])
    socs_legend, boxs_legend = zip(*sorted(zip(socs_legend, boxs_legend)))
    ax.legend(boxs_legend, socs_legend, loc='best', frameon=True, framealpha=1,
              edgecolor='0', fontsize=14)  # , bbox_to_anchor = (1.35, 0.5))
    fig.tight_layout()
    if not os.path.exists(SAVEPATH):
        os.makedirs(SAVEPATH)
    fig.savefig(SAVEPATH + 'rssi_distance_boxplot.pdf')


if __name__ == '__main__':
    plot_rssi()
