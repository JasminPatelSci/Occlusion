function [qDown]=HH_checkQuit
%
% Checks for the Q key to be down. Use to abort while loops during
% debugging. ie (if HH_checkQuit 
%                   break
%                end)
%

% Hinze: 14-05-2009: Revised to tolerate other buttons always being down
%

qDown=0;
[keyIsDown,secs,keyCode] = KbCheck;
if keyCode(KbName('q')),
    qDown=1;
end