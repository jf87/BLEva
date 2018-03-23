from __future__ import division
import os
import util
import matplotlib.pyplot as plt
import numpy as np
SAVEPATH = './output/'


def plot_rssi():
    path = "../benchmark-results/rssi"
    df = util.process_folder(path, filter_benchmark='rssi')
    # df = df[(df["Phone Model"] == "Motorola MotoE2")]
    df = df[(df['RSSI (dBm)'] < 0)]
    df["Phone Model"] = df["Phone Model"].astype("category")
    d = get_distances(df["RSSI (dBm)"])
    df["Estimated Distance (m)"] = d

    df = df[(df['Distance (m)'] == 1.0) |
            (df['Distance (m)'] == 05.0) |
            (df['Distance (m)'] == 10.0) |
            (df['Distance (m)'] == 20.0)]

#    # figure 6 all distances
#    plt.figure(figsize=(10, 4))
#    g = sns.pointplot(x="Distance (m)", y="RSSI (dBm)", hue="Phone Model", markers=['.','v','^','<','>','*','s','h','+','d'], data=df, ci=None) #, size=10, aspect=2.0, legend=False)
#    # Now add the legend with some customizations.
#    #plt.legend(bbox_to_anchor=(0.45, -0.1), loc="upper center", ncol=4)
#    #ax.set_title("Distance = 1 m", fontweight="bold")
#    plt.ylabel('RSSI (dBm)')
#    plt.xlabel('Distance (m)')
#
#    # ref: http://stackoverflow.com/a/10154763/1843698
#    handles, labels = plt.gca().get_legend_handles_labels()
#    lgd = plt.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.45,-0.2), ncol=5, fontsize=10)
#    g.get_figure().savefig(SAVEPATH+'rssi-line-distance.pdf', bbox_extra_artists=(lgd,), bbox_inches='tight')
# figure 1b 4 distances
    plt.figure(figsize=(10, 5))
    markers = ['p', 'v', '^', '<', '>', '*', 's', 'h', 'P', 'd']
    linestyles = ['-', '--', '-.', ':']
    models = ['Asus Nexus 7', 'HTC One M9', 'LG G3', 'LG Nexus 4',
              'LG Nexus 5', 'LG Nexus 5X', 'Motorola Moto G',
              'Motorola MotoE2', 'Motorola Nexus 6', 'Samsung Galaxy S3']
    for i in range(len(models)):
        m = models[i]
        df_sub = df[(df['Phone Model'] == m)]
        grouped = df_sub.groupby('Distance (m)')['RSSI (dBm)'].mean()
        print m
        print markers[i]
        grouped.plot(x='Distance (m)', y="RSSI (dBm)", marker=markers[i],
                     linestyle=linestyles[i % len(linestyles)], label=m)  # , size=10, aspect=2.0, legend=False)
    # Now add the legend with some customizations.
    # plt.legend(bbox_to_anchor=(0.45, -0.1), loc="upper center", ncol=4)
    # ax.set_title("Distance = 1 m", fontweight="bold")
    plt.ylabel('RSSI (dBm)')
    plt.xlabel('Distance (m)')
    plt.xlim(0, 21)

    # ref: http://stackoverflow.com/a/10154763/1843698
    handles, labels = plt.gca().get_legend_handles_labels()
    lgd = plt.legend(handles, labels, loc='center right', bbox_to_anchor=(1.43, 0.5))
    if not os.path.exists(SAVEPATH):
        os.makedirs(SAVEPATH)
    plt.savefig(SAVEPATH + 'rssi_vs_true_dist.pdf', bbox_extra_artists=(lgd,), bbox_inches='tight')

#    sns.plt.show()


#    # Box plot
#    plt.figure(figsize=(10, 4))
#    g = sns.boxplot(x="Distance (m)", y="RSSI (dBm)", hue="Phone Model", data=df_sub) #, size=10, aspect=2.0, legend=False)
#    # Now add the legend with some customizations.
#    #plt.legend(bbox_to_anchor=(0.45, -0.1), loc="upper center", ncol=4)
#    #ax.set_title("Distance = 1 m", fontweight="bold")
#    plt.ylabel('RSSI (dBm)')
#    plt.xlabel('Distance (m)')
#
#    # ref: http://stackoverflow.com/a/10154763/1843698
#    handles, labels = plt.gca().get_legend_handles_labels()
#    lgd = plt.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.45,-0.2), ncol=5, fontsize=10)
#    g.get_figure().savefig(SAVEPATH+'rssi-box-distance-4.pdf', bbox_extra_artists=(lgd,), bbox_inches='tight')
#
#
#    # Bar plot
#    plt.figure(figsize=(10, 4))
#    g = sns.pointplot(x="Distance (m)", y="RSSI (dBm)", hue="Phone Model", data=df_sub) #, size=10, aspect=2.0, legend=False)
#    # Now add the legend with some customizations.
#    #plt.legend(bbox_to_anchor=(0.45, -0.1), loc="upper center", ncol=4)
#    #ax.set_title("Distance = 1 m", fontweight="bold")
#    plt.ylabel('RSSI (dBm)')
#    plt.xlabel('Distance (m)')
#
#    # ref: http://stackoverflow.com/a/10154763/1843698
#    handles, labels = plt.gca().get_legend_handles_labels()
#    lgd = plt.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.45,-0.2), ncol=5, fontsize=10)
#    g.get_figure().savefig(SAVEPATH+'rssi_vs_true_dist.pdf', bbox_extra_artists=(lgd,), bbox_inches='tight')


def get_distances(rssis):
    # rssis = np.asarray(rssis)
    print rssis
    alpha = 1.7  # Environment factor
    rssi_0 = -74  # Estimote reference RSSI
    p = (rssis - rssi_0) / (-10.0 * alpha)
    d = np.power(10., p)
    return d


if __name__ == '__main__':
    style_rc = {'lines.linewidth': 2, 'lines.markersize': 10}
    util.set_style(font_scale=1.7, style_rc=style_rc)
    util.set_colors()
    plot_rssi()
