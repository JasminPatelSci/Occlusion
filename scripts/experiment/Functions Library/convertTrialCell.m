function [TrialList] = convertTrialCell(TrialCell)
%converts cell array to matrix

%adds zeroes to make every cell the same length
FirstNCols = @(M,n) M(:,1:n);
PadToN = @(M,n) FirstNCols([M, zeros(size(M,1),n)], n);
width_needed = max( cellfun(@(M) size(M,2), TrialCell) );
PaddedTrialCell = cellfun(@(M) PadToN(M, width_needed), TrialCell, 'uniform', 0);

TrialList = cell2mat(PaddedTrialCell);
end

