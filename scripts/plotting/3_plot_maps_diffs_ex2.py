# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 14:06:35 2026

Plotting code for cross-decoding maps + difference plots Experiment 2

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
from plot_funcs import load_data, occlu_by_size, cluster_correct
import matplotlib 
import gc
import pickle
import pandas as pd

from rpy2.robjects import r, pandas2ri, numpy2ri, default_converter
import rpy2.robjects as ro
from rpy2.robjects.packages import importr
import rpy2.robjects.packages as rpackages
from rpy2.robjects.conversion import localconverter


time = 3
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

# ##plot appearance & disappearance maps
fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(13, 7))
inds = [0, 2]

for i, ax in enumerate(axes.ravel()):
    plotData = np.mean(
        np.stack([
            np.mean(scores[inds[i], :, :, :], axis=0),
            np.flip(np.mean(scores[inds[i] + 1, :, :, :], axis=0), axis=1),
            np.mean(scores[inds[i] + 6, :, :, :], axis=0),
            np.flip(np.mean(scores[inds[i] + 7, :, :, :], axis=0), axis=1),
            np.mean(scores[inds[i] + 12, :, :, :], axis=0),
            np.flip(np.mean(scores[inds[i] + 13, :, :, :], axis=0), axis=1)
        ]), axis=0)
    
    plotData = gaussian_filter(plotData, sigma)
    
    im = ax.matshow(plotData, extent=[0, 40, -1000, 1000],
                        vmin=0.025 - scaler, vmax=0.025 + scaler, 
                        cmap='PuOr_r', origin='lower', aspect = 'auto')  
    
    ax.axhline(0, color='k', linestyle='--', lw=3)
    
    if i in [0]:
        ax.plot([20, 40], [0, 500], color = 'k', lw=2)
        ax.plot([0, 20], [500, 1000], color = 'k', lw=2)
        ax.set_ylabel('Time (ms)', fontweight='bold')
        ax.set_xlabel('\nPosition', fontweight='bold')
        ax.set_title('Appearance\n', fontweight='bold')
        ax.set_yticks([-250, 0, 1000])

    else:
        ax.plot([20, 40], [-1000, -500], color = 'k', lw=2)
        ax.plot([0, 20], [-500, 0], color = 'k', lw=2)
        ax.plot([20, 40], [0, 500], color = 'k', lw=2, linestyle=':')
        ax.set_title('Disappearance\n', fontweight='bold')
        ax.set_yticks([])
        dis = plotData

        
    ax.xaxis.set_ticks_position('bottom')
    
    ax.set_xticks([0, 20, 40], [r'$-\pi$', '0', r'$\pi$'])
    ax.set_ylim((-100, 1000))
    
cb_ax = fig.add_axes([0.93, 0.12, 0.03, 0.76])
cbar = fig.colorbar(im, cax=cb_ax)
chance=1/40 
cbar.set_ticks([chance - scaler, chance, chance + scaler])
cbar.set_ticklabels(['-' + str(round(scaler*10000)), '', 
                     str(round(scaler*10000))])
cbar.ax.set_ylabel('Position Evidence (1e-4)', rotation=270,
                    fontweight='bold')


##plot occlusion maps all together

fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(24, 9))
inds = [10, 4, 16]

