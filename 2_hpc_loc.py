# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 16:38:47 2024

Within-decoding of localiser presentations for occlusion experiment. 

@authororig: willturner williamfrancisturner@gmail.com
: JasminPatel 19.06.24 re-written

file locations removed 30.07.26
"""

import os
import mne
from efuncs import epoch_localisers
from dfuncs import load_data, save_data, decode_tgm, decode_search

#specify where data found, get list of files
dataFolder = '_'
mne.set_log_level(verbose=False) # simplify HPC output
files = [f for f in os.listdir(dataFolder) if not 
         os.path.isdir(dataFolder + f)]
files.sort() 
print(files,flush=True)

#run pairwise LDA within-decoding
def run_tgm(xTrain, yTrain, pID):
        
    tgmScores, diagScores = decode_tgm(xTrain, yTrain)
        
    save_data('_' + pID + '_tgmLDA.pickle', tgmScores)
    save_data('_' + pID + '_diagLDA.pickle', diagScores)
    
def run_search(stimEpochs, pID):
    searchScores = decode_search(stimEpochs)
    save_data('_' + pID + '_searchLDA.pickle', searchScores)

#run decoding per file (all of above functions)
def decode(file):
    
    #get raw data for tgm
    pID = file[:-8] # get ID and session number
    raw = load_data(file, dataFolder)
    #get train/test data for tgm decoding
    xTrain, yTrain, stimEpochs = epoch_localisers(raw, pID)
    del raw # try to reduce memory overhead 
    
    #get tgm
    run_tgm(xTrain, yTrain, pID)
    print('tgm & diag complete' + pID, flush=True)
    del xTrain, yTrain
    
    #get search
    # run_search(stimEpochs, pID)
    # print('search complete ' + pID, flush=True)
    #run for each timewindow instead on sep file
    del stimEpochs
    

for x, file in enumerate(files):
    decode(file)
