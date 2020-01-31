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
# bmap = brewer2mpl.get_map('Paired', 'qualitative', 12)
bmap = brewer2mpl.get_map('Dark2', 'qualitative', 6)
colors = bmap.mpl_colors
 
params = {
    'axes.labelsize': 36,
    'font.size': 36,
    'legend.fontsize': 36,
    'xtick.labelsize': 36,
    'ytick.labelsize': 36,
    'text.usetex': False,
    'figure.figsize': [12, 8],
    'legend.loc': 'upper center',
    'legend.columnspacing': 0.8,
    'legend.handlelength'  : 1.0,
    'legend.handletextpad' : 0.4
}
rcParams.update(params)

dx = 0/72.; dy = -15/72. 
offset = matplotlib.transforms.ScaledTranslation(dx, dy, plt.gcf().dpi_scale_trans)

all_types = ["SmartNIC", "NetBricks", "SafeBricks"]
all_tasks = ["Firewall", "DPI", "NAT", "Maglev", "LPM", "Monitor"]
all_tasks_figure = ["FW", "DPI", "NAT", "LB", "LPM", "Mon."]
all_ipsecs = ["no_ipsec", "gcm_ipsec", "sha_ipsec"]
all_traces = ["ICTF", "64B", "256B", "512B", "1KB"]
all_cores = ["1", "2", "4", "8", "16"]

tasks_nic = ["firewall", "lpm", "maglev", "monitor", "nat", "hfa-se-maxperf-check"]
tasks_ipsec_nic = ["firewall-ipsec", "lpm-ipsec", "maglev-ipsec", "monitor-ipsec", "nat-ipsec", "hfa-se-maxperf-ipsec-check"]
tasks_nb = ["acl-fw", "dpi", "lpm", "maglev", "monitoring", "nat-tcp-v4"]
tasks_ipsec_nb = ["acl-fw-ipsec", "dpi-ipsec", "lpm-ipsec", "maglev-ipsec", "monitoring-ipsec", "nat-tcp-v4-ipsec"]

traces = ["ICTF", "CAIDA64", "CAIDA256", "CAIDA512", "CAIDA1024"]
traces_acl = ["ICTF_ACL", "CAIDA64_ACL", "CAIDA256_ACL", "CAIDA512_ACL", "CAIDA1024_ACL"]
traces_ipsec = ["ICTF_IPSEC", "CAIDA64_IPSEC", "CAIDA256_IPSEC", "CAIDA512_IPSEC", "CAIDA1024_IPSEC"]
traces_ipsec_acl = ["ICTF_IPSEC_ACL", "CAIDA64_IPSEC_ACL", "CAIDA256_IPSEC_ACL", "CAIDA512_IPSEC_ACL", "CAIDA1024_IPSEC_ACL"]

cores_nic = ["0x1", "0x3", "0x7", "0xF", "0x1F", "0x3F", "0x7F", "0xFF", "0xFFF", "0xFFFF"]
cores_sb = ["1", "2", "3", "4", "5"]
cores_nb = ["1", "2", "3", "4", "5", "6"]

def get_type(ori_name):
    switcher = {
        **dict.fromkeys(["./rawdata/nic/sixnfs.res"], "SmartNIC"), 
        **dict.fromkeys(["./rawdata/nb/sixnfs.res"], "NetBricks"), 
        **dict.fromkeys(["./rawdata/sb/sixnfs.res"], "SafeBricks"), 
    }
    return switcher.get(ori_name, "Invalid path name %s" % (ori_name,))

def get_task(ori_name):
    switcher = {
        **dict.fromkeys(["firewall", "firewall-ipsec", "firewall-ipsec-sha", "acl-fw", "acl-fw-ipsec", "acl-fw-ipsec-sha"], "Firewall"), 
        **dict.fromkeys(["hfa-se-maxperf-check", "hfa-se-maxperf-ipsec-check", "hfa-se-maxperf-ipsec-check-sha", "dpi", "dpi-ipsec", "dpi-ipsec-sha"], "DPI"), 
        **dict.fromkeys(["nat", "nat-ipsec", "nat-ipsec-sha", "nat-tcp-v4", "nat-tcp-v4-ipsec", "nat-tcp-v4-ipsec-sha"], "NAT"), 
        **dict.fromkeys(["maglev", "maglev-ipsec", "maglev-ipsec-sha"], "Maglev"), 
        **dict.fromkeys(["lpm", "lpm-ipsec", "lpm-ipsec-sha"], "LPM"), 
        **dict.fromkeys(["monitor", "monitor-ipsec", "monitor-ipsec-sha", "monitoring", "monitoring-ipsec", "monitoring-ipsec-sha"], "Monitor")
    }
    return switcher.get(ori_name, "Invalid task name %s" % (ori_name,))

