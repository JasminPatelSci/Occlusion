function [TrialList] = createTrialListOcclusion_2(nFlashLocations, localizerTrials, motionTrials)

% CREATETRIALLIST This function creates the trial list for the occlusion
% project. 

if rem(localizerTrials,nFlashLocations) ~= 0
    error('pick a number of localizer trials that is a multiple of %d', nFlashLocations)
end

%% TrialList cell array that contains all trial lists for different block types
TrialList = [];

%% Localizer block
    
allLocs = linspace(3,360,120); % all possible stimulus positions
flashLocs = allLocs(1:120/nFlashLocations:end)+6; % get flash locations
locTrialList = repelem(flashLocs,1,localizerTrials/nFlashLocations)';
locTrialList = locTrialList(randperm(size(locTrialList,1)),1);

TrialList{1,1} = locTrialList;
TrialList{1,2} = locTrialList(randperm(size(locTrialList,1)),1);

%% Smooth motion block

startLoc = repelem(flashLocs,1,motionTrials/nFlashLocations)';
trialDir = repelem([-1,1], 1, motionTrials/2)';

for session = 1:2
    
    % only choose localiser positions for start, stop, and occlusion points
    startLoc = startLoc(randperm(size(startLoc,1)),1);
    endLoc = startLoc(randperm(size(startLoc,1)),1);
    occlusionLoc = startLoc(randperm(size(startLoc,1)),1);
    
    trialDir = trialDir(randperm(size(trialDir,1)),1);
      
    TrialList{2,session} = [startLoc, endLoc, trialDir, occlusionLoc];
    
end

end

