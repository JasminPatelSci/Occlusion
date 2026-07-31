# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 09:54:23 2026

Plotting code for cross-decoding maps + difference plots Experiment 1

@author: JasminPatel, based on code from 
William Turner bootstrapbill.github.io, williamfrancisturner@gmail.com
& Tim Cottier https://github.com/TCottier96

file locations removed 30.07.26
"""

import os
os.chdir(r'_')

import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
from scipy.ndimage import gaussian_filter
from plot_funcs import load_data, cluster_correct
import matplotlib 
import pickle
import pandas as pd
import matplotlib as mpl
from matplotlib.ticker import FuncFormatter

from rpy2.robjects import r, pandas2ri
import rpy2.robjects as ro
from rpy2.robjects.packages import importr
import rpy2.robjects.packages as rpackages
from rpy2.robjects.conversion import localconverter


time = 1 #change per timewindow
if time == 2:
    times = 38
else:
    times = 26
    


dataFolder = fr'_'
allScores = load_data(dataFolder)
scores = np.mean(allScores, axis=0)

font = {'family' : 'DejaVu Sans',
        'weight' : 'normal',
        'size'   : 34}
plt.rc('font', **font)
matplotlib.rc('font', **font)
plt.rcParams['axes.unicode_minus'] = False


sigma = 1
scaler = 0.0005


###############################################################################


fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(24, 9))
inds = [0, 2, 4]

for i, ax in enumerate(axes.ravel()):
    
    plotData = np.mean(np.stack((np.mean(scores[inds[i], :, :, :], axis = 0), 
                        np.flip(np.mean(scores[inds[i] + 1, :, :, :], 
                                        axis = 0), axis = 1)), axis = 2), 
                       axis = 2)
    plotData = gaussian_filter(plotData, sigma)
    
    im = ax.matshow(plotData, extent=[0, 40, -1000, 1000],
                        vmin=0.025 - scaler, vmax=0.025 + scaler, 
                        cmap='PuOr_r', origin='lower', aspect = 'auto')  
 

    ax.axhline(0, color='k', linestyle='--', lw=3)
    
            
        
    if i in [0]:
        ax.plot([20, 40], [0, 500], color = 'k', lw=2)
        ax.plot([0, 20], [500, 1000], color = 'k', lw=2)
        ax.set_title('Appearance\n', fontweight='bold')
        ax.set_ylabel('Time (ms)', fontweight='bold')
        ax.set_xlabel('\nPosition', fontweight='bold')
        ax.set_yticks([-250, 0, 1000])

    if i in [1]:
        ax.plot([20, 40], [-1000, -500], color = 'k', lw=3)
        ax.plot([0, 20], [-500, 0], color = 'k', lw=3)
        ax.plot([20, 40], [0, 500], color = 'k', lw=3, linestyle=':')
        ax.set_yticks([])
        ax.set_title('Disappearance\n', fontweight='bold')
    if i in [2]:
        ax.plot([20, 40], [0, 500], color = 'k', lw=2, linestyle='--')
        ax.plot([0, 20], [500, 1000], color = 'k', lw=2)
        ax.plot([0, 20], [-500, 0], color = 'k', lw=2)
        ax.set_yticks([])
        ax.set_title('Occlusion\n', fontweight='bold')        
        ax.axhline(500, color='k', linestyle='--', lw=3)
        
    ax.xaxis.set_ticks_position('bottom')
    ax.set_xticks([0, 20, 40], [r'$-\pi$', '0', r'$\pi$'])
    ax.set_ylim((-250, 1000))
    
cb_ax = fig.add_axes([0.93, 0.12, 0.02, 0.76])
cbar = fig.colorbar(im, cax=cb_ax)
chance=1/40
cbar.set_ticks([chance - scaler, chance, chance + scaler])
cbar.set_ticklabels(['-' + str(round(scaler*10000)), '', 
                     str(round(scaler*10000))])
cbar.ax.set_ylabel('Position Evidence (1e-4)', rotation=270, labelpad=25, 
                    fontweight='bold')


###############################################################################
allData = np.array(allScores)
allData = allData.reshape(22, 2, 6, times, 1024, 40)
allData = allData.mean(axis=1)

inds = 2

offset = []

for p in range(allData.shape[0]):
    data = allData[p]
    data = np.mean(np.stack((np.mean(data[inds, :, :, :], axis = 0), 
                       np.flip(np.mean(data[inds + 1, :, :, :], axis = 0), 
                               axis = 1)), axis = 2), axis = 2)

    offset.append(data)
    
offset = np.stack(offset, axis=0)
    
inds = 4

occlu = []

for p in range(allData.shape[0]):
    data = allData[p]
    data = np.mean(np.stack((np.mean(data[inds, :, :, :], axis = 0), 
                        np.flip(np.mean(data[inds + 1, :, :, :], axis = 0), 
                                axis = 1)), axis = 2), axis = 2)
    
    occlu.append(data)
    
occlu = np.stack(occlu, axis = 0)


dis = np.mean(offset, axis=0)
occlusion = np.mean(occlu, axis=0)

def shiftMap(data):
    
    time, pos = data.shape
    realigned = np.empty_like(data)
    shifts = np.linspace(10, 0, time)
    for t in range(time):
        realigned[t] = np.roll(data[t], int(round(shifts[t])))
        
    return realigned


Slice = np.mean([dis[383:512], occlusion[383:512]], axis=0)
rSlice = shiftMap(Slice)




#visualise realignment

# fig, ax = plt.subplots(nrows=1,ncols=1, figsize=(12, 6))

# chance=1/40 #change for diff
# im = ax.matshow(rSlice, extent=[0, 40, -250, 0],
                    # vmin=chance - scaler, vmax=chance + scaler, 
                    # cmap='PuOr_r', origin='lower', aspect = 'auto')  
# ax.set_title(f'd & o av realign T{time}\n', fontweight='bold')
# ax.set_ylabel('Time (ms)', fontweight='bold')
# ax.set_xlabel('\n  Relative position', fontweight='bold')        
# ax.xaxis.set_ticks_position('bottom')
# ax.set_ylim((-250, 0))
# ax.axvline(20, color='k', lw=3)
# ax.set_xticks([0, 20, 40], [r'$-\pi$', '0', r'$\pi$'])




#visualise relative position realigned slice plot
tSlice = np.mean(rSlice, axis=0)

# fig, ax = plt.subplots(1, 1, figsize = (12,6))
# xtimes = np.linspace(0,40,40)

# ax.plot(xtimes, tSlice, color='r', zorder=10)

# ax.axhline(1/40, color='k', lw=3)
# ax.set_xlim(xmin=0, xmax=40)
# ax.set_ylabel('Position Evidence (1e-4)', fontweight='bold')
# ax.spines['right'].set_visible(False)
# ax.spines['top'].set_visible(False)


# d = tSlice - 1/40
# crossings = np.where(np.diff(np.sign(d)) != 0)[0]
# print(crossings)





###############################################################################

tSlice = np.mean(rSlice, axis=0)

fig, ax = plt.subplots(1, 1, figsize=(12,9))
xpos = np.arange(len(tSlice))

chance = 1/40

vals = tSlice - chance

norm = mpl.colors.TwoSlopeNorm(
    vmin=np.min(vals),
    vcenter=0,
    vmax=np.max(vals)
)

cmap = plt.cm.PuOr_r
colors = cmap(norm(vals))

# Width chosen so adjacent bars touch
bar_width = np.diff(xpos).mean()

ax.bar(
    xpos,
    vals,      # height relative to chance
    bottom=0,
    width=bar_width,
    color=colors,
    edgecolor='none',
    alpha=0.8,
    align='center',
    zorder=2
)

ax.plot(xpos, vals, color='r', lw=2, zorder=10)
ax.axhline(0, color='k', lw=3)
ax.set_xlim(0, len(tSlice)-1)
ax.axvline(20, color='k', linestyle='--', lw=3)
ax.set_ylabel('Position Evidence (1e-4)', fontweight='bold')
ax.yaxis.set_major_formatter(
    FuncFormatter(lambda y, _: f'{y*10000:.0f}')
)


ax.hlines(
    0.00055,
    left,
    right,
    color='k',
    linewidth=4,
    zorder=20
)

ax.set_xlabel('Relative Position', fontweight='bold')
ax.set_xticks([0, 20, 40], [r'$-\pi$', '0', r'$\pi$'])

ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)




#run before above
peak_idx = np.argmax(vals)
peak_val = vals[peak_idx]

half_height = peak_val / 2

above_half = vals >= half_height

# contiguous region containing the peak
left = peak_idx
while left > 0 and above_half[left]:
    left -= 1

right = peak_idx
while right < len(vals)-1 and above_half[right]:
    right +=1

print(f"FWHM region: {left}–{right}")








# visualise/plot of masked area
# n_time = 1024
# n_pos = 40

# mask = np.zeros((n_time, n_pos), dtype=bool)

# shifts = np.linspace(0, -80, n_time)

# for t in range(n_time):

#     shift = int(round(shifts[t]))

#     roi_realigned = np.arange(left, right)

#     roi_original = (roi_realigned - shift) % n_pos

#     mask[t, roi_original] = True
    
# plt.imshow(mask.T,
#            aspect='auto',
#            origin='lower',
#            interpolation='none')
# plt.xlabel('Time')
# plt.ylabel('Position')



###############################################################################
# visualise/plot of masked area on data
# fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(16, 9))
# inds = [2, 4]

# for i, ax in enumerate(axes.ravel()):
    
    # plotData = np.mean(np.stack((np.mean(scores[inds[i], :, :, :], axis = 0), 
    #                     np.flip(np.mean(scores[inds[i] + 1, :, :, :], 
    #                                     axis = 0), axis = 1)), axis = 2), 
    #                    axis = 2)
    # plotData = gaussian_filter(plotData, sigma)
    
    # ax.matshow(plotData, extent=[0, 40, -1000, 1000],
    #                     vmin=0.025 - scaler, vmax=0.025 + scaler, 
    #                     cmap='Greys', origin='lower', aspect = 'auto')  
    # masked_data = np.ma.masked_where(~mask, plotData)
    # ax.matshow(masked_data, extent=[0, 40,-1000, 1000],
    #                       vmin=chance - scaler, vmax=chance + scaler, 
    #                       cmap='PuOr_r', origin='lower', aspect = 'auto')
 

#     ax.axhline(0, color='k', linestyle='--', lw=3)
    

#     if i in [0]:
#         ax.plot([20, 40], [-1000, -500], color = 'k', lw=3)
#         ax.plot([0, 20], [-500, 0], color = 'k', lw=3)
#         ax.plot([20, 40], [0, 500], color = 'k', lw=3, linestyle=':')
#         ax.set_title('Disappearance\n', fontweight='bold')
#         ax.set_yticks([-250, 0, 1000])
#     if i in [1]:
#         ax.plot([20, 40], [0, 500], color = 'k', lw=2, linestyle='--')
#         ax.plot([0, 20], [500, 1000], color = 'k', lw=2)
#         ax.plot([0, 20], [-500, 0], color = 'k', lw=2)
#         ax.set_yticks([])
#         ax.set_title('Occlusion\n', fontweight='bold')        
#         ax.axhline(500, color='k', linestyle='--', lw=3)
        
#     ax.xaxis.set_ticks_position('bottom')
#     ax.set_xticks([0, 20, 40], [r'$-\pi$', '0', r'$\pi$'])
#     ax.set_ylim((-250, 1000))


###############################################################################

chance = 1/40
xtimes = np.linspace(-1000,1000,1024)
x = xtimes
mask = (xtimes >= -250) & (xtimes <= 1000)

def shiftData(data, left, right):
    
    subj, time, pos = data.shape
    realigned = np.empty_like(data)

    shifts = np.linspace(0, -80, time)

    for k in range(data.shape[0]):  
        for t in range(time):             
            realigned[k, t] = np.roll(data[k, t], int(round(shifts[t])))
            
    data = realigned[:, :, left:(right-1)]
    data = data - chance
    data = np.mean(data, axis=2)
    
    plot = np.mean(data, axis=0)
    plot = plot * 10000
    sem = np.std(data, axis=0) / np.sqrt(data.shape[0])
    sem = sem * 10000
        
    return data, plot, sem

oData, oPlot, oSEM = shiftData(occlu, left, right)
dData, dPlot, dSEM = shiftData(offset, left, right)

diffData = oData - dData

pvals = cluster_correct(diffData)
sig_marker = pvals < 0.05



def save_data(file, scores):
    with open(file, 'wb') as f:
        pickle.dump(scores, f)

from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

cmap = LinearSegmentedColormap.from_list(
    'grey_green',
    [
        '#666666',   # strong H0
        '#FFFFFF',   # inconclusive
        '#00AA00'    # strong H1
    ]
)

cmapo = LinearSegmentedColormap.from_list(
    'grey_yellow',
    [
        '#666666',   # strong H0
        '#FFFFFF',   # inconclusive
        '#FFB915'    # strong H1
    ]
)

cmapd = LinearSegmentedColormap.from_list(
    'grey_blue',
    [
        '#666666',   # strong H0
        '#FFFFFF',   # inconclusive
        '#003F66'    # strong H1
    ]
)

norm = TwoSlopeNorm(
    vmin=-1,    # BF = 0.01
    vcenter=0,  # BF = 1
    vmax=1      # BF = 100
)


def bayes_factors(data, cmap):

    utils = rpackages.importr('utils')
    utils.chooseCRANmirror(ind=1)
    packnames = ('BayesFactor', 'ggplot2')
    from rpy2.robjects.vectors import StrVector
    names_to_install = [x for x in packnames if not rpackages.isinstalled(x)]
    if len(names_to_install) > 0:
        utils.install_packages(StrVector(names_to_install))
    bf_package = importr('BayesFactor')
    timepoints = data.shape[1]
    df_norm = pd.DataFrame((data))
    with localconverter(ro.default_converter + pandas2ri.converter):
        rData = ro.conversion.py2rpy(df_norm)
    bf = []
    cols = []
    for t in range(timepoints): # t loops through the columns
        results = bf_package.ttestBF(x=rData[t], mu=0, rscale='medium')
        bf.append(np.asarray(r['as.vector'](results))[0])
        
    logBF = np.log10(bf)
    cols = cmap(norm(logBF))
    
    return bf, logBF, cols




bf_o, logBFo, bf_colorsO = bayes_factors(oData, cmapo)
bf_d, logBFd, bf_colorsD = bayes_factors(dData, cmapd)
bf_diff, logBFdiff, bf_colorsDiff = bayes_factors(diffData, cmap)

# save_data(fr'_', bf_o)
# save_data(fr'_', bf_d)
# save_data(fr'_', bf_diff)





# ############################################################################

font = {'family' : 'DejaVu Sans',
        'weight' : 'normal',
        'size'   : 24}
plt.rc('font', **font)
matplotlib.rc('font', **font)
plt.rcParams['axes.unicode_minus'] = False



##with bayes
fig, ax = plt.subplots(
    nrows=4,
    ncols=1,
    figsize=(12, 10),
    sharex=True,
    gridspec_kw={"height_ratios": [8, 1, 1, 1]}
)

ax_main = ax[0]
ax_o    = ax[1]
ax_d    = ax[2]
ax_diff = ax[3]

x = xtimes
oPlotData = gaussian_filter(oPlot, sigma)
dPlotData = gaussian_filter(dPlot, sigma)
oSEMl = gaussian_filter(oPlot - oSEM, sigma)
oSEMh = gaussian_filter(oPlot + oSEM, sigma)
dSEMl = gaussian_filter(dPlot - dSEM, sigma)
dSEMh = gaussian_filter(dPlot + dSEM, sigma)


ax_main.plot(xtimes, oPlotData, color='#FFB915', zorder=10)
ax_main.plot(xtimes, dPlotData, color='#003F66', zorder=9)

ax_main.fill_between(xtimes, oSEMh, oSEMl, alpha=0.3, color='#FFB915', 
                     zorder=5)
ax_main.fill_between(xtimes, dSEMh, dSEMl, alpha=0.3, color='#003F66', 
                     zorder=4)

ax_main.set_ylabel('Position Evidence (1e-4)', fontweight='bold', fontsize=20)
ax_main.hlines(0, -250, 1000, color="black")
ax_o.set_xlim(xmin=-250, xmax=1000)
ax_main.set_ylim(ymin=-5, ymax=13)
from matplotlib.ticker import MultipleLocator, FuncFormatter

ax_main.yaxis.set_major_locator(MultipleLocator(5))

ax_main.yaxis.set_major_formatter(
    FuncFormatter(lambda y, _: f'{y:.0f}')
)
ax_main.spines['right'].set_visible(False)
ax_main.spines['top'].set_visible(False)
ax_main.axvspan(-250, 0, color='grey', alpha=0.2, zorder=1)
ax_main.axvspan(500, 1000, color='grey', alpha=0.2, zorder=1)


ax_main.scatter(xtimes[mask], np.full(np.sum(mask), -4), s=4, c="black", 
alpha=sig_marker[mask], linewidths=0)


legend_handles = [
     mlines.Line2D([], [], color='#FFB915', linestyle='-', linewidth=2, 
                   label='Occlusion'),
     mlines.Line2D([], [], color='#003F66', linestyle='-', linewidth=2, 
                   label='Disappearance'),
]

ax_main.legend(handles=legend_handles, loc='upper right', 
               bbox_to_anchor=(1, 1), fontsize=12, frameon=True)


for i in range(len(bf_o)):
    ax_o.plot(x[i], logBFo[i], color=bf_colorsO[i], marker='o', 
              markersize=3, markeredgecolor='black', markeredgewidth=0.1, 
              lw=0)

ax_o.set_ylim([-5, 5]) 
ax_o.set_yticks([-5, 0, 5], [r'10$^{-5}$', '0', r'10$^5$'], fontsize=16)
ax_o.set_xlim(xmin=-250, xmax=1000)
ax_o.spines['right'].set_visible(False)
ax_o.spines['top'].set_visible(False)
ax_o.hlines(0, -250, 1000, color="black", linewidth=0.5)
ax_o.axvspan(-250, 0, color='grey', alpha=0.2, zorder=1)
ax_o.axvspan(500, 1000, color='grey', alpha=0.2, zorder=1)



for i in range(len(bf_d)):
    ax_d.plot(x[i], logBFd[i], color=bf_colorsD[i], marker='o', markersize=3, 
              markeredgecolor='black', markeredgewidth=0.1, lw=0)

ax_d.set_ylim([-5, 5]) 
ax_d.set_yticks([-5, 0, 5], [r'10$^{-5}$', '0', r'10$^5$'], fontsize=16)
ax_d.set_xlim(xmin=-250, xmax=1000)
ax_d.spines['right'].set_visible(False)
ax_d.spines['top'].set_visible(False)
ax_d.hlines(0, -250, 1000, color="black", linewidth=0.5)
ax_d.axvspan(-250, 0, color='grey', alpha=0.2, zorder=1)
ax_d.axvspan(500, 1000, color='grey', alpha=0.2, zorder=1)



for i in range(len(bf_diff)):
    ax_diff.plot(x[i], logBFdiff[i], color=bf_colorsDiff[i], marker='o', 
                 markersize=3, markeredgecolor='black', markeredgewidth=0.1, 
                 lw=0)

ax_diff.set_ylim([-5, 5]) 
ax_diff.set_yticks([-5, 0, 5], [r'10$^{-5}$', '0', r'10$^5$'], fontsize=16)
ax_diff.set_xlim(xmin=-250, xmax=1000)
ax_diff.spines['right'].set_visible(False)
ax_diff.spines['top'].set_visible(False)
ax_diff.hlines(0, -250, 1000, color="black", linewidth=0.5)
ax_diff.set_xlabel('Time (ms)', fontweight='bold', fontsize=20)
ax_diff.axvspan(-250, 0, color='grey', alpha=0.2, zorder=1)
ax_diff.axvspan(500, 1000, color='grey', alpha=0.2, zorder=1)






#############################################appear############################



allData = np.array(allScores)
allData = allData.reshape(22, 2, 6, times, 1024, 40)
allData = allData.mean(axis=1)

inds = 0

onset = []

for p in range(allData.shape[0]):
    data = allData[p]
    data = np.mean(np.stack((np.mean(data[inds, :, :, :], axis = 0), 
                        np.flip(np.mean(data[inds + 1, :, :, :], axis = 0), 
                                axis = 1)), axis = 2), axis = 2)

    onset.append(data)
    
onset = np.stack(onset, axis=0)
    
inds = 4

occlu = []

for p in range(allData.shape[0]):
    data = allData[p]
    data = np.mean(np.stack((np.mean(data[inds, :, :, :], axis = 0), 
                        np.flip(np.mean(data[inds + 1, :, :, :], axis = 0), 
                                axis = 1)), axis = 2), axis = 2)
    
    occlu.append(data)
    
occlu = np.stack(occlu, axis = 0)






xtimes = np.linspace(-1000,1000,1024)
x = xtimes

def shiftData(data, left, right):
    
    chance = 1/40
    subj, time, pos = data.shape
    realigned = np.empty_like(data)

    shifts = np.linspace(0, -80, time)

    for k in range(data.shape[0]):  
        for t in range(time):             
            realigned[k, t] = np.roll(data[k, t], int(round(shifts[t])))
            
    data = realigned[:, :, left:(right-1)]
    data = data - chance
    data = np.mean(data, axis=2)
    
    plot = np.mean(data, axis=0)
    plot = plot * 10000
    sem = np.std(data, axis=0) / np.sqrt(data.shape[0])
    sem = sem * 10000
        
    return data, plot, sem



oData, oPlot, oSEM = shiftData(occlu, left, right)
aData, aPlot, aSEM = shiftData(onset, left, right)

asData, asPlot, asSEM = aData[:, 461:666], aPlot[461:666], aSEM[461:666]
osData, osPlot, osSEM = oData[:, 717:922], oPlot[717:922], oSEM[717:922]

diffData = osData - asData



cmap = LinearSegmentedColormap.from_list(
    'grey_green',
    [
        '#666666',   # strong H0
        '#FFFFFF',   # inconclusive
        '#00AA00'    # strong H1
    ]
)

norm = TwoSlopeNorm(
    vmin=-1,    # BF = 0.01
    vcenter=0,  # BF = 1
    vmax=1      # BF = 100
)


def bayes_factors(data, cmap):

    utils = rpackages.importr('utils')
    utils.chooseCRANmirror(ind=1)
    packnames = ('BayesFactor', 'ggplot2')
    from rpy2.robjects.vectors import StrVector
    names_to_install = [x for x in packnames if not rpackages.isinstalled(x)]
    if len(names_to_install) > 0:
        utils.install_packages(StrVector(names_to_install))
    bf_package = importr('BayesFactor')
    timepoints = data.shape[1]
    df_norm = pd.DataFrame((data))
    with localconverter(ro.default_converter + pandas2ri.converter):
        rData = ro.conversion.py2rpy(df_norm)
    bf = []
    cols = []
    for t in range(timepoints): # t loops through the columns
        results = bf_package.ttestBF(x=rData[t], mu=0, rscale='medium')
        bf.append(np.asarray(r['as.vector'](results))[0])
        
    logBF = np.log10(bf)
    cols = cmap(norm(logBF))
    
    return bf, logBF, cols



bf_diff, logBFdiff, bf_colorsDiff = bayes_factors(diffData, cmap)



# save_data(fr'_', bf_diff)






font = {'family' : 'DejaVu Sans',
        'weight' : 'normal',
        'size'   : 24}
plt.rc('font', **font)
matplotlib.rc('font', **font)
plt.rcParams['axes.unicode_minus'] = False



##with bayes
fig, ax = plt.subplots(
    nrows=2,
    ncols=1,
    figsize=(12, 7),
    sharex=True,
    gridspec_kw={"height_ratios": [8, 1]}
)

ax_main = ax[0]
ax_diff = ax[1]
xtimes = np.linspace(-100,300,205)
x = xtimes
oPlotData = gaussian_filter(osPlot, sigma)
dPlotData = gaussian_filter(asPlot, sigma)
oSEMl = gaussian_filter(osPlot - osSEM, sigma)
oSEMh = gaussian_filter(osPlot + osSEM, sigma)
dSEMl = gaussian_filter(asPlot - asSEM, sigma)
dSEMh = gaussian_filter(asPlot + asSEM, sigma)


ax_main.plot(xtimes, oPlotData, color='#FFB915', zorder=10)
ax_main.plot(xtimes, dPlotData, color='#0292eb', zorder=9)

ax_main.fill_between(xtimes, oSEMh, oSEMl, alpha=0.2, color='#FFB915', 
                     zorder=5)
ax_main.fill_between(xtimes, dSEMh, dSEMl, alpha=0.2, color='#0292eb', 
                     zorder=4)

ax_main.set_ylabel('Position Evidence (1e-4)', fontweight='bold', fontsize=20)
ax_main.hlines(0, -100, 300, color="black")
ax_main.set_ylim(ymin=-5, ymax=20)
from matplotlib.ticker import MultipleLocator, FuncFormatter

ax_main.yaxis.set_major_locator(MultipleLocator(5))

ax_main.yaxis.set_major_formatter(
    FuncFormatter(lambda y, _: f'{y:.0f}')
)
ax_main.spines['right'].set_visible(False)
ax_main.spines['top'].set_visible(False)
ax_main.axvspan(-100, 0, color='grey', alpha=0.2, zorder=1)


legend_handles = [
    mlines.Line2D([], [], color='#FFB915', linestyle='-', linewidth=2, 
                  label='Occlusion'),
    mlines.Line2D([], [], color='#0292eb', linestyle='-', linewidth=2, 
                  label='Appearance'),
]

ax_main.legend(handles=legend_handles, loc='upper right', 
               bbox_to_anchor=(1, 1), fontsize=12, frameon=True)


for i in range(len(bf_diff)):
    ax_diff.plot(x[i], logBFdiff[i], color=bf_colorsDiff[i], marker='o', 
                 markersize=4, markeredgecolor='black', markeredgewidth=0.1, 
                 lw=0)

ax_diff.set_ylim([-5, 5]) 
ax_diff.set_yticks([-5, 0, 5], [r'10$^{-5}$', '0', r'10$^5$'], fontsize=16)
ax_diff.set_xlim(xmin=-100, xmax=300)
ax_diff.spines['right'].set_visible(False)
ax_diff.spines['top'].set_visible(False)
ax_diff.hlines(0, -100, 300, color="black", linewidth=0.5)
ax_diff.set_xlabel('Time (ms)', fontweight='bold', fontsize=20)
ax_diff.axvspan(-100, 0, color='grey', alpha=0.2, zorder=1)



