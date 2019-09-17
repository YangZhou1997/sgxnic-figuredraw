#!/usr/bin/python3

import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib import rcParams
from collections import defaultdict
import brewer2mpl
import glob

 # brewer2mpl.get_map args: set name  set type  number of colors
bmap = brewer2mpl.get_map('Dark2', 'qualitative', 6)
colors = bmap.mpl_colors

params = {
    'axes.labelsize': 22,
    'font.size': 22,
    'legend.fontsize': 22,
    'xtick.labelsize': 22,
    'ytick.labelsize': 22,
    'text.usetex': False,
    'figure.figsize': [12, 4],
    'legend.loc': 'best'
    # 'legend.columnspacing': 0.8,
    # 'legend.handlelength'  : 1.0,
    # 'legend.handletextpad' : 0.4
}
rcParams.update(params)

linestyles = ['--', '-.', '-', ':', (0, (3, 5, 1, 5, 1, 5)), (0, (3, 1, 1, 1))]
markers = ['*', '^', 'o', 'P', 'p', 'v']
markersizes = [30, 24, 24, 24, 24, 24]

dx = 0/72.; dy = -0/72. 
offset = matplotlib.transforms.ScaledTranslation(dx, dy, plt.gcf().dpi_scale_trans)


all_framesizes = ["1500B", "6000B", "9000B"]
all_threads = ["16", "32", "48"]
curvers = [[0.7584, 1.2416, 1.3397], [0.7008, 1.175, 1.3138], [0.6975, 1.1739, 1.3105]]

# 1500,0x1,0.7584,
# 1500,0x3,1.2416,
# 1500,0x7,1.3397,
# 6000,0x1,0.7008,
# 6000,0x3,1.175,
# 6000,0x7,1.3138,
# 9000,0x1,0.6975,
# 9000,0x3,1.1739,
# 9000,0x7,1.3105,

def draw_t_trend_for_dpi_threads():

    N = len(all_threads)
    ind = np.arange(N) * 10 + 10    # the x locations for the groups    

    cnt = 0
    legends = list()
    for _curve in curvers:
        p1, = plt.plot(ind, _curve, linestyle = linestyles[cnt], marker = markers[cnt], markersize = markersizes[cnt],
            color=colors[cnt], linewidth=3)
        print(str(all_framesizes[cnt]) + ": " + str(_curve))        

        legends.append(p1)
        cnt += 1

    plt.legend(legends, all_framesizes, ncol=3)
    plt.ylabel('Throughput (Mpps)')
    plt.xticks(ind, all_threads)
    plt.xlabel('\# of hardware threads')

    # apply offset transform to all x ticklabels.
    for label in plt.axes().xaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offset)

    plt.axes().set_ylim(ymin=0, ymax=1.5)

    plt.tight_layout()
    plt.savefig('./figures/dpi_thread/t_trend_dpithread.pdf')
    plt.clf()


if __name__ == '__main__':
    plt.rc('text', usetex=True)
    font = fm.FontProperties(
       family = 'Gill Sans',
       fname = '/usr/share/fonts/truetype/adf/GilliusADF-Regular.otf')

    draw_t_trend_for_dpi_threads()