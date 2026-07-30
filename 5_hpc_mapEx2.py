#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  7 15:57:30 2023

Cross-decoding of localiser->motion/visibility events for occlusion 
experiment 2

@authororig: willturner williamfrancisturner@gmail.com
: JasminPatel 15.04.25 re-written

file locations removed 30.07.26
"""

import os 
import mne
from efuncsEx2 import epoch_motion
from dfuncs import load_data, save_data, LDA_map

#specify where data found, get list of files
dataFolder = '_'
mne.set_log_level(verbose=False) # simplify HPC output
files = [f for f in os.listdir(dataFolder) if not 
         os.path.isdir(dataFolder + f)]
files.sort() 
print(files,flush=True)
        
def run_decoding(x, file):
    
    #get raw data for LDA
    pID = file[:-8] # get ID and session number
    raw = load_data(file, dataFolder)

    #get train/test data for LDA
    xTrain, yTrain, xTest, yTest = epoch_motion(raw, pID)
    #run LDA
    xmin = 38
    xmax = 77
    scores = LDA_map(xTrain, yTrain, xTest, yTest, xmin, xmax)
    #save
    save_data('_' + pID + '_LDA.pickle', scores)
    

for x, file in enumerate(files):
    run_decoding(x, file)
