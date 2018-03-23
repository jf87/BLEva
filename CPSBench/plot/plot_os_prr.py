from __future__ import division
import sys
import os
import util
# import matplotlib.patches as mpatches
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import math

patterns = ["*.json"]
SAVEPATH = './output/'


def plot_prr(path):
    frames = []
    for path in paths:
        frame = util.process_folder(path,
                                    filter_replicas=1, filter_benchmark="prr")
        frames.append(frame)
    all_frames = pd.concat(frames)
    all_frames["Advertising Interval (ms)"] = \
        all_frames["Advertising Interval (ms)"].astype('category')
    all_frames["Phone Model"] = all_frames["Phone Model"].astype('category')
    all_frames["SoC"] = all_frames["SoC"].astype('category')
    all_frames["API Version"] = all_frames["API Version"].astype('category')
    all_frames["WiFi State"] = all_frames["WiFi State"].astype('category')

    all_frames = all_frames[(all_frames["Advertising Interval (ms)"] == 160)]
    all_frames = all_frames[(all_frames["Scan Mode"] == "balanced")]
    wifi_idle = all_frames[(all_frames["WiFi State"] == "on")]

    nexus5 = wifi_idle[(wifi_idle["Phone Model"] == "LG Nexus 5")]
    nexus6 = wifi_idle[(wifi_idle["Phone Model"] == "Motorola Nexus 6")]
    nexus7 = wifi_idle[(wifi_idle["Phone Model"] == "Asus Nexus 7")]

    fig, axarr = plt.subplots(1, 3, sharey=True)
    fig.subplots_adjust(wspace=0, hspace=0)
    sns.barplot(x='PRR (%)', y="API Version", data=nexus7,
                ax=axarr[0])
    axarr[0].set_title("Asus Nexus 7", fontweight="bold")
    axarr[0].set_xlabel('Mean PRR (%)')
    axarr[0].set_ylabel('API Version')
    axarr[0].set_xlim(0, 100)

    print "\n"
    # add numbers on top of bars
    for p in axarr[0].patches:
        print "width: ", p.get_width()
        print "y: ", p.get_y()
        if math.isnan(p.get_width()):
            axarr[0].annotate('Not Available', (10, p.get_y() + 0.5))
        else:
            axarr[0].annotate('%.2f' % p.get_width(), (p.get_width() + 5, p.get_y() + 0.5))

    sns.barplot(x='PRR (%)', y="API Version", data=nexus5,
                ax=axarr[1])
    axarr[1].set_title("LG Nexus 5", fontweight="bold")
    axarr[1].set_ylabel('')
    axarr[1].set_xlabel('Mean PRR (%)')
    axarr[1].set_xlim(0, 100)

    print "\n"
    # add numbers on top of bars
    for p in axarr[1].patches:
        print "width: ", p.get_width()
        print "y: ", p.get_y()
        if math.isnan(p.get_width()):
            axarr[1].annotate('Not Available', (10, p.get_y() + 0.5))

    sns.barplot(x='PRR (%)', y="API Version", data=nexus6,
                ax=axarr[2])
    axarr[2].set_title("Motorola Nexus 6", fontweight="bold")
    axarr[2].set_ylabel('')
    axarr[2].set_xlabel('Mean PRR (%)')
    axarr[2].set_xlim(0, 100)

    print "\n"
    # add numbers on top of bars
    for p in axarr[2].patches:
        print "width: ", p.get_width()
        print "y: ", p.get_y()
        if math.isnan(p.get_width()):
            axarr[2].annotate('Not Available', (10, p.get_y() + 0.5))
#        else:
#            axarr[2].annotate('%.2f' % p.get_width(), (p.get_width() + 5, p.get_y()+0.5))

    return fig, axarr


def save_fig(fig):
    # sns.set_context(font_scale=2)
    fig.set_size_inches(8, 3)
    plt.tight_layout()
    if not os.path.exists(SAVEPATH):
        os.makedirs(SAVEPATH)
    fig.savefig(SAVEPATH + 'os_prr.pdf', bbox_inches='tight')


if __name__ == '__main__':
    args = sys.argv[1:]
    util.set_style(font_scale=1.0)
    util.set_colors()
    path = "../data/OS/connection-less"
    paths = [path]
    fig, axarr = plot_prr(paths)
    save_fig(fig)
