function close_eeg_ports(Port, s)
%
% Closes any open EEG ports and resets the parallel port state to zero
%
% Written by Daniel Feuerriegel at the Decision Neuroscience Lab,
% University of Melbourne


% Close parallel port that was used to send triggers to EEG system
if Port.isOn
    
    if strcmp(Port.type, 'USB')
            
        outputSingleScan(s, [0 0 0 0 0 0 0 0]);

    elseif strcmp(Port.type, 'Parallel')

        clear ioObj; % Close the parallel port

    end % of if strcmp
        
end % of if Port.isOn