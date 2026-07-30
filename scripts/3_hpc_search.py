# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 16:38:47 2024

Within-decoding of localiser presentation searchlight for occlusion experiment 

@authororig: willturner williamfrancisturner@gmail.com
: JasminPatel 21.04.25 re-written

file locations removed 30.07.26
"""

import os
import mne
from efuncs import epoch_localisers
from dfuncs import load_data, save_data, decode_search

#specify where data found, et list of files
dataFolder = '_'
mne.set_log_level(verbose=False) # simplify HPC output
files = [f for f in os.listdir(dataFolder) if not 
         os.path.isdir(dataFolder + f)]
files.sort() 
print(files,flush=True)
    
def run_search(stimEpochs, time, pID):
    
    times = [(141, 167), (167, 205), (205, 231)] 
    tmin, tmax = times[time]
    searchScores = decode_search(stimEpochs, tmin, tmax)
    save_data(f'_', searchScores)

#run decoding per file (all of above functions)
def decode(file):
    
    #get raw data for tgm
    pID = file[:-8] # get ID and session number
    raw = load_data(file, dataFolder)
    #get train/test data for tgm decoding
    stimEpochs = epoch_localisers(raw, pID)
    del raw

    for time in range(3):

        run_search(stimEpochs, time, pID)
        print(f'search complete {pID} T{time+1}', flush=True)
        
    del stimEpochs
    

for x, file in enumerate(files):
    decode(file)
