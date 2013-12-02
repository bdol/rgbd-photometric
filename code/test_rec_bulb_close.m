M = get_frame_matrix('~/code/datasets/photometric/bulb_close/frames/rgb/', [40 20 120 160]);

%%
MSub = M(1:30, :);
[U S V] = svd(MSub);
r = 4;
d_fr = S(:, 1:r);
d_rn = S(1:r, :);

%%
L_tilde = U*sqrt(d_fr);
S_tilde = sqrt(d_rn)*V;
S_tilde = bsxfun(@rdivide, S_tilde, sqrt(sum(S_tilde.*S_tilde, 2)));