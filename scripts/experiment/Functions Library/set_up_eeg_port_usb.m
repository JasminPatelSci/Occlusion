function [Port, s, ch] = set_up_eeg_port_usb(Port)
% 
% This function sets up the parallel port for sending EEG triggers to the
% Biosemi EEG system (or whatever system is being used). This function sets
% up the USB to parallel port interface, and creates the objects 's' and
% 'ch' for this purpose.
%
% For setting up the parallel port without using a USB interface see the
% function comtrak_set_up_eeg_port
%
% Written by Daniel Feuerriegel for the Change of Mind project at the
% University of Melbourne
% 
% 
% 
        
s = daq.createSession('ni'); % Initialise the session

ch = addDigitalChannel(s, 'Dev1', 'Port2/Line0:7', 'OutputOnly'); % Setup 8-bit range of triggers

Port.pulseDuration = 0.002; % Duration of triggers for Biosemi

% Reset triggers to zero (in case someone left parallel ports open)
outputSingleScan(s, [0 0 0 0 0 0 0 0]);