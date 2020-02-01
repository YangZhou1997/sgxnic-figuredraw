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
from util_dataparse_throughput import *
rcParams.update(params_bar)

dx = 0/72.; dy = -15/72. 
offset = matplotlib.transforms.ScaledTranslation(dx, dy, plt.gcf().dpi_scale_trans)

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
        p1 = plt.bar(ind + width * (cnt - len(all_types) / 2.0 + 0.5), data_vec, width, color=colors[cnt], hatch=patterns[cnt], edgecolor = 'k', align="center")
        legends.append(p1)
        cnt += 1
    
    plt.legend(legends, all_types, ncol=3, frameon=False)
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
        plt.savefig('./figures/throughput/t_bar_%scores_%s_%s_norm.pdf' % (_core, _ipsec, _trace))
    else:
        plt.savefig('./figures/throughput/t_bar_%scores_%s_%s.pdf' % (_core, _ipsec, _trace))
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