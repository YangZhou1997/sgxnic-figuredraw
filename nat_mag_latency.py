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
bmap = brewer2mpl.get_map('Dark2', 'qualitative', 8)
# bmap = brewer2mpl.get_map('Paired', 'qualitative', 12)
colors = bmap.mpl_colors

params = {
    'axes.labelsize': 22,
    'font.size': 22,
    'legend.fontsize': 22,
    'xtick.labelsize': 22,
    'ytick.labelsize': 22,
    'text.usetex': False,
    'figure.figsize': [12, 5],
    'legend.loc': 'best'
    # 'legend.columnspacing': 0.8,
    # 'legend.handlelength'  : 1.0,
    # 'legend.handletextpad' : 0.4
}
rcParams.update(params)

# linestyles = ['--', '-.', '-', ':', (0, (3, 10, 1, 10)), (0, (3, 5, 1, 5, 1, 5)), (0, (3, 1, 1, 1)), (0, (3, 1, 1, 1, 1, 1))]
linestyles = ['-', '-', '-', '-', '-', '-', '-', '-']
markers = ['*', '^', 'o', 'P', 'p', 'v', 'X', 'd']
markersizes = [30, 24, 24, 24, 24, 24, 24, 24]

dx = 0/72.; dy = -0/72. 
offset = matplotlib.transforms.ScaledTranslation(dx, dy, plt.gcf().dpi_scale_trans)


x_val_nat = list()
y_val_nat = list()

x_val_mag = list()
y_val_mag = list()

x_low = 339399072 * 10
x_high = x_low + 339399072/10


# x_low = 0
# x_high = 9000000000000


# first load **all** files to the dict
def data_load(filename):
    # f_list = glob.glob(fileDir + '/*')
    # print(f_list)
    f_list = [filename]
    for f_name in f_list:
        with open(f_name, 'r') as f:
            raw_entry = f.readline()
            while raw_entry:
                entry_array = raw_entry.rstrip("\n").split(",")
                # print(entry_array)
                nf_type = entry_array[0]
                start_time = int(entry_array[1])
                latency = float(entry_array[2])
                if latency <= 200 and x_low <= start_time and start_time <= x_high:
                    if nf_type == "maglev":
                        x_val_mag.append(start_time)
                        y_val_mag.append(latency)
                    else:
                        x_val_nat.append(start_time)
                        y_val_nat.append(latency)
                        
                raw_entry = f.readline()
        # currently we only load the data of the first file
        # break 

# 0x, 1x, 3x, 5x. in %
pkt_loss_rate = [0.0079, 0.0746, 0.2510, 0.4387]

def draw_nat_maglev(filename):
    x_val_nat.clear()
    y_val_nat.clear()
    x_val_mag.clear()
    y_val_mag.clear()

    data_load(filename)
    cnt = 0
    legends = list()

    x_val_nat_ad = x_val_nat
    y_val_nat_ad = y_val_nat

    x_val_mag_ad = x_val_mag
    y_val_mag_ad = y_val_mag


    p1, = plt.plot(x_val_nat_ad, y_val_nat_ad, linestyle = linestyles[cnt], color=colors[cnt], linewidth=1)
    cnt += 1
    # p2, = plt.plot(x_val_mag_ad, y_val_mag_ad, linestyle = linestyles[cnt], marker = None, color=colors[cnt], linewidth=1)
    # cnt += 1

    legends.append(p1)
    # legends.append(p2)


    plt.legend(legends, ["NAT", "LB"])
    plt.ylabel('Per packet latency (us)')
    plt.xlabel('Time in CPU cycles')

    # apply offset transform to all x ticklabels.
    for label in plt.axes().xaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offset)

    plt.axes().set_ylim(ymin=0,ymax=100)

    plt.tight_layout()

    sufix_index = filename.find(".dat")
    sufix = filename[sufix_index - 3:sufix_index]
    if sufix == "0x":
        plt.title("0.25Mpps NAT")
    elif sufix == "1x":
        plt.title("0.25Mpps NAT vs. 0.25Mpps Maglev")
    elif sufix == "3x":
        plt.title("0.25Mpps NAT vs. 0.75Mpps Maglev")
    elif sufix == "5x":
        plt.title("0.25Mpps NAT vs. 1.25Mpps Maglev")

    # How maglev influces nat
    plt.savefig('./figures/two/%s_nat_maglev.pdf' % (sufix,))
    plt.clf()


if __name__ == '__main__':
    plt.rc('text', usetex=True)
    font = fm.FontProperties(
       family = 'Gill Sans',
       fname = '/usr/share/fonts/truetype/adf/GilliusADF-Regular.otf')

    f_list = glob.glob("./rawdata/two_latency/*")
    print(f_list)
    for f in f_list:
        draw_nat_maglev(f)