def get_ipsec(ori_name):
    no_ipsec_names = ["firewall", "acl-fw", "hfa-se-maxperf-check", "dpi", "nat", "nat-tcp-v4", "maglev", "lpm", "monitor", "monitoring"]
    gcm_ipsec_names = ["firewall-ipsec", "acl-fw-ipsec", "hfa-se-maxperf-ipsec-check", "dpi-ipsec", "nat-ipsec", "nat-tcp-v4-ipsec", "maglev-ipsec", "lpm-ipsec", "monitor-ipsec", "monitoring-ipsec"]
    sha_ipsec_names = ["firewall-ipsec-sha", "acl-fw-ipsec-sha", "hfa-se-maxperf-ipsec-check-sha", "dpi-ipsec-sha", "nat-ipsec-sha", "nat-tcp-v4-ipsec-sha", "maglev-ipsec-sha", "lpm-ipsec-sha", "monitor-ipsec-sha", "monitoring-ipsec-sha"]
    
    switcher = {
        **dict.fromkeys(no_ipsec_names, "no_ipsec"), 
        **dict.fromkeys(gcm_ipsec_names, "gcm_ipsec"),
        **dict.fromkeys(sha_ipsec_names, "sha_ipsec")
    }
    return switcher.get(ori_name, "Invalid task name %s" % (ori_name,))

def get_trace(ori_name):
    switcher = {
        **dict.fromkeys(["ICTF", "ICTF_ACL", "ICTF_IPSEC", "ICTF_IPSEC_ACL", "ICTF_IPSEC_SHA", "ICTF_IPSEC_ACL_SHA"], "ICTF"), 
        **dict.fromkeys(["CAIDA64", "CAIDA64_ACL", "CAIDA64_IPSEC", "CAIDA64_IPSEC_ACL", "CAIDA64_IPSEC_SHA", "CAIDA64_IPSEC_ACL_SHA"], "64B"), 
        **dict.fromkeys(["CAIDA256", "CAIDA256_ACL", "CAIDA256_IPSEC", "CAIDA256_IPSEC_ACL", "CAIDA256_IPSEC_SHA", "CAIDA256_IPSEC_ACL_SHA"], "256B"), 
        **dict.fromkeys(["CAIDA512", "CAIDA512_ACL", "CAIDA512_IPSEC", "CAIDA512_IPSEC_ACL", "CAIDA512_IPSEC_SHA", "CAIDA512_IPSEC_ACL_SHA"], "512B"), 
        **dict.fromkeys(["CAIDA1024", "CAIDA1024_ACL", "CAIDA1024_IPSEC", "CAIDA1024_IPSEC_ACL", "CAIDA1024_IPSEC_SHA", "CAIDA1024_IPSEC_ACL_SHA"], "1KB")
    }
    return switcher.get(ori_name, "Invalid trace name %s" % (ori_name,))

def get_core(ori_name):
    switcher = {
        **dict.fromkeys(["0x1", "1"], "1"), 
        **dict.fromkeys(["0x3", "2"], "2"), 
        **dict.fromkeys(["0x7", "3"], "3"), 
        **dict.fromkeys(["0xF", "4"], "4"), 
        **dict.fromkeys(["0x1F", "5"], "5"),
        **dict.fromkeys(["0x3F", "6"], "6"),
        **dict.fromkeys(["0x7F", "7"], "7"),
        **dict.fromkeys(["0xFF", "8"], "8"),
        **dict.fromkeys(["0xFFF", "12"], "12"),
        **dict.fromkeys(["0xFFFF", "16"], "16")
    }
    return switcher.get(ori_name, "Invalid core name %s" % (ori_name,))



# type (nic, nb, sb) -> task -> ipsecs -> trace -> core -> throughput/latency values for 10 runs
t_val = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list)))))
avg_l_val = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list)))))
tail_l_val = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list)))))

# we report the median of the 10 runs. 
# type (nic, nb, sb) -> task -> ipsecs -> trace -> core -> median throughput/latency values for 10 runs
t_val_med = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(float)))))
avg_l_val_med = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(float)))))
tail_l_val_med = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(float)))))

# first load **all** files to the dict
def data_load(f_name):
    with open(f_name, 'r') as f:
        raw_entry = f.readline()
        while raw_entry:
            entry_array = raw_entry.rstrip("\n").split(",")
            # print(entry_array)
            _type = get_type(f_name)
            _task = get_task(entry_array[0])
            _ipsec = get_ipsec(entry_array[0])
            _trace = get_trace(entry_array[1])
            _core = get_core(entry_array[2])
            _t = float(entry_array[3])
            _avg_l = float(entry_array[4])
            _tail_l = float(entry_array[5])
            t_val[_type][_task][_ipsec][_trace][_core].append(float(_t))
            avg_l_val[_type][_task][_ipsec][_trace][_core].append(float(_avg_l))
            tail_l_val[_type][_task][_ipsec][_trace][_core].append(float(_tail_l))
            raw_entry = f.readline()
    # currently we only load the data of the first file
    # break 

