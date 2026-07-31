function [TrialList] = createTrialListOcclusion(nFlashLocations, localizerTrials, motionTrials, nReports)

% CREATETRIALLIST This function creates the trial list for the occlusion
% project. 

if rem(localizerTrials,nFlashLocations) ~= 0
    error('pick a number of localizer trials that is a multiple of %d', nFlashLocations)
end

%% TrialList cell array that contains all trial lists for different block types
TrialList = [];

%% Localizer block

for session = 1:2
    
    allLocs = linspace(3,360,120); % all possible stimulus positions
    flashLocs = allLocs(1:120/nFlashLocations:end)+6; % get flash locations
    duration = repmat(repelem(Shuffle([1,2]'),localizerTrials/8,1),4,1); % is flash on for a short or long duration?
    subsetLocalizers = repelem(flashLocs,1,localizerTrials/(nFlashLocations*2))'; % creat half size version of localizers
    locTrialList = NaN(localizerTrials, 1); % populate full size variable with just nans for now
    
    % by adding in a randomization of the subset, we can balance between
    % the two conditions
    locTrialList(duration == 1) = subsetLocalizers(randperm(size(subsetLocalizers,1)),1); % randomize within short condition
    locTrialList(duration == 2) = subsetLocalizers(randperm(size(subsetLocalizers,1)),1); % randomize within long condition
    
    reports = zeros(localizerTrials/2, 1);
    reports(1:(nReports/2)) = 1; % halve nReports because we double on the next line
    reportsAll = [reports(randperm(length(reports))); reports(randperm(length(reports)))];
    
    TrialList{1,session} = [locTrialList, duration, reportsAll];
    
end

%% Smooth motion block

for session = 1:2
    
    % sample only the 'flash' locations (from all possible stim locations)
    startLoc = repelem(flashLocs,1,motionTrials/nFlashLocations)';
    startLoc = startLoc(randperm(size(startLoc,1)),1);
    endLoc = startLoc(randperm(size(startLoc,1)),1);
    occlusionLoc = startLoc(randperm(size(startLoc,1)),1);
    
    trialDir = repelem([-1,1], 1, motionTrials/2)';
    trialDir = trialDir(randperm(size(trialDir,1)),1);
    
    TrialList{2,session} = [startLoc, endLoc, trialDir, occlusionLoc];
    
end

end

