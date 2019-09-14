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
    'axes.labelsize': 36,
    'font.size': 36,
    'legend.fontsize': 36,
    'xtick.labelsize': 36,
    'ytick.labelsize': 36,
    'text.usetex': False,
    'figure.figsize': [12, 8],
    'legend.loc': 'best', 
    'legend.columnspacing': 1
}
rcParams.update(params)

linestyles = ['--', '-.', '-', ':', (0, (3, 5, 1, 5, 1, 5)), (0, (3, 1, 1, 1))]
markers = ['*', '^', 'o', 'P', 'p', 'v']
markersizes = [30, 24, 24, 24, 24, 24]

dx = 0/72.; dy = -15/72. 
offset = matplotlib.transforms.ScaledTranslation(dx, dy, plt.gcf().dpi_scale_trans)

all_types = ["SmartNIC", "NetBricks", "SafeBricks"]
all_tasks = ["Firewall", "DPI", "NAT", "Maglev", "LPM", "Monitor"]
all_tasks_legend = ["FW", "DPI", "NAT", "LB", "LPM", "Mon."]
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
        **dict.fromkeys(["./rawdata/nic"], "SmartNIC"), 
        **dict.fromkeys(["./rawdata/nb"], "NetBricks"), 
        **dict.fromkeys(["./rawdata/sb"], "SafeBricks"), 
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
        # break 

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
                        

def get_t_draw_data_vary_core(_type, _task, _ipsec, _trace):
    data_vec = list()
    for _core in all_cores:
        data_vec.append(t_val_med[_type][_task][_ipsec][_trace][_core])
    return data_vec

def draw_t_trend_for_task_ipsec_trace(_task, _ipsec, _trace):
    N = len(all_cores)
    ind = np.arange(N) * 10 + 10    # the x locations for the groups    
    width = 6.0/len(all_types)       # the width of the bars: can also be len(x) sequence

    cnt = 0
    legends = list()
    for _type in all_types:
        data_vec = get_t_draw_data_vary_core(_type, _task, _ipsec, _trace)
        p1, = plt.plot(ind, data_vec, linestyle = linestyles[cnt], marker = markers[cnt], markersize = markersizes[cnt],
            color=colors[cnt], linewidth=3)

        legends.append(p1)
        cnt += 1

    plt.legend(legends, all_types)
    plt.ylabel('Throughput (Mpps)')
    plt.xlabel('\# cores')
    plt.xticks(ind, all_cores)
    # apply offset transform to all x ticklabels.
    for label in plt.axes().xaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offset)

    plt.axes().set_ylim(ymin=0)
    plt.tight_layout()
    plt.savefig('./figures/trend_core/throughput/t_trend_core_%s_%s_%s.pdf' % (_task, _trace, _ipsec))
    plt.clf()



def get_l_draw_data_vary_core(_type, _task, _ipsec, _trace):
    data_vec_avg = list()
    data_vec_tail = list()
    for _core in all_cores:
        data_vec_avg.append(avg_l_val_med[_type][_task][_ipsec][_trace][_core])
        data_vec_tail.append(tail_l_val_med[_type][_task][_ipsec][_trace][_core])
    return data_vec_avg, data_vec_tail

def draw_l_trend_for_task_ipsec_trace(_task, _ipsec, _trace):
    N = len(all_cores)
    ind = np.arange(N) * 10 + 10    # the x locations for the groups    
    width = 6.0/len(all_types)       # the width of the bars: can also be len(x) sequence

    cnt = 0
    legends = list()
    for _type in all_types:
        data_vec_avg, data_vec_tail = get_l_draw_data_vary_core(_type, _task, _ipsec, _trace)
        yerr = np.zeros((2, len(data_vec_avg)))
        yerr[0, :] = np.array(data_vec_avg) - np.array(data_vec_avg)
        yerr[1, :] = np.array(data_vec_tail) - np.array(data_vec_avg)
        
        (p1, caps, _) = plt.errorbar(ind, data_vec_avg, yerr = yerr[1, :],
            linestyle = linestyles[cnt], marker = markers[cnt], markersize = markersizes[cnt],
            color=colors[cnt], linewidth=3, capthick=2, capsize=10, elinewidth=2, lolims=True, ecolor=colors[cnt])
        legends.append(p1)
        caps[0].set_marker('_')
        caps[1].set_marker('')

        cnt += 1

    plt.legend(legends, all_types)
    plt.ylabel('Avg. and 99th tail latency (microsecond)')
    plt.xlabel('\# cores')
    plt.xticks(ind, all_cores)
    # apply offset transform to all x ticklabels.
    for label in plt.axes().xaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offset)

    plt.axes().set_ylim(ymin=0)
    plt.tight_layout()
    plt.savefig('./figures/trend_core/latency/l_trend_core_%s_%s_%s.pdf' % (_task, _trace, _ipsec))
    plt.clf()

    


def get_t_draw_data_vary_core_6nfs(_type, _task, _ipsec, _trace):
    data_vec = list()
    for _core in all_cores:
        data_vec.append(t_val_med[_type][_task][_ipsec][_trace][_core])
    return data_vec

def draw_t_trend_for_ipsec_trace_6nfs(_ipsec, _trace):
    N = len(all_cores)
    ind = np.arange(N) * 10 + 10    # the x locations for the groups    
    width = 6.0/len(all_tasks)       # the width of the bars: can also be len(x) sequence

    cnt = 0
    legends = list()
    for _task in all_tasks:
        data_vec = get_t_draw_data_vary_core_6nfs("SmartNIC", _task, _ipsec, _trace)
        p1, = plt.plot(ind, data_vec, linestyle = linestyles[cnt], marker = markers[cnt], markersize = markersizes[cnt],
            color=colors[cnt], linewidth=3)

        legends.append(p1)
        cnt += 1

    plt.legend(legends, all_tasks_legend, ncol=2)
    plt.ylabel('Throughput (Mpps)')
    plt.xlabel('\# cores')
    plt.xticks(ind, all_cores)
    # apply offset transform to all x ticklabels.
    for label in plt.axes().xaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offset)
    # plt.yscale('log')

    plt.axes().set_ylim(ymin=0)
    plt.tight_layout()
    plt.savefig('./figures/trend_core/sixnfs/t_trend_core_%s_%s.pdf' % (_trace, _ipsec))
    plt.clf()


if __name__ == '__main__':
    plt.rc('text', usetex=True)
    font = fm.FontProperties(
       family = 'Gill Sans',
       fname = '/usr/share/fonts/truetype/adf/GilliusADF-Regular.otf')

    data_load("./rawdata/nic")
    data_load("./rawdata/nb")
    data_load("./rawdata/sb")

    process_draw_data()

    # for _ipsec in all_ipsecs:
    #     for _trace in all_traces:
    #         for _task in all_tasks:
    #             draw_t_trend_for_task_ipsec_trace(_task, _ipsec, _trace)
    #             draw_l_trend_for_task_ipsec_trace(_task, _ipsec, _trace)


    draw_t_trend_for_ipsec_trace_6nfs("gcm_ipsec", "64B")