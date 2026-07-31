function [direction] = createDirectionVector()
%CREATEDIRECTIONVECTOR 
%   Creates a vector that adequately indicates the direction of the motion
%   PLEASE FIND A BETTER WAY TO DO THIS.

direction = Expand([0 1]',1,8);

direction = vertcat(direction, direction, direction, direction);
direction = vertcat(direction, direction, direction, direction);
direction = vertcat(direction, direction, direction, direction);

direction = direction(1:896,:);
end