for i, ax in enumerate(axes.ravel()):
    
    
    plotData = np.mean(np.stack((np.mean(scores[inds[i], :, :, :], axis = 0), 
                        np.flip(np.mean(scores[inds[i] + 1, :, :, :], 
                                        axis = 0), axis = 1)), axis = 2), 
                       axis = 2)
    
    plotData = gaussian_filter(plotData, sigma)
    
    ax.matshow(plotData, extent=[0, 40, -1000, 1000],
                       vmin=0.025 - scaler, vmax=0.025 + scaler, cmap='PuOr_r', 
                       origin='lower', aspect = 'auto') 
     
    
    ax.axhline(0, color='k', linestyle='--', lw=3)
    
    if i in [0, 1, 2]:
        if i in [0]:
            ax.set_yticks([-100, 0, 1000])
            ax.set_ylabel('Time (ms)', fontweight='bold')
            ax.set_xlabel('\nPosition', fontweight='bold')
        else:
            ax.set_yticks([])
        
        if i in [0]:
            ax.set_title('Occlusion (S)\n', fontweight='bold') 

        if i in [1]:
            ax.set_title('Occlusion (M)\n', fontweight='bold')

        if i in [2]:
            ax.set_title('Occlusion (L)\n', fontweight='bold')

        
        
    if i in [0]:
        ax.plot([20, 32], [0, 300], color = 'k', lw=2, linestyle='--')
        ax.plot([32, 40], [300, 500], color = 'k', lw=2)
        ax.plot([0, 20], [500, 1000], color = 'k', lw=2)
        ax.plot([0, 20], [-500, 0], color = 'k', lw=2)
        ax.axhline(300, color='k', linestyle='--', lw=3)
        
    if i in [1]:
        ax.plot([20, 40], [0, 500], color = 'k', lw=2, linestyle='--')
        ax.plot([0, 20], [500, 1000], color = 'k', lw=2)
        ax.plot([0, 20], [-500, 0], color = 'k', lw=2)
        ax.axhline(500, color='k', linestyle='--', lw=3)
        
    if i in [2]:
        ax.plot([20, 40], [0, 500], color = 'k', lw=2, linestyle='--')
        ax.plot([0, 8], [500, 700], color = 'k', lw=2, linestyle='--')
        ax.plot([8, 20], [700, 1000], color = 'k', lw=2)
        ax.plot([0, 20], [-500, 0], color = 'k', lw=2)       
        ax.axhline(700, color='k', linestyle='--', lw=3)
        
    ax.xaxis.set_ticks_position('bottom')
    ax.set_xticks([0, 20, 40], [r'$-\pi$', '0', r'$\pi$'])
    ax.set_ylim((-100, 1000))
    
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
allData = allData.reshape(10, 4, 18, times, 1024, 40)
allData = allData.mean(axis=1)


inds = 2

offset = []

for p in range(allData.shape[0]):
    data = allData[p]
    data = np.mean(np.stack([
        np.mean(data[inds, :, :, :], axis=0),
        np.flip(np.mean(data[inds + 1, :, :, :], axis=0), axis=1),
        np.mean(data[inds + 6, :, :, :], axis=0),
        np.flip(np.mean(data[inds + 7, :, :, :], axis=0), axis=1),
        np.mean(data[inds + 12, :, :, :], axis=0),
        np.flip(np.mean(data[inds + 13, :, :, :], axis=0), axis=1)
    ], axis=0), axis=0)

    offset.append(data)
    
offset = np.stack(offset, axis=0)
    
occluS = occlu_by_size(allData, 10)
occluM = occlu_by_size(allData, 4)
occluL = occlu_by_size(allData, 16)
del allData
gc.collect()





dis = np.mean(offset, axis=0)
occlusionS = np.mean(occluS, axis=0)
occlusionM = np.mean(occluM, axis=0)
occlusionL = np.mean(occluL, axis=0)






def shiftMap(data):
    
    time, pos = data.shape
    realigned = np.empty_like(data)
    shifts = np.linspace(4, 0, time)
    for t in range(time):
        realigned[t] = np.roll(data[t], int(round(shifts[t])))
        
    return realigned


Slice = np.mean([dis[461:512], occlusionS[461:512], occlusionM[461:512], 
                 occlusionL[461:512]], axis=0)
rSlice = shiftMap(Slice)





# fig, ax = plt.subplots(nrows=1,ncols=1, figsize=(12, 6))

chance=1/40 #change for diff
# im = ax.matshow(rSlice, extent=[0, 40, -100, 0],
                    # vmin=chance - scaler, vmax=chance + scaler, 
                    # cmap='PuOr_r', origin='lower', aspect = 'auto')  
# ax.set_title(f'd & o av realign T{time}\n', fontweight='bold')
# ax.set_ylabel('Time (ms)', fontweight='bold')
# ax.set_xlabel('\n  Relative position', fontweight='bold')        
# ax.xaxis.set_ticks_position('bottom')
# ax.set_ylim((-100, 0))
# ax.axvline(20, color='k', lw=3)
# ax.set_xticks([0, 20, 40], [r'$-\pi$', '0', r'$\pi$'])





