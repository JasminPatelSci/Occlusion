function send_event_trigger_neurospec(serial_object, trigger_duration, event_code)

% Send a trigger over the serial port, as defined in 'event_code'
% There is an imposed delay (duration) of 'trigger_duration' seconds
% and then the port is flushed again with zero, ready for next use.
%
% The trigger_duration variable is in seconds, and should be at least one
% sample duration of the EEG recording device. E.g., if sample rate is
% 500Hz, then trigger_duration should be at least 0.002  i.e., 2ms.

fwrite(serial_object, event_code); % Send the trigger
WaitSecs(trigger_duration); % Wait for the trigger duration

fwrite(serial_object, 0); % Reset to event code to 0

% Note: resetting not required in 'Pulse' mode, but retaining here just in
% case the hardware is changed to 'Simple' mode for consistency across
% these firmware settings.

fwrite('COM1', 1)

end % Of function