# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 10:24:59 2024

Plotting code for localiser within-decoding plots

@author: JasminPatel, based on code from 
William Turner bootstrapbill.github.io, williamfrancisturner@gmail.com
& Tim Cottier https://github.com/TCottier96

file locations removed 30.07.26
"""

import mne
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib.patches import ConnectionPatch
import numpy as np
import os
from plot_funcs import read_data, load_data, cluster_correct


from rpy2.robjects import r, pandas2ri
import rpy2.robjects as ro
from rpy2.robjects.packages import importr
import rpy2.robjects.packages as rpackages
from rpy2.robjects.conversion import localconverter
import pandas as pd



font = {'family' : 'DejaVu Sans',
        'weight' : 'normal',
        'size'   : 28}
plt.rc('font', **font)



########################################################################

##plot TGM##########################################

dataFolder = r'_'
tgm = load_data(dataFolder)
meanTgm = np.mean(tgm, axis = 0)
tgm = np.array(tgm)
tgm = tgm.reshape(10, 4, 615, 615)
tgm = tgm.mean(axis=1)

scaler = 0.005
chance = 1/40
meanTgm = meanTgm - chance
fig, ax = plt.subplots(figsize=(15, 12))
im = plt.imshow(meanTgm, extent=[-200, 1000, -200, 1000], vmin=-scaler, vmax=scaler, cmap='seismic', origin='lower', aspect='auto', alpha = 1) #gray_r
plt.xlabel('Testing Time (ms)', fontweight='bold', fontsize=36) 
plt.ylabel('Training Time (ms)', fontweight='bold', fontsize=36) 
ax.set_ylim((-200, 800))
ax.set_xlim((-200, 800))

#colour bar
cbar = plt.colorbar()
cbar.set_ticks([- scaler, 0, scaler])
cbar.set_ticklabels([- scaler, '0', scaler])
cbar.ax.set_ylabel('Decoding Score', rotation=270,fontsize=36,
                    fontweight='bold')

plt.savefig('_', dpi = 150)


#######################################################################################



##plot diag from diag decoding w BFs#################################

dataFolder = r'_'
files = [f for f in os.listdir(dataFolder)]

fig, ax= plt.subplots(2,1,figsize=(19, 15))
xtimes = np.linspace(-200,1000,615)

chance = 1/40


#loop through files to plot all
allScores = []
temp = []
mean_scores = []

#=====ex1=====
# for i, file in enumerate(files):
    
#     scores = read_data(dataFolder, file)
#     temp.append(scores)
    
#     # every 2 files, average and plot
#     if (i + 1) % 2 == 0:
#         mean_scores = np.mean(temp, axis=0)
#         mean_scores = mean_scores-chance
#         ax[0].plot(xtimes, mean_scores, color='#E3E3E3', zorder=0)
#         allScores.append(mean_scores)
#         temp = [] 

#=====ex2=====
for i, file in enumerate(files):
#for file in files:
    
    scores = read_data(dataFolder, file)
    temp.append(scores)
    
    # every 4 files, average and plot
    if (i + 1) % 4 == 0:
        mean_scores = np.mean(temp, axis=0)
        mean_scores = mean_scores-chance
        ax[0].plot(xtimes, mean_scores, color='#E3E3E3', zorder=0)
        allScores.append(mean_scores)
        temp = []  # reset for next group
        
    
###################run up to here then run BFs#########
    
#calc & plot mean + sem
allScores = np.array(allScores)
meanScores = np.mean(allScores, axis=0)
semScores = np.std(allScores, axis=0) / np.sqrt(len(files))

#ax[0].set_position([0.1, 0.35, 0.85, 0.6]) 
ax[0].set_xlim(xmin=-200, xmax=800)

ax[0].set_ylim(ymin=-0.015, ymax=0.03)
ax[0].set_yticks(np.arange(-0.010, 0.031, 0.01))


ax[0].hlines(0, -200, 1000, color="black")
ax[0].plot(xtimes, meanScores, color='r', zorder=10)
ax[0].fill_between(xtimes, meanScores + semScores, 
                   meanScores - semScores, alpha=0.3, color='r', zorder=5)

ax[0].axvspan(0, 100, color='grey', alpha=0.2, zorder=1)
ax[0].set_ylabel('Decoding score', fontweight='bold', fontsize=36)
ax[0].spines['right'].set_visible(False)
ax[0].spines['top'].set_visible(False)

pvals = cluster_correct(allScores)
sig_marker = pvals < 0.05
ax[0].scatter(xtimes, np.repeat(-0.01, 615), s=4, c = "black", 
              alpha = sig_marker, linewidths=0)


for i in range(len(bf)):
    ax[1].plot(x[i], logBF[i], color=bf_colors[i], marker='o', markersize=4, 
               markeredgecolor='black', markeredgewidth=0.1, lw=0)

ax[1].set_ylim([-5, 5]) 
ax[1].set_yticks([-5, 0, 5], [r'10$^{-5}$', '0', r'10$^5$'])
ax[1].set_xlim(xmin=-200, xmax=800)
ax[1].set_ylabel('BF', fontweight='bold', fontsize=36)
ax[1].set_xlabel('Time (ms)', fontweight='bold', fontsize=36)
ax[1].spines['right'].set_visible(False)
ax[1].spines['top'].set_visible(False)
ax[1].hlines(0, -200, 1000, color="black", linewidth=0.5)


legend_handles = [
    mlines.Line2D([], [], color='r', marker='o', markeredgecolor='black', 
                  markeredgewidth=0.1, linestyle='None', label='BF > 10'),
    mlines.Line2D([], [], color='white', marker='o', markeredgecolor='black', 
                  markeredgewidth=0.1, linestyle='None', label='1/10 < BF < 10'),
    mlines.Line2D([], [], color='grey', marker='o', markeredgecolor='black', 
                  markeredgewidth=0.1, linestyle='None', label='1/10 < BF')
]

ax[1].legend(handles=legend_handles, loc='upper right', 
             bbox_to_anchor=(1, 1.7), fontsize=20, frameon=True)



#search 1
dataFolder = r'_'
files = [f for f in os.listdir(dataFolder)]

#get configuration of channels + srate (biosemi64 layout)
montage = mne.channels.make_standard_montage('biosemi64')
info = mne.create_info(montage.ch_names, 512, ch_types='eeg')
info.set_montage(montage)

#load data
allSearch1 = []
for file in files:
    search1 = read_data(dataFolder, file)
    allSearch1.append(search1)
    
ins = ax[0].inset_axes([0.45, 0.65, 0.21, 0.28])

con1 = ConnectionPatch(xyA=(75, 0), coordsA=ax[0].transData, xyB = (0.5,0), 
                      coordsB=ins.transAxes,  axesA=ax[0], axesB=ins, 
                      color='black', linestyle='-')
con2 = ConnectionPatch(xyA=(125, 0), coordsA=ax[0].transData, xyB = (0.5,0), 
                      coordsB=ins.transAxes,  axesA=ax[0], axesB=ins, 
                      color='black', linestyle='-')
ax[0].add_artist(con1)
ax[0].add_artist(con2)

searchMean1 = np.mean(allSearch1, axis = 0)
scaler = 0.005


mne.viz.plot_topomap(np.mean(searchMean1, 1)- chance, info, axes=ins, cmap='coolwarm', 
                     contours=0, vlim=(-scaler, scaler), res=1000, show=False)



#search 2
dataFolder = r'_'
files = [f for f in os.listdir(dataFolder)]

#get configuration of channels + srate (biosemi64 layout)
montage = mne.channels.make_standard_montage('biosemi64')
info = mne.create_info(montage.ch_names, 512, ch_types='eeg')
info.set_montage(montage)

#load data
allSearch2 = []
for file in files:
    search2 = read_data(dataFolder, file)
    search2 = search2[:, :38]
    allSearch2.append(search2)
    
ins2 = ax[0].inset_axes([0.62, 0.65, 0.21, 0.28])

con3 = ConnectionPatch(xyA=(125, 0), coordsA=ax[0].transData, xyB = (0.5,0), 
                      coordsB=ins2.transAxes,  axesA=ax[0], axesB=ins2, 
                      color='black', linestyle='-')
con4 = ConnectionPatch(xyA=(200, 0), coordsA=ax[0].transData, xyB = (0.5,0), 
                      coordsB=ins2.transAxes,  axesA=ax[0], axesB=ins2, 
                      color='black', linestyle='-')
ax[0].add_artist(con3)
ax[0].add_artist(con4)

searchMean2 = np.mean(allSearch2, axis = 0)
scaler = 0.005

mne.viz.plot_topomap(np.mean(searchMean2, 1)- chance, info, axes=ins2, 
                     cmap='coolwarm', contours=0, vlim=(-scaler, scaler), 
                     res=1000, show=False)



#search 3
dataFolder = r'_'
files = [f for f in os.listdir(dataFolder)]

#get configuration of channels + srate (biosemi64 layout)
montage = mne.channels.make_standard_montage('biosemi64')
info = mne.create_info(montage.ch_names, 512, ch_types='eeg')
info.set_montage(montage)

#load data
allSearch3 = []
for file in files:
    search3 = read_data(dataFolder, file)
    allSearch3.append(search3)
    
ins3 = ax[0].inset_axes([0.79, 0.65, 0.21, 0.28])

con5 = ConnectionPatch(xyA=(200, 0), coordsA=ax[0].transData, xyB = (0.5,0), 
                      coordsB=ins3.transAxes,  axesA=ax[0], axesB=ins3, 
                      color='black', linestyle='-')
con6 = ConnectionPatch(xyA=(250, 0), coordsA=ax[0].transData, xyB = (0.5,0), 
                      coordsB=ins3.transAxes,  axesA=ax[0], axesB=ins3, 
                      color='black', linestyle='-')
ax[0].add_artist(con5)
ax[0].add_artist(con6)

searchMean3 = np.mean(allSearch3, axis = 0)
scaler = 0.005

mne.viz.plot_topomap(np.mean(searchMean3, 1)- chance, info, axes=ins3, 
                     cmap='coolwarm', contours=0, vlim=(-scaler, scaler), 
                     res=1000, show=False)

fig.savefig('_', dpi = 150)




#BFs################################################################
#run before messing around with plotting, save on processing time

#https://github.com/LinaTeichmann1/BFF_repo/blob/master/codes/...
#BF_colour_python.ipynb

utils = rpackages.importr('utils')
utils.chooseCRANmirror(ind=1)

packnames = ('BayesFactor', 'ggplot2')
from rpy2.robjects.vectors import StrVector
names_to_install = [x for x in packnames if not rpackages.isinstalled(x)]
if len(names_to_install) > 0:
    utils.install_packages(StrVector(names_to_install))
    
allScores = np.array(allScores)

bf_package = importr('BayesFactor')

chance = 1/40

#loop over time, make decoding accuracy into effect size & convert to r object
timepoints = allScores.shape[1]
df_norm = pd.DataFrame((allScores))

#convert to R object
with localconverter(ro.default_converter + pandas2ri.converter):
    rData = ro.conversion.py2rpy(df_norm)
# Loop over timepoints
bf = []
for t in range(timepoints): # t loops through the columns
    results = bf_package.ttestBF(x=rData[t], mu=0, rscale='medium', 
                                 nullInterval=[0.5, float('inf')])
    bf.append(np.asarray(r['as.vector'](results))[0])


# Define threshold-based color mapping
logBF = np.log10(bf)
x = xtimes
bf_colors = []
for val in bf:
    if val > 10:
        bf_colors.append('r')         # Strong evidence for H1
    elif val < 0.1:
        bf_colors.append('grey')        # Strong evidence for H0
    else:
        bf_colors.append('white')       # Inconclusive