tSlice = np.mean(rSlice, axis=0)
vals = tSlice - chance

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





###############################################################################

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from matplotlib.ticker import FuncFormatter

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
    0.0004,
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















n_time = 1024
n_pos = 40

mask = np.zeros((n_time, n_pos), dtype=bool)

shifts = np.linspace(0, -80, n_time)

for t in range(n_time):

    shift = int(round(shifts[t]))

    roi_realigned = np.arange(left, right)

    roi_original = (roi_realigned - shift) % n_pos

    mask[t, roi_original] = True
    


empty = np.ones_like(plotData)
empty -= 5
maskedEmpty = np.ma.masked_where(~mask, empty)
maskedEmpty -= 10

fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(24, 9))
inds = [10, 4, 16]

for i, ax in enumerate(axes.ravel()):
    
    plotData = np.zeros([1024, 40])
    
    ax.matshow(empty, extent=[0, 40, -1000, 1000],
                        vmin=chance-10, vmax=chance+10, cmap='Greys', 
                        origin='lower', aspect = 'auto') 
    ax.matshow(maskedEmpty, extent=[0, 40, -1000, 1000],
                       vmin=chance-10, vmax=chance+10, cmap='Greys', 
                       origin='lower', aspect = 'auto') 
     
    if i in [0]:
        ax.axhline(0, color='k', linestyle='--', lw=3)
        ax.set_yticks([-100, 0, 1000], [])
        ax.plot([0, 20], [-500, 0], color = 'k', lw=2)
    else:
        ax.set_yticks([])
        ax.set_xticks([])
    
    
    ax.xaxis.set_ticks_position('bottom')
    ax.set_xticks([0, 20, 40], [])
    ax.set_ylim((-100, 1000))
    
cb_ax = fig.add_axes([0.93, 0.12, 0.02, 0.76])
cbar = fig.colorbar(im, cax=cb_ax)
chance=0
cbar.set_ticks([chance - scaler, chance, chance + scaler])
cbar.set_ticklabels(['-' + str(round(scaler*10000)), '', 
                     str(round(scaler*10000))])
cbar.ax.set_ylabel('Position Evidence (1e-4)', rotation=270, labelpad=25, 
                    fontweight='bold')


###############################################################################






chance = 1/40

fig, axes = plt.subplots(nrows=1, ncols=4, figsize=(26, 6))
inds = [2, 10, 4, 16]

