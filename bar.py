#!/usr/bin/python3

import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from collections import defaultdict
import brewer2mpl
import glob

 # brewer2mpl.get_map args: set name  set type  number of colors
bmap = brewer2mpl.get_map('Paired', 'qualitative', 12)
colors = bmap.mpl_colors
 
params = {
    'axes.labelsize': 18,
    'font.size': 18,
    'legend.fontsize': 18,
    'xtick.labelsize': 18,
    'ytick.labelsize': 18,
    'text.usetex': False,
    'figure.figsize': [20, 8],
    'legend.loc': 'best'
}
rcParams.update(params)


all_types = ["SmartNIC", "NetBricks", "SafeBricks"]
all_tasks = ["Firewall", "DPI", "NAT", "Maglev", "LPM", "Monitor"]
all_ipsecs = ["w/ IPsec", "w/o IPsec"]
all_traces = ["ICTF", "64B", "256B", "512B", "1KB"]
all_cores = ["1", "2", "3", "4", "5"]

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
        **dict.fromkeys(["./rawdata/nic"], "SmartNIC"), 
        **dict.fromkeys(["./rawdata/nb"], "NetBricks"), 
        **dict.fromkeys(["./rawdata/sb"], "SafeBricks"), 
    }
    return switcher.get(ori_name, "Invalid path name %s" % (ori_name,))

def get_task(ori_name):
    switcher = {
        **dict.fromkeys(["firewall", "firewall-ipsec", "acl-fw", "acl-fw-ipsec"], "Firewall"), 
        **dict.fromkeys(["hfa-se-maxperf-check", "hfa-se-maxperf-ipsec-check", "dpi", "dpi-ipsec"], "DPI"), 
        **dict.fromkeys(["nat", "nat-ipsec", "nat-tcp-v4", "nat-tcp-v4-ipsec"], "NAT"), 
        **dict.fromkeys(["maglev", "maglev-ipsec"], "Maglev"), 
        **dict.fromkeys(["lpm", "lpm-ipsec"], "LPM"), 
        **dict.fromkeys(["monitor", "monitor-ipsec", "monitoring", "monitoring-ipsec"], "Monitor")
    }
    return switcher.get(ori_name, "Invalid task name %s" % (ori_name,))

def get_ipsec(ori_name):
    without_ipsec_names = ["firewall", "acl-fw", "hfa-se-maxperf-check", "dpi", "nat", "nat-tcp-v4", "maglev", "lpm", "monitor", "monitoring"]
    with_ipsec_names = ["firewall-ipsec", "acl-fw-ipsec", "hfa-se-maxperf-ipsec-check", "dpi-ipsec", "nat-ipsec", "nat-tcp-v4-ipsec", "maglev-ipsec", "lpm-ipsec", "monitor-ipsec", "monitoring-ipsec"]
    switcher = {
        **dict.fromkeys(without_ipsec_names, "w/o IPsec"), 
        **dict.fromkeys(with_ipsec_names, "w/ IPsec")
    }
    return switcher.get(ori_name, "Invalid task name %s" % (ori_name,))

def get_trace(ori_name):
    switcher = {
        **dict.fromkeys(["ICTF", "ICTF_ACL", "ICTF_IPSEC", "ICTF_IPSEC_ACL"], "ICTF"), 
        **dict.fromkeys(["CAIDA64", "CAIDA64_ACL", "CAIDA64_IPSEC", "CAIDA64_IPSEC_ACL"], "64B"), 
        **dict.fromkeys(["CAIDA256", "CAIDA256_ACL", "CAIDA256_IPSEC", "CAIDA256_IPSEC_ACL"], "256B"), 
        **dict.fromkeys(["CAIDA512", "CAIDA512_ACL", "CAIDA512_IPSEC", "CAIDA512_IPSEC_ACL"], "512B"), 
        **dict.fromkeys(["CAIDA1024", "CAIDA1024_ACL", "CAIDA1024_IPSEC", "CAIDA1024_IPSEC_ACL"], "1KB")
    }
    return switcher.get(ori_name, "Invalid trace name %s" % (ori_name,))

