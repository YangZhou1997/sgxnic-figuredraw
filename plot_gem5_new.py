#!/usr/bin/python3

import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib import rcParams
from collections import defaultdict
import glob
import re
import os
from termcolor import colored
from util_serilize import *
from util_patterns import *
params_line = {
    'axes.labelsize': 36,
    'font.size': 36,
    'legend.fontsize': 36,
    'xtick.labelsize': 36,
    'ytick.labelsize': 36,
    'text.usetex': False,
    'figure.figsize': [12, 8],
    'legend.fontsize': 36,
    'legend.handlelength': 1.5,
    'legend.loc': 'best', 
    'legend.columnspacing': 0.8,
    "lines.markersize": 14,
    "lines.markerfacecolor": "none",
    "lines.markeredgewidth": 3,
}
rcParams.update(params_line)

dx = 0/72.; dy = -15/72. 
offset = matplotlib.transforms.ScaledTranslation(dx, dy, plt.gcf().dpi_scale_trans)

nfinvoke = ['acl-fw', 'dpi', 'nat-tcp-v4', 'maglev', 'lpm', 'monitoring']
nfinvoke_legend = ["FW", "DPI", "NAT", "LB", "LPM", "Mon."]
cpus = ['detailed']
modes = ['none', 'tp']
l2_size = ['8kB', '16kB', '32kB', '64kB', '128kB', '256kB', '512kB', '1MB', '2MB', '4MB', '8MB', '16MB']
datadir = 'gem5data/lowl2cache'

def bit_num(x):
    cnt = 0
    for i in range(32):
        if ((x >> i) & 1) == 1:
            cnt += 1
    return cnt        

singleprog = nfinvoke
multiprog = []
for i in range(1, 1 << 6):
    prog_set = []
    bitn = bit_num(i)
    if bitn not in [1, 2, 4]:
        continue
    for j in range(6):
        if (i >> j) & 1 == 1:
            prog_set.append(nfinvoke[j])
    multiprog.append(prog_set)
# print(multiprog, len(multiprog))

for i in range(6):
    for j in range(6):
        if j == i:
            continue
        for k in range(6):
            if k == j or k == i:
                continue
            prog_set = []
            prog_set.append(nfinvoke[i])
            prog_set.append(nfinvoke[j])
            prog_set.append(nfinvoke[k])
            multiprog.append(prog_set)

def prog_set_to_cmd(prog_set):
    ret = ''
    num_prog = len(prog_set)
    if num_prog != 0:
        for i in range(num_prog - 1):
            ret += prog_set[i] + '.'
        ret += prog_set[-1]
    return ret
multiprog = list(map(lambda x: prog_set_to_cmd(x), multiprog))

# "ipc"/"l2missrate" -> "detailed" -> "monitoring" -> "nat-tcp-v4.lpm" -> "l2 cache size" -> "tp"/"none" -> value
rawdata = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(float))))))


def extract_m5out(f_name):
    found = re.search('m5out\/(.+?)\/', f_name).group(1)
    return found

def extract_miss_rate(contents, nf, cpu_id, num_nfs, mode):
    if contents == '':
        print(colored('Error: m5out content null', 'red'))
        return 1

    lines = contents.split('\n')

    if num_nfs == 1:
        for line in lines:
            if 'system.l2.overall_miss_rate::total' in line:
                miss_rate = float(line.split()[1])
                return miss_rate
        print(colored('Error: m5out no l2.overall_miss_rate', 'red'))            
        return 1
    else: # num_nfs = 2 or 4:
        if mode == 'tp':
            for line in lines:
                if f'system.l2{cpu_id}.overall_miss_rate::total' in line:
                    miss_rate = float(line.split()[1])
                    return miss_rate
            print(colored(f'Error: m5out no l2{cpu_id}.overall_miss_rate', 'red'))            
        else: # none
            overall_accesses = 0
            overall_hits = 0
            overall_misses = 0
            for line in lines:
                if f'system.l2.overall_accesses::switch_cpus{cpu_id}.data' in line:
                    overall_accesses += int(line.split()[1])
                if f'system.l2.overall_accesses::switch_cpus{cpu_id}.inst' in line:
                    overall_accesses += int(line.split()[1])

                if f'system.l2.overall_hits::switch_cpus{cpu_id}.data' in line:
                    overall_hits += int(line.split()[1])
                if f'system.l2.overall_hits::switch_cpus{cpu_id}.inst' in line:
                    overall_hits += int(line.split()[1])

                if f'system.l2.overall_misses::switch_cpus{cpu_id}.data' in line:
                    overall_misses += int(line.split()[1])
                if f'system.l2.overall_misses::switch_cpus{cpu_id}.inst' in line:
                    overall_misses += int(line.split()[1])
            
            if overall_accesses == 0:
                print(colored('Error: m5out overall_accesses is zero', 'red'))
                return 1
            if overall_misses != 0:
                return overall_misses * 1.0 / overall_accesses
            if overall_hits != 0:
                return 1- overall_hits * 1.0 / overall_accesses
            
            print(colored('Error: m5out no overall_hits and overall_misses', 'red'))
            return 1

