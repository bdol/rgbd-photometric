clear; close all;
I = imread('~/Dropbox/depth_00019.png');
I = I(44:212, 131:220);
I(I>489) = 0;
D = depthtocloud(double(I));
N = pcnormal(D);
imwrite(N, 'normals.png');