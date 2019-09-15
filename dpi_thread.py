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

all_types = ["SmartNIC"]
all_tasks = ["16 threads", "32 threads", "48 threads"]
all_tasks_legend = ["16", "32", "48"]
all_ipsecs = ["no_ipsec", "gcm_ipsec"]
all_traces = ["ICTF", "64B", "256B", "512B", "1KB"]
all_cores = ["1", "2", "4", "8", "16", "32"]

def get_type(ori_name):
    switcher = {
        **dict.fromkeys(["./rawdata/dpi"], "SmartNIC")
    }
    return switcher.get(ori_name, "Invalid path name %s" % (ori_name,))

def get_task(ori_name):
    switcher = {
        **dict.fromkeys(["hfa-se-maxperf-check-0x1", "hfa-se-maxperf-ipsec-check-0x1"], "16 threads"), 
        **dict.fromkeys(["hfa-se-maxperf-check-0x3", "hfa-se-maxperf-ipsec-check-0x3"], "32 threads"), 
        **dict.fromkeys(["hfa-se-maxperf-check-0x7", "hfa-se-maxperf-ipsec-check-0x7"], "48 threads")
    }
    return switcher.get(ori_name, "Invalid task name %s" % (ori_name,))

def get_ipsec(ori_name):
    no_ipsec_names = ["hfa-se-maxperf-check-0x1", "hfa-se-maxperf-check-0x3", "hfa-se-maxperf-check-0x7"]
    gcm_ipsec_names = ["hfa-se-maxperf-ipsec-check-0x1", "hfa-se-maxperf-ipsec-check-0x3", "hfa-se-maxperf-ipsec-check-0x7"]

    switcher = {
        **dict.fromkeys(no_ipsec_names, "no_ipsec"), 
        **dict.fromkeys(gcm_ipsec_names, "gcm_ipsec")
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
        **dict.fromkeys(["0xFFFF", "16"], "16"),
        **dict.fromkeys(["0xFFFFFFFF", "32"], "32")
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
                        

def get_t_draw_data_vary_task_dpi(_type, _ipsec, _trace, _core):
    data_vec = list()
    for _task in all_tasks:
        data_vec.append(t_val_med[_type][_task][_ipsec][_trace][_core])
    return data_vec

def draw_t_trend_for_ipsec_trace_core_dpi(_ipsec, _trace, _core):

    N = len(all_tasks)
    ind = np.arange(N) * 10 + 10    # the x locations for the groups    

    cnt = 0
    legends = list()
    for _type in all_types:
        data_vec = get_t_draw_data_vary_task_dpi(_type, _ipsec, _trace, _core)
        p1, = plt.plot(ind, data_vec, linestyle = linestyles[cnt], marker = markers[cnt], markersize = markersizes[cnt],
            color=colors[cnt], linewidth=3)
        print(str(all_types[cnt]) + ": " + str(data_vec))        

        legends.append(p1)
        cnt += 1

    # plt.legend(legends, all_types)
    plt.ylabel('Throughput (Mpps)')
    plt.xticks(ind, all_tasks_legend)
    plt.xlabel('\# of hardware threads')

    # apply offset transform to all x ticklabels.
    for label in plt.axes().xaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offset)

    # plt.axes().set_ylim(ymin=0, ymax=0.8)
    plt.axes().set_ylim(ymin=0)

    plt.tight_layout()
    plt.savefig('./figures/dpi_thread/t_trend_dpithread_%s_%s_%score.pdf' % (_ipsec, _trace, _core))
    plt.clf()


if __name__ == '__main__':
    plt.rc('text', usetex=True)
    font = fm.FontProperties(
       family = 'Gill Sans',
       fname = '/usr/share/fonts/truetype/adf/GilliusADF-Regular.otf')

    data_load("./rawdata/dpi")

    process_draw_data()

    for _ipsec in all_ipsecs:
        for _trace in all_traces:
            for _core in all_cores:
                draw_t_trend_for_ipsec_trace_core_dpi(_ipsec, _trace, _core)