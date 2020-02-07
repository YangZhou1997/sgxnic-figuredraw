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
    'legend.fontsize': 28,
    'legend.handlelength': 2,
    'legend.loc': 'best', 
    'legend.columnspacing': 1
}
rcParams.update(params_line)

dx = 0/72.; dy = -15/72. 
offset = matplotlib.transforms.ScaledTranslation(dx, dy, plt.gcf().dpi_scale_trans)


nfinvoke = ['acl-fw', 'dpi', 'nat-tcp-v4', 'maglev', 'lpm', 'monitoring']
nfinvoke_legend = ["FW", "DPI", "NAT", "LB", "LPM", "Mon."]
cpus = ['detailed']
modes = ['none', 'tp']
l2_size = ['1MB', '2MB', '4MB', '8MB', '16MB']
datadir = 'gem5data/tp_100mins_sec_mix'

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
            # print(cpu_ids)

            miss_rate = extract_miss_rate(contents, nf, cpu_id, num_nfs, mode)
            ipc = extract_ipc(contents, nf, cpu_id, num_nfs, mode)

            rawdata['l2missrate'][cpu][nf][corun_nfs][cachesize][mode] = miss_rate
            rawdata['ipc'][cpu][nf][corun_nfs][cachesize][mode] = ipc

            print('l2missrate', cpu, nf, corun_nfs, cachesize, mode, miss_rate)
            print('ipc', cpu, nf, corun_nfs, cachesize, mode, ipc)
         
        print('')


def get_datavec_vary_cachesize(_type, _cpu, _nf, _domain):
    data_vec = list()
    for _cachesize in l2_size:
        nf_combs = multiprog.copy()
        tp = 0.0
        none = 0.0
        cnt = 0
        for nf_comb in nf_combs:
            if _nf in nf_comb:
                dot_num = nf_comb.count('.')
                if dot_num + 1 == _domain:
                    tp += rawdata[_type][_cpu][_nf][nf_comb][_cachesize]['tp']
                    none += rawdata[_type][_cpu][_nf][nf_comb][_cachesize]['none']
                    cnt += 1
        tp /= cnt
        none /= cnt          
        if _type == 'ipc':
            data_vec.append((none - tp) / none)
        else:
            data_vec.append((tp - none) / none)
    return list(map(lambda x: x * 100, data_vec))

# type: ipc or l2missrate
def plot_vary_cachesize(_type, _cpu, _domain):
    N = len(l2_size)
    ind = np.arange(N) * 10 + 10    # the x locations for the groups   
    width = 1       # the width of the bars: can also be len(x) sequence

    avg_4mb = []

    cnt = 0
    legends = list()
    for _nf in singleprog:
        data_vec = get_datavec_vary_cachesize(_type, _cpu, _nf, _domain)
        if _type == 'ipc' and _domain == 2:
            print(data_vec)
            avg_4mb.append(data_vec[2])
        # p1, = plt.plot(ind, data_vec, linestyle = linestyles[cnt], marker = markers[cnt], markersize = markersizes[cnt],
            # color=colors[cnt], linewidth=3)
        p1 = plt.bar(ind + width * (cnt - (N - 1) / 2.0 - 0.5), data_vec, width, color=colors[cnt], hatch=patterns[cnt], edgecolor = 'k', align="center")
        legends.append(p1)
        cnt += 1
    if _type == 'ipc' and _domain == 2:
        print(np.average(avg_4mb))

    plt.legend(legends, nfinvoke_legend, loc='best', ncol=2, frameon=False)
    if _type == 'ipc':
        plt.ylabel('IPC degrading percent (\%)')
    elif _type == 'l2missrate':
        plt.ylabel('L2 missing rate increasing')

    # plt.xticks(ind, l2_size, rotation=45, ha="right", rotation_mode="anchor")
    plt.xticks(ind, l2_size)
    # plt.axes().set_ylim(ymin=0)

    # apply offset transform to all x ticklabels.
    for label in plt.axes().xaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offset)
    plt.axes().grid(which='major', axis='y', linestyle=':')
    plt.axes().set_axisbelow(True)

    plt.gcf().set_size_inches(15, 8)
    plt.tight_layout()
    plt.savefig(f'./figures/gem5/cachesize_{_type}_{_cpu}_{_domain}domains.pdf')
    plt.clf()

