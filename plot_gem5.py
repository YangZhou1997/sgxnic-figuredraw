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
import re

 # brewer2mpl.get_map args: set name  set type  number of colors
# bmap = brewer2mpl.get_map('Paired', 'qualitative', 12)
bmap = brewer2mpl.get_map('Dark2', 'qualitative', 6)
colors = bmap.mpl_colors

linestyles = ['--', '-.', '-', ':', (0, (3, 5, 1, 5, 1, 5)), (0, (3, 1, 1, 1))]
markers = ['*', '^', 'o', 'P', 'p', 'v']
markersizes = [30, 24, 24, 24, 24, 24]

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


nfinvoke = ['acl-fw', 'dpi-queue', 'nat-tcp-v4', 'maglev', 'lpm', 'monitoring']
cpus = ['TimingSimpleCPU', 'DerivO3CPU']
l2_size = ['4MB', '2MB', '1MB', '512kB', '256kB']

singleprog = nfinvoke
multiprog = []
for i in range(1, 1 << 6):
    prog_set = []
    for j in range(6):
        if (i >> j) & 1 == 1:
            prog_set.append(nfinvoke[j])
    multiprog.append(prog_set)
multiprog = list(filter(lambda x: len(x) > 1, multiprog))
# print(multiprog, len(multiprog))

def prog_set_to_cmd(prog_set):
    ret = ''
    num_prog = len(prog_set)
    if num_prog != 0:
        for i in range(num_prog - 1):
            ret += prog_set[i] + '.'
        ret += prog_set[-1]
    return ret
multiprog = list(map(lambda x: prog_set_to_cmd(x), multiprog))

# "throughput" -> "TimingSimpleCPU" -> "monitoring" -> "standalone"/"nat-tcp-v4" -> "l2 cache"
rawdata = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(float)))))

def extract_stdout(f_name):
    found = re.search('stdout_(.+?)\.out', f_name).group(1)
    return found

def extract_m5out(f_name):
    found = re.search('m5out\/(.+?)\/', f_name).group(1)
    return found

ticks_base = 1000000000000 # one second
def extract_lasting_times(contents):
    r = re.search('Switched\ CPUS\ \@\ tick\ (.+?)\n', contents)
    if r: 
        start_ticks = int(r.group(1))
    else:
        start_ticks = 0

    r = re.search('Exiting\ \@\ tick\ (.+?)\ ', contents)
    if r:
        end_ticks = int(r.group(1))
    else:
        end_ticks = 5 * ticks_base    

    return (end_ticks - start_ticks) * 1.0 / ticks_base

def extract_packet_num(contents, nf):
    lines = contents.split('\n')
    start_num = 0
    end_num = 0
    for line in lines:
        if f'{nf} packets processed:' in line:
            start_num = int(line.split()[3])
            break
    for line in lines[::-1]:
        if f'{nf} packets processed:' in line:
            end_num = int(line.split()[3])
            break
    return end_num - start_num        

def extract_miss_rate(contents):
    lines = contents.split('\n')
    for line in lines:
        if 'system.l2.overall_miss_rate::total' in line:
            return float(line.split()[1])
    return 0        

def load_data():
    f_list = glob.glob('./gem5data2/results/*.out')
    for f_name in f_list:
        # print(f_name)
        splits = extract_stdout(f_name).split('_')
        cpu = splits[0]
        nfs_str = splits[1].replace('dpi-queue', 'dpi')
        cachesize = splits[2]

        contents = open(f_name).read()
        index = contents.find('Switched CPUS @ tick ')
        contents = contents[index:]

        nfs = nfs_str.split('.')
        
        lasting_time = extract_lasting_times(contents)
        for nf in nfs:
            packet_num = extract_packet_num(contents, nf)
            th_value = packet_num / lasting_time / (1000000)
            
            corun_nfs_list = nfs.copy()
            corun_nfs_list.remove(nf)
            corun_nfs = prog_set_to_cmd(corun_nfs_list)
            if corun_nfs == '':
                corun_nfs = 'standalone'
            
            rawdata['throughput'][cpu][nf][corun_nfs][cachesize] = th_value

            # print('throughput', cpu, nf, corun_nfs, cachesize, th_value)

    f_list = glob.glob('./gem5data2/m5out/*')
    for f_name in f_list:
        dir_name = extract_m5out(f_name + '/')
        
        splits = dir_name.split('_')
        cpu = splits[0]
        nfs_str = splits[1].replace('dpi-queue', 'dpi')
        cachesize = splits[2]

        # this is a standalone nf
        if '.' not in nfs_str:
            nf = nfs_str
            corun_nfs = 'standalone'

            f_name = f'{f_name}/{dir_name}_stats.txt'
            print(f_name)
            contents = open(f_name).read()
            miss_rate = extract_miss_rate(contents)

            rawdata['l2missrate'][cpu][nf][corun_nfs][cachesize] = miss_rate
            print('throughput', cpu, nf, corun_nfs, cachesize, miss_rate)
        else:
            pass # not sure if we can extract the l2 cache miss rate for individual nf




if __name__ == '__main__':
    plt.rc('text', usetex=True)
    font = fm.FontProperties(
       family = 'Gill Sans',
       fname = '/usr/share/fonts/truetype/adf/GilliusADF-Regular.otf')

    load_data()