#!/usr/bin/python3

import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib import rcParams
from collections import defaultdict
from util_patterns import *
import glob
rcParams.update(params_line)

dx = 0/72.; dy = -15/72. 
offset = matplotlib.transforms.ScaledTranslation(dx, dy, plt.gcf().dpi_scale_trans)

all_tasks = ["AC-DPI", "Hyperscan-DPI", "SmartNIC-DPI"]
all_ipsecs = ["no_ipsec", "gcm_ipsec", "sha_ipsec"]
all_traces = ["ICTF", "64B", "256B", "512B", "1KB"]
all_traces_pktsize = ["64B", "256B", "512B", "1KB"]
all_cores = ["1", "2", "4", "8", "16"]
all_rules = ["1k", "5k", "10k", "20k", "30k", "33.5k"]

def get_task(ori_name):
    switcher = {
        **dict.fromkeys(["dpi", "dpi-ipsec", "dpi-ipsec-sha"], "AC-DPI"), 
        **dict.fromkeys(["dpi-hs", "dpi-hs-ipsec", "dpi-hs-ipsec-sha"], "Hyperscan-DPI"), 
        **dict.fromkeys(["hfa-se-maxperf-check", "hfa-se-maxperf-ipsec-check", "hfa-se-maxperf-ipsec-check-sha"], "SmartNIC-DPI"), 
    }
    return switcher.get(ori_name, "Invalid task name %s" % (ori_name,))

def get_ipsec(ori_name):
    no_ipsec_names = ["firewall", "acl-fw", "hfa-se-maxperf-check", "dpi", "nat", "nat-tcp-v4", "maglev", "lpm", "monitor", "monitoring", "dpi-hs"]
    gcm_ipsec_names = ["firewall-ipsec", "acl-fw-ipsec", "hfa-se-maxperf-ipsec-check", "dpi-ipsec", "nat-ipsec", "nat-tcp-v4-ipsec", "maglev-ipsec", "lpm-ipsec", "monitor-ipsec", "monitoring-ipsec", "dpi-hs-ipsec"]
    sha_ipsec_names = ["firewall-ipsec-sha", "acl-fw-ipsec-sha", "hfa-se-maxperf-ipsec-check-sha", "dpi-ipsec-sha", "nat-ipsec-sha", "nat-tcp-v4-ipsec-sha", "maglev-ipsec-sha", "lpm-ipsec-sha", "monitor-ipsec-sha", "monitoring-ipsec-sha", "dpi-hs-ipsec-sha"]
    
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

def get_rule(ori_name):
    switcher = {
        **dict.fromkeys(["1000", "1k"], "1k"), 
        **dict.fromkeys(["5000", "5k"], "5k"), 
        **dict.fromkeys(["10000", "10k"], "10k"), 
        **dict.fromkeys(["20000", "20k"], "20k"), 
        **dict.fromkeys(["30000", "30k"], "30k"), 
        **dict.fromkeys(["33471", "full"], "33.5k")
    }
    return switcher.get(ori_name, "Invalid rule name %s" % (ori_name,))

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
            _task = get_task(entry_array[0])
            _ipsec = get_ipsec(entry_array[0])
            _trace = get_trace(entry_array[1])
            _core = get_core(entry_array[2])
            _rule = get_rule(entry_array[3])
            _t = float(entry_array[4])
            _avg_l = float(entry_array[5])
            _tail_l = float(entry_array[6])
            t_val[_task][_ipsec][_trace][_core][_rule].append(float(_t))
            avg_l_val[_task][_ipsec][_trace][_core][_rule].append(float(_avg_l))
            tail_l_val[_task][_ipsec][_trace][_core][_rule].append(float(_tail_l))
            raw_entry = f.readline()
    # currently we only load the data of the first file
    # break 

