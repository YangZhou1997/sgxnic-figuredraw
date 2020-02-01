#!/usr/bin/python3

import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib import rcParams
from collections import defaultdict
import glob
from util_patterns import *

params = {
    'axes.labelsize': 18,
    'font.size': 18,
    'legend.fontsize': 18,
    'xtick.labelsize': 18,
    'ytick.labelsize': 18,
    'text.usetex': False,
    'figure.figsize': [12, 4],
    'legend.loc': 'best'
}
rcParams.update(params)

legends_launch = ["TLB setup \&config. reading", "Blacklisting", "SHA-256 digesting"]
legends_destroy = ["Whitelisting", "Memory scrubing"]

nfs = ["FW", "DPI", "NAT", "LB", "LPM", "Mon."]
def format_func(value, tick_number):
    return nfs[tick_number]
    
# nf_launch
# nf_destroy
latencies = np.array([
            [0.019615, 0.004425, 38.082837], 
            [0.003783, 2.704083, 0], 
            [0.019615, 0.004425, 323.602302], 
            [0.003783, 22.983011, 0], 
            [0.019616, 0.004425, 145.944469], 
            [0.003783, 10.364937, 0], 
            [0.019616, 0.004425, 29.622514], 
            [0.003783, 2.103230, 0], 
            [0.019615, 0.004425, 95.187180], 
            [0.003783, 6.759915, 0], 
            [0.019615, 0.004425, 763.517971], 
            [0.003783, 54.227230, 0]], np.float64)



if __name__ == '__main__':
    plt.rc('text', usetex=True)
    # plt.rc('font', family='Gill Sans')
    font = fm.FontProperties(
       family = 'Gill Sans',
       fname = '/usr/share/fonts/truetype/adf/GilliusADF-Regular.otf')

    N = 6

    ind = np.arange(N) * 10 + 5    # the x locations for the groups

    # print ind
    width = 3.5       # the width of the bars: can also be len(x) sequence
    
    ax1 = plt.subplot(121)
    p1 = ax1.bar(ind, latencies[:, 0][::2], width, label=legends_launch[0], bottom=latencies[:, 1][::2]+latencies[:, 2][::2], color=colors[0], hatch=patterns[0], align="center", edgecolor = 'k')
    p2 = ax1.bar(ind, latencies[:, 1][::2], width, label=legends_launch[1], bottom=latencies[:, 2][::2], color=colors[1], hatch=patterns[1], align="center", edgecolor = 'k')
    p3 = ax1.bar(ind, latencies[:, 2][::2], width, label=legends_launch[2], color=colors[2], hatch=patterns[2], align="center", edgecolor = 'k')
    
    # ax1.set_title(r"\textsf{nf\_launch}")
    ax1.set_ylabel('Latency (ms)')
    ax1.set_xticks(ind)
    ax1.xaxis.set_major_formatter(plt.FuncFormatter(format_func))

    dx = 0/72.; dy = -5/72. 
    offset = matplotlib.transforms.ScaledTranslation(dx, dy, plt.gcf().dpi_scale_trans)    
    # apply offset transform to all x ticklabels.
    for label in ax1.xaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offset)
    ax1.grid(which='major', axis='y', linestyle=':')
    ax1.set_axisbelow(True)

    # plt.yticks(np.arange(0, 81, 10))
    # ax1.xticks(rotation = 35, ha="right", rotation_mode="anchor")
    

    ax2 = plt.subplot(122)
    p1 = ax2.bar(ind, latencies[:, 0][1::2], width, label=legends_destroy[0], bottom=latencies[:, 1][1::2], color=colors[3], hatch=patterns[3], align="center", edgecolor = 'k')
    p4 = ax2.bar(ind, latencies[:, 1][1::2], width, label=legends_destroy[1], color=colors[4], hatch=patterns[4], align="center", edgecolor = 'k')
    
    # ax2.set_title(r"\textsf{nf\_destroy}")
    ax2.set_ylabel('Latency (ms)')
    ax2.set_xticks(ind)
    ax2.xaxis.set_major_formatter(plt.FuncFormatter(format_func))

    for label in ax2.xaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offset)
    ax2.grid(which='major', axis='y', linestyle=':')
    ax2.set_axisbelow(True)

    # ax2.yticks(np.arange(0, 81, 10))
    # ax2.xticks(rotation = 35, ha="right", rotation_mode="anchor")
    
    
    lines_labels = [ax1.get_legend_handles_labels()]
    lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]
    l = ax1.legend(lines, labels, title=r"\textsf{nf\_launch}")
    l.get_title().set_position((-41, 0))

    lines_labels = [ax2.get_legend_handles_labels()]
    lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]
    ax2.legend(lines, labels, title=r"\textsf{nf\_destroy}")

    plt.tight_layout()

    plt.savefig('figures/ins_latency/ins_latency.pdf')
    plt.clf()
