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

def get_t_draw_data_vary_task(_type, _ipsec, _trace, _core, norm_flag=False):
    data_vec = list()
    for _task in all_tasks:
        if _type == "SmartNIC": 
            data_vec.append(t_val_med[_type][_task][_ipsec][_trace]['4'])
            # data_vec.append(t_val_med[_type][_task][_ipsec][_trace]['1'])
        else:
            data_vec.append(t_val_med[_type][_task][_ipsec][_trace][_core])
    return data_vec

def draw_t_bar_for_core_ipsec_trace(_core, _ipsec, _trace, norm_flag=False):
    N = len(all_tasks)
    ind = np.arange(N) * 10 + 10    # the x locations for the groups    
    width = 6.0/len(all_types)       # the width of the bars: can also be len(x) sequence

    height = 0.0
    
    fig, ax = plt.subplots()
    cnt = 0
    legends = list()
    all_data_vec = []
    for _type in all_types:
        data_vec = get_t_draw_data_vary_task(_type, _ipsec, _trace, _core)
        if _ipsec == "no_ipsec" and _trace == "ICTF":
            print(list(map(lambda x: float('%.02f'%(x,)), data_vec)))
        all_data_vec.append(data_vec)
        height = max(height, max(data_vec))
        p1 = plt.bar(ind + width * (cnt - len(all_types) / 2.0 + 0.5), data_vec, width, color=colors[cnt], hatch=patterns[cnt], edgecolor = 'k', align="center")
        legends.append(p1)
        cnt += 1
    
    if _trace in ['ICTF', '64B'] and _ipsec == 'sha_ipsec' and norm_flag == False:
        print("Section 5.4,", _trace, 'SHA, No NORM: nic dpi vs nb ac: {:.2f}'.format(all_data_vec[0][1]/all_data_vec[1][1]))
        print("Section 5.4,", _trace, 'SHA, No NORM: nic dpi vs sb ac: {:.2f}'.format(all_data_vec[0][1]/all_data_vec[2][1]))

    if _trace == '64B' and _ipsec == 'sha_ipsec' and norm_flag:
        nb_min, sb_min = 1 << 30, 1 << 30
        nb_max, sb_max = 0, 0
        for i in range(N):
            nb_factor = all_data_vec[0][i]/all_data_vec[1][i]
            sb_factor = all_data_vec[0][i]/all_data_vec[2][i]
            nb_min = min(nb_min, nb_factor)
            sb_min = min(sb_min, sb_factor)
            nb_max = max(nb_max, nb_factor)
            sb_max = max(sb_max, sb_factor)
            # if i in [1, 7]:
            #     print(i, '{:.2f}'.format(nb_factor), '{:.2f}'.format(sb_factor))
        print('Appendix A 64B, SHA, NORM: NIC vs NB {:.2f}--{:.2f}'.format(nb_min, nb_max))
        print('Appendix A 64B, SHA, NORM: NIC vs SB {:.2f}--{:.2f}'.format(sb_min, sb_max))

    if _trace == 'ICTF' and _ipsec == 'no_ipsec' and norm_flag == False:
        print("Appendix A", _trace, 'RAW, No NORM: nic dpi vs nb ac: {:.2f}'.format(all_data_vec[0][1]/all_data_vec[1][1]))
        print("Appendix A", _trace, 'RAW, No NORM: nic dpi vs sb ac: {:.2f}'.format(all_data_vec[0][1]/all_data_vec[2][1]))

    if _trace == '64B' and _ipsec == 'gcm_ipsec' and norm_flag == False:
        nb_min, sb_min = 1 << 30, 1 << 30
        nb_max, sb_max = 0, 0
        for i in range(N):
            nb_factor = all_data_vec[0][i]/all_data_vec[1][i]
            sb_factor = all_data_vec[0][i]/all_data_vec[2][i]
            nb_min = min(nb_min, nb_factor)
            sb_min = min(sb_min, sb_factor)
            nb_max = max(nb_max, nb_factor)
            sb_max = max(sb_max, sb_factor)
        # print(_ipsec)        
        print('Appendix A, GCM, 64B, No NORM: NIC vs NB {:.2f}--{:.2f}'.format(nb_min, nb_max))
        print('Appendix A, GCM, 64B, No NORM: NIC vs SB {:.2f}--{:.2f}'.format(sb_min, sb_max))


    ax.legend(legends, all_types, ncol=3, frameon=False)
    if norm_flag:
        ax.set_ylabel('Throughput per dollar (Mpps/\$)', fontsize=34)
    else:
        ax.set_ylabel('Throughput (Mpps)', fontsize=34)
    plt.xticks(ind, all_tasks_figure)
    # apply offset transform to all x ticklabels.
    for label in ax.xaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offset)
    ax.grid(which='major', axis='y', linestyle=':')
    ax.set_axisbelow(True)
    
    ax.set_ylim(ymin = 0, ymax=height * 1.25)

    plt.tight_layout()
    if norm_flag:
        plt.savefig('./figures/throughput/t_bar_%scores_%s_%s_norm.pdf' % (_core, _ipsec, _trace))
    else:
        plt.savefig('./figures/throughput/t_bar_%scores_%s_%s.pdf' % (_core, _ipsec, _trace))
    plt.clf()

