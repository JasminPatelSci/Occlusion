#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  7 14:43:43 2023

Preprocessing for occlusion experiment. 

@authororig: willturner williamfrancisturner@gmail.com
: JasminPatel 28.01.25 re-written

file locations removed 30.07.26
"""

import os
import mne
import numpy as np

# set up logging (to simplify HPC output)
mne.set_log_level(verbose=False)
#specify where bdf data is found
dataFolder = '_'

#function to re-reference, drop externals, add montage to file
def preProcess(raw):
    
    raw.drop_channels(raw.info.ch_names[64:-1]) # drop externals 
    montage = mne.channels.make_standard_montage('biosemi64') #channel set-up
    raw = raw.set_montage(montage)        
    raw.set_eeg_reference() # re-reference to average
    return raw

# get list of all files in data folder
files = [f for f in os.listdir(dataFolder) 
         if not os.path.isdir(dataFolder + f)]
files.sort() 
print(files,flush=True)

#loops through files
for x, file in enumerate(files):
    
    dataRawFile = os.path.join(dataFolder, file)
    raw = mne.io.read_raw_bdf(dataRawFile, preload=True)
    
    #appy notch filter at 50 & multiples of
    raw = raw.copy().notch_filter(freqs=np.arange(50, 251, 50)) 
    
    #print the participant & sampling rate, check in on the output file
    print('participant ' + file + ' srate = ' 
          + str(raw.info['sfreq']), flush = True)
    
    raw = preProcess(raw) #run preprocessing
    
    pID = file[:-8]
    session = file[6:7]
    
    raw.save(fname = f'_.fif', overwrite = True)
    print('finished ' + str(pID), flush=True)
    






