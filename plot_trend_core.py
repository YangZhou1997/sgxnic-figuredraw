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
from util_patterns import *
from util_dataparse_throughput import *
rcParams.update(params_line)

dx = 0/72.; dy = -15/72. 
offset = matplotlib.transforms.ScaledTranslation(dx, dy, plt.gcf().dpi_scale_trans)

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

    plt.legend(legends, all_types, frameon=False)
    plt.ylabel('Throughput (Mpps)')
    plt.xlabel('\# cores')
    plt.xticks(ind, all_cores)
    # apply offset transform to all x ticklabels.
    for label in plt.axes().xaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offset)
    plt.axes().grid(which='major', axis='y', linestyle=':')
    plt.axes().set_axisbelow(True)

    plt.axes().set_ylim(ymin=0)
    plt.tight_layout()
    plt.savefig('./figures/trend_core/throughput/t_trend_%scores_%s_%s.pdf' % (_task, _trace, _ipsec))
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

    plt.legend(legends, all_types, frameon=False)
    plt.ylabel('Avg. and 99th tail latency (microsecond)')
    plt.xlabel('\# cores')
    plt.xticks(ind, all_cores)
    # apply offset transform to all x ticklabels.
    for label in plt.axes().xaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offset)
    plt.axes().grid(which='major', axis='y', linestyle=':')
    plt.axes().set_axisbelow(True)

    plt.axes().set_ylim(ymin=0)
    plt.tight_layout()
    plt.savefig('./figures/trend_core/latency/l_trend_%scores_%s_%s.pdf' % (_task, _trace, _ipsec))
    plt.clf()

    


def get_t_draw_data_vary_core_6nfs(_type, _task, _ipsec, _trace):
    data_vec = list()
    for _core in all_cores:
        data_vec.append(t_val_med[_type][_task][_ipsec][_trace][_core])
    return data_vec

def draw_t_trend_for_ipsec_trace_6nfs(_type, _ipsec, _trace):
    N = len(all_cores)
    ind = np.arange(N) * 10 + 10    # the x locations for the groups    
    width = 6.0/len(all_tasks)       # the width of the bars: can also be len(x) sequence

    cnt = 0
    legends = list()
    for _task in all_tasks:
        data_vec = get_t_draw_data_vary_core_6nfs(_type, _task, _ipsec, _trace)
        p1, = plt.plot(ind, data_vec, linestyle = linestyles[cnt], marker = markers[cnt], markersize = markersizes[cnt],
            color=colors[cnt], linewidth=3)
        print(str(all_tasks_figure[cnt]) + ": " + str(data_vec))        

        legends.append(p1)
        cnt += 1

    plt.legend(legends, all_tasks_figure, ncol=2, frameon=False)
    plt.ylabel('Throughput (Mpps)')
    plt.xlabel('\# of cores')
    plt.xticks(ind, all_cores)
    # apply offset transform to all x ticklabels.
    for label in plt.axes().xaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offset)
    # plt.yscale('log')
    plt.axes().grid(which='major', axis='y', linestyle=':')
    plt.axes().set_axisbelow(True)

    plt.axes().set_ylim(ymin=0)
    plt.tight_layout()
    plt.savefig('./figures/trend_core/sixnfs/t_trend_core_6nfs_%s_%s_%s.pdf' % (_type, _trace, _ipsec))
    plt.clf()


if __name__ == '__main__':
    plt.rc('text', usetex=True)
    font = fm.FontProperties(
       family = 'Gill Sans',
       fname = '/usr/share/fonts/truetype/adf/GilliusADF-Regular.otf')

    data_load(f'./{data_dir}/nic/sixnfs.res')
    data_load(f'./{data_dir}/nb/sixnfs.res')
    data_load(f'./{data_dir}/sb/sixnfs.res')

    process_draw_data()

    # for _ipsec in all_ipsecs:
    #     for _trace in all_traces:
    #         for _task in all_tasks:
    #             draw_t_trend_for_task_ipsec_trace(_task, _ipsec, _trace)
    #             draw_l_trend_for_task_ipsec_trace(_task, _ipsec, _trace)


    draw_t_trend_for_ipsec_trace_6nfs("SmartNIC", "gcm_ipsec", "64B")
    draw_t_trend_for_ipsec_trace_6nfs("SmartNIC", "sha_ipsec", "64B")

    draw_t_trend_for_ipsec_trace_6nfs("SmartNIC", "gcm_ipsec", "ICTF")
    draw_t_trend_for_ipsec_trace_6nfs("SmartNIC", "sha_ipsec", "ICTF")
