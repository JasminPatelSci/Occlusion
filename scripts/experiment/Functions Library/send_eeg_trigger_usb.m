function send_eeg_trigger_usb(Port, eventCode)
%
% This function sends EEG event codes via the vitrual COM port box (big
% yellow N shape!). 
%
% Written by William Turner 7/2024
if Port.isOn

    fwrite(Port.address,eventCode);
    WaitSecs(Port.EventTriggerDuration);
    fwrite(Port.address,0);
    
end
