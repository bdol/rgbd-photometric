function M = get_frame_matrix(rootFramesPath, cropRect)

if nargin<2
   cropRect = [1 1 320 240]; 
end

M = [];
minVal = 1000; maxVal = -1;

files = dir(rootFramesPath);
t = CTimeleft(numel(files));

for i=1:numel(files)
    t.timeleft();
    if ~strcmp(files(i).name(1), '.') % skip the '.' files
        f = [rootFramesPath files(i).name];
        I = imread(f);
        I = double(rgb2gray(imcrop(I, cropRect)));
        
        mn = min(I(:));
        mx = max(I(:));
        if mn<minVal
            minVal = mn;
        end
        
        if mx>maxVal
            maxVal = mx;
        end
        
        M = [M; I(:)'];
    end
    
end

% Normalize
M = bsxfun(@minus, M, minVal);
M = bsxfun(@rdivide, M, maxVal-minVal);


end