for i, ax in enumerate(axes.ravel()):
    
    if i in [0]:
        plotData = dis
    else:
        plotData = np.mean(np.stack((np.mean(scores[inds[i], :, :, :], 
                                             axis = 0), 
                            np.flip(np.mean(scores[inds[i] + 1, :, :, :], 
                                            axis = 0), axis = 1)), 
                            axis = 2), axis = 2)
    
    plotData = gaussian_filter(plotData, sigma)
    
    ax.matshow(plotData, extent=[0, 40, -1000, 1000],
                       vmin=0.025 - scaler, vmax=0.025 + scaler, cmap='Greys', 
                       origin='lower', aspect = 'auto') 
    
    masked_data = np.ma.masked_where(~mask, plotData)
    ax.matshow(masked_data, extent=[0, 40,-1000, 1000],
                          vmin=chance - scaler, vmax=chance + scaler, 
                          cmap='PuOr_r', origin='lower', aspect = 'auto')
     
    
    ax.axhline(0, color='k', linestyle='--', lw=3)

    if i in [0]:
        ax.plot([20, 40], [-1000, -500], color = 'k', lw=2)
        ax.plot([0, 20], [-500, 0], color = 'k', lw=2)
        ax.plot([20, 40], [0, 500], color = 'k', lw=2, linestyle=':')
        ax.set_title('Disappearance\n', fontweight='bold')
        ax.set_yticks([-100, 0, 1000])
        ax.set_ylabel('Time (ms)', fontweight='bold')
        ax.set_xlabel('\nPosition', fontweight='bold')
        
    if i in [1]:
        ax.plot([20, 32], [0, 300], color = 'k', lw=2, linestyle='--')
        ax.plot([32, 40], [300, 500], color = 'k', lw=2)
        ax.plot([0, 20], [500, 1000], color = 'k', lw=2)
        ax.plot([0, 20], [-500, 0], color = 'k', lw=2)
        ax.axhline(300, color='k', linestyle='--', lw=3)
        ax.set_title('Occlusion (S)\n', fontweight='bold') 
        ax.set_yticks([])
        
    if i in [2]:
        ax.plot([20, 40], [0, 500], color = 'k', lw=2, linestyle='--')
        ax.plot([0, 20], [500, 1000], color = 'k', lw=2)
        ax.plot([0, 20], [-500, 0], color = 'k', lw=2)
        ax.axhline(500, color='k', linestyle='--', lw=3)
        ax.set_title('Occlusion (M)\n', fontweight='bold')
        ax.set_yticks([])
        
    if i in [3]:
        ax.plot([20, 40], [0, 500], color = 'k', lw=2, linestyle='--')
        ax.plot([0, 8], [500, 700], color = 'k', lw=2, linestyle='--')
        ax.plot([8, 20], [700, 1000], color = 'k', lw=2)
        ax.plot([0, 20], [-500, 0], color = 'k', lw=2)       
        ax.axhline(700, color='k', linestyle='--', lw=3)
        ax.set_title('Occlusion (L)\n', fontweight='bold')
        ax.set_yticks([])
        
    ax.xaxis.set_ticks_position('bottom')
    ax.set_xticks([0, 20, 40], [r'$-\pi$', '0', r'$\pi$'])
    ax.set_ylim((-100, 1000))




###############################################################################


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
            
    
    data = realigned - chance
    data = data[:, :, left:right]
    data = np.mean(data, axis=2)
    
    plot = np.mean(data, axis=0)
    plot = plot * 10000
    sem = np.std(data, axis=0) / np.sqrt(data.shape[0])
    sem = sem * 10000
        
    return data, plot, sem

sData, sPlot, sSEM = shiftData(occluS, left, right)
mData, mPlot, mSEM = shiftData(occluM, left, right)
lData, lPlot, lSEM = shiftData(occluL, left, right)
dData, dPlot, dSEM = shiftData(offset, left, right)

mDiff = mData - dData
sDiff = sData - dData
lDiff = lData - dData

pvalsM = cluster_correct(mDiff)
sig_markerM = pvalsM < 0.05
pvalsS = cluster_correct(sDiff)
sig_markerS = pvalsS < 0.05
pvalsL = cluster_correct(lDiff)
sig_markerL = pvalsL < 0.05


def save_data(file, scores):
    with open(file, 'wb') as f:
        pickle.dump(scores, f)

from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

cmapm = LinearSegmentedColormap.from_list(
    'grey_yellow',
    [
        '#666666',   # strong H0
        '#FFFFFF',   # inconclusive
        '#FFB915'    # strong H1
    ]
)


cmaps = LinearSegmentedColormap.from_list(
    'grey_yellow',
    [
        '#666666',   # strong H0
        '#FFFFFF',   # inconclusive
        '#FFE015'    # strong H1
    ]
)

