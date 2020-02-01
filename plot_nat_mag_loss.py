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
    'axes.labelsize': 36,
    'font.size': 36,
    'legend.fontsize': 36,
    'xtick.labelsize': 36,
    'ytick.labelsize': 36,
    'text.usetex': False,
    'figure.figsize': [12, 8],
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

dx = 0/72.; dy = -15/72. 
offset = matplotlib.transforms.ScaledTranslation(dx, dy, plt.gcf().dpi_scale_trans)

def get_ratio(ori_name):
    switcher = {
        **dict.fromkeys(["1"], "16"), 
        **dict.fromkeys(["3"], "32"), 
        **dict.fromkeys(["7"], "48")
    }
    return switcher.get(ori_name, "Invalid core name %s" % (ori_name,))

# all_nfs = ["64", "256", "512", "1024", "1500", "6000", "9000", "2000000"]
# all_legends = ["64B", "256B", "512B", "1KB", "1.5KB", "6KB", "9KB", "2MB"]
all_nfs = ["NAT", "Maglev"]
all_legends = ["NAT", "Maglev"]
all_ratios = ["0", "1", "3", "5", "10"]

t_val = defaultdict(lambda: defaultdict(list))
t_val_med = defaultdict(lambda: defaultdict(float))

# first load **all** files to the dict
def data_load(fileDir):
    f_list = glob.glob(fileDir + '/*')
    print(f_list)
    for f_name in f_list:
        with open(f_name, 'r') as f:
            raw_entry = f.readline()
            while raw_entry:
                entry_array = raw_entry.rstrip("\n").split(",")
                # print(entry_array)
                _ratio = entry_array[0]
                _t_nat = float(entry_array[2])
                if _ratio == "0":
                    _t_mag = 0
                else:                
                    _t_mag = float(entry_array[3])
                t_val["NAT"][_ratio].append(float(_t_nat))
                t_val["Maglev"][_ratio].append(float(_t_mag))
                raw_entry = f.readline()
        # currently we only load the data of the first file
        # break 

# then process data to get graph drawing data
def process_draw_data():
    for _nf in all_nfs:
        for _ratio in all_ratios:
            try:
                t_val_med[_nf][_ratio] = np.median(t_val[_nf][_ratio])
            except IndexError:
                t_val_med[_nf][_ratio] = 0
            
def get_t_draw_data_vary_ratio(_nf):
    data_vec = list()
    for _ratio in all_ratios:
        data_vec.append(t_val_med[_nf][_ratio])
    # print(data_vec)
    return data_vec


def draw_t_trend_for_natmag_loss():
    data_load("./rawdata/two_loss")
    process_draw_data()

    N = len(all_ratios)
    ind = np.arange(N) * 10 + 10    # the x locations for the groups    

    cnt = 0
    legends = list()
    for _nf in all_nfs:
        data_vec = get_t_draw_data_vary_ratio(_nf)
        p1, = plt.plot(ind, data_vec, linestyle = linestyles[cnt], marker = markers[cnt], markersize = markersizes[cnt],
            color=colors[cnt], linewidth=2)
        print(str(all_nfs[cnt]) + ": " + str(data_vec))        

        legends.append(p1)
        cnt += 1

    plt.legend(legends, all_legends, ncol=2, frameon=False)
    plt.ylabel('packet loss rate (\%)')
    plt.xticks(ind, all_ratios)
    plt.xlabel('Maglev traffic rate : NAT traffic rate')

    # apply offset transform to all x ticklabels.
    for label in plt.axes().xaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offset)

    plt.axes().set_ylim(ymin=0)

    plt.tight_layout()
    plt.savefig('./figures/two/nat_mag_lossrate.pdf')
    plt.clf()


if __name__ == '__main__':
    plt.rc('text', usetex=True)
    font = fm.FontProperties(
       family = 'Gill Sans',
       fname = '/usr/share/fonts/truetype/adf/GilliusADF-Regular.otf')

    draw_t_trend_for_natmag_loss()