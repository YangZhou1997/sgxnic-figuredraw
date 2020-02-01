import brewer2mpl
import glob

 # brewer2mpl.get_map args: set name  set type  number of colors
# bmap = brewer2mpl.get_map('Paired', 'qualitative', 12)
bmap = brewer2mpl.get_map('Dark2', 'qualitative', 6)
colors = bmap.mpl_colors

linestyles = ['--', '-.', '-', ':', (0, (3, 5, 1, 5, 1, 5)), (0, (3, 1, 1, 1))]
markers = ['*', '^', 'o', 'P', 'p', 'v']
markersizes = [30, 24, 24, 24, 24, 24]
patterns = [ "|" , "\\" , "/" , "+" , "-", ".", "*","x", "o", "O" ]

params_line = {
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
params_bar = {
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