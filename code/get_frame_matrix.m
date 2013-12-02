function M = get_frame_matrix(rootFramesPath, cropRect)

if nargin<2
   cropRect = [1 1 320 240]; 
end

M = [];
files = dir(rootFramesPath);
t = CTimeleft(numel(files));
for i=1:numel(files)
    t.timeleft();
    if ~strcmp(files(i).name(1), '.') % skip the '.' files
        f = [rootFramesPath files(i).name];
        I = imread(f);
        I = rgb2gray(imcrop(I, cropRect));
        M = [M; I(:)'];
    end
    
end



end