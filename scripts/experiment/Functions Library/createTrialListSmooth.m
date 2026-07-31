function [TrialList] = createTrialListSmooth(nFlashLocations, localizerTrials, motionTrials)

%CREATETRIALLIST This function creates the Trial list for the smooth motion
%EEG project

if rem(localizerTrials,nFlashLocations) ~= 0
   error('pick a number of localizer trials that is a multiple of %d', nFlashLocations) 
end

%% TrialList cell array that contains all trial lists for different block types
TrialList = [];

%% localizer block

allLocs = linspace(3,360,120); % all possible stimulus positions
flashLocs = allLocs(1:120/nFlashLocations:end)+6; % get flash locations
locTrialList = repelem(flashLocs,1,localizerTrials/nFlashLocations)';
locTrialList = locTrialList(randperm(size(locTrialList,1)),1);

TrialList{1,1} = locTrialList(1:localizerTrials/2);
TrialList{1,2} = locTrialList(localizerTrials/2+1:end);

%% Smooth motion blocks

startLoc = repelem(flashLocs,1,motionTrials/nFlashLocations)'; % sample only the 'flash' locations (from all possible stim locations)
startLoc = startLoc(randperm(size(startLoc,1)),1); 
endLoc = startLoc(randperm(size(startLoc,1)),1); 

trialDir = repelem([-1,1], 1, motionTrials/2)';
trialDir = trialDir(randperm(size(trialDir,1)),1);

TrialList{2,1} = [startLoc(1:motionTrials/2), endLoc(1:motionTrials/2), trialDir(1:motionTrials/2), NaN(motionTrials/2, 1)]; % NaNs in fourth column will be overwritten with new endpoint for reversal trials
TrialList{2,2} = [startLoc(motionTrials/2+1:end), endLoc(motionTrials/2+1:end), trialDir(motionTrials/2+1:end), NaN(motionTrials/2, 1)];

end

