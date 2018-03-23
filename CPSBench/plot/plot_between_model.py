from __future__ import division
import os
import util
import matplotlib.pyplot as plt
import seaborn as sns
SAVEPATH = './output/'


def add_phone_id(df, id_map):
    return df


def plot_rssi():
    # get dataframe for RSSI
    path_rssi = "../data/rssi"
    df_rssi = util.process_folder(path_rssi, filter_benchmark='rssi')
#    df_rssi["Phone Model"] = df_rssi["Phone Model"].astype("category")
    df_rssi = df_rssi[(df_rssi['RSSI (dBm)'] < 0)]
    id_map = {}  # {phone model: [next_id, {old id : new id}}]
    # add phone id
    df_rssi = df_rssi[(df_rssi["Phone Model"].isin([
        "Asus Nexus 7", "LG Nexus 5", "Motorola MotoE2", "Motorola Nexus 6"])) &
        (df_rssi['Device ID'] != 'unknown')]
    df_rssi['Phone ID'] = ""
    df_rssi.index = range(len(df_rssi))
    for index, row in df_rssi.iterrows():
        model = row['Phone Model']
        if model not in id_map:
            id_map[model] = [1, {}]
        device = row['Device ID']
        if device not in id_map[model][1]:
            id_map[model][1][device] = "Phone " + str(id_map[model][0])
            id_map[model][0] += 1
        df_rssi.set_value(index, 'Phone ID', id_map[model][1][device])

    # get dataframe for latency
    path_latency = "../data/soc/adv-prr-latency/1280ms"
    df_latency = util.process_folder(path_latency, filter_scan_mode="balanced",
                                     filter_replicas=None,
                                     filter_benchmark='first')
    # df_latency["Phone Model"] = df_latency["Phone Model"].astype("category")
    df_latency = df_latency.rename(columns={'OS Timestamp (ms)': 'OS Timestamp (s)'})
    df_latency["OS Timestamp (s)"] = df_latency["OS Timestamp (s)"] / 1000.0
    # add phone id
    df_latency = df_latency[(df_latency["Phone Model"].isin([
        "Asus Nexus 7", "LG Nexus 5", "Motorola MotoE2", "Motorola Nexus 6"])) &
        (df_latency['Device ID'] != 'unknown')]
    df_latency['Phone ID'] = ""
    df_latency.index = range(len(df_latency))
    for index, row in df_latency.iterrows():
        model = row['Phone Model']
        if model not in id_map:
            id_map[model] = [1, {}]
        device = row['Device ID']
        if device not in id_map[model][1]:
            id_map[model][1][device] = "Phone " + str(id_map[model][0])
            id_map[model][0] += 1
        df_latency.set_value(index, 'Phone ID', id_map[model][1][device])

    print df_rssi["Phone Model"].unique()
    print df_latency["Phone Model"].unique()
    print id_map

    # figure 12
    # sns.set_context("paper")
    # sns.set(style="whitegrid", font_scale=1.5)
    fig, axarr = plt.subplots(1, 2, sharey='row', figsize=(10, 4))
    # fig.subplots_adjust(wspace=0, hspace=0)
    print df_rssi[(df_rssi['Distance (m)'] == 1.0)]
    hue_order = sorted(df_rssi['Phone ID'].unique())
    df_rssi["Phone Model"] = df_rssi["Phone Model"].astype("category")
    sns.boxplot(x="RSSI (dBm)", y="Phone Model", data=df_rssi[(
        df_rssi['Distance (m)'] == 1.0)], hue="Phone ID", hue_order=hue_order,
        ax=axarr[0])  # , size=10, aspect=2.0, legend=False)
    # Now add the legend with some customizations.
    axarr[0].legend_.remove()  # (frameon=True, framealpha=1, edgecolor='0')
    axarr[0].set_title("Distance = 1 m", fontweight="bold")
    axarr[0].set_ylabel('')
    axarr[0].set_xlabel('RSSI (dBm)')
    axarr[0].set_xlim(-110, -50)

    df_latency["Phone Model"] = df_latency["Phone Model"].astype("category")
    sns.boxplot(x="OS Timestamp (s)", y="Phone Model", data=df_latency,
                hue="Phone ID", hue_order=hue_order, ax=axarr[1])  # , size=10, aspect=2.0, legend=False)
    # Now add the legend with some customizations.
    axarr[1].legend_.remove()  # (frameon=True, framealpha=1, edgecolor='0')
    axarr[1].set_title("Scan Mode = balanced", fontweight="bold")
    axarr[1].set_ylabel('')
    axarr[1].set_xlabel('OS Timestamp (s)')
    # axarr[1].set_xlim(-110, )

    fig.tight_layout()
    if not os.path.exists(SAVEPATH):
        os.makedirs(SAVEPATH)
    fig.savefig(SAVEPATH + 'between_model.pdf')


if __name__ == '__main__':
    util.set_style(font_scale=1.5)
    util.set_colors()
    plot_rssi()
