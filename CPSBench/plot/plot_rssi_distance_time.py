from __future__ import division
import os
import util
import matplotlib.pyplot as plt
import seaborn as sns
SAVEPATH = './output/'


def plot_rssi():
    path = "../data/rssi"
    df = util.process_folder(path, filter_benchmark='rssi')
    df = df[(df['RSSI (dBm)'] < 0)]
    df["Phone Model"] = df["Phone Model"].astype("category")
    util.set_style(font_scale=1.7)
    util.set_colors()

    # figure 2a
    fig, axarr = plt.subplots(1, 2, sharey='row', figsize=(12, 5.5))

    models = ['Samsung Galaxy S3', 'LG Nexus 5X', 'Motorola Nexus 6', 'HTC One M9',
              'Motorola MotoE2', 'Motorola Moto G', 'LG Nexus 4', 'Asus Nexus 7',
              'LG Nexus 5', 'LG G3']
    models = models[::-1]
    sns.pointplot(x="RSSI (dBm)", y="Phone Model", order=models, hue="Time of Day",
                  hue_order=['Morning', 'Noon', 'Afternoon', 'Night'],
                  markers=['*', '^', '.', 'x'], data=df[(df['Distance (m)'] == 1.0)],
                  join=False, ci=None, ax=axarr[0])  # , size=10, aspect=2.0, legend=False)
    # Now add the legend with some customizations.
    axarr[0].legend(loc='best', frameon=True, framealpha=1, edgecolor='0', fontsize=14)
    axarr[0].set_title("Distance = 1 m", fontweight="bold")
    axarr[0].set_ylabel('')
    axarr[0].set_xlabel('RSSI (dBm)')
    axarr[0].set_xlim(-110, -50)

    sns.pointplot(x="RSSI (dBm)", y="Phone Model", order=models, hue="Time of Day",
                  hue_order=['Morning', 'Noon', 'Afternoon', 'Night'],
                  markers=['*', '^', '.', 'x'], data=df[(df['Distance (m)'] == 10.0)],
                  join=False, ci=None, ax=axarr[1])  # , size=10, aspect=2.0, legend=False)
    # Now add the legend with some customizations.
    axarr[1].legend_.remove()  # (frameon=True, framealpha=1, edgecolor='0')
    axarr[1].set_title("Distance = 10 m", fontweight="bold")
    axarr[1].set_ylabel('')
    axarr[1].set_xlabel('RSSI (dBm)')
    axarr[1].set_xlim(-110, -50)

    fig.tight_layout()
    if not os.path.exists(SAVEPATH):
        os.makedirs(SAVEPATH)
    fig.savefig(SAVEPATH + 'rssi_distance_time.pdf')


if __name__ == '__main__':
    plot_rssi()
