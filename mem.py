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
bmap = brewer2mpl.get_map('Paired', 'qualitative', 12)
colors = bmap.mpl_colors
linestyles = ['--', '-.', '-', ':']
markers = ['*', '^', 'o', 's']
markersizes = [15, 12, 12, 12]

params = {
    'axes.labelsize': 36,
    'font.size': 36,
    'legend.fontsize': 36,
    'xtick.labelsize': 36,
    'ytick.labelsize': 36,
    'text.usetex': False,
    'figure.figsize': [12, 8],
    'legend.loc': 'best'
}
rcParams.update(params)

dx = 0/72.; dy = -15/72. 
offset = matplotlib.transforms.ScaledTranslation(dx, dy, plt.gcf().dpi_scale_trans)

all_tasks = ["acl-fw-ipsec", "dpi-ipsec", "nat-tcp-v4-ipsec", "maglev-ipsec", "lpm-ipsec", "monitoring-ipsec"]

tasks = ["acl-fw-ipsec", "dpi-ipsec", "nat-tcp-v4-ipsec", "maglev-ipsec", "lpm-ipsec"]
pktgen_types = ["ICTF_IPSEC", "CAIDA64_IPSEC", "CAIDA256_IPSEC", "CAIDA512_IPSEC", "CAIDA1024_IPSEC"]

tasks_mon = ["monitoring-ipsec"]
pktgen_types_mon = map(lambda x: "chunck%d_ipsec.dat" % (x,), range(12))

num_queues = ["1", "2", "3", "4", "5", "6"]

# per-task mem time series
mem_time_all = defaultdict(list)

# per-task mem_val vector
mem_val = defaultdict(list)
mem_val_min = defaultdict(float)
mem_val_med = defaultdict(float)
mem_val_max = defaultdict(float)

utli_ratio = defaultdict(list)
utli_ratio_min = defaultdict(float)
utli_ratio_med = defaultdict(float)
utli_ratio_max = defaultdict(float)


# first load **all** files to the dict
def load(fileDir):
    f_list = glob.glob(fileDir + '/*')
    print(f_list)
    for f_name in f_list:
        with open(f_name, 'r') as f:
            raw_entry = f.readline()
            while raw_entry:
                key_array = raw_entry.rstrip("\n").split(",")
                mem_array = list(map(lambda x: float(x), f.readline().strip("[").rstrip("]\n").split(",")))
                max_mem = float(f.readline().rstrip("\n"))

                mem_time_all[key_array[0]].append(mem_array)
                # print(entry_array)
                mem_val[key_array[0]].append(max_mem)
                utli_ratio[key_array[0]].append((max_mem - mem_array[-1]) / max_mem)

                raw_entry = f.readline()


# then process data to get graph drawing data
def process_draw_data():
    for task in all_tasks:

        mem_val_min[task] = np.percentile(mem_val[task], 5)
        mem_val_med[task] = np.median(mem_val[task])
        mem_val_max[task] = max(mem_val[task])
        # mem_val_max[task] = np.percentile(mem_val[task], 95)

        utli_ratio_min[task] = np.percentile(utli_ratio[task], 5)
        utli_ratio_med[task] = np.median(utli_ratio[task])
        utli_ratio_max[task] = utli_ratio[task][mem_val[task].index(mem_val_max[task])]
        # utli_ratio_max[task] = np.percentile(utli_ratio[task], 95)

# next, get maxmem vector indexed by task
def get_draw_data_for_maxmem():
    mem_vec_min = list()
    mem_vec_med = list()
    mem_vec_max = list()
    for task in all_tasks:
        mem_vec_min.append(mem_val_min[task])
        mem_vec_med.append(mem_val_med[task])
        mem_vec_max.append(mem_val_max[task])
    return mem_vec_min, mem_vec_med, mem_vec_max

# next, get utli vector indexed by task
def get_draw_data_for_utli():
    utli_vec_min = list()
    utli_vec_med = list()
    utli_vec_max = list()
    for task in all_tasks:
        utli_vec_min.append(utli_ratio_min[task])
        utli_vec_med.append(utli_ratio_med[task])
        utli_vec_max.append(utli_ratio_max[task])
    return utli_vec_min, utli_vec_med, utli_vec_max


# finally, draw graph by passing pktgen vector (index vector), and multiple throughput vector
# def

