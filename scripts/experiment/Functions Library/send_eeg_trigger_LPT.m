function send_eeg_trigger_LPT(Port, eventCode)
%
% This function sends EEG event codes via a Parallel Port Card 
% Sunix 1-Port Parallel Card (PCIe) on Windows 10. 
%
% Written by William Turner 6/2023
if Port.isOn
    
io64(Port.ioObj,Port.address,eventCode);   
WaitSecs(Port.EventTriggerDuration);
io64(Port.ioObj,Port.address,0);   

end
