#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  7 15:15:26 2023

Epoching functions for occlusion experiment 

@authororig: willturner williamfrancisturner@gmail.com
: JasminPatel 15.04.25 re-written

file locations removed 30.07.26
"""

import mne
import numpy as np

#function to epoch the localisers
def epoch_localisers(raw, pID):
    
    #get full set of triggers
    events = mne.find_events(raw, stim_channel='Status', min_duration = 0.001,
                             consecutive=True)
    
    #drop trigger channel, to be passed to epoching function
    picks = mne.pick_channels(raw.ch_names, include= [], exclude=['Status'])
    
    #localiser triggers (1-40)
    stim = events[np.isin(events[:,2], np.linspace(1,40,40))]
    
    #epoch localisers(applied low-pass filter to signal to avoid aliasing)
    stimEpochs = mne.Epochs(raw, stim, picks=picks, baseline=(-0.2,0), 
                            tmin=-0.2, tmax=1, preload=True)
    stimEpochs.resample(sfreq = 512)
    
    #print no. of traning trials & how many epochs produced + no. dropped
    print('p' + str(pID) + '\n' +  str(stim.shape[0]) + 
          ' available training trials \n' + str(len(stimEpochs)) + 
          ' selected training trials')
    
    xTrain = stimEpochs.get_data()
    yTrain = stimEpochs.events[:,2].copy()
    
    print('\nlocation counts:')
    for loc in np.unique(yTrain):
        print(f'location {loc}: {np.sum(yTrain == loc)}')
    
    return xTrain, yTrain, stimEpochs

#function to epoch around events for moving stimulus    
def epoch_motion(raw, pID, tmin=-0.2, tmax=0.25):
 
    events = mne.find_events(raw,stim_channel='Status', output ='onset',
                             min_duration = 0.0015, consecutive=True)
                
    picks = mne.pick_channels(raw.ch_names, ['P7', 'P5', 'P3', 'P1', 'Pz', 
                                            'P2', 'P4', 'P6', 'P8', 'PO7',
                                            'PO3', 'POz', 'PO4', 'PO8',
                                            'O1', 'Oz', 'O2', 'CPz']) 
    
    
    # extract stim epochs
    stim = np.argwhere(np.isin(events[:,2], np.linspace(1,40,40))).ravel() 
        
    eventInd = np.isin(events[stim + 1, 2], [41, 42, 43, 44])
    events[stim[eventInd], 2] += 500   
    
    stim = events[np.isin(events[:,2], np.linspace(501,640,140))] 
    
    stimEpochs = mne.Epochs(raw, stim, 
                             baseline=(-0.2,0), 
                             tmin=tmin, 
                             tmax=tmax, picks = picks,
                             preload=True) 
        
    # https://mne.tools/0.11/auto_examples/preprocessing/plot_resample.html
    stimEpochs.resample(sfreq = 512) # this will lowpass and resample 
    
    xTrain = stimEpochs.get_data() # EEG signals: n_epochs, n_channels, n_times
    xTrain = xTrain[:,:,102:]
    yTrain = stimEpochs.events[:, 2].copy() - 500
    
    xTest = []
    yTest = []
    
    triggers = events[:,2]
    moving = np.array(np.where(np.isin(triggers, 
                                       np.linspace(51,90,40).astype(int))))
               
    # prevent crash if final trigger is a moving trigger 
    moving = moving[moving < (len(events) - 1)]
    
    occlusion = [135, 143]
    stops     = [133, 141]
    starts    = [132, 140]
            
    triggerCodes = [starts, stops, occlusion]
        
    for epochType in triggerCodes:
        for subType in epochType:
            
            eventInd = events[moving + 1, 2] == subType
            events[moving[eventInd], 2] += 500   
            event = events[np.isin(events[:,2],np.array(range(551,591)))]
            eventEpochs = mne.Epochs(raw, event, picks = picks,
                        baseline = (-1, 0), 
                        tmin= -1,tmax = 1, 
                        preload=True)
                      
            events[moving[eventInd], 2] -= 500   
            eventEpochs.resample(512)
    
            xTest.append(eventEpochs.get_data(copy=False))
            yTestTemp = eventEpochs.events[:, 2].copy() 
            yTest.append((yTestTemp-550)-1)
    
    return xTrain, yTrain, xTest, yTest
          
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

