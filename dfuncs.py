# -*- coding: utf-8 -*-
"""
Created on Mon Oct 27 12:46:20 2025

Decoding functions library for occlusion experiment. 

@authororig: willturner williamfrancisturner@gmail.com
: JasminPatel 27.10.25 re-written

file locations removed 30.07.26
"""

import os
import mne         
import numpy as np
import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from mne.decoding import GeneralizingEstimator, cross_val_multiscore
from mne.decoding import SlidingEstimator


def load_data(file, dataFolder):
    dataRawFile = os.path.join(dataFolder, file)
    return mne.io.read_raw_fif(dataRawFile, preload=True)

def save_data(file, scores):
    with open(file, 'wb') as f:
        pickle.dump(scores, f)

#LDA within-decoding
def decode_tgm(x, y):
    """Run temporally-generalized decoding (King & Dehaene, 2014)
    xTrain = EEG data. 
    yTrain = index of circular stim positions.
    nPos = number of localizer positions
    """
    print(y)
    clf = make_pipeline(StandardScaler(), 
                        LinearDiscriminantAnalysis(solver='lsqr', 
                                                   shrinkage='auto'))
    estimator = GeneralizingEstimator(clf, scoring='accuracy', n_jobs=4)

    scores = cross_val_multiscore(estimator, x, y, cv=5, n_jobs=4)    

    tgm = np.mean(scores, axis = 0)
    diag = np.diag(tgm)
    
    return tgm, diag

#LDA within-decoding 
def decode_search(stimEpochs, xmin, xmax):
    """Run a searchlight version of the diagonal decoding.
    Loop through each electrode and, including only its immediate neighbours, 
    re-run the diag decoding analysis and return peak decoding accuracy.
    """

    scoresAll = np.zeros((64, xmax-xmin)) # chans x time points #!!change

    adj, names = mne.channels.find_ch_adjacency(stimEpochs.info,ch_type='eeg')
        
    clf = make_pipeline(StandardScaler(), 
                        LinearDiscriminantAnalysis(solver='lsqr', 
                                                   shrinkage='auto'))
    estimator = SlidingEstimator(clf, n_jobs=4)

    for k in range(len(names)): 
        
        neigh_idx = np.where(adj[k,:].toarray().ravel())[0]
        
        if k not in neigh_idx:
            neigh_idx = np.append(neigh_idx, k)
    
        neigh_names = [names[i] for i in neigh_idx]
        
        xTrain = stimEpochs.get_data(picks=neigh_names)
        xTrain = np.ndarray.copy(xTrain[:, :, xmin:xmax])
        yTrain = stimEpochs.events[:, 2].copy()
        
        scores = cross_val_multiscore(estimator, xTrain, yTrain, cv=5)
        scoresAll[k, :] = scores.mean(axis=0) 
        
    return scoresAll



##LDA

def centre_map(scores, y):
    
    """Re-centre probability values"""
        
    for ind in range(0, len(y)):
        scores[ind,:,:,:] = np.concatenate((scores[ind,:,:,y[ind]:], 
                                            scores[ind,:,:,:y[ind]]),axis=2)

    scores = np.mean(scores,axis=0)
    scores = np.concatenate((scores[:,:,20:], scores[:,:,:20]), axis = 2)
    
    return scores

#LDA cross-decoding from flashed localiser training data to moving/events
def LDA_map(xTrain, yTrain, xTest, yTest, xmin, xmax, synth=False, nPos=40):
    
    """Extract a probabilistic map over stimulus positions via LDA.
       We pre-train the models on the localizer data and then use the 
       predict_proba function to get a probability for each class (position).
       If using the synthetic data we need to seperately scale the testing and
       training data.""" 
      
       
    # forcing a copy (not view) to try to save on memory
        # Sampling point 25 = 50ms 
        # So if you wanted to do 50-250, it would be: 25:129
        # xTrain is from 0ms-250ms
        
    xTrain = np.ndarray.copy(xTrain[:, :, xmin:xmax]) #varied for timewindow
      
    clf = make_pipeline(LinearDiscriminantAnalysis(
                            solver='lsqr',
                            shrinkage='auto',
                            priors=np.tile(1/nPos, nPos))) #no PCA
    scaler = StandardScaler()
    
    for i in range(xTrain.shape[2]):
        xTrain[:,:,i] = scaler.fit_transform(xTrain[:,:,i].T).T

    trainedClassifier = GeneralizingEstimator(clf, n_jobs=1, verbose=True)
    trainedClassifier.fit(xTrain,yTrain)
    
    
    decodingScores = np.zeros((len(xTest), xTrain.shape[2], 
                               xTest[0].shape[2], nPos))

    for trialType in range(0, len(xTest)):

        for i in range(xTest[trialType].shape[2]):
            xTest[trialType][:,:,i] = scaler.fit_transform(xTest[trialType]
                                                           [:,:,i].T).T

        
        scores = trainedClassifier.predict_proba(xTest[trialType])
        decodingScores[trialType, :, :, :] = centre_map(scores, 
                                                        yTest[trialType])
    
    return decodingScores






























    