def extract_ipc(contents, nf, cpu_id, num_nfs, mode):
    if contents == '':
        print(colored('Error: m5out content null', 'red'))
        return 1

    lines = contents.split('\n')

    if num_nfs == 1:
        for line in lines:
            if 'system.switch_cpus.ipc_total' in line:
                ipc = float(line.split()[1])
                return ipc
        print(colored('Error: m5out no system.switch_cpus.ipc_total', 'red'))            
        return 1
    else: # num_nfs = 2 or 4:
        for line in lines:
            if f'system.switch_cpus{cpu_id}.ipc_total' in line:
                ipc = float(line.split()[1])
                return ipc
        print(colored(f'Error: m5out no system.switch_cpus{cpu_id}.ipc_total', 'red'))            


# system.l2.demand_hits::.switch_cpus0.data
def get_cpuids_from_name(nfs_str):
    nf_cpu_ids = defaultdict(lambda : [])
    nfs = nfs_str.split('.')
    idx = 0
    for nf in nfs:
        nf_cpu_ids[nf] = f'{idx}'
        idx += 1
    return nf_cpu_ids    

def load_data():
    f_list = glob.glob(f'./{datadir}/m5out/*')
    for f_name in f_list:
        # if 'TimingSimpleCPU_dpi-queue_' not in f_name:
        #     continue

        print(f_name)
        dir_name = extract_m5out(f_name + '/')
        
        splits = dir_name.split('_')
        cpu = splits[0]
        nfs_str = splits[1]
        cachesize = splits[2]
        mode = splits[3]

        f_name = f'{f_name}/{dir_name}_stats.txt'
        # print(f_name)
        contents = open(f_name).read()

        nf_cpu_ids = get_cpuids_from_name(nfs_str)
        nfs = nfs_str.split('.')
        num_nfs = len(nfs)

        for nf in nfs:
            corun_nfs = prog_set_to_cmd(nfs)
            cpu_id = nf_cpu_ids[nf]
            # print(nf)
            # print(cpu_id)

            miss_rate = extract_miss_rate(contents, nf, cpu_id, num_nfs, mode)
            ipc = extract_ipc(contents, nf, cpu_id, num_nfs, mode)

            rawdata['l2missrate'][cpu][nf][corun_nfs][cachesize][mode] = miss_rate
            rawdata['ipc'][cpu][nf][corun_nfs][cachesize][mode] = ipc

            print('l2missrate', cpu, nf, corun_nfs, cachesize, mode, miss_rate)
            print('ipc', cpu, nf, corun_nfs, cachesize, mode, ipc)
         
        print('')

nf_to_corun_nfs = defaultdict(lambda: defaultdict(lambda: []))

def load_nf_to_corun_nfs():
    f_list = glob.glob(f'./gem5data/tp_100M_ins_8_16_nfs/m5out/*')
    for f_name in f_list:
        dir_name = extract_m5out(f_name + '/')
        splits = dir_name.split('_')
        nfs_str = splits[1]

        nfs = nfs_str.split('.')
        nf = nfs[0]
        corun_nfs = prog_set_to_cmd(nfs)
        nf_to_corun_nfs[nf][len(nfs)].append(corun_nfs)
    