# then process data to get graph drawing data
def process_draw_data():
    for _task in all_tasks:
        for _ipsec in all_ipsecs:
            for _trace in all_traces:
                for _core in all_cores:
                    for _rule in all_rules:
                        try:
                            t_val_med[_task][_ipsec][_trace][_core][_rule] = np.median(t_val[_task][_ipsec][_trace][_core][_rule])
                        except IndexError:
                            t_val_med[_task][_ipsec][_trace][_core][_rule] = 0
                        try:
                            avg_l_val_med[_task][_ipsec][_trace][_core][_rule] = np.median(avg_l_val[_task][_ipsec][_trace][_core][_rule])
                        except IndexError:
                            avg_l_val_med[_task][_ipsec][_trace][_core][_rule] = 0
                        try:
                            tail_l_val_med[_task][_ipsec][_trace][_core][_rule] = np.median(tail_l_val[_task][_ipsec][_trace][_core][_rule])
                        except IndexError:
                            tail_l_val_med[_task][_ipsec][_trace][_core][_rule] = 0
                        
def get_t_draw_data_vary_rule(_task, _ipsec, _trace, _core):
    data_vec = list()
    for _rule in all_rules:
        data_vec.append(t_val_med[_task][_ipsec][_trace][_core][_rule])
    return data_vec

def draw_t_bar_for_rule(_ipsec, _trace, _core):
    N = len(all_rules)
    ind = np.arange(N) * 10 + 10    # the x locations for the groups    
    width = 6.0/N       # the width of the bars: can also be len(x) sequence

    cnt = 0
    legends = list()
    for _task in all_tasks:
        data_vec = get_t_draw_data_vary_rule(_task, _ipsec, _trace, _core)
        p1, = plt.plot(ind, data_vec, linestyle = linestyles[cnt], marker = markers[cnt], markersize = markersizes[cnt],
            color=colors[cnt], linewidth=3)
        legends.append(p1)
        cnt += 1

    plt.legend(legends, all_tasks, frameon=False)
    plt.ylabel('Throughput (Mpps)')
    plt.xticks(ind, all_rules)

    # apply offset transform to all x ticklabels.
    for label in plt.axes().xaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offset)
    plt.axes().grid(which='major', axis='y', linestyle=':')
    plt.axes().set_axisbelow(True)

    plt.tight_layout()
    plt.savefig('./figures/ac-hs/throughput/t_bar_%s_%s_%score.pdf' % (_ipsec, _trace, _core))
    plt.clf()

               
def get_t_draw_data_vary_trace(_task, _ipsec, _core, _rule):
    data_vec = list()
    for _trace in all_traces_pktsize:
        data_vec.append(t_val_med[_task][_ipsec][_trace][_core][_rule])
    return data_vec

def draw_t_bar_for_trace(_ipsec, _core, _rule):
    N = len(all_traces_pktsize)
    ind = np.arange(N) * 10 + 10    # the x locations for the groups    
    width = 6.0/N       # the width of the bars: can also be len(x) sequence

    cnt = 0
    legends = list()
    for _task in all_tasks:
        data_vec = get_t_draw_data_vary_trace(_task, _ipsec, _core, _rule)
        p1, = plt.plot(ind, data_vec, linestyle = linestyles[cnt], marker = markers[cnt], markersize = markersizes[cnt],
            color=colors[cnt], linewidth=3)
        legends.append(p1)
        cnt += 1

    plt.legend(legends, all_tasks, frameon=False)
    plt.ylabel('Throughput (Mpps)')
    plt.xticks(ind, all_traces_pktsize)

    # apply offset transform to all x ticklabels.
    for label in plt.axes().xaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offset)
    plt.axes().grid(which='major', axis='y', linestyle=':')
    plt.axes().set_axisbelow(True)

    plt.tight_layout()
    plt.savefig('./figures/ac-hs/throughput/t_bar_%s_%score_%srule.pdf' % (_ipsec, _core, _rule))
    plt.clf()

if __name__ == "__main__":
    plt.rc('text', usetex=True)
    font = fm.FontProperties(
       family = 'Gill Sans',
       fname = '/usr/share/fonts/truetype/adf/GilliusADF-Regular.otf')

    data_load("./rawdata/nic/ac-hs.res")
    data_load("./rawdata/nb/ac-hs.res")
    process_draw_data()
    draw_t_bar_for_rule("no_ipsec", "ICTF", "1")
    draw_t_bar_for_trace("no_ipsec", "1", "33.5k")
    draw_t_bar_for_trace("no_ipsec", "1", "1k")