def get_core(ori_name):
    switcher = {
        **dict.fromkeys(["0x1", "1"], "1"), 
        **dict.fromkeys(["0x3", "2"], "2"), 
        **dict.fromkeys(["0x7", "3"], "3"), 
        **dict.fromkeys(["0xF", "4"], "4"), 
        **dict.fromkeys(["0x1F", "5"], "5")
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
def data_load(fileDir):
    f_list = glob.glob(fileDir + '/*')
    print(f_list)
    for f_name in f_list:
        with open(f_name, 'r') as f:
            raw_entry = f.readline()
            while raw_entry:
                entry_array = raw_entry.rstrip("\n").split(",")
                # print(entry_array)
                _type = get_type(fileDir)
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
        break 

# then process data to get graph drawing data
def process_draw_data():
    for _type in all_types:
        for _task in all_tasks:
            for _ipsec in all_ipsecs:
                for _trace in all_traces:
                    for _core in all_cores:
                        try:
                            t_val_med[_type][_task][_ipsec][_trace][_core] = np.median(t_val[_type][_task][_ipsec][_trace][_core])
                        except IndexError:
                            t_val_med[_type][_task][_ipsec][_trace][_core] = 0
                        try:
                            avg_l_val_med[_type][_task][_ipsec][_trace][_core] = np.median(avg_l_val[_type][_task][_ipsec][_trace][_core])
                        except IndexError:
                            avg_l_val_med[_type][_task][_ipsec][_trace][_core] = 0
                        try:
                            tail_l_val_med[_type][_task][_ipsec][_trace][_core] = np.median(tail_l_val[_type][_task][_ipsec][_trace][_core])
                        except IndexError:
                            tail_l_val_med[_type][_task][_ipsec][_trace][_core] = 0
                        



# # next, get throughput vector indexed by trace for specific task and core case
# # ipsec: with or without
# def get_draw_data_for_task_core(task, core, ipsec):
#     data_vec = list()

#     for trace in all_traces:
#         data_vec.append(t_val_med["SmartNIC"][task][ipsec][trace][core])
#     return data_vec

# def draw_smartnic():
#     data_load("./rawdata/nic")
#     process_draw_data()

#     N = len(all_traces)
#     ind = np.arange(N) * 10 + 10    # the x locations for the groups    
#     width = 6.0/len(all_cores)       # the width of the bars: can also be len(x) sequence

#     for task in all_tasks:
#         cnt = 0
#         legends = list()
#         for core in all_cores:
#             data_vec = get_draw_data_for_task_core(task, core, "w/o IPsec")
#             p1 = plt.bar(ind + width * (cnt - len(all_cores) / 2 + 0.5), data_vec, width, color=colors[cnt], edgecolor = 'k', align="center")
#             legends.append(p1)
#             cnt += 1

#         plt.legend(legends, map(lambda x: '# core = %s' % (x,), all_cores))
#         plt.ylabel('Throughput (Mpps)')
#         plt.xticks(ind, all_traces)
#         plt.savefig('./figures/t_%s.pdf' % (task,))
#         plt.clf()

#         cnt = 0
#         legends = list()
#         for core in all_cores:
#             data_vec = get_draw_data_for_task_core(task, core, "w/ IPsec")
#             p1 = plt.bar(ind + width * (cnt - len(all_cores) / 2 + 0.5), data_vec, width, color=colors[cnt], edgecolor = 'k', align="center")
#             legends.append(p1)
#             cnt += 1

#         plt.legend(legends, map(lambda x: '# core = %s' % (x,), all_cores))
#         plt.ylabel('Throughput (Mpps)')
#         plt.xticks(ind, all_traces)
#         plt.savefig('./figures/t_%s_ipsec.pdf' % (task,))
#         plt.clf()




def get_t_draw_data_vary_task(_type, _ipsec, _trace, _core):
    data_vec = list()
    for _task in all_tasks:
        data_vec.append(t_val_med[_type][_task][_ipsec][_trace][_core])
    return data_vec

def draw_t_bar_for_core(_core):
    data_load("./rawdata/nic")
    data_load("./rawdata/nb")
    data_load("./rawdata/sb")

    process_draw_data()

    N = len(all_tasks)
    ind = np.arange(N) * 10 + 10    # the x locations for the groups    
    width = 6.0/len(all_types)       # the width of the bars: can also be len(x) sequence

    cnt = 0
    legends = list()
    for _type in all_types:
        data_vec = get_t_draw_data_vary_task(_type, "w/ IPsec", "ICTF", _core)
        p1 = plt.bar(ind + width * (cnt - len(all_types) / 2 + 0.5), data_vec, width, color=colors[cnt], edgecolor = 'k', align="center")
        legends.append(p1)
        cnt += 1

    if _core not in ["1", "2", "3", "4"]:
        for i in range(N):
            if all_tasks[i] == "DPI":
                x_base = ind[i]
                cnt = 0
                for _type in all_types:
                    if _type == "SmartNIC":
                        # x = x_base + width * (cnt - len(all_types) / 2 + 0.5 - 0.2)
                        # y = 0.4
                        # plt.text(x, y, "Not Applied", fontsize=18, rotation=90)
                        x = (x_base + width * (cnt - len(all_types) / 2 + 0.5)) / (N * 10 + 10 + 10)
                        y = 0.13
                        plt.text(x, y, "Not Applied", fontsize=18, rotation=90, horizontalalignment='center', verticalalignment='center', transform=plt.axes().transAxes)
                    cnt += 1


    plt.legend(legends, all_types)
    plt.ylabel('Throughput (Mpps)')
    plt.xticks(ind, all_tasks)
    plt.savefig('./figures/t_bar_%scores.pdf' % (_core,))
    plt.clf()



def get_l_draw_data_vary_task(_type, _ipsec, _trace, _core):
    data_vec_avg = list()
    data_vec_tail = list()
    for _task in all_tasks:
        data_vec_avg.append(avg_l_val_med[_type][_task][_ipsec][_trace][_core])
        data_vec_tail.append(tail_l_val_med[_type][_task][_ipsec][_trace][_core])
    return data_vec_avg, data_vec_tail

def draw_l_bar_for_core(_core):
    data_load("./rawdata/nic")
    data_load("./rawdata/nb")
    data_load("./rawdata/sb")

    process_draw_data()

    N = len(all_tasks)
    ind = np.arange(N) * 10 + 10    # the x locations for the groups    
    width = 6.0/len(all_types)       # the width of the bars: can also be len(x) sequence

    cnt = 0
    legends = list()
    for _type in all_types:
        data_vec_avg, data_vec_tail = get_l_draw_data_vary_task(_type, "w/ IPsec", "ICTF", _core)
        yerr = np.zeros((2, len(data_vec_avg)))
        yerr[0, :] = np.array(data_vec_avg) - np.array(data_vec_avg)
        yerr[1, :] = np.array(data_vec_tail) - np.array(data_vec_avg)
        
        p1 = plt.bar(ind + width * (cnt - len(all_types) / 2 + 0.5), data_vec_avg, width, yerr=yerr, color=colors[cnt], edgecolor = 'k', ecolor='k', align="center")
        legends.append(p1)
        cnt += 1

    if _core not in ["1", "2", "3", "4"]:
        for i in range(N):
            if all_tasks[i] == "DPI":
                x_base = ind[i]
                cnt = 0
                for _type in all_types:
                    if _type == "SmartNIC":
                        # x = x_base + width * (cnt - len(all_types) / 2 + 0.5 - 0.2)
                        # y = 0.4
                        # plt.text(x, y, "Not Applied", fontsize=18, rotation=90)
                        x = (x_base + width * (cnt - len(all_types) / 2 + 0.5)) / (N * 10 + 10 + 10)
                        y = 0.13
                        plt.text(x, y, "Not Applied", fontsize=18, rotation=90, horizontalalignment='center', verticalalignment='center', transform=plt.axes().transAxes)
                    cnt += 1

    plt.legend(legends, all_types)
    plt.ylabel('Average and 99th tail latency (microsecond)')
    plt.xticks(ind, all_tasks)
    plt.savefig('./figures/l_bar_%scores.pdf' % (_core,))
    plt.clf()

    

if __name__ == '__main__':
    for _core in all_cores:
        draw_t_bar_for_core(_core)
        draw_l_bar_for_core(_core)