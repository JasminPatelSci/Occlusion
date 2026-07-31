%% Task code: decoding across occlusions project spin-off

% History:
% Code written by William Turner, based on code from earlier projects with 
% Philippa Johnson and Tessel Blom. 
% Adapted by William Turner 30/6/2024 to remove working memory and report
% Adapted by Jasmin Patel 15/05/2025 diff. occlusion sizes
% File locations removed by Jasmin Patel 31/07/2026

% Trigger codes:

% 254 start exp
% 252 response 
% 255 end exp

% Single presentation trials 
% triggerValue1 = stimulusLocation 
% triggerValue2 = hasTarget 

% Motion trials:
% triggerValue1 = 50 + stimulusLocation + (hasTarget*40)
% triggerValue2 = 131 + (firstInTrial*1) + (lastInTrial*2) + 
% (startOcclusion*4) + ((direction==1)*8) + (onsetOccluder*16) + (occluder
% size*32) where 0=normal, 1=smaller 2=larger

%% Housekeeping 

clear
commandwindow

cd('_')
%cd('_')


addpath(genpath('Functions Library'));

%% Screen Initialisation

whichScreen = 0;
Screen('Preference', 'SkipSyncTests', 0); % set to 0 for experiment!! 1=debug

%% Input participant and session info

newParticipant = [];
while isempty(newParticipant)
    newParticipant = input('Is this a new participant? (1 = Yes, 0 = No): ','s');
end

subID = [];
while isempty(subID)
    subID = input('Participant ID: ','s');
end

sessionID = [];
while isempty(sessionID)
    sessionID = input('Session number: ','s');
end

filename = [subID '_' sessionID '.mat'];

if exist(filename, 'file')
    disp('File already exists! Please restart experiment.')
    return
end

%% Trigger info and mode 
USB = 1; % send triggers via usb virtual COM port. 

Port = struct();
Port.EventTriggerDuration = 0.002; % trigger duration in seconds (2 ms)
Port.isOn = 1; % 1 sends triggers to the sport, set to 0 for debugging

% Set up trigger port
if Port.isOn
    % % if USB == 0
    % % Port.ioObj = io64;
    % % Port.address = hex2dec('3fd8'); % Can find in System Info, Hardware Resources, I/O, look at the SUNIX Port Card Addresses. 
    % % status = io64(Port.ioObj);
    % else 
   Port.address = serial('COM3', 'BaudRate', 115200, 'DataBits', 8, 'StopBits', 1, 'Parity', 'none');
   % from https://www.biosemi.com/faq/USB%20Trigger%20interface%20cable.htm
   get(Port.address);
   fopen(Port.address);
    % end
end

if  Port.isOn && Screen('FrameRate', whichScreen) ~= 120
    error('Change the refreshrate!')
end

%% Stimulus properties

backCol = 128; % background color

nFlashLocs = 40;
allLocs = linspace(3,360,120);
flashLocs = allLocs(1:120/nFlashLocs:end) + 6; % add 6 to make locations start from top

nFrames = 120; % refresh rate of the monitor
stimRadius = 317; % center of stim, in pixels from the center of the screen
stimSize = 150; % in pixels
stimWidth = deg2rad(360/nFlashLocs); % PJ: suggestion of 9 degrees
stimRadialWidth =  stimRadius/10; % radial width of wedge, in pixels

occluderRadius = 2 * (stimRadius + stimSize); % radius of occluder 
occluderWidth = [180, 108, 252]; % occluder covers 180 degrees of circle + 108 (smaller) + 252 (larger)
occluderWidthRad = deg2rad(occluderWidth);

flashDur = 100; % 100 ms on
flashFrames = flashDur/(1000/nFrames); 
ISIframes = flashFrames; % ISI is also 100ms

% Note, these values are for one session 
localizerTrials = 1000; % 25 per position (per session) (~3.5 mins static flashes); 2 blocks for session 1
motionTrials = 720; % 12 * 40 (x 3 occlusion events per trial) = 1440 occlusions (36 per pos) #=> attempting to make this x3 as many over multiple session- see how close can get; at current is 3x, 4 sessions