def load_data_8_16_nfs():
    f_list = glob.glob(f'./gem5data/tp_100M_ins_8_16_nfs/m5out/*')
    for f_name in f_list:
        # if 'TimingSimpleCPU_dpi-queue_' not in f_name:
        #     continue

        print(f_name)
        dir_name = extract_m5out(f_name + '/')
        
        splits = dir_name.split('_')
        cpu = splits[0]
        nfs_str = splits[1]
        cachesize = splits[2]
        mode = splits[3]

        f_name = f'{f_name}/{dir_name}_stats.txt'
        # print(f_name)
        contents = open(f_name).read()

        nfs = nfs_str.split('.')
        num_nfs = len(nfs)

        # for nf in nfs:
        nf = nfs[0]
        corun_nfs = prog_set_to_cmd(nfs)
        cpu_id = '00' if len(nfs) == 16 else '0'
        # print(nf)
        # print(cpu_id)

        miss_rate = extract_miss_rate(contents, nf, cpu_id, num_nfs, mode)
        ipc = extract_ipc(contents, nf, cpu_id, num_nfs, mode)

        rawdata['l2missrate'][cpu][nf][corun_nfs][cachesize][mode] = miss_rate
        rawdata['ipc'][cpu][nf][corun_nfs][cachesize][mode] = ipc

        print('l2missrate', cpu, nf, corun_nfs, cachesize, mode, miss_rate)
        print('ipc', cpu, nf, corun_nfs, cachesize, mode, ipc)
         
        print('')


def get_datavec_vary_cachesize(_type, _cpu, _nf, _domain):
    data_vec = list()
    data_vec_tail = list()
    data_vec_lowtail = list()
    for _cachesize in l2_size:
        tps = []
        nones = []
        nf_combs = multiprog.copy()
        for nf_comb in nf_combs:
            if _nf in nf_comb:
                dot_num = nf_comb.count('.')
                if dot_num + 1 == _domain:
                    tps.append(rawdata[_type][_cpu][_nf][nf_comb][_cachesize]['tp'])
                    nones.append(rawdata[_type][_cpu][_nf][nf_comb][_cachesize]['none'])
        tp = np.array(tps)
        none = np.array(nones)
        if _type == 'ipc':
            ratios = (none - tp) / none
        else:
            ratios = (tp - none) / none
        data_vec.append(np.median(ratios))
        data_vec_tail.append(np.percentile(ratios, 99))
        data_vec_lowtail.append(np.percentile(ratios, 1))
    return list(map(lambda x: x * 100, data_vec)), list(map(lambda x: x * 100, data_vec_tail)), list(map(lambda x: x * 100, data_vec_lowtail))

