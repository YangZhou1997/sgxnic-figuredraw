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
    for i in range(num_prog - 1):
        ret += prog_set[i] + '.'
    ret += prog_set[-1]
    return ret
multiprog = list(map(lambda x: prog_set_to_cmd(x), multiprog))

def load_data():
    f_list = glob.glob('./m5out/*')
    for f in f_list:
        f_stats = open(f'{f}/{f}_stats.txt')
        lines = f_stats.read().split('\n')
        


if __name__ == '__main__':
    plt.rc('text', usetex=True)
    font = fm.FontProperties(
       family = 'Gill Sans',
       fname = '/usr/share/fonts/truetype/adf/GilliusADF-Regular.otf')