if __name__ == '__main__':
    plt.rc('text', usetex=True)
    font = fm.FontProperties(
       family = 'Gill Sans',
       fname = '/usr/share/fonts/truetype/adf/GilliusADF-Regular.otf')

    load("./rawdata/mem")

    process_draw_data()

    file_out = open("./tables/mem.txt", "w")

    N = len(all_tasks)
    ind = np.arange(N) * 10 + 10    # the x locations for the groups
    width = 3.0       # the width of the bars: can also be len(x) sequence

    t_vec_min, t_vec_med, t_vec_max = get_draw_data_for_maxmem()
    yerr = np.zeros((2, len(t_vec_min)))
    yerr[0, :] = np.array(t_vec_med) - np.array(t_vec_min)
    yerr[1, :] = np.array(t_vec_max) - np.array(t_vec_med)
    p1 = plt.bar(ind, t_vec_med, width, yerr=yerr, color=colors[0], edgecolor = 'k', ecolor='k', align="center")
    file_out.write(str(all_tasks).strip("[").rstrip("]") + "\n")
    file_out.write(str(t_vec_med).strip("[").rstrip("]") + "\n")

    plt.legend([p1], ["Maximum memory usage (MB)"])
    plt.ylabel("Maximum memory usage (MB)")
    plt.xticks(ind, all_tasks)
    plt.savefig('./figures/mem/maxmem.pdf')
    plt.clf()

    t_vec_min_temp, t_vec_med_temp, t_vec_max_temp = t_vec_min, t_vec_med, t_vec_max

    t_vec_min, t_vec_med, t_vec_max = get_draw_data_for_utli()
    yerr = np.zeros((2, len(t_vec_min)))
    yerr[0, :] = np.array(t_vec_med) - np.array(t_vec_min)
    yerr[1, :] = np.array(t_vec_max) - np.array(t_vec_med)
    p1 = plt.bar(ind, t_vec_med, width, yerr=yerr, color=colors[0], edgecolor = 'k', ecolor='k', align="center")
    file_out.write(str(t_vec_med).strip("[").rstrip("]") + "\n")

    plt.legend([p1], ["Memory wasting ratio"])
    plt.ylabel("Memory wasting ratio")
    plt.xticks(ind, all_tasks)
    plt.savefig('./figures/mem/memratio.pdf')
    plt.clf()

    for i in range(len(t_vec_max_temp)):
        print(t_vec_max_temp[i] * (1 - t_vec_max[i]), t_vec_max_temp[i], 1 - t_vec_max[i])

    mem_val_max_dpi = max(mem_val["monitoring-ipsec"])
    mem_val_max_dpi_index = mem_val["monitoring-ipsec"].index(mem_val_max_dpi)
    print(mem_val_max_dpi_index)

    mem_time = mem_time_all["monitoring-ipsec"][mem_val_max_dpi_index]
    length_mem_time = len(mem_time)
    # print mem_time
    ind = np.arange(length_mem_time)
    p1, = plt.plot(ind, mem_time, marker = None, color='b', linewidth=2)
    
    max_mem_usage = max(mem_time)
    max_mem_time = mem_time.index(max_mem_usage)

    plt.axes().annotate('The minimum size of\n preallocated memory', xy=(max_mem_time, max_mem_usage), xytext=(max_mem_time - 2500, max_mem_usage - 120), 
            arrowprops=dict(facecolor='black', shrink=0.05), horizontalalignment='right', verticalalignment='bottom',)
    
    last_mem_usage = mem_time[-1]
    last_mem_time = len(mem_time) - 1

    plt.axes().annotate('The size of memory\n actually used by the NF', xy=(last_mem_time, last_mem_usage), xytext=(last_mem_time - 500, last_mem_usage - 235), 
            arrowprops=dict(facecolor='black', shrink=0.05), horizontalalignment='right', verticalalignment='bottom',)

    # plt.legend([p1], ["Memory usage vs. time"])
    plt.ylabel("Memory usage (MB)")
    plt.xticks(ind[::3000], ind[::3000] / 100)

    # apply offset transform to all x ticklabels.
    for label in plt.axes().xaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offset)

    plt.xlabel("Time (s)")
    plt.tight_layout()
    plt.savefig('./figures/mem/mem_time_%s_%s.pdf' % ("monitoring-ipsec", "caida_chunk0"))
    plt.clf()

    file_out.close()