# type: ipc or l2missrate
def plot_vary_cachesize(_type, _cpu, _domain):
    N = len(l2_size)
    ind = np.arange(N) * 10 + 10    # the x locations for the groups   
    width = 0.5       # the width of the bars: can also be len(x) sequence

    avg_4mb = []

    fig = plt.figure()
    ax = fig.subplots(nrows=1, ncols=1)
    
    cnt = 0
    legends = list()
    for _nf in singleprog:
        data_vec, data_vec_tail, data_vec_lowtail = get_datavec_vary_cachesize(_type, _cpu, _nf, _domain)
        yerr = np.zeros((2, len(data_vec)))
        yerr[0, :] = np.array(data_vec) - np.array(data_vec_lowtail)
        yerr[1, :] = np.array(data_vec_tail) - np.array(data_vec)
        
        if _type == 'ipc' and _domain == 2:
            print(_nf)
            print(data_vec)
            print(data_vec_tail)
            print(data_vec_lowtail)
            print()
            avg_4mb.append(data_vec[-3])
            
        (p1, caps, _) = ax.errorbar(ind + width * (cnt - (N - 7) / 2.0), data_vec, yerr = yerr,
            linestyle = linestyles[cnt], marker = markers[cnt], markersize = markersizes[cnt]*2/3,
            color=colors[cnt], linewidth=3, capthick=2, capsize=5, elinewidth=2, ecolor=colors[cnt])
        caps[0].set_marker('_')
        caps[1].set_marker('_')

        # p1, = plt.plot(ind, data_vec, linestyle = linestyles[cnt], marker = markers[cnt], markersize = markersizes[cnt],
            # color=colors[cnt], linewidth=3)
        # p1 = plt.bar(ind + width * (cnt - (N - 7) / 2.0), data_vec, width, color=colors[cnt], hatch=patterns[cnt], edgecolor = 'k', align="center")
        legends.append(p1)
        cnt += 1
    if _type == 'ipc' and _domain == 2:
        print('{:.2f}'.format(np.average(avg_4mb)))

    ax.legend(legends, nfinvoke_legend, loc='best', ncol=2, frameon=False)
    if _type == 'ipc':
        ax.set_ylabel('IPC degrading percent (\%)')
    elif _type == 'l2missrate':
        ax.set_ylabel('L2 missing rate increasing')

    ax.set_xticks(ind, list(map(lambda x: x.upper(), l2_size)), rotation=45, ha="right", rotation_mode="anchor")
    # plt.xticks(ind, l2_size)
    # plt.axes().set_ylim(ymin=0)

    # apply offset transform to all x ticklabels.
    for label in ax.xaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offset)
    ax.grid(which='major', axis='y', linestyle=':')
    ax.set_axisbelow(True)

    plt.gcf().set_size_inches(12, 8)
    plt.tight_layout()
    plt.savefig(f'./figures/gem5/cachesize_{_type}_{_cpu}_{_domain}domains.pdf')
    plt.clf()
    
    fig_folder = './figures/gem5/'
    fig_full_name = f'./figures/gem5/cachesize_{_type}_{_cpu}_{_domain}domains'

    os.system(
        f"pdf-crop-margins -suv -p 1 -o {fig_folder} {fig_full_name}.pdf -mo >"
        " /dev/null"
    )
    os.system(f"rm {fig_full_name}_uncropped.pdf > /dev/null")


def get_datavec_vary_corun(_type, _cpu, _nf, _l2size):
    nf_combs = multiprog.copy()
    nf_combs.extend(singleprog)
    
    data_vec = []
    data_vec_tail = []
    data_vec_lowtail = []
    tps = [[] for i in range(5)]
    nones = [[] for i in range(5)]
    
    for nf_comb in nf_combs:
        if _nf in nf_comb:
            dot_num = nf_comb.count('.')
            if dot_num == 0:
                continue

            tps[dot_num - 1].append(rawdata[_type][_cpu][_nf][nf_comb][_l2size]['tp'])
            nones[dot_num - 1].append(rawdata[_type][_cpu][_nf][nf_comb][_l2size]['none'])

    # for 8 and 16 nfs
    for i, num_nf in zip([3, 4], [8, 16]):
        for corun_nf in nf_to_corun_nfs[_nf][num_nf]:
            tps[i].append(rawdata[_type][_cpu][_nf][corun_nf][_l2size]['tp'])
            nones[i].append(rawdata[_type][_cpu][_nf][corun_nf][_l2size]['none'])

    for i in range(5):
        if _type == 'ipc':
            ratios = (np.array(nones[i]) - np.array(tps[i])) / np.array(nones[i])
        else:
            ratios = (np.array(tps[i]) - np.array(nones[i])) / np.array(nones[i])
        data_vec.append(np.median(ratios))
        data_vec_tail.append(np.percentile(ratios, 99))
        data_vec_lowtail.append(np.percentile(ratios, 1))
   
    return list(map(lambda x: x * 100, data_vec)), list(map(lambda x: x * 100, data_vec_tail)), list(map(lambda x: x * 100, data_vec_lowtail))