def get_datavec_vary_corun(_type, _cpu, _nf, _l2size):
    cnt_vec = [0, 0, 0, 0]    
    data_vec = [0.0, 0.0, 0.0, 0.0]
    nf_combs = multiprog.copy()
    nf_combs.extend(singleprog)

    for nf_comb in nf_combs:
        if _nf in nf_comb:
            dot_num = nf_comb.count('.')
            tp = rawdata[_type][_cpu][_nf][nf_comb][_l2size]['tp']
            none = rawdata[_type][_cpu][_nf][nf_comb][_l2size]['none']
            if _type == 'ipc':
                data_vec[dot_num] += (none - tp) / none
            else:
                data_vec[dot_num] += (tp - none) / none
            cnt_vec[dot_num] += 1
    for i in [0, 1, 2, 3]:
        data_vec[i] /= cnt_vec[i] * 1.0
    del data_vec[0]
    return list(map(lambda x: x * 100, data_vec))

# type: ipc or l2missrate
def plot_vary_corun(_type, _cpu, _l2size):
    N = 3
    ind = np.array([10, 20, 30])    # the x locations for the groups    
    width = 1       # the width of the bars: can also be len(x) sequence

    avg_4dom = []
    cnt = 0
    legends = list()
    for _nf in singleprog:
        data_vec = get_datavec_vary_corun(_type, _cpu, _nf, _l2size)
        if _type == 'ipc' and _l2size == '4MB':
            print(data_vec)
            avg_4dom.append(data_vec[1])
        # p1, = plt.plot(ind, data_vec, linestyle = linestyles[cnt], marker = markers[cnt], markersize = markersizes[cnt],
        #     color=colors[cnt], linewidth=3)
        p1 = plt.bar(ind + width * (cnt - (N - 1) / 2.0 - 2.0), data_vec, width, color=colors[cnt], hatch=patterns[cnt], edgecolor = 'k', align="center")
        legends.append(p1)
        cnt += 1
    print(np.average(avg_4dom))

    plt.legend(legends, nfinvoke_legend, loc='upper left', ncol=1, frameon=False)
    if _type == 'ipc':
        plt.ylabel('IPC degrading percent (\%)')
    elif _type == 'l2missrate':
        plt.ylabel('L2 missing rate increasing')
        
    plt.xticks(ind, ['2 NFs', '3 NFs', '4 NFs'])
    plt.axes().set_xlim(xmin=4, xmax=36)
    # plt.xticks(ind, ['1 domain', '2 domains', '4 domains'], rotation=45, ha="right", rotation_mode="anchor", fontsize=24)
    # plt.axes().set_ylim(ymin=0)

    # apply offset transform to all x ticklabels.
    for label in plt.axes().xaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offset)
    plt.axes().grid(which='major', axis='y', linestyle=':')
    plt.axes().set_axisbelow(True)

    plt.gcf().set_size_inches(9, 8)
    plt.tight_layout()
    plt.savefig(f'./figures/gem5/domain_{_type}_{_cpu}_{_l2size}.pdf')
    plt.clf()


if __name__ == '__main__':
    plt.rc('text', usetex=True)
    font = fm.FontProperties(
       family = 'Gill Sans',
       fname = '/usr/share/fonts/truetype/adf/GilliusADF-Regular.otf')

    # load_data()
    # write_to_file(rawdata, f'./{datadir}/drawdata/thrput_l2miss.res')

    rawdata = read_from_file(f'./{datadir}/drawdata/thrput_l2miss.res')
    for _type in ['ipc', 'l2missrate']:
        for _cpu in cpus:
            for _domain in [2]:
                plot_vary_cachesize(_type, _cpu, _domain)
            for _l2size in ['4MB']:
                plot_vary_corun(_type, _cpu, _l2size)

