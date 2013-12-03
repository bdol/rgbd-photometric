%% One image
clear; close all;
I = imread('~/Desktop/dframes/depth_00019.png');
I = I(44:212, 131:220);
I(I>489) = 0;
D = depth_to_cloud(double(I));
N = pcnormal(D);
imshow(N);
imwrite(N, 'normals.png');

%% Averaged over 100 frames
clear; close all;
F = dir('~/Desktop/dframes/');
D_sum = zeros(169, 90, 3);
c = 0;
t = CTimeleft(100);
for i=3:102
    t.timeleft();
    I = imread(['~/Desktop/dframes/' F(i).name]);
    I = I(44:212, 131:220);
    I(I>489) = 0;
    D = depth_to_cloud(double(I));
    D_sum = D_sum+D;
    c = c+1;
end
N = pcnormal(D_sum/c);
imshow(N);

%% Averaged over all frames
clear; close all;
F = dir('~/Desktop/dframes/');
D_sum = zeros(169, 90, 3);
c = 0;
t = CTimeleft(numel(F)-2);
for i=3:numel(F)
    t.timeleft();
    I = imread(['~/Desktop/dframes/' F(i).name]);
    I = I(44:212, 131:220);
    I(I>489) = 0;
    D = depth_to_cloud(double(I));
    D_sum = D_sum+D;
    c = c+1;
end
depth = D_sum(:, :, 3);
depth(depth/c<300) = 0;
D_sum(:, :, 3) = depth;
N = pcnormal(D_sum/c);
imshow(N);
imwrite(N, 'normals_averaged.png');
