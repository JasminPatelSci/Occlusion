function send_port_codes_usb(s, stimCode, pulseDuration)
%
% This function sends a trigger code through the USB to parallel port
% interface.
%
%
% Written by Daniel Feuerriegel for the Change of Mind Project at the
% University of Melbourne

% Use the USB-to-parallel-port converter to send port codes

outputSingleScan(s, dec2binvec(stimCode, 8)); % sends the trigger

% WaitSecs(pulseDuration); % Duration of the trigger pulse

outputSingleScan(s, [0 0 0 0 0 0 0 0]); % Stop sending a trigger
