function [pclouds, distance] = depth_to_cloud(depth, topleft)
% Category and instance recognition using the rgb channel
% Written by Liefeng Bo on March 26, 2011


if nargin < 2
    topleft = [1 1];
end

% Primesense constants
center = [320 240];
[imh, imw] = size(depth);
constant = 570.3;

% convert depth image to 3d point clouds
pclouds = zeros(imh,imw,3);
xgrid = ones(imh,1)*(1:imw) + (topleft(1)-1) - center(1);
ygrid = (1:imh)'*ones(1,imw) + (topleft(2)-1) - center(2);
pclouds(:,:,1) = xgrid.*depth/constant;
pclouds(:,:,2) = ygrid.*depth/constant;
pclouds(:,:,3) = depth;
distance = sqrt(sum(pclouds.^2,3));

