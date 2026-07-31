function send_eeg_event_codes(Port, eventCodeNo, s)
%
% This function sends EEG event codes via either the USB interface of the
% parallel port.
%
% Written by Daniel Feuerriegel, 4/18

if Port.isOn
            
    if strcmp(Port.type, 'USB') % If using USB to parallel port converter

        send_port_codes_usb(s, eventCodeNo, Port.pulseDuration)

    elseif strcmp(Port.type, 'Parallel') % If using parallel port directly

        send_port_codes(Port.ioObj, Port.address, eventCodeNo, Port.pulseDuration)

    end % of if strcmp Parallel/USB

end % of if Port.isOn