blockOrder = randperm(2); % (currently one block flashes, one block smooth motion), will keep same with interleaved 3 occlusion sizes
targetsPerBlock = [20, 50];

ITI = 500; % mean ITI (ms) becomes 550ms (500-600ms)

%% TrialList

if newParticipant
    
    TrialList = createTrialListOcclusion_sizes(nFlashLocs,localizerTrials,motionTrials);                                              

    mkdir(['Data\' subID])
    save([pwd '\Data\' subID '\TrialList.mat'],'TrialList');
    
else
    
    TrialList = load([pwd '\Data\' subID '\TrialList.mat']);
    
end


try
   
    [winID,winRect] = Screen('OpenWindow',whichScreen,backCol);
    
    % optimising system for running the experiment
    HideCursor; % hide mouse cursor
    FlushEvents ''; % flush events
    
    % set max priority to psychtoolbox to increase performance
    priorityLevel = MaxPriority(winID);
    Priority(priorityLevel);
    clear priorityLevel;
    
    % screen dimensions
    hRes = winRect(3);
    vRes = winRect(4);
    
    % load fixation dot and create texture
    [fixationimage, map, alpha] = imread('fix_dot.png'); 
    fixationimage(:,:,4) = alpha; % adds transparency
    FixationTexture = Screen('MakeTexture', winID, fixationimage);
    Screen('BlendFunction', winID, 'GL_SRC_ALPHA', 'GL_ONE_MINUS_SRC_ALPHA'); % allows transparent picture
    % fixation dot citation: https://www.sciencedirect.com/science/article/pii/S0042698912003380
    
    % %timestamping
    % %initalise log variables
    % eventLabels = {};           % Initialize as an empty cell array
    % eventTimestamps = [];       % Initialize as an empty numeric array
    % triggerCodes = [];
    % triggerTimestamps = [];
    % t0 = GetSecs;


    %%%%%%%%%% Prepare stimuli %%%%%%%%%
    
    % this is used later when drawing the stimulus to screen.
    stimRectCenter = CenterRect([0 0 stimSize stimSize],winRect);

    % make wedge-shaped mask
    stimMask=mkAngle(stimSize,0,[(stimSize+1)/2,(stimSize+1)/2-stimRadius]);
    stimMask=double(abs(stimMask)<stimWidth/2);
    stimMaskRadial=mkR(stimSize,1,[(stimSize+1)/2,(stimSize+1)/2-stimRadius]);
    stimMaskRadial=abs(stimMaskRadial-stimRadius)< stimRadialWidth;
    
    % put the two together and make texture
    stim = backCol+0.5*254*stimMask.*stimMaskRadial;
    stimID = Screen('MakeTexture',winID,stim);
    
    % target is purple 
    stimTargetID = Screen('MakeTexture',winID,cat(3,backCol*ones(stimSize,stimSize,1),255-stim,stim));
    
    % make pizza-shaped occluders #not sure if this works yet
    occluderMask=mkAngle(occluderRadius,0,[(occluderRadius+1)/2,(occluderRadius+1)/2]);

    for i = 1:length(occluderWidthRad)
        
        occluderMask=mkAngle(occluderRadius,0,[(occluderRadius+1)/2,(occluderRadius+1)/2]);
        occluderMask=double(abs(occluderMask)<occluderWidthRad(i)/2);
        occluderMaskRadial=mkR(occluderRadius,1,[(occluderRadius+1)/2,(occluderRadius+1)/2]);
        occluderMaskRadial=(occluderMaskRadial) < (occluderRadius/2);
        
        occluder=254*((occluderMask.*occluderMaskRadial).*rand(occluderRadius));
        occluderOpaque = cat(3, occluder, occluder);
        occluderOpaque = cat(3, occluderOpaque, occluderOpaque); 
        occluderOpaque(:, :, 4) = (occluder ~= 0)*255;
        occluderID(i) = Screen('MakeTexture',winID,occluderOpaque);
    end
    
    
    %%%%%%%%%% Get Ready to run %%%%%%%%%%
    
    % present general instructions and wait for keypress
    HH_centerText(winID,'Always focus on the fixation dot at the center of the screen.',winRect,-1,-150);
    HH_centerText(winID,'Follow the moving object with your attention (but not your eyes!)',winRect,-1,-100);
    HH_centerText(winID,'Press the "x" key to begin',winRect,-1,200);
    [VBLTimestamp, lastOnset] = Screen('Flip', winID);
    HH_waitForKeyPress({'x'});
    
    WaitSecs(1)
    
    % Send first trigger code (experiment start)
    if Port.isOn
        send_eeg_trigger_usb(Port, 254)            
    end 
    
    allresponses = {[], []}; % stores responses to targets from both blocks
    responseTime = []; % stores RTs for given section of training block (reset to zero at each break)
    targetCount = 0; % counts targets within given section of training block (reset to zero at each break)
    
    %% Block loop
    
    % store reports of flash position when prompted
    results = zeros(localizerTrials, 5, 1); % results: trial, [stim pos, duration condition, abs response, error, rt], session =========don't currently have the code in to store this? see first occlusion script=======

    for b = 1:length(blockOrder)
        
        if b == 2
            missedTargs = targetCount-length(responseTime);
            HH_centerText(winID,'End of block 1. Feel free to have a short break.',winRect,0,-150)
            HH_centerText(winID,['You missed ' num2str(missedTargs) ' out of ' num2str(targetCount) ' targets.'],winRect,0,-50)
            if ~isempty(responseTime)
                avgResponseTime = mean(responseTime)*1000; % convert to ms
                HH_centerText(winID,['Your average response time is: ' num2str(avgResponseTime) 'ms'],winRect,-1,50)
            end
            HH_centerText(winID,'Press "x" to start block 2',winRect,-1,150)
            [VBLTimestamp, lastOnset] = Screen('Flip', winID);
            HH_waitForKeyPress({'x'});
            responseTime = []; targetCount = 0;
        end
        
        % block = 1; % uncomment this line (and comment one below) for testing a specific block
        block = blockOrder(b);
        
        trialInfo = TrialList{block,str2double(sessionID)};
        
        WaitSecs(0.5);
        
        %% Trial loop
        
        taskRunning = 0;
        responseCounter = 0;
        hasTarget = 0;
        totalfnum = 0; 
        
        %%% below we create a full-block-length array of
        %%% things to draw on each frame
        
        fullFrameVect=[];
        
        % pick a jittered ITI
        allITIs=round((ITI+rand(1,length(trialInfo))*100)/1000*nFrames, 0); % 500-600 ms ITI (in frames!)
                                                                                                
        % loop through trials and pre-allocated frames
        for trialnum = 1:size(trialInfo,1)
            
            startPos = trialInfo(trialnum, 1);
            
            
            if block > 1
                
                endPos = trialInfo(trialnum, 2);
                direction = trialInfo(trialnum, 3); % 1 = CW / -1 = CCW
                occluderPos = trialInfo(trialnum, 4); 
                
                occluderSize = trialInfo(trialnum,5); 
                occluderSizei = occluderSize; %get size for use seperate than frame value
                
                if direction == 1 % clockwise
                    
                    first180 = mod(startPos:-3:startPos-180,360);
                    rotateToTop = first180(end)-3:-3:0;
                    fullRotation = 357:-3:0;
                    rotateToEnd = 357:-3:endPos;
                    
                else % if anticlockwise
                    
                    first180 = mod(startPos:3:startPos+180,360);
                    rotateToTop = first180(end)+3:3:360;
                    fullRotation = 3:3:360;
                    rotateToEnd = 3:3:endPos;
               
                end
                
                frameVector = [first180 rotateToTop fullRotation ...
                              fullRotation fullRotation fullRotation ... % occluded rotations
                              fullRotation rotateToEnd]; % washout

                frameVector(frameVector==0) = 360; % stimulus cannot be drawn at 0deg
                
                % get frames for this sequence
                framesPerTrial = size(frameVector, 2);
                
                direction = Expand(direction, framesPerTrial, 1); % expand for storage in the full frame vector below.                    
                
                occluderSize = Expand(occluderSize, framesPerTrial, 1);

                trialStart = [trialnum zeros(1,length(frameVector)-1)];
                
                lastPos = zeros(1, length(frameVector));
                lastPos(end) = 1; % length of trialOrderUnpack marks the last position
                
                % mark flash locations to send triggers at
                triggerNow = ismember(frameVector, flashLocs);
                
                loop = 1;
                
                while loop  % set up while loop
                    
                    % Mark occluder onset, offset and beginning of each clean
                    % occlusion.
                    % onsetPos = randsample(flashLocs, 1);
                    occluderHalf = (occluderWidth(occluderSizei+1))*0.5;
                    if direction == 1
                        onsetPos = mod(occluderPos - (occluderHalf + 6), 360); % -96 because occluder is 90 degrees => changed to calc based on size half width, + 6 means stim is just fully out. 
                        offsetPos = onsetPos; 
                    else
                        onsetPos = mod(occluderPos + (occluderHalf + 6), 360);
                        offsetPos = onsetPos; 
                    end
                    
                    % offsetPos = randsample(flashLocs, 1);

                    if direction == 1
                        stepsToOccluderEdge = 120 - ((occluderPos/3) + (occluderHalf/3)); % 1/2 occluder width = 180/2 = 90 => changed to calc based on size... in stimulus steps = 90/3 = 30 steps.
                        if stepsToOccluderEdge > 120
                            stepsToOccluderEdge = 120-stepsToOccluderEdge;
                        end
                        stepsToOnset = 120 - (onsetPos/3);
                        stepsToOffset = 120 - (offsetPos/3);
                    else
                        stepsToOccluderEdge = ((occluderPos/3) - (occluderHalf/3));
                        stepsToOnset = (onsetPos/3);
                        stepsToOffset = (offsetPos/3);
                    end
                    
                    occlusionNow = zeros(1,length(frameVector));
                    occlusionNow(length(first180) + length(rotateToTop) + stepsToOnset) = 2; % occluder onset occurs at random point in first full rotation
                    occlusionNow(length(first180) + length(rotateToTop) + length(fullRotation) + stepsToOccluderEdge) = 1; % 1st occlusion
                    occlusionNow(length(first180) + length(rotateToTop) + (2 * length(fullRotation)) + stepsToOccluderEdge) = 1; % 2nd occlusion
                    occlusionNow(length(first180) + length(rotateToTop) + (3 * length(fullRotation)) + stepsToOccluderEdge) = 1; % 3rd occlusion
                    occlusionNow(length(first180) + length(rotateToTop) + (4 * length(fullRotation)) + stepsToOffset) = -1; % occluder offset occurs at random point in last full rotation
                    
                    % check that occluder onset happens before the first
                    % occlusion is meant to occur, and that occluder offset doesn't
                    % happen before final occlusion is done. These scenarios can happen very
                    % occasionally (for example, if the occluder is near the edge of the circle and
                    % occluder onset is, by chance, very late).
                    onsetCorrect = length(first180) + length(rotateToTop) + length(fullRotation) + stepsToOccluderEdge + 180 > length(first180) + length(rotateToTop) + stepsToOnset;
                    offsetCorrect = length(first180) + length(rotateToTop) + (3 * length(fullRotation)) + stepsToOccluderEdge + 90 < length(first180) + length(rotateToTop) + (4 * length(fullRotation)) + stepsToOffset;
                    if onsetCorrect || offsetCorrect
                        loop = 0;
                    end
                end
                
                % define point where first full cycle begins
                onsetOccluder = occlusionNow == 2; 
                
            else % if flash condition
                                
                endPos = NaN;
                direction = NaN;
                
                framesPerLoc = flashFrames; 
                framesBetweenLoc = ISIframes;
                
                frameVector = [Expand(startPos,framesPerLoc,1)];
                trialStart = [trialnum zeros(1,length(frameVector)-1)]; 
                triggerNow = [1 zeros(1,length(frameVector)-1)];
                
                % Don't need these for flashes so set to zero
                onsetOccluder = zeros(1,length(frameVector));
                occlusionNow = zeros(1,length(frameVector));
                lastPos = zeros(1,length(frameVector)); 
                direction = zeros(1,length(frameVector));
                occluderSize = zeros(1,length(frameVector));

            end
                                    
            % full frame vector will contain
            % row 1: position of stimulus
            % row 2: trial number
            % row 3: direction of motion sequence (1 = clockwise, -1 =
            % counterclockwise)
            % row 4: whether this is the last stim in the sequence or not (1 = yes, 0 = no)
            % row 5: whether to send triggers or not 
            % row 6: whether an occlusion trigger should be sent
            % row 7: point at which start of first full cycle begins 
            % row 8: occluder size

            % These rows are added later
            % row 9: whether target is present (1 = present, 0 = not
            % present)
            
            if block > 1
                fullFrameVect=[fullFrameVect zeros(8,allITIs(trialnum)) [frameVector;trialStart;direction;lastPos;triggerNow;occlusionNow;onsetOccluder;occluderSize]];
            else
                fullFrameVect=[fullFrameVect zeros(8,framesBetweenLoc) [frameVector;trialStart;direction;lastPos;triggerNow;occlusionNow;onsetOccluder;occluderSize]];
            end
            
        end % of for trialnum
              
        % pick random stimuli to make into targets by selecting frames in
        % which a stimulus has just been absent and now appears:
        firstPresentations=find(diff(fullFrameVect(2,:))>0) + 1; 
        
        task{block}=[];
        
        % exclude first 5 seconds and last 5 seconds
        firstPresentations=firstPresentations(firstPresentations>(5*nFrames) & firstPresentations<(length(fullFrameVect)-(5*nFrames)));
            
        % here I am buffering a variable which will be used to determine
        % when to present the target in the smooth blocks. Ones will later
        % be inserted in the time periods where targets will be presented
        targetOnSmooth = zeros(1, length(fullFrameVect));

        for i = 1:targetsPerBlock(block)
            
                % select one presentation to turn into a target, and remove it
                % and its neighbors from the possible choices:
                target=firstPresentations(randperm(length(firstPresentations),1));
                firstPresentations=firstPresentations(firstPresentations>target+(5*nFrames) | firstPresentations<target-(5*nFrames));
            
            if block == 2
               
                offset = randperm(120,1); % the onset of the target can occur anywhere within the first second of the stimulus (can change this to whatever time range we want).
                targetOnSmooth(target + offset + [0:11]) = 1; % Code 12 frames (100 ms) ms as 1 (this is when the target will be on).                         

            end

            task{block}=[task{block} target];
            fullFrameVect(9,target + [0:11])=1; % first 12 frames (100 ms) of flash are target
           
        end % of for i
        
        %% Create triggers ahead of time       
        
        if block < 2
            stimInFlashLoc = find(diff(fullFrameVect(2,:))>0) + 1; % take first onsets for flash trials
            firstFrame = fullFrameVect(:, stimInFlashLoc);
        else
            stimInFlashLoc = find(diff(fullFrameVect(5,:))>0) + 1;
            firstFrame = fullFrameVect(:, stimInFlashLoc);
        end
        
        triggers = 255 * ones(length(firstFrame), 2);
        
        %% Single presentation blocks
        
        if block < 2
            
            for trial = 1:length(firstFrame)
                
                location = trialInfo(trial, 1); 
                flashLoc = find(location == flashLocs); % find which of the 40 possible flash locations are we currently at
                hasTarget =  firstFrame(9, trial);

                triggers(trial,1) = flashLoc; % location 
                triggers(trial,2) = 41 + hasTarget; % is target present (41 = no, 42 = yes)
                
            end
            
            %% Sequential presentation blocks
        else
            
            for trial = 1:length(firstFrame)
                
                % get stimulus location
                location = firstFrame(1,trial);
                flashLoc = find(location == flashLocs);
                              
                % EDIT #2: this is actually the trial number... not an
                % index for whether its the first frame (my bad!)! So we need to
                % check whether it is greater than zero to get an idex of the
                % first stim in the trial. 
                % see if this is the start of a sequence
                firstInTrial = firstFrame(2, trial) > 0; % EDIT MADE HERE
                
                % get direction of each sequence
                direction = firstFrame(3, trial);

                % get occluder size
                occluderSize = firstFrame(8, trial);
                % occluderSize = 1;
                
                % check to see if this is the last stimulus in the sequence
                lastInTrial = firstFrame(4, trial);
                
                % check whether stimulus is about to be occluded (has
                % reached edge of occluder)
                startOcclusion = firstFrame(6, trial) > 0;
                
                % check for occluder onset
                onsetOccluder = firstFrame(7, trial);
                
                % check to see if a target is present
                hasTarget = firstFrame(9, trial);
                
                % code first and second trigger
                triggers(trial,1) = 50 + (flashLoc) + (hasTarget*40);
                
                % EDIT #3: removed the variable 'hasTarget' from below...
                % it shouldn't have been there (again my bad!!!). removed
                % 'onsetOccluder as isn't in other participants & worried
                % something is going wrong there
                triggers(trial,2) = 131 + (firstInTrial*1) + (lastInTrial*2) + (startOcclusion*4) + ((direction==1)*8) + (occluderSize*32);

                % Get trigger values for the sequential blocks (can
                % run these loops to confirm triggers are unique across all
                % possible combos)

                % first trigger 
%                 trigger1 = []
%                 for hasTarget = 0
%                     for flashLoc = 1:40
%                         trigger1 = [trigger1; 50 + (flashLoc) + (hasTarget*40)];
%                     end
%                 end
%                 trigger1 

% %                 % second trigger
%                 trigger2 = [];
%                 for onsetOccluder = 0
%                     for direction = [-1, 1] % NOTE: direction coding is
%                     %actually -1 and 1... but in practise this doesn't
%                     %matter since we use a logical statement (==1) when
%                     %making the trigger code. 
%                         for occluderSize = 0:2
    %                         for startOcclusion = 1
    %                             for lastInTrial = 0
    %                                 for firstInTrial = 0
    %                                             trigger2 = [trigger2; 131 + (firstInTrial*1) + (lastInTrial*2) + (startOcclusion*4) + ((direction==1)*8) + (onsetOccluder*16) + (occluderSize*32)];
    %                                 end
    %                             end
    %                         end
    %                     end
%                     end
%                 end
%                 trigger2

            end
        end
        
        % Initialise task variables
        keyWasDown = 0; 
        responseMatrix = zeros(targetsPerBlock(block),6);
        taskTimeOut = 5;
        currentTrialNum = 1; 
        triggerInd = 1; % we iterate this to move through the pre-allocated triggers
        occluderOn = 0; 


        
        % Now that all frames are prepared, actually display everything:
        for fnum = 1:length(fullFrameVect)
            
            % at the start of each new trial
            if fullFrameVect(2,fnum)~=0 % if its the start of a new trial
                currentTrialNum = fullFrameVect(2,fnum); % get current trial number 
            end
            
            if fullFrameVect(6,fnum) > 0 
                
                occluderOn = 1;
                occluderPos = trialInfo(currentTrialNum, 4); 
                occluderSize = trialInfo(currentTrialNum, 5);
                
            elseif fullFrameVect(6, fnum) == -1
                
                occluderOn = 0; 
                
            end

            % flash condition
            if fullFrameVect(1,fnum) ~= 0 && block == 1
                
                % calculate stimulus position
                polarAngleNow = deg2rad(fullFrameVect(1, fnum)) - pi/2;                 
                stimRectNow = OffsetRect(stimRectCenter,stimRadius*cos(polarAngleNow),stimRadius*sin(polarAngleNow));
                Screen('DrawTexture', winID, stimID, [0 0 stimSize stimSize],stimRectNow,polarAngleNow/pi*180);

                 % smooth condition
            else if fullFrameVect(1,fnum) ~= 0 && block == 2
                    
                    % calculate stimulus position
                    polarAngleNow = deg2rad(fullFrameVect(1,fnum)) - pi/2;
                    stimRectNow = OffsetRect(stimRectCenter,stimRadius*cos(polarAngleNow),stimRadius*sin(polarAngleNow));
                    Screen('DrawTexture', winID, stimID, [0 0 stimSize stimSize],stimRectNow,polarAngleNow/pi*180);

                end
            end
            
            % if there is a target in this trial (for flash trials)
            if fullFrameVect(9,fnum) && block == 1
                Screen('DrawTexture', winID, stimTargetID, [0 0 stimSize stimSize] ,stimRectNow,polarAngleNow/pi*180);
                if fullFrameVect(9,fnum-1)==0 % only update the counter at the first frame of each target (not all frames!)
                    targetCount = targetCount+1;
                end
            end
            
            % if there is a target in this trial (for smooth trials)
            if targetOnSmooth(fnum) == 1
                Screen('DrawTexture', winID, stimTargetID, [0 0 stimSize stimSize] ,stimRectNow,polarAngleNow/pi*180);
                if targetOnSmooth(fnum-1) == 0 % only update the counter at the first frame of each target (not all frames!)
                    targetCount = targetCount+1;
                end
            end
            
            if occluderOn 
                occluderAngle = deg2rad(occluderPos) - pi/2; 
                Screen('DrawTexture', winID, occluderID(occluderSize+1), [0 0 occluderRadius occluderRadius],[],occluderAngle/pi*180);
            end
            
            Screen('DrawTexture', winID, FixationTexture);

            [VBLTimestamp, lastOnset ] = Screen('Flip', winID, lastOnset + 1/(2*nFrames));
            
            %timestamping
            % if (fullFrameVect(5,fnum)==1) % if send trigger is true 
            % 
            %     eventTime = VBLTimestamp;
            %     eventLabel = ['stim_onset_' num2str(triggers(triggerInd, 1)) '_' num2str(triggers(triggerInd, 2))];
            %     eventLabels{end+1} = eventLabel;
            %     eventLabels{end+1} = eventLabel;
            %     eventTimestamps(end+1) = eventTime-t0;
            %     eventTimestamps(end+1) = eventTime-t0;
            % 
            % end

            if Port.isOn
                
                if (fullFrameVect(5,fnum)==1) % if send trigger is true
                    
                    send_eeg_trigger_usb(Port, triggers(triggerInd, 1))
                    %timestamping
                    % triggerCodes(end+1) = triggers(triggerInd, 1); % The trigger value 
                    % triggerTimestamps(end+1) = GetSecs-t0; % Timestamp of that trigger
                    
                    send_eeg_trigger_usb(Port, triggers(triggerInd, 2))
                    %timestamping
                    % triggerCodes(end+1) = triggers(triggerInd, 2); % The trigger value 
                    % triggerTimestamps(end+1) = GetSecs-t0; % Timestamp of that trigger
                        
                        % troubleshoot timing of occlusion trigger by 
                        % pausing just after it is sent (stimulus should
                        % pause right as it enters the occluder)
                        % if ismember(triggers(triggerInd, 2), [135, 143])
                        %     pause 
                        % end
                        
                    triggerInd = triggerInd + 1; % iterate upwards 
                        
                end
            end % of if port
            
            %% check for target 
            % If a target was presented that needs a response, start a timer
            % for flash trials
            if (fullFrameVect(9,fnum)) && block == 1
                
                taskTimer = tic;
                taskRunning = 1;
                responseCounter = responseCounter+1;
                
            end

            % for smooth motion trials (yes this is disgusting code)
            if fnum > 1 && targetOnSmooth(fnum) == 1 && targetOnSmooth(fnum-1) == 0 && block == 2
                
                taskTimer = tic;
                taskRunning = 1;
                responseCounter = responseCounter+1;
                
            end
            
            % check if subject is responding
            [keyIsDown, secs, keyCode, deltaSecs] = KbCheck;
            
            if keyCode(32) && ~keyWasDown && taskRunning % subject pressed a button that was not yet down
                
                responseMatrix(responseCounter,1:3)=[1 fnum toc(taskTimer)];
                keyWasDown=1;
                taskRunning=0;
                
                responseTime = [responseTime responseMatrix(responseCounter, 3)];
                
                % send trigger when subject responds
                if Port.isOn
                    
                    % send_event_trigger_neurospec(Port.sObj, Port.EventTriggerDuration, 252);

                    send_eeg_trigger_usb(Port, 252)                        


                end % of if port
                
            elseif keyWasDown && ~keyCode(32) % subject released the button

                keyWasDown = 0;

            end % of if key
            
            % check to see if a task has timed out
            if taskRunning && toc(taskTimer)>5
                taskRunning = 0;
            end

            if HH_checkQuit
                break
            end
            
            % break time!
            if fnum < length(fullFrameVect) && fullFrameVect(2,fnum + 1)~=0 && fullFrameVect(2, fnum)==0  % if the next frame is the start of a new stimulus
                
                % 9 sub-blocks in the smooth block
                if block == 2 && mod(currentTrialNum,80)==0 && currentTrialNum ~= motionTrials
                    
                    missedTargs = targetCount-length(responseTime);
                    HH_centerText(winID,'Feel free to have a short break.',winRect,0,-150)
                    HH_centerText(winID,['You missed ' num2str(missedTargs) ' out of ' num2str(targetCount) ' targets.'],winRect,0,-50)
                    
                    if ~isempty(responseTime)
                        avgResponseTime = mean(responseTime)*1000; % convert to ms
                        HH_centerText(winID,['Your average response time is: ' num2str(avgResponseTime) 'ms'],winRect,-1,50)
                    end
                    
                    HH_centerText(winID,'Press "x" to continue the block',winRect,-1,150)
                    [VBLTimestamp, lastOnset] = Screen('Flip', winID);
                    HH_waitForKeyPress({'x'});
                    responseTime = []; targetCount = 0;
                    WaitSecs(1)
                    
                end
                
                % 1 sub-block in the flash block; 2 in S1 so triggers then,
                % not very robust coding here
                % there is a screen for changing blocks
                if block == 1 && currentTrialNum == 1000 % for flash blocks give a break every 1000 trials

                     missedTargs = targetCount-length(responseTime);
                     HH_centerText(winID,'Feel free to have a short break.',winRect,0,-150)
                     HH_centerText(winID,['You missed ' num2str(missedTargs) ' out of ' num2str(targetCount) ' targets.'],winRect,0,-50)
                     if ~isempty(responseTime)
                         avgResponseTime = mean(responseTime)*1000; % convert to ms
                         HH_centerText(winID,['Your average response time is: ' num2str(avgResponseTime) 'ms'],winRect,-1,50)
                     end
                     HH_centerText(winID,'Press "x" to continue the block',winRect,-1,150)
                     [VBLTimestamp, lastOnset] = Screen('Flip', winID);
                     HH_waitForKeyPress({'x'});
                     responseTime = []; targetCount = 0;

                end
            end
            
        end % of frame loop
        
        if HH_checkQuit
            break
        end
        
        allresponses{block}=responseMatrix;
    
    end % of for block
    

    %% End Screen
    HH_centerText(winID,'Congratulations! You have completed the experiment.',winRect,0,-150);
    missedTargs = targetCount-length(responseTime);
    HH_centerText(winID,['You missed ' num2str(missedTargs) ' out of ' num2str(targetCount) ' targets.'],winRect,0,-50)
    if ~isempty(responseTime)
        avgResponseTime = mean(responseTime)*1000; % convert to ms
        HH_centerText(winID,['Your average response time is: ' num2str(avgResponseTime) 'ms'],winRect,-1,50)
    end

    Screen('Flip', winID);
    WaitSecs(4);
    
    Screen('CloseAll')
    save([pwd '\Data\' subID '\' filename]);
    disp('file saved!')
    
    % timestamps save
    folderPath = fullfile('Data', subID);
    if ~exist(folderPath, 'dir')
        mkdir(folderPath);
    end
    
    %timestamping
    % triggerCodes = triggerCodes(:);
    % triggerTimestamps = triggerTimestamps(:);
    % eventTimestamps = eventTimestamps(:);
    % eventLabels = eventLabels(:);
    % triggerLog = table(triggerCodes(:), triggerTimestamps(:), eventTimestamps(:), eventLabels, ...
    %            'VariableNames', {'TriggerCode', 'TriggerTime', 'EventTime', 'EventLabel'});
    % 
    % filenameT = ['trigger_log_' subID '_' sessionID '.csv'];
    % fullFilePath = fullfile(folderPath, filenameT);
    % if ~exist(folderPath, 'dir')
    %     mkdir(folderPath);
    % end
    % 
    % writetable(triggerLog, fullFilePath);
    % disp('trigger file saved!')
    
catch errorReport
    
    Screen('CloseAll')
    errorReport.getReport 
    
end % of try

% end of experiment trigger 
if Port.isOn
    
    send_eeg_trigger_usb(Port, 255); 
    fclose(Port.address);

end