def draw_t_bar_for_core_trace(_core, _trace, norm_flag=False):
    N = len(all_tasks) * 3
    ind = np.array([10, 20, 30, 40, 50, 60,  75, 85, 95, 105, 115, 125,  140, 150, 160, 170, 180, 190])
    width = 2       # the width of the bars: can also be len(x) sequence

    height = 0.0

    fig, ax = plt.subplots()
    cnt = 0
    legends = list()
    for _type in all_types:
        data_vec = []
        for _ipsec in all_ipsecs:
            _data_vec = get_t_draw_data_vary_task(_type, _ipsec, _trace, _core, norm_flag)
            data_vec.extend(_data_vec)
        height = max(height, max(data_vec))
        p1 = plt.bar(ind + width * (cnt - len(all_types) / 2.0 + 0.5), data_vec, width, color=colors[cnt], hatch=patterns[cnt], edgecolor = 'k', align="center")
        legends.append(p1)
        cnt += 1
    
    ax.legend(legends, all_types, ncol=3, frameon=False, fontsize=32, handlelength=2, loc='best', columnspacing=2)
    plt.text(35, -2.5 * height / 11.3144, 'W/o IPSec', fontsize=28, horizontalalignment='center', verticalalignment='center')
    plt.text(100, -2.5 * height / 11.3144, 'W/ AES\_GCM128 IPSec', fontsize=28, horizontalalignment='center', verticalalignment='center')
    plt.text(165, -2.5 * height / 11.3144, 'W/ AES\_CBC128\_SHA256 IPSec', fontsize=28, horizontalalignment='center', verticalalignment='center')

    if norm_flag:
        ax.set_ylabel('Throughput per dollar (Mpps/\$)')
    else:
        ax.set_ylabel('Throughput (Mpps)')
    plt.xticks(ind, all_tasks_figure * 3, fontsize=28)
    # apply offset transform to all x ticklabels.
    for label in ax.xaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offset)
    ax.grid(which='major', axis='y', linestyle=':')
    ax.set_axisbelow(True)
    
    # ax.set_ylim(ymin = 0, ymax=height * 1.25)
    print(height)
    plt.gcf().set_size_inches(24, 8)

    plt.tight_layout()
    if norm_flag:
        plt.savefig('./figures/throughput/3in1/t_bar_%scores_%s_norm.pdf' % (_core, _trace))
    else:
        plt.savefig('./figures/throughput/3in1/t_bar_%scores_%s.pdf' % (_core, _trace))
    plt.clf()


def draw_t_bar_for_core_ipsec(_core, _ipsec, norm_flag=False):
    N = len(all_tasks) * 2
    ind = np.array([10, 20, 30, 40, 50, 60,  75, 85, 95, 105, 115, 125])
    width = 2       # the width of the bars: can also be len(x) sequence

    height = 0.0

    fig, ax = plt.subplots()
    cnt = 0
    legends = list()
    all_data_vec = []
    for _type in all_types:
        data_vec = []
        for _trace in ['64B', 'ICTF']:
            _data_vec = get_t_draw_data_vary_task(_type, _ipsec, _trace, _core, norm_flag)
            data_vec.extend(_data_vec)
        height = max(height, max(data_vec))
        p1 = plt.bar(ind + width * (cnt - len(all_types) / 2.0 + 0.5), data_vec, width, color=colors[cnt], hatch=patterns[cnt], edgecolor = 'k', align="center")
        legends.append(p1)
        cnt += 1
        all_data_vec.append(data_vec)

    if _ipsec == 'sha_ipsec':
        nb_min, sb_min = 1 << 30, 1 << 30
        nb_max, sb_max = 0, 0
        for i in range(N):
            nb_factor = all_data_vec[0][i]/all_data_vec[1][i]
            sb_factor = all_data_vec[0][i]/all_data_vec[2][i]
            nb_min = min(nb_min, nb_factor)
            sb_min = min(sb_min, sb_factor)
            nb_max = max(nb_max, nb_factor)
            sb_max = max(sb_max, sb_factor)
        print('Section 5.4, SHA, No NORM: NIC vs NB {:.2f}--{:.2f}'.format(nb_min, nb_max))
        print('Section 5.4, SHA, No NORM: NIC vs SB {:.2f}--{:.2f}'.format(sb_min, sb_max))

    ax.legend(legends, all_types, ncol=3, frameon=False, fontsize=32, handlelength=2, loc='upper center', columnspacing=2)
    plt.text(35, -0.25 * height, '64B CAIDA trace', fontsize=32, horizontalalignment='center', verticalalignment='center')
    plt.text(100, -0.25 * height, 'ICTF trace', fontsize=32, horizontalalignment='center', verticalalignment='center')

    if norm_flag:
        ax.set_ylabel('Throughput per dollar (Mpps/\$)')
    else:
        ax.set_ylabel('Throughput (Mpps)')
    plt.xticks(ind, all_tasks_figure * 2, fontsize=28)
    # apply offset transform to all x ticklabels.
    for label in ax.xaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offset)
    ax.grid(which='major', axis='y', linestyle=':')
    ax.set_axisbelow(True)
    
    ax.set_ylim(ymin = 0, ymax=height * 1.25)
    # print(height)
    plt.gcf().set_size_inches(24, 8)

    plt.tight_layout()
    if norm_flag:
        plt.savefig('./figures/throughput/2in1/t_bar_%scores_%s_norm.pdf' % (_core, _ipsec))
    else:
        plt.savefig('./figures/throughput/2in1/t_bar_%scores_%s.pdf' % (_core, _ipsec))
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

    # process_draw_data()
    # all_cores_wecare = ["1"]
    # for _core in all_cores_wecare:
    #     draw_t_bar_for_core_trace(_core, "64B")
    #     draw_t_bar_for_core_trace(_core, "ICTF")

    # process_draw_data(norm_flag=True)
    # all_cores_wecare = ["1"]
    # for _core in all_cores_wecare:
    #     draw_t_bar_for_core_trace(_core, "64B", norm_flag=True)
    #     draw_t_bar_for_core_trace(_core, "ICTF", norm_flag=True)

    process_draw_data()
    all_cores_wecare = ["1"]
    for _core in all_cores_wecare:
        for _ipsec in all_ipsecs:
            draw_t_bar_for_core_ipsec(_core, _ipsec)

    # process_draw_data(norm_flag=True)
    # all_cores_wecare = ["1"]
    # for _core in all_cores_wecare:
    #     for _ipsec in all_ipsecs:
    #         draw_t_bar_for_core_ipsec(_core, _ipsec, norm_flag=True)
