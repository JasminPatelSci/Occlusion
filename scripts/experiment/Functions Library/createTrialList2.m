function [TrialList] = createTrialList2(localizerTrials, nSequences)
% CREATETRIALLIST This function creates the Trial list
% First column: localizer, Second row: CW, Third row: CCW, Fourth row: 50/50

%% TrialList cell array that contains all trial lists for different block types
TrialList = [];

%% set up sequences:
[x,y]=meshgrid(1:8,1:8);
ordersCW=repmat(mod(x+y-1,8)+1,1,2);
ordersCCW=fliplr(ordersCW);

%% localizer block --> 640 = 10 min

%creates two blocks of localisers, one of which will be made white at
%runtime, one of which will be black at runtime. 

locTrialList = repelem([1:8],1,localizerTrials/8)';
locTrialList = num2cell(locTrialList(randperm(size(locTrialList,1)),1));

TrialList{1,1} = locTrialList(1:localizerTrials/2);
TrialList{1,2} = locTrialList(localizerTrials/2+1:end);

locTrialList = repelem([1:8],1,localizerTrials/8)';
locTrialList = num2cell(locTrialList(randperm(size(locTrialList,1)),1));

TrialList{2,1} = locTrialList(1:localizerTrials/2);
TrialList{2,2} = locTrialList(localizerTrials/2+1:end);
% % % %% CW & CCW blocks
% % % singlePresentations = repelem([1:8],1,singlePresentationTrials/8);
% % % 
% % % CW_SP = num2cell(singlePresentations(1,randperm(size(singlePresentations,2))))';
% % % CCW_SP = num2cell(singlePresentations(1,randperm(size(singlePresentations,2))))';
% % % 
% % % CWblock = [];
% % % CCWblock = [];
% % % 
% % % for i = 1:proportionSequenceSingles*singlePresentationTrials
% % %     seqLength = randperm(7,1)+1; %between 2 and 8
% % %     startPos = randperm(8,1);
% % %     CWblock = cat(1,CWblock,mat2cell(ordersCW(startPos,1:seqLength),1,seqLength));
% % % end
% % % 
% % % for i = 1:proportionSequenceSingles*singlePresentationTrials
% % %     seqLength = randperm(7,1)+1; %between 2 and 8
% % %     startPos = randperm(8,1);
% % %     CCWblock = cat(1,CCWblock,mat2cell(ordersCCW(startPos,1:seqLength),1,seqLength));
% % % end
% % % 
% % % cwTrialList = cat(1,CWblock,CW_SP);
% % % cwTrialList = cwTrialList(randperm(size(cwTrialList,1)),1);
% % % TrialList{2,1} = cwTrialList(1:length(cwTrialList)/2);
% % % TrialList{2,2} = cwTrialList(length(cwTrialList)/2+1:end);
% % % 
% % % ccwTrialList = cat(1,CCWblock,CCW_SP);
% % % ccwTrialList = ccwTrialList(randperm(size(ccwTrialList,1)),1);
% % % TrialList{3,1} = ccwTrialList(1:length(ccwTrialList)/2);
% % % TrialList{3,2} = ccwTrialList(length(ccwTrialList)/2+1:end);

%% 50/50 block 
% creates two blocks of 50/50, one of which will be attend white at
% runtime, one of which will be attend black at runtime

singlePresentations = repelem([1:8],1,nSequences/8);
% SP_50 = num2cell(singlePresentations(1,randperm(size(singlePresentations,2))))';
block50 = [];

motionDirection = repelem([0 1],1,nSequences/2);
motionDirection = motionDirection(1,randperm(size(motionDirection,2)));

for i = 1:nSequences
    %%%HH changed sequence length to 5-12
    seqLength = randperm(8,1)+4; %
    startPos = randperm(8,1);
    direction = motionDirection(i);
    
    if direction
        block50 = cat(1,block50,mat2cell(ordersCW(startPos,1:seqLength),1,seqLength));
    else
        block50 = cat(1,block50,mat2cell(ordersCCW(startPos,1:seqLength),1,seqLength));
    end
end

% TrialList50 = cat(1,block50,SP_50);
TrialList50 = block50(randperm(size(block50,1)),1);
TrialList{3,1} = TrialList50(1:length(TrialList50)/2);
TrialList{3,2} = TrialList50(length(TrialList50)/2+1:end);

%second time
singlePresentations = repelem([1:8],1,nSequences/8);
% SP_50 = num2cell(singlePresentations(1,randperm(size(singlePresentations,2))))';
block50 = [];

motionDirection = repelem([0 1],1,nSequences/2);
motionDirection = motionDirection(1,randperm(size(motionDirection,2)));

for i = 1:nSequences
    %%%HH changed sequence length to 5-12
    seqLength = randperm(8,1)+4; %
    startPos = randperm(8,1);
    direction = motionDirection(i);
    
    if direction
        block50 = cat(1,block50,mat2cell(ordersCW(startPos,1:seqLength),1,seqLength));
    else
        block50 = cat(1,block50,mat2cell(ordersCCW(startPos,1:seqLength),1,seqLength));
    end
end

% TrialList50 = cat(1,block50,SP_50);
TrialList50 = block50(randperm(size(block50,1)),1);
TrialList{4,1} = TrialList50(1:length(TrialList50)/2);
TrialList{4,2} = TrialList50(length(TrialList50)/2+1:end);
end