# https://homes.cs.washington.edu/~arvind/papers/ipipe.pdf
#  For example, a 10/25GbE SmartNIC typically costs 100∼400$ more than a corresponding standard NIC
smartnic_percore_price = 400/16
cpu_percore_price = 379/6
print(f'smartnic_percore_price: {smartnic_percore_price} vs. cpu_percore_price: {cpu_percore_price}')

# then process data to get graph drawing data
def process_draw_data(norm_flag=False):
    for _type in all_types:
        norm_base = 1
        if norm_flag:
            if _type == "SmartNIC":
                norm_base = smartnic_percore_price
            else:
                norm_base = cpu_percore_price
        for _task in all_tasks:
            for _ipsec in all_ipsecs:
                for _trace in all_traces:
                    for _core in all_cores:
                        try:
                            t_val_med[_type][_task][_ipsec][_trace][_core] = np.median(t_val[_type][_task][_ipsec][_trace][_core])/norm_base
                        except IndexError:
                            t_val_med[_type][_task][_ipsec][_trace][_core] = 0
                        try:
                            avg_l_val_med[_type][_task][_ipsec][_trace][_core] = np.median(avg_l_val[_type][_task][_ipsec][_trace][_core])/norm_base
                        except IndexError:
                            avg_l_val_med[_type][_task][_ipsec][_trace][_core] = 0
                        try:
                            tail_l_val_med[_type][_task][_ipsec][_trace][_core] = np.median(tail_l_val[_type][_task][_ipsec][_trace][_core])/norm_base
                        except IndexError:
                            tail_l_val_med[_type][_task][_ipsec][_trace][_core] = 0


def add_text(N, ind, _core, width, core_list, plt, type_s, task=None):
    if _core not in list(core_list):
        for i in range(N):
            if all_tasks[i] == task or task == None:
                x_base = ind[i]
                cnt = 0
                for _type in all_types:
                    if _type == type_s:
                        # x = x_base + width * (cnt - len(all_types) / 2 + 0.5 - 0.2)
                        # y = 0.46
                        # plt.text(x, y, "Not Applied", fontsize=18, rotation=90)
                        x = (x_base + width * (cnt - len(all_types) / 2.0 - 1.5)) / (N * 10)
                        y = 0.13
                        plt.text(x, y, "Not Applied", fontsize=18, rotation=90, horizontalalignment='center', verticalalignment='center', transform=plt.axes().transAxes)
                    cnt += 1


def get_t_draw_data_vary_task(_type, _ipsec, _trace, _core):
    data_vec = list()
    for _task in all_tasks:
        data_vec.append(t_val_med[_type][_task][_ipsec][_trace][_core])
    return data_vec

def draw_t_bar_for_core_ipsec_trace(_core, _ipsec, _trace, norm_flag=False):
    N = len(all_tasks)
    ind = np.arange(N) * 10 + 10    # the x locations for the groups    
    width = 6.0/len(all_types)       # the width of the bars: can also be len(x) sequence

    cnt = 0
    legends = list()
    for _type in all_types:
        data_vec = get_t_draw_data_vary_task(_type, _ipsec, _trace, _core)
        p1 = plt.bar(ind + width * (cnt - len(all_types) / 2.0 + 0.5), data_vec, width, color=colors[cnt], edgecolor = 'k', align="center")
        legends.append(p1)
        cnt += 1
    
    plt.legend(legends, all_types, ncol=3)
    if norm_flag:
        plt.ylabel('Throughput per dollar (Mpps/\$)')
    else:
        plt.ylabel('Throughput (Mpps)')
    plt.xticks(ind, all_tasks_figure)
    # apply offset transform to all x ticklabels.
    for label in plt.axes().xaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offset)

    plt.tight_layout()
    if norm_flag:
        plt.savefig('./figures/bar/throughput/t_bar_%scores_%s_%s_norm.pdf' % (_core, _ipsec, _trace))
    else:
        plt.savefig('./figures/bar/throughput/t_bar_%scores_%s_%s.pdf' % (_core, _ipsec, _trace))
    plt.clf()

if __name__ == '__main__':
    plt.rc('text', usetex=True)
    font = fm.FontProperties(
       family = 'Gill Sans',
       fname = '/usr/share/fonts/truetype/adf/GilliusADF-Regular.otf')

    data_load("./rawdata/nic/sixnfs.res")
    data_load("./rawdata/nb/sixnfs.res")
    data_load("./rawdata/sb/sixnfs.res")

    process_draw_data()

    all_cores_wecare = ["1"]
    for _ipsec in all_ipsecs:
        for _core in all_cores_wecare:
            draw_t_bar_for_core_ipsec_trace(_core, _ipsec, "64B")
            draw_t_bar_for_core_ipsec_trace(_core, _ipsec, "ICTF")


    process_draw_data(norm_flag=True)

    all_cores_wecare = ["1"]
    for _ipsec in all_ipsecs:
        for _core in all_cores_wecare:
            draw_t_bar_for_core_ipsec_trace(_core, _ipsec, "64B", norm_flag=True)
            draw_t_bar_for_core_ipsec_trace(_core, _ipsec, "ICTF", norm_flag=True)