cmapl = LinearSegmentedColormap.from_list(
    'grey_yellow',
    [
        '#666666',   # strong H0
        '#FFFFFF',   # inconclusive
        '#FF8215'    # strong H1
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

cmapsd = LinearSegmentedColormap.from_list(
    'grey_greenS',
    [
        '#666666',   # strong H0
        '#FFFFFF',   # inconclusive
        '#94e010'    # strong H1
    ]
)

cmapmd = LinearSegmentedColormap.from_list(
    'grey_greenM',
    [
        '#666666',   # strong H0
        '#FFFFFF',   # inconclusive
        '#00AA00'    # strong H1
    ]
)

cmapld = LinearSegmentedColormap.from_list(
    'grey_greenL',
    [
        '#666666',   # strong H0
        '#FFFFFF',   # inconclusive
        '#07611d'    # strong H1
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




bf_m, logBFm, bf_colorsM = bayes_factors(mData, cmapm)
bf_s, logBFs, bf_colorsS = bayes_factors(sData, cmaps)
bf_l, logBFl, bf_colorsL = bayes_factors(lData, cmapl)
bf_d, logBFd, bf_colorsD = bayes_factors(dData, cmapd)     


#diff 
mDiff = mData - dData
sDiff = sData - dData
lDiff = lData - dData

bf_md, logBFmd, bf_colorsMd = bayes_factors(mDiff, cmapmd)
bf_sd, logBFsd, bf_colorsSd = bayes_factors(sDiff, cmapsd)
bf_ld, logBFld, bf_colorsLd = bayes_factors(lDiff, cmapld)







###############################################################################
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
# ax_s    = ax[1]
# ax_m    = ax[2]
# ax_l    = ax[3]
# ax_d    = ax[4]
ax_sd    = ax[1]
ax_md    = ax[2]
ax_ld    = ax[3]

xtimes = np.linspace(-1000,1000,1024)
x = xtimes
mask = (xtimes >= -100) & (xtimes <= 1000)

ax_main.plot(xtimes, gaussian_filter(dPlot, sigma), color='#003F66', zorder=10)
ax_main.plot(xtimes, gaussian_filter(lPlot, sigma), color='#FF8215', zorder=11)
ax_main.plot(xtimes, gaussian_filter(mPlot, sigma), color='#FFB915', zorder=12)
ax_main.plot(xtimes, gaussian_filter(sPlot, sigma), color='#FFE015', zorder=13)


ax_main.fill_between(xtimes, gaussian_filter(dPlot + dSEM, sigma), 
                     gaussian_filter(dPlot - dSEM, sigma), alpha=0.1, 
                     color='#003F66', zorder=10)
ax_main.fill_between(xtimes, gaussian_filter(lPlot + lSEM, sigma), 
                     gaussian_filter(lPlot - lSEM, sigma), alpha=0.1, 
                     color='#FF8215', zorder=11)
ax_main.fill_between(xtimes, gaussian_filter(mPlot + mSEM, sigma), 
                     gaussian_filter(mPlot - mSEM, sigma), alpha=0.1, 
                     color='#FFB915', zorder=12)
ax_main.fill_between(xtimes, gaussian_filter(sPlot + sSEM, sigma), 
                     gaussian_filter(sPlot - sSEM, sigma), alpha=0.1, 
                     color='#FFE015', zorder=13)


ax_main.set_ylabel('Position Evidence (1e-4)', fontweight='bold', fontsize=20)
ax_main.hlines(0, -100, 1000, color="black")
# ax_main.set_ylim(ymin=-2, ymax=10)
ax_main.set_xlim(xmin=-100, xmax=1000)
ax_main.spines['right'].set_visible(False)
ax_main.spines['top'].set_visible(False)
ax_main.axvspan(-100, 0, color='grey', alpha=0.3, zorder=3)
ax_main.axvspan(700, 1000, color='grey', alpha=0.3, zorder=3)
ax_main.axvspan(500, 700, color='grey', alpha=0.2, zorder=2)
ax_main.axvspan(300, 500, color='grey', alpha=0.1, zorder=1)
ax_main.set_ylim(ymin=-4, ymax=13)
from matplotlib.ticker import MultipleLocator, FuncFormatter

ax_main.yaxis.set_major_locator(MultipleLocator(5))

ax_main.yaxis.set_major_formatter(
    FuncFormatter(lambda y, _: f'{y:.0f}')
)

ax_main.scatter(xtimes[mask], np.full(np.sum(mask), -3), s=4, c="#FFE015", 
                alpha=sig_markerS[mask], linewidths=0)
ax_main.scatter(xtimes[mask], np.full(np.sum(mask), -4), s=4, c="#FFB915", 
                alpha=sig_markerM[mask], linewidths=0)
ax_main.scatter(xtimes[mask], np.full(np.sum(mask), -5), s=4, c="#FF8215", 
                alpha=sig_markerL[mask], linewidths=0)

legend_handles = [
    mlines.Line2D([], [], color='#FFE015', linestyle='-', linewidth=2, 
                  label='Occlusion (S)'),
    mlines.Line2D([], [], color='#FFB915', linestyle='-', linewidth=2, 
                  label='Occlusion (M)'),
    mlines.Line2D([], [], color='#FF8215', linestyle='-', linewidth=2, 
                  label='Occlusion (L)'),
    mlines.Line2D([], [], color='#003F66', linestyle='-', linewidth=2, 
                  label='Disappearance'),
]

ax_main.legend(handles=legend_handles, loc='upper right', 
               bbox_to_anchor=(1, 1), fontsize=12, frameon=True)


for i in range(len(bf_sd)):
    ax_sd.plot(x[i], logBFsd[i], color=bf_colorsSd[i], marker='o', 
               markersize=3, markeredgecolor='black', markeredgewidth=0.1, 
               lw=0)

ax_sd.set_ylim([-5, 5]) 
ax_sd.set_yticks([-5, 0, 5], [], fontsize=8)
ax_sd.set_xlim(xmin=-100, xmax=1000)
ax_sd.spines['right'].set_visible(False)
ax_sd.spines['top'].set_visible(False)
ax_sd.hlines(0, -100, 1000, color="black", linewidth=0.5)
ax_sd.axvspan(-100, 0, color='grey', alpha=0.3, zorder=3)
ax_sd.axvspan(300, 1000, color='grey', alpha=0.3, zorder=3)

for i in range(len(bf_md)):
    ax_md.plot(x[i], logBFmd[i], color=bf_colorsMd[i], marker='o', 
               markersize=3, markeredgecolor='black', markeredgewidth=0.1, 
               lw=0)

ax_md.set_ylim([-5, 5]) 
ax_md.set_yticks([-5, 0, 5], [], fontsize=8)
ax_md.set_xlim(xmin=-100, xmax=1000)
ax_md.spines['right'].set_visible(False)
ax_md.spines['top'].set_visible(False)
ax_md.hlines(0, -100, 1000, color="black", linewidth=0.5)
ax_md.axvspan(-100, 0, color='grey', alpha=0.3, zorder=3)
ax_md.axvspan(500, 1000, color='grey', alpha=0.3, zorder=3)

for i in range(len(bf_ld)):
    ax_ld.plot(x[i], logBFld[i], color=bf_colorsLd[i], marker='o', 
               markersize=3, markeredgecolor='black', markeredgewidth=0.1, 
               lw=0)

ax_ld.set_ylim([-5, 5]) 
ax_ld.set_yticks([-5, 0, 5], [], fontsize=8)
ax_ld.set_xlim(xmin=-100, xmax=1000)
ax_ld.spines['right'].set_visible(False)
ax_ld.spines['top'].set_visible(False)
ax_ld.hlines(0, -100, 1000, color="black", linewidth=0.5)
ax_ld.axvspan(-100, 0, color='grey', alpha=0.3, zorder=3)
ax_ld.axvspan(700, 1000, color='grey', alpha=0.3, zorder=3)
ax_ld.set_xlabel('Time (ms)', fontweight='bold', fontsize=20)











#############################################appear############################




allData = np.array(allScores)
allData = allData.reshape(10, 4, 18, times, 1024, 40)
allData = allData.mean(axis=1)

inds = 0

onset = []

for p in range(allData.shape[0]):
    data = allData[p]
    data = np.mean(np.stack([
        np.mean(data[inds, :, :, :], axis=0),
        np.flip(np.mean(data[inds + 1, :, :, :], axis=0), axis=1),
        np.mean(data[inds + 6, :, :, :], axis=0),
        np.flip(np.mean(data[inds + 7, :, :, :], axis=0), axis=1),
        np.mean(data[inds + 12, :, :, :], axis=0),
        np.flip(np.mean(data[inds + 13, :, :, :], axis=0), axis=1)
    ], axis=0), axis=0)

    onset.append(data)
    
onset = np.stack(onset, axis=0)

    
occluS = occlu_by_size(allData, 10)
occluM = occlu_by_size(allData, 4)
occluL = occlu_by_size(allData, 16)
del allData
gc.collect()









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
            
    
    data = realigned - chance
    data = data[:, :, left:right]
    data = np.mean(data, axis=2)
    
    plot = np.mean(data, axis=0)
    plot = plot * 10000
    sem = np.std(data, axis=0) / np.sqrt(data.shape[0])
    sem = sem * 10000
        
    return data, plot, sem

sData, sPlot, sSEM = shiftData(occluS, left, right)
mData, mPlot, mSEM = shiftData(occluM, left, right)
lData, lPlot, lSEM = shiftData(occluL, left, right)
aData, aPlot, aSEM = shiftData(onset, left, right)



asData, asPlot, asSEM = aData[:, 461:666], aPlot[461:666], aSEM[461:666]
saData, saPlot, saSEM = sData[:, 614:819], sPlot[614:819], sSEM[614:819]
maData, maPlot, maSEM = mData[:, 717:922], mPlot[717:922], mSEM[717:922]
laData, laPlot, laSEM = lData[:, 819:1024], lPlot[819:1024], lSEM[819:1024]

maDiff = maData - asData
saDiff = saData - asData
laDiff = laData - asData




from rpy2.robjects import r, pandas2ri, numpy2ri, default_converter
import rpy2.robjects as ro
from rpy2.robjects.packages import importr
import rpy2.robjects.packages as rpackages
from rpy2.robjects import numpy2ri
from rpy2.robjects.conversion import localconverter
import seaborn as sns
import pandas as pd
def save_data(file, scores):
    with open(file, 'wb') as f:
        pickle.dump(scores, f)

from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

cmapsd = LinearSegmentedColormap.from_list(
    'grey_greenS',
    [
        '#666666',   # strong H0
        '#FFFFFF',   # inconclusive
        '#94e010'    # strong H1
    ]
)

cmapmd = LinearSegmentedColormap.from_list(
    'grey_greenM',
    [
        '#666666',   # strong H0
        '#FFFFFF',   # inconclusive
        '#00AA00'    # strong H1
    ]
)

cmapld = LinearSegmentedColormap.from_list(
    'grey_greenL',
    [
        '#666666',   # strong H0
        '#FFFFFF',   # inconclusive
        '#07611d'    # strong H1
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



bf_mad, logBFmad, bf_colorsMad = bayes_factors(maDiff, cmapmd)
bf_sad, logBFsad, bf_colorsSad = bayes_factors(saDiff, cmapsd)
bf_lad, logBFlad, bf_colorsLad = bayes_factors(laDiff, cmapld)











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
    figsize=(12, 9),
    sharex=True,
    gridspec_kw={"height_ratios": [6, 1, 1, 1]}
)

ax_main = ax[0]
ax_sd    = ax[1]
ax_md    = ax[2]
ax_ld    = ax[3]

xtimes = np.linspace(-100,300,205)
x = xtimes

ax_main.plot(xtimes, gaussian_filter(asPlot, sigma), color='#0292eb', 
             zorder=10)
ax_main.plot(xtimes, gaussian_filter(laPlot, sigma), color='#FF8215', 
             zorder=11)
ax_main.plot(xtimes, gaussian_filter(maPlot, sigma), color='#FFB915', 
             zorder=12)
ax_main.plot(xtimes, gaussian_filter(saPlot, sigma), color='#FFE015', 
             zorder=13)


ax_main.fill_between(xtimes, gaussian_filter(asPlot + asSEM, sigma), 
                     gaussian_filter(asPlot - asSEM, sigma), alpha=0.1, 
                     color='#0292eb', zorder=10)
ax_main.fill_between(xtimes, gaussian_filter(laPlot + laSEM, sigma), 
                     gaussian_filter(laPlot - laSEM, sigma), alpha=0.1, 
                     color='#FF8215', zorder=11)
ax_main.fill_between(xtimes, gaussian_filter(maPlot + maSEM, sigma), 
                     gaussian_filter(maPlot - maSEM, sigma), alpha=0.1, 
                     color='#FFB915', zorder=12)
ax_main.fill_between(xtimes, gaussian_filter(saPlot + saSEM, sigma), 
                     gaussian_filter(saPlot - saSEM, sigma), alpha=0.1, 
                     color='#FFE015', zorder=13)


ax_main.set_ylabel('Position Evidence (1e-4)', fontweight='bold', fontsize=20)
ax_main.hlines(0, -100, 300, color="black")
# ax_main.set_ylim(ymin=-2, ymax=10)
ax_main.set_xlim(xmin=-100, xmax=300)
ax_main.spines['right'].set_visible(False)
ax_main.spines['top'].set_visible(False)
ax_main.set_ylim(ymin=-5, ymax=20)
ax_main.axvspan(-100, 0, color='grey', alpha=0.2, zorder=1)

from matplotlib.ticker import MultipleLocator, FuncFormatter

ax_main.yaxis.set_major_locator(MultipleLocator(5))

ax_main.yaxis.set_major_formatter(
    FuncFormatter(lambda y, _: f'{y:.0f}')
)


legend_handles = [
    mlines.Line2D([], [], color='#FFE015', linestyle='-', linewidth=2, 
                  label='Occlusion (S)'),
    mlines.Line2D([], [], color='#FFB915', linestyle='-', linewidth=2, 
                  label='Occlusion (M)'),
    mlines.Line2D([], [], color='#FF8215', linestyle='-', linewidth=2, 
                  label='Occlusion (L)'),
    mlines.Line2D([], [], color='#0292eb', linestyle='-', linewidth=2, 
                  label='Appearance'),
]

ax_main.legend(handles=legend_handles, loc='upper right', 
               bbox_to_anchor=(1, 1), fontsize=12, frameon=True)



for i in range(len(bf_sad)):
    ax_sd.plot(x[i], logBFsad[i], color=bf_colorsSad[i], marker='o', 
               markersize=4, markeredgecolor='black', markeredgewidth=0.1, 
               lw=0)

ax_sd.set_ylim([-5, 5]) 
ax_sd.set_yticks([-5, 0, 5], [r'10$^{-5}$', '0', r'10$^5$'], fontsize=16)
ax_sd.set_xlim(xmin=-100, xmax=300)
ax_sd.spines['right'].set_visible(False)
ax_sd.spines['top'].set_visible(False)
ax_sd.hlines(0, -100, 300, color="black", linewidth=0.5)
ax_sd.axvspan(-100, 0, color='grey', alpha=0.2, zorder=1)

for i in range(len(bf_mad)):
    ax_md.plot(x[i], logBFmad[i], color=bf_colorsMad[i], marker='o', 
               markersize=4, markeredgecolor='black', markeredgewidth=0.1, 
               lw=0)

ax_md.set_ylim([-5, 5]) 
ax_md.set_yticks([-5, 0, 5], [r'10$^{-5}$', '0', r'10$^5$'], fontsize=16)
ax_md.set_xlim(xmin=-100, xmax=300)
ax_md.spines['right'].set_visible(False)
ax_md.spines['top'].set_visible(False)
ax_md.hlines(0, -100, 300, color="black", linewidth=0.5)
ax_md.axvspan(-100, 0, color='grey', alpha=0.2, zorder=1)


for i in range(len(bf_lad)):
    ax_ld.plot(x[i], logBFlad[i], color=bf_colorsLad[i], marker='o', 
               markersize=4, markeredgecolor='black', markeredgewidth=0.1, 
               lw=0)

ax_ld.set_ylim([-5, 5]) 
ax_ld.set_yticks([-5, 0, 5], [r'10$^{-5}$', '0', r'10$^5$'], fontsize=16)
ax_ld.set_xlim(xmin=-100, xmax=300)
ax_ld.spines['right'].set_visible(False)
ax_ld.spines['top'].set_visible(False)
ax_ld.hlines(0, -100, 300, color="black", linewidth=0.5)
ax_ld.set_xlabel('Time (ms)', fontweight='bold', fontsize=20)
ax_ld.axvspan(-100, 0, color='grey', alpha=0.2, zorder=1)