# type: ipc or l2missrate
def plot_vary_corun(_type, _cpu, _l2size):
    N = 5
    ind = np.array([10, 20, 30, 40, 50])    # the x locations for the groups    
    width = 1.2       # the width of the bars: can also be len(x) sequence

    fig = plt.figure()
    ax = fig.subplots(nrows=1, ncols=1)

    avg_8dom = []
    avg_16dom = []
    cnt = 0
    legends = list()
    for _nf in singleprog:
        data_vec, data_vec_tail, data_vec_lowtail = get_datavec_vary_corun(_type, _cpu, _nf, _l2size)
        yerr = np.zeros((2, len(data_vec)))
        yerr[0, :] = np.array(data_vec) - np.array(data_vec_lowtail)
        yerr[1, :] = np.array(data_vec_tail) - np.array(data_vec)
        
        if _type == 'ipc' and _l2size == '4MB':
            print(_nf)
            print(data_vec)
            print(data_vec_tail)
            print(data_vec_lowtail)
            print()
            avg_8dom.append(data_vec[-2])
            avg_16dom.append(data_vec[-1])

        # p1, = plt.plot(ind, data_vec, linestyle = linestyles[cnt], marker = markers[cnt], markersize = markersizes[cnt],
        #     color=colors[cnt], linewidth=3)
        p1 = ax.bar(ind + width * (cnt - (N - 1) / 2.0 - 0.5), data_vec, width, yerr = yerr, color=colors[cnt], hatch=patterns[cnt], 
            edgecolor = 'k', align="center", capsize=5, ecolor='k', error_kw = dict(capthick=2, elinewidth=2))
        
        # (_, caps, _) = plt.errorbar(ind + width * (cnt - (N - 1) / 2.0 - 1.5), data_vec_tail, yerr = yerr[1, :],
        #     linestyle = linestyles[cnt], color=colors[cnt], linewidth=3, capthick=2, capsize=5, elinewidth=2, lolims=True, ecolor='k')
        # caps[0].set_marker('_')
        # caps[1].set_marker('')
        
        legends.append(p1)
        cnt += 1
    if _type == 'ipc' and _l2size == '4MB':
        print('{:.2f} {:.2f}'.format(np.average(avg_8dom), np.average(avg_16dom)))

    ax.legend(legends, nfinvoke_legend, loc='upper left', ncol=2, frameon=False)
    if _type == 'ipc':
        ax.set_ylabel('IPC degrading percent (\%)')
    elif _type == 'l2missrate':
        ax.set_ylabel('L2 missing rate increasing')
        
    ax.set_xticks(ind, ['2 NFs', '3 NFs', '4 NFs', '8 NFs', '16 NFs'], rotation=45, ha="right", rotation_mode="anchor")
    ax.set_xlim(xmin=4, xmax=56)
    # plt.xticks(ind, ['1 domain', '2 domains', '4 domains'], rotation=45, ha="right", rotation_mode="anchor", fontsize=24)
    # plt.axes().set_ylim(ymin=0)

    # apply offset transform to all x ticklabels.
    for label in ax.xaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offset)
    ax.grid(which='major', axis='y', linestyle=':')
    ax.set_axisbelow(True)

    plt.gcf().set_size_inches(12, 8)
    plt.tight_layout()
    plt.savefig(f'./figures/gem5/domain_{_type}_{_cpu}_{_l2size}.pdf')
    plt.clf()

    fig_folder = './figures/gem5/'
    fig_full_name = f'./figures/gem5/domain_{_type}_{_cpu}_{_l2size}'

    os.system(
        f"pdf-crop-margins -suv -p 1 -o {fig_folder} {fig_full_name}.pdf -mo >"
        " /dev/null"
    )
    os.system(f"rm {fig_full_name}_uncropped.pdf > /dev/null")


if __name__ == '__main__':
    plt.rc('text', usetex=True)
    font = fm.FontProperties(
       family = 'Gill Sans',
       fname = './GilliusADF-Regular.otf')

    # load_data()
    # load_data_8_16_nfs()
    # write_to_file(rawdata, f'./{datadir}/drawdata/thrput_l2miss.res')

    rawdata = read_from_file(f'./{datadir}/drawdata/thrput_l2miss.res')
    load_nf_to_corun_nfs()
    # plot_vary_cachesize('l2missrate', cpus[0], 2)
    plot_vary_cachesize('ipc', cpus[0], 2)
    plot_vary_corun('ipc', cpus[0], '